"""Lire un notebook marimo, ou des corps de cellules, sans importer marimo.

Deux entrées :

- `lire_fichier(chemin)` : le format fichier (`@app.cell`, `@app.function`,
  `@app.class_definition`, `with app.setup:`), tel que marimo l'écrit ;
- `lire_corps(codes)` : des corps de cellules, tels que `ctx.cells[...].code` les donne en
  code mode, ou tels qu'un assistant s'apprête à les insérer.

Pour chaque cellule on calcule ce qu'elle définit et ce qu'elle lit. Le calcul passe par
`symtable`, appliqué au corps enveloppé dans une fonction asynchrone : un `await` de premier
niveau, permis dans une cellule, reste ainsi analysable.
"""

from __future__ import annotations

import ast
import re
import symtable
from dataclasses import dataclass, field
from pathlib import Path

ENTETE_PEP723 = re.compile(r"(?m)^# /// script\s*$(?P<corps>(?:\n#.*)*?)\n# ///\s*$")


@dataclass
class Cellule:
    index: int
    genre: str  # "cell", "function", "class", "setup"
    instructions: list[ast.stmt]
    code: str
    nom: str | None = None
    ligne: int = 1  # ligne de la cellule dans le fichier (ou 1 pour un corps)
    decalage: int = 0  # à ajouter aux numéros de ligne des nœuds pour retrouver le fichier
    hide_code: bool = False
    definitions: set[str] = field(default_factory=set)
    lectures: set[str] = field(default_factory=set)
    imports: dict[str, str] = field(default_factory=dict)  # nom lié -> module importé
    retour_final: bool = False  # un `return` de premier niveau dans un corps (mode corps)
    erreur_syntaxe: str | None = None

    @property
    def etiquette(self) -> str:
        if self.nom and self.nom != "_":
            return f"cellule {self.index + 1} « {self.nom} »"
        return f"cellule {self.index + 1}"


@dataclass
class Carnet:
    cellules: list[Cellule]
    chemin: Path | None = None
    source: str = ""
    entete: str | None = None  # contenu du bloc PEP 723, sans les dièses
    mode: str = "fichier"  # "fichier" ou "corps"
    complet: bool = True  # False : des cellules du notebook manquent, un nom inconnu peut y être défini

    def proprietaire(self, nom: str) -> Cellule | None:
        for cellule in self.cellules:
            if nom in cellule.definitions:
                return cellule
        return None

    @property
    def definitions(self) -> set[str]:
        return set().union(*(c.definitions for c in self.cellules)) if self.cellules else set()


def _est_decorateur_app(deco: ast.expr, nom: str) -> bool:
    cible = deco.func if isinstance(deco, ast.Call) else deco
    return isinstance(cible, ast.Attribute) and cible.attr == nom and isinstance(cible.value, ast.Name)


def _hide_code(deco: ast.expr) -> bool:
    if isinstance(deco, ast.Call):
        for mot in deco.keywords:
            if mot.arg == "hide_code" and isinstance(mot.value, ast.Constant):
                return bool(mot.value.value)
    return False


PORTEES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
           ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def definitions_de(instructions: list[ast.stmt]) -> set[str]:
    """Les noms liés au premier niveau d'une cellule, sans entrer dans les fonctions ni les compréhensions.

    `symtable` ne suffit pas ici : depuis Python 3.12, les variables d'une compréhension
    apparaissent comme des locaux de la fonction qui la contient.
    """
    noms: set[str] = set()
    pile: list[ast.AST] = list(instructions)
    while pile:
        noeud = pile.pop()
        if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            noms.add(noeud.name)
            pile.extend(noeud.decorator_list)
            continue
        if isinstance(noeud, PORTEES):
            continue
        if isinstance(noeud, ast.Name) and isinstance(noeud.ctx, ast.Store):
            noms.add(noeud.id)
        elif isinstance(noeud, ast.Import):
            noms.update(alias.asname or alias.name.split(".")[0] for alias in noeud.names)
        elif isinstance(noeud, ast.ImportFrom):
            noms.update(alias.asname or alias.name for alias in noeud.names if alias.name != "*")
        elif isinstance(noeud, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and noeud.name:
            noms.add(noeud.name)
        elif isinstance(noeud, ast.MatchMapping) and noeud.rest:
            noms.add(noeud.rest)
        pile.extend(ast.iter_child_nodes(noeud))
    return noms


def _noms_lies(fonction_table: symtable.SymbolTable, definitions: set[str]) -> set[str]:
    """Ce que le corps lit sans le définir (les globaux de l'enveloppe et de ses fonctions)."""
    lectures: set[str] = set()

    def parcourir(table: symtable.SymbolTable, locaux_parents: set[str]) -> None:
        for symbole in table.get_symbols():
            nom = symbole.get_name()
            if symbole.is_referenced() and symbole.is_global() and nom not in locaux_parents:
                lectures.add(nom)
            if symbole.is_declared_global() and (symbole.is_referenced() or symbole.is_assigned()):
                lectures.add(nom)
        locaux = locaux_parents | {s.get_name() for s in table.get_symbols() if s.is_local()}
        for enfant in table.get_children():
            parcourir(enfant, locaux)

    parcourir(fonction_table, set())
    return lectures - definitions


def analyser(instructions: list[ast.stmt]) -> tuple[set[str], set[str], dict[str, str], str | None]:
    """Définitions, lectures et imports d'un corps de cellule."""
    enveloppe = ast.parse("async def __cellule__():\n    pass\n")
    enveloppe.body[0].body = list(instructions) or [ast.Pass()]
    ast.fix_missing_locations(enveloppe)
    try:
        table = symtable.symtable(ast.unparse(enveloppe), "<cellule>", "exec")
    except SyntaxError as erreur:
        return set(), set(), {}, str(erreur)
    fonction = table.get_children()[0]
    definitions = definitions_de(instructions)
    lectures = _noms_lies(fonction, definitions)
    imports: dict[str, str] = {}
    for noeud in instructions:
        for sous in ast.walk(noeud):
            if isinstance(sous, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue
            if isinstance(sous, ast.Import):
                for alias in sous.names:
                    imports[alias.asname or alias.name.split(".")[0]] = alias.name if alias.asname else alias.name.split(".")[0]
            elif isinstance(sous, ast.ImportFrom) and sous.level == 0 and sous.module:
                for alias in sous.names:
                    imports[alias.asname or alias.name] = f"{sous.module}.{alias.name}"
    return definitions, lectures, imports, None


def _sans_app(noeud):
    """La définition sans ses décorateurs `@app.…`, qui appartiennent au fichier et pas à la cellule."""
    import copy

    copie = copy.copy(noeud)
    copie.decorator_list = [d for d in noeud.decorator_list
                            if not (_est_decorateur_app(d, "function") or _est_decorateur_app(d, "class_definition"))]
    return copie


def _segment(lignes: list[str], debut: int, fin: int) -> str:
    import textwrap

    return textwrap.dedent("\n".join(lignes[debut - 1:fin]))


def lire_entete(source: str) -> str | None:
    trouve = ENTETE_PEP723.search(source)
    if not trouve:
        return None
    return "\n".join(ligne[2:] if ligne.startswith("# ") else ligne[1:] for ligne in trouve.group("corps").splitlines() if ligne)


def lire_source(source: str, chemin: Path | None = None) -> Carnet:
    arbre = ast.parse(source)
    lignes = source.splitlines()
    cellules: list[Cellule] = []
    for noeud in arbre.body:
        if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decos = noeud.decorator_list
            if any(_est_decorateur_app(d, "cell") for d in decos):
                corps = list(noeud.body)
                retour = bool(corps) and isinstance(corps[-1], ast.Return)
                if retour:
                    corps = corps[:-1]
                code = _segment(lignes, corps[0].lineno, corps[-1].end_lineno or corps[-1].lineno) if corps else ""
                cellule = Cellule(index=len(cellules), genre="cell", instructions=corps, code=code, nom=noeud.name,
                                  ligne=noeud.lineno, hide_code=any(_hide_code(d) for d in decos))
            elif any(_est_decorateur_app(d, "function") for d in decos):
                fin = noeud.end_lineno or noeud.lineno
                cellule = Cellule(index=len(cellules), genre="function", instructions=[_sans_app(noeud)], nom=noeud.name,
                                  code=_segment(lignes, noeud.lineno, fin), ligne=noeud.lineno)
            else:
                continue
        elif isinstance(noeud, ast.ClassDef) and any(_est_decorateur_app(d, "class_definition") for d in noeud.decorator_list):
            cellule = Cellule(index=len(cellules), genre="class", instructions=[_sans_app(noeud)], nom=noeud.name,
                              code=_segment(lignes, noeud.lineno, noeud.end_lineno or noeud.lineno), ligne=noeud.lineno)
        elif isinstance(noeud, ast.With) and any(
            isinstance(item.context_expr, ast.Attribute) and item.context_expr.attr == "setup" for item in noeud.items
        ):
            corps = list(noeud.body)
            cellule = Cellule(index=len(cellules), genre="setup", instructions=corps, nom="setup", ligne=noeud.lineno,
                              code=_segment(lignes, corps[0].lineno, corps[-1].end_lineno or corps[-1].lineno) if corps else "")
        else:
            continue
        cellule.definitions, cellule.lectures, cellule.imports, cellule.erreur_syntaxe = analyser(cellule.instructions)
        if cellule.genre in ("function", "class"):
            cellule.definitions.add(cellule.nom or "")
        cellules.append(cellule)
    return Carnet(cellules=cellules, chemin=chemin, source=source, entete=lire_entete(source), mode="fichier")


def lire_fichier(chemin: str | Path) -> Carnet:
    chemin = Path(chemin)
    return lire_source(chemin.read_text(encoding="utf-8"), chemin)


def est_notebook(source: str) -> bool:
    return "marimo.App(" in source and ("@app.cell" in source or "app.setup" in source or "@app.function" in source)


def lire_corps(codes: list[str], noms: list[str | None] | None = None, complet: bool = False) -> Carnet:
    """Des corps de cellules (sans `@app.cell` ni `return`), dans l'ordre du notebook.

    `complet=True` quand `codes` contient toutes les cellules du notebook : on peut alors dire
    qu'un nom n'est défini nulle part.
    """
    cellules = []
    for index, code in enumerate(codes):
        nom = noms[index] if noms and index < len(noms) else None
        try:
            arbre = ast.parse(code, type_comments=False, feature_version=None)
            erreur = None
        except SyntaxError as exc:
            # un `await` de premier niveau est permis dans une cellule : on réessaie dans une fonction
            try:
                enveloppe = ast.parse("async def __c__():\n" + "\n".join("    " + ligne for ligne in code.splitlines()))
                arbre = ast.Module(body=enveloppe.body[0].body, type_ignores=[])
                erreur = None
                for noeud in ast.walk(arbre):
                    if hasattr(noeud, "lineno"):
                        noeud.lineno -= 1
                        if getattr(noeud, "end_lineno", None):
                            noeud.end_lineno -= 1
            except SyntaxError:
                arbre, erreur = ast.Module(body=[], type_ignores=[]), f"{exc.msg} (ligne {exc.lineno})"
        cellule = Cellule(index=index, genre="cell", instructions=list(arbre.body), code=code, nom=nom)
        cellule.retour_final = any(isinstance(n, ast.Return) for n in arbre.body)
        cellule.definitions, cellule.lectures, cellule.imports, erreur_analyse = analyser(cellule.instructions)
        cellule.erreur_syntaxe = erreur or erreur_analyse
        cellules.append(cellule)
    return Carnet(cellules=cellules, mode="corps", complet=complet)


def joindre(carnet: Carnet, nouvelles: list[str]) -> Carnet:
    """Le notebook suivi des cellules qu'un agent s'apprête à ajouter, analysé comme un tout."""
    proposees = lire_corps(nouvelles)
    depart = len(carnet.cellules)
    for decalage, cellule in enumerate(proposees.cellules):
        cellule.index = depart + decalage
        cellule.nom = cellule.nom or f"proposée {decalage + 1}"
    return Carnet(cellules=[*carnet.cellules, *proposees.cellules], chemin=carnet.chemin, source=carnet.source,
                  entete=carnet.entete, mode="corps", complet=carnet.complet)
