"""Les règles : ce que `marimo check` ne voit pas et qu'un agent écrit souvent de travers.

Chaque règle a un code `AGnnn`, une gravité, une raison et une correction. La gravité dit ce
que l'agent doit en faire :

- `erreur` : la cellule plante, ou montre un résultat faux. À corriger avant de rendre la main.
- `avertissement` : le notebook tourne, mais la réactivité ou la lecture en souffre. À corriger,
  sauf raison dite à l'utilisateur.
- `conseil` : lisibilité pour un humain. À appliquer quand c'est simple.

Les règles ne lisent que la syntaxe : elles ne connaissent pas les types. Une règle qui se
trompe se désactive par `--ignorer AG101` ; sa raison est dans `reference/regles.md`.
"""

from __future__ import annotations

import ast
import builtins
import re
import sys
from collections.abc import Callable, Iterator
from dataclasses import asdict, dataclass

from .carnet import Carnet, Cellule

GRAVITES = ("erreur", "avertissement", "conseil")


@dataclass
class Diagnostic:
    code: str
    nom: str
    gravite: str
    message: str
    correction: str
    cellule: int | None = None  # index à partir de 0
    etiquette: str = ""
    ligne: int | None = None
    source: str = "regles"

    def en_dict(self) -> dict:
        return asdict(self)


@dataclass
class Regle:
    code: str
    nom: str
    gravite: str
    resume: str
    pourquoi: str
    correction: str
    fonction: Callable[[Carnet, Contexte], Iterator[tuple[Cellule | None, ast.AST | None, str]]]
    modes: tuple[str, ...] = ("fichier", "corps")


REGLES: dict[str, Regle] = {}


def regle(code: str, nom: str, gravite: str, resume: str, pourquoi: str, correction: str, modes=("fichier", "corps")):
    def enregistrer(fonction):
        REGLES[code] = Regle(code, nom, gravite, resume, pourquoi, correction, fonction, modes)
        return fonction

    return enregistrer


# ---------------------------------------------------------------- outils communs

BUILTINS = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__builtins__", "__spec__", "__loader__", "__package__"}

UI_AFFICHAGE = {"table", "dataframe", "data_explorer", "altair_chart", "plotly", "matplotlib", "tabs", "anywidget"}
UI_ENVELOPPES = {"array", "dictionary", "batch"}
UI_CONTINUS = {"slider", "range_slider", "number", "text", "text_area", "dropdown", "multiselect", "radio",
               "checkbox", "switch", "date", "datetime", "date_range", "code_editor"}
UI_A_ETIQUETTE = UI_CONTINUS | {"button", "run_button", "file"}
MO_AFFICHAGE = {"md", "hstack", "vstack", "callout", "image", "Html", "accordion", "tabs", "mermaid", "as_html", "center",
                "left", "right", "carousel", "sidebar", "plain_text", "json", "tree", "stat", "lazy", "download", "pdf",
                "video", "audio", "iframe", "latex", "nav_menu", "routes", "plain"}
LOURDS = {"fit", "fit_transform", "fit_predict", "train", "minimize", "urlopen", "sample_posterior_predictive",
          "sample_prior_predictive", "find_MAP"}
MODULES_BAYES = {"pymc", "bambi", "numpyro", "nutpie", "pystan", "cmdstanpy"}
MUTANTES = {"append", "extend", "insert", "add", "discard", "clear", "remove", "setdefault", "popitem",
            "insert_column", "drop_in_place"}
MUTANTES_AMBIGUES = {"sort", "reverse", "update", "pop"}  # fonctionnelles sur un DataFrame polars


class Contexte:
    """Ce que les règles partagent : alias de marimo, modules importés, éléments d'interface."""

    def __init__(self, carnet: Carnet):
        self.carnet = carnet
        self.resolution: dict[str, str] = {}
        for cellule in carnet.cellules:
            self.resolution.update(cellule.imports)
        self.mo = {nom for nom, module in self.resolution.items() if module == "marimo"} or {"mo"}
        self.parents: dict[int, ast.AST] = {}
        for cellule in carnet.cellules:
            for instruction in cellule.instructions:
                for noeud in ast.walk(instruction):
                    for enfant in ast.iter_child_nodes(noeud):
                        self.parents[id(enfant)] = noeud
        self.ui: dict[str, str] = {}  # nom public -> genre d'élément ("slider", "form"…)
        self.ui_cellule: dict[str, int] = {}
        for cellule in carnet.cellules:
            for instruction in cellule.instructions:
                if isinstance(instruction, ast.Assign) and len(instruction.targets) == 1:
                    cible = instruction.targets[0]
                    genre = self.genre_ui(instruction.value)
                    if isinstance(cible, ast.Name) and genre:
                        self.ui[cible.id] = genre
                        self.ui_cellule[cible.id] = cellule.index
        self.lectures_ailleurs: dict[int, set[str]] = {}
        for cellule in carnet.cellules:
            autres = set().union(*(c.lectures for c in carnet.cellules if c is not cellule)) if len(carnet.cellules) > 1 else set()
            self.lectures_ailleurs[cellule.index] = autres

    def parent(self, noeud: ast.AST) -> ast.AST | None:
        return self.parents.get(id(noeud))

    def pointe(self, noeud: ast.AST) -> str:
        """`mo.ui.slider` pour un appel ou un attribut ; "" si la forme n'est pas un nom pointé."""
        morceaux = []
        while isinstance(noeud, ast.Attribute):
            morceaux.append(noeud.attr)
            noeud = noeud.value
        if isinstance(noeud, ast.Name):
            morceaux.append(noeud.id)
            return ".".join(reversed(morceaux))
        return ""

    def module_de(self, nom_pointe: str) -> str:
        """`plt.show` -> `matplotlib.pyplot.show`, d'après les imports du notebook."""
        tete, _, reste = nom_pointe.partition(".")
        base = self.resolution.get(tete)
        if base is None:
            return nom_pointe
        return f"{base}.{reste}" if reste else base

    def est_mo(self, nom_pointe: str, *suite: str) -> bool:
        tete, _, reste = nom_pointe.partition(".")
        return tete in self.mo and (not suite or reste in suite)

    def genre_ui(self, noeud: ast.AST) -> str:
        """Le genre d'élément construit par cette expression, ou "" si ce n'en est pas un."""
        if not isinstance(noeud, ast.Call):
            return ""
        fonction = noeud.func
        if isinstance(fonction, ast.Attribute) and fonction.attr in ("form", "batch") and self.genre_ui(fonction.value):
            return fonction.attr
        if isinstance(fonction, ast.Attribute) and fonction.attr == "batch":  # mo.md("…").batch(…)
            return "batch"
        nom = self.pointe(fonction)
        tete, _, reste = nom.partition(".")
        if tete in self.mo and reste.startswith("ui.") and reste.count(".") == 1:
            return reste[3:]
        return ""

    def racine(self, noeud: ast.AST) -> ast.Name | None:
        while isinstance(noeud, (ast.Attribute, ast.Subscript, ast.Call)):
            noeud = noeud.func if isinstance(noeud, ast.Call) else noeud.value
        return noeud if isinstance(noeud, ast.Name) else None


def premier_niveau(instructions: list[ast.stmt]) -> Iterator[ast.AST]:
    """Les nœuds d'une cellule, sans entrer dans les fonctions, classes et lambdas."""
    pile: list[ast.AST] = list(instructions)
    while pile:
        noeud = pile.pop(0)
        yield noeud
        if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        pile.extend(ast.iter_child_nodes(noeud))


def tous(instructions: list[ast.stmt]) -> Iterator[ast.AST]:
    for instruction in instructions:
        yield from ast.walk(instruction)


def cellules_de_code(carnet: Carnet) -> Iterator[Cellule]:
    for cellule in carnet.cellules:
        if cellule.genre in ("cell", "setup"):
            yield cellule


def texte_hors_maths(texte: str) -> str:
    """Masque les formules, le code en ligne et les blocs de code, en gardant les positions."""
    def blanc(m: re.Match) -> str:
        return " " * len(m.group(0))

    for motif in (r"```.*?```", r"`[^`\n]*`", r"\$\$.*?\$\$", r"\\\[.*?\\\]", r"\\\(.*?\\\)", r"(?<!\\)\$[^$\n]+?(?<!\\)\$"):
        texte = re.sub(motif, blanc, texte, flags=re.S)
    return texte


# ---------------------------------------------------------------- erreurs

@regle("AG001", "valeur-ui-meme-cellule", "erreur",
       "Lire `.value` d'un élément d'interface dans la cellule qui le crée.",
       "marimo lève `RuntimeError: Accessing the value of a UIElement in the cell that created it is not allowed`.",
       "Crée l'élément dans une cellule, lis `.value` dans une autre.")
def _valeur_meme_cellule(carnet: Carnet, ctx: Contexte):
    for cellule in carnet.cellules:
        crees = set()
        for instruction in premier_niveau(cellule.instructions):
            if isinstance(instruction, ast.Assign):
                for cible in instruction.targets:
                    if isinstance(cible, ast.Name) and ctx.genre_ui(instruction.value):
                        crees.add(cible.id)
        vus = set()
        for noeud in premier_niveau(cellule.instructions):
            if (isinstance(noeud, ast.Attribute) and noeud.attr == "value" and isinstance(noeud.value, ast.Name)
                    and noeud.value.id in crees and isinstance(noeud.ctx, ast.Load) and noeud.value.id not in vus):
                vus.add(noeud.value.id)
                yield cellule, noeud, f"`{noeud.value.id}.value` est lu dans la cellule qui crée `{noeud.value.id}`."


@regle("AG002", "asyncio-run", "erreur",
       "Appeler `asyncio.run()` ou `run_until_complete()` dans une cellule.",
       "Le noyau de marimo tourne déjà dans une boucle d'événements : l'appel échoue dans l'éditeur, une app et un "
       "export (`asyncio.run() cannot be called from a running event loop`), alors qu'il passe avec `python notebook.py`.",
       "Écris `resultat = await coroutine()` directement dans la cellule : marimo accepte `await` au premier niveau.")
def _asyncio_run(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call):
                nom = ctx.module_de(ctx.pointe(noeud.func))
                if nom == "asyncio.run" or (isinstance(noeud.func, ast.Attribute) and noeud.func.attr == "run_until_complete"):
                    yield cellule, noeud, f"`{ctx.pointe(noeud.func) or 'run_until_complete'}(…)` échouera dans le noyau de marimo."


@regle("AG003", "habitude-jupyter", "erreur",
       "`display()`, `get_ipython()` ou `IPython.display` dans une cellule.",
       "Ces noms n'existent pas dans marimo : `display(df)` lève `NameError`.",
       "Mets l'objet en dernière expression de la cellule, ou `mo.output.append(objet)` pour plusieurs sorties ; "
       "`mo.md`, `mo.Html`, `mo.image` remplacent `IPython.display`.")
def _jupyter(carnet: Carnet, ctx: Contexte):
    definis = carnet.definitions
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Name) and noeud.func.id in ("display", "get_ipython"):
                if noeud.func.id not in definis:
                    yield cellule, noeud, f"`{noeud.func.id}(…)` n'existe pas dans marimo."
            elif isinstance(noeud, ast.ImportFrom) and (noeud.module or "").startswith("IPython"):
                yield cellule, noeud, f"`from {noeud.module} import …` : une habitude de Jupyter."
            elif isinstance(noeud, ast.Import) and any(a.name.startswith("IPython") for a in noeud.names):
                yield cellule, noeud, "`import IPython` : une habitude de Jupyter."


PLACEHOLDER = re.compile(r"(?<![\\\w^_{$])\{([A-Za-z_][A-Za-z0-9_]*)((?:\.[A-Za-z_]\w*|\[[^\]{}]*\])*)(?:![rsa])?(?::[^{}]*)?\}")


@regle("AG004", "md-sans-f", "erreur",
       "`mo.md(\"… {variable} …\")` sans le préfixe `f`.",
       "Sans `f`, marimo affiche les accolades telles quelles : le lecteur voit `{moyenne}` au lieu du nombre.",
       "Ajoute le préfixe : `mo.md(f\"… {variable} …\")` (et `rf\"…\"` s'il y a des antislashs LaTeX).")
def _md_sans_f(carnet: Carnet, ctx: Contexte):
    definis = carnet.definitions
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if not (isinstance(noeud, ast.Call) and ctx.est_mo(ctx.pointe(noeud.func), "md") and noeud.args):
                continue
            argument = noeud.args[0]
            if not (isinstance(argument, ast.Constant) and isinstance(argument.value, str)):
                continue
            parent = ctx.parent(noeud)
            if isinstance(parent, ast.Attribute) and parent.attr in ("batch", "format"):
                continue
            noms = [m.group(1) for m in PLACEHOLDER.finditer(texte_hors_maths(argument.value)) if m.group(1) in definis]
            if noms:
                liste = ", ".join(f"`{{{n}}}`" for n in dict.fromkeys(noms))
                yield cellule, noeud, f"{liste} sera affiché tel quel : la chaîne n'est pas une f-string."


SECRETS = re.compile(r"\b(sk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|"
                     r"glpat-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|hf_[A-Za-z0-9]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|"
                     r"AIza[0-9A-Za-z_-]{35})\b")
NOM_SECRET = re.compile(r"(?i)(api_?key|apikey|token|secret|password|passwd|mot_?de_?passe|mdp|credential)")
FACTICE = re.compile(r"(?i)(<|>|xxx|\.\.\.|changeme|votre|your|exemple|example|placeholder|dummy|\$\{|todo)")


@regle("AG005", "secret-en-clair", "erreur",
       "Une clé d'API, un jeton ou un mot de passe écrit dans le code.",
       "Le code d'un notebook part avec lui : dans git, dans un export HTML ou WASM, dans le contexte envoyé à "
       "l'assistant d'IA.",
       "Lis-le dans l'environnement (`os.environ[\"NOM\"]`), ou demande-le par `mo.ui.text(kind=\"password\")`.")
def _secret(carnet: Carnet, ctx: Contexte):
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str) and SECRETS.search(noeud.value):
                yield cellule, noeud, "Cette chaîne a la forme d'une clé d'API."
            elif isinstance(noeud, (ast.Assign, ast.AnnAssign, ast.keyword)):
                valeur = noeud.value
                if isinstance(noeud, ast.keyword):
                    noms = [noeud.arg or ""]
                elif isinstance(noeud, ast.Assign):
                    noms = [c.id for c in noeud.targets if isinstance(c, ast.Name)]
                else:
                    noms = [noeud.target.id] if isinstance(noeud.target, ast.Name) else []
                if (isinstance(valeur, ast.Constant) and isinstance(valeur.value, str) and len(valeur.value) >= 8
                        and " " not in valeur.value and not FACTICE.search(valeur.value)
                        and any(NOM_SECRET.search(n) for n in noms) and not SECRETS.search(valeur.value)):
                    yield cellule, noeud, f"`{noms[0]}` reçoit une valeur écrite en clair."


@regle("AG006", "code-mode-dans-cellule", "erreur",
       "Importer `marimo._code_mode` dans une cellule.",
       "C'est une API privée réservée au bloc-notes temporaire de marimo pair ; elle change sans préavis.",
       "Garde `import marimo._code_mode as cm` dans `marimo pair execute`, jamais dans le notebook.")
def _code_mode(carnet: Carnet, ctx: Contexte):
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Import) and any(a.name.startswith("marimo._code_mode") for a in noeud.names):
                yield cellule, noeud, "`import marimo._code_mode` dans une cellule."
            elif isinstance(noeud, ast.ImportFrom) and (noeud.module == "marimo._code_mode" or (
                    noeud.module == "marimo" and any(a.name == "_code_mode" for a in noeud.names))):
                yield cellule, noeud, "`marimo._code_mode` importé dans une cellule."


@regle("AG007", "nom-indefini", "erreur",
       "Lire un nom qu'aucune cellule ne définit, ou un nom privé (`_x`) défini dans une autre cellule.",
       "La cellule lèvera `NameError`. Un nom qui commence par `_` reste local à sa cellule.",
       "Définis le nom dans une cellule, corrige la faute de frappe, ou retire le `_` du nom partagé.")
def _nom_indefini(carnet: Carnet, ctx: Contexte):
    if not carnet.complet:
        return
    definis = carnet.definitions
    for cellule in carnet.cellules:
        if cellule.erreur_syntaxe:
            continue
        for nom in sorted(cellule.lectures):
            if nom in BUILTINS or nom in ("display", "get_ipython"):  # AG003 s'en charge
                continue
            noeud = next((n for n in tous(cellule.instructions) if isinstance(n, ast.Name) and n.id == nom), None)
            if nom not in definis:
                yield cellule, noeud, f"`{nom}` n'est défini par aucune cellule."
            elif nom.startswith("_") and nom != "_":
                proprietaire = carnet.proprietaire(nom)
                ou = proprietaire.etiquette if proprietaire else "une autre cellule"
                yield cellule, noeud, f"`{nom}` est privé à la {ou} : il n'existe pas ici."


@regle("AG008", "corps-au-format-fichier", "erreur",
       "Un corps de cellule envoyé à code mode contient `return`, `@app.cell` ou `app = marimo.App`.",
       "`create_cell` et `edit_cell` prennent le contenu de la cellule, pas l'enveloppe du fichier.",
       "Envoie seulement les instructions de la cellule ; marimo calcule les entrées et les sorties.",
       modes=("corps",))
def _corps_format_fichier(carnet: Carnet, ctx: Contexte):
    for cellule in carnet.cellules:
        if cellule.retour_final:
            noeud = next((n for n in cellule.instructions if isinstance(n, ast.Return)), None)
            yield cellule, noeud, "`return` au premier niveau d'un corps de cellule."
        if "@app.cell" in cellule.code or "marimo.App(" in cellule.code:
            yield cellule, None, "Le corps contient l'enveloppe du fichier (`@app.cell` ou `marimo.App`)."


@regle("AG009", "nom-redefini", "erreur",
       "Un nom public défini par deux cellules.",
       "marimo refuse le notebook (`Multiply-defined names`) ; en code mode, tout le lot de modifications est rejeté.",
       "Modifie la cellule propriétaire, ou donne un nouveau nom au résultat (`propre = df.dropna()`).",
       modes=("corps",))
def _redefini(carnet: Carnet, ctx: Contexte):
    vus: dict[str, Cellule] = {}
    for cellule in carnet.cellules:
        for nom in sorted(cellule.definitions):
            if nom.startswith("_"):
                continue
            if nom in vus:
                yield cellule, None, f"`{nom}` est déjà défini par la {vus[nom].etiquette}."
            else:
                vus[nom] = cellule


# ---------------------------------------------------------------- avertissements

@regle("AG101", "mutation-inter-cellules", "avertissement",
       "Modifier en place un objet défini dans une autre cellule (`df[\"c\"] = …`, `liste.append`, `inplace=True`).",
       "marimo suit les noms, pas les mutations : les cellules qui lisent l'objet ne sont pas relancées, et relancer "
       "cette cellule applique la mutation une seconde fois.",
       "Crée un nouvel objet (`df2 = df.assign(c=…)`, `df.with_columns(…)`, `liste2 = [*liste, x]`) ou fais la "
       "modification dans la cellule qui définit l'objet.")
def _mutation(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        etrangers = {n for n in cellule.lectures if n not in BUILTINS and n not in ctx.resolution and n not in ctx.ui}
        finale = cellule.instructions[-1] if cellule.instructions else None
        for noeud in premier_niveau(cellule.instructions):
            cibles: list[ast.AST] = []
            if isinstance(noeud, ast.Assign):
                cibles = list(noeud.targets)
            elif isinstance(noeud, (ast.AugAssign, ast.AnnAssign)):
                cibles = [noeud.target]
            elif isinstance(noeud, ast.Delete):
                cibles = list(noeud.targets)
            for cible in cibles:
                if isinstance(cible, (ast.Subscript, ast.Attribute)):
                    racine = ctx.racine(cible)
                    if racine is not None and racine.id in etrangers:
                        yield cellule, noeud, f"`{racine.id}` (défini dans une autre cellule) est modifié en place."
            if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute):
                racine = ctx.racine(noeud.func.value)
                if racine is None or racine.id not in etrangers:
                    continue
                en_place = any(m.arg == "inplace" and isinstance(m.value, ast.Constant) and m.value.value is True
                               for m in noeud.keywords)
                instruction = ctx.parent(noeud)
                seule = isinstance(instruction, ast.Expr) and instruction.value is noeud
                ambigu = noeud.func.attr in MUTANTES_AMBIGUES and seule and instruction is not finale
                appel = ast.unparse(noeud.func)
                appel = appel if len(appel) <= 40 else appel[:37] + "…"
                if ambigu and not en_place:
                    yield cellule, noeud, (f"`{appel}(…)` : sur une liste, il modifie en place un objet d'une autre "
                                           "cellule ; sur un DataFrame, son résultat est perdu.")
                elif en_place or (noeud.func.attr in MUTANTES and seule):
                    yield cellule, noeud, f"`{appel}(…)` modifie en place un objet d'une autre cellule (`{racine.id}`)."


@regle("AG102", "ui-non-liee", "avertissement",
       "Un élément d'interface qui n'est pas affecté à un nom public (dans une liste, dans `mo.hstack`, ou `_nom`).",
       "marimo ne relance les cellules qu'à partir d'un élément lié à une variable globale : toucher ce curseur ne "
       "fera rien, et sa valeur n'est lisible nulle part.",
       "Affecte-le à un nom public (`seuil = mo.ui.slider(…)`) dans sa propre instruction ; pour une liste ou un "
       "dictionnaire d'éléments, utilise `mo.ui.array([...])` ou `mo.ui.dictionary({...})`.")
def _ui_non_liee(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in premier_niveau(cellule.instructions):
            genre = ctx.genre_ui(noeud) if isinstance(noeud, ast.Call) else ""
            if not genre or genre in UI_AFFICHAGE or genre in ("form", "batch"):
                continue
            # On remonte jusqu'à l'instruction ; une enveloppe (`mo.ui.array`, `.form()`, `.batch()`) absorbe
            # l'élément : c'est elle qui doit être liée à un nom public.
            courant, haut, en_liste, dans_appel = noeud, ctx.parent(noeud), False, False
            while haut is not None and not isinstance(haut, ast.stmt):
                if isinstance(haut, ast.Call) and ctx.genre_ui(haut) in UI_ENVELOPPES | {"form", "batch"}:
                    courant = haut
                elif isinstance(haut, ast.IfExp) and courant in (haut.body, haut.orelse):
                    courant = haut  # `a = mo.ui.slider(…) if x else mo.ui.number(…)`
                elif isinstance(haut, ast.Call):
                    dans_appel = True
                elif isinstance(haut, (ast.List, ast.ListComp, ast.Dict, ast.DictComp, ast.Tuple, ast.SetComp)) and courant is noeud:
                    en_liste = True
                haut = ctx.parent(haut)
            cible = _cible_publique(haut, courant)
            if cible is True:
                continue
            if isinstance(cible, str):
                yield cellule, noeud, f"`mo.ui.{genre}` est lié à `{cible}`, un nom privé : ses changements ne relancent rien."
            elif en_liste and not dans_appel:
                yield cellule, noeud, f"`mo.ui.{genre}(…)` est rangé dans une liste ou un dictionnaire ordinaire : utilise `mo.ui.array` ou `mo.ui.dictionary`."
            else:
                yield cellule, noeud, f"`mo.ui.{genre}(…)` n'est affecté à aucun nom public : il ne déclenchera rien."


def _cible_publique(instruction: ast.AST, valeur: ast.AST) -> bool | str:
    """True si `valeur` est affectée à un nom public ; le nom s'il est privé ; False sinon."""
    if isinstance(instruction, ast.AnnAssign) and instruction.value is not None:
        cible = instruction.target
    elif isinstance(instruction, ast.Assign) and len(instruction.targets) == 1:
        cible = instruction.targets[0]
    else:
        return False
    if instruction.value is valeur and isinstance(cible, ast.Name):
        return True if not cible.id.startswith("_") else cible.id
    if isinstance(cible, ast.Tuple) and isinstance(instruction.value, ast.Tuple):
        for c, v in zip(cible.elts, instruction.value.elts, strict=False):
            if v is valeur and isinstance(c, ast.Name):
                return True if not c.id.startswith("_") else c.id
    return False


@regle("AG103", "bouton-sans-action", "avertissement",
       "Lire `.value` d'un `mo.ui.button` créé sans `on_click`.",
       "La valeur d'un `mo.ui.button` sans `on_click` reste `None` : `if bouton.value:` n'est jamais vrai.",
       "Pour lancer un calcul : `lancer = mo.ui.run_button(label=\"…\")`, puis `mo.stop(not lancer.value)` dans la "
       "cellule du calcul. Pour compter des clics : `on_click=lambda n: n + 1, value=0`.")
def _bouton(carnet: Carnet, ctx: Contexte):
    lus = set()
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Attribute) and noeud.attr == "value" and isinstance(noeud.value, ast.Name):
                lus.add(noeud.value.id)
    for cellule in carnet.cellules:
        for instruction in cellule.instructions:
            if isinstance(instruction, ast.Assign) and isinstance(instruction.value, ast.Call):
                appel = instruction.value
                if ctx.genre_ui(appel) == "button" and not any(m.arg in ("on_click", "on_change") for m in appel.keywords):
                    for cible in instruction.targets:
                        if isinstance(cible, ast.Name) and cible.id in lus:
                            yield cellule, instruction, f"`{cible.id}` est un `mo.ui.button` sans `on_click` : `{cible.id}.value` vaut toujours `None`."


@regle("AG104", "garde-if-valeur", "avertissement",
       "Un `if element.value:` qui définit un nom lu par d'autres cellules, sans `else`.",
       "Quand la condition est fausse, le nom n'existe pas : les cellules qui le lisent affichent une erreur "
       "(`Name … is not defined`) au lieu d'attendre.",
       "En tête de cellule : `mo.stop(not lancer.value, mo.md(\"Clique sur **Lancer** pour calculer.\"))`, puis le "
       "calcul sans `if`.")
def _garde_if(carnet: Carnet, ctx: Contexte):
    from .carnet import definitions_de

    for cellule in cellules_de_code(carnet):
        lus_ailleurs = ctx.lectures_ailleurs.get(cellule.index, set())
        for instruction in cellule.instructions:
            if not isinstance(instruction, ast.If):
                continue
            teste_valeur = any(isinstance(n, ast.Attribute) and n.attr == "value" and isinstance(n.value, ast.Name)
                               and n.value.id in cellule.lectures for n in ast.walk(instruction.test))
            if not teste_valeur:
                continue
            manquants = sorted((definitions_de(instruction.body) - definitions_de(instruction.orelse)) & lus_ailleurs)
            if manquants:
                noms = ", ".join(f"`{n}`" for n in manquants)
                yield cellule, instruction, f"{noms} n'existe que si la condition est vraie."


@regle("AG105", "sortie-perdue", "avertissement",
       "Une expression d'affichage (`mo.md(…)`, `df`, `df.head()`) qui n'est pas la dernière de la cellule.",
       "marimo n'affiche que la dernière expression : celle-ci ne sera jamais vue.",
       "Mets-la en dernier, regroupe plusieurs sorties avec `mo.vstack([...])`, ou utilise `mo.output.append(…)`.")
def _sortie_perdue(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for instruction in cellule.instructions[:-1]:
            if not isinstance(instruction, ast.Expr):
                continue
            valeur = instruction.value
            if isinstance(valeur, ast.Constant):  # docstring ou chaîne de commentaire
                continue
            perdue = isinstance(valeur, (ast.Name, ast.Attribute, ast.Subscript))
            if isinstance(valeur, ast.Call):
                nom = ctx.pointe(valeur.func)
                tete, _, reste = nom.partition(".")
                perdue = (tete in ctx.mo and (reste in MO_AFFICHAGE or (reste.startswith("ui.") and reste.count(".") == 1))) \
                    or (isinstance(valeur.func, ast.Attribute) and valeur.func.attr in ("head", "tail", "describe")
                        and not valeur.keywords)
            if perdue:
                extrait = ast.unparse(valeur)
                extrait = extrait if len(extrait) <= 40 else extrait[:37] + "…"
                yield cellule, instruction, f"`{extrait}` ne sera pas affiché : ce n'est pas la dernière expression."


@regle("AG106", "boucle-bloquante", "avertissement",
       "Une boucle `while True` avec `sleep` dans une cellule.",
       "Elle bloque le noyau : plus aucune cellule ni aucun élément d'interface ne répond.",
       "Rafraîchis avec `mo.ui.refresh(default_interval=\"5s\")` lu dans une cellule, ou lance le travail dans "
       "`mo.Thread`.")
def _boucle(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in premier_niveau(cellule.instructions):
            infinie = isinstance(noeud, ast.While) and isinstance(noeud.test, ast.Constant) and noeud.test.value
            if infinie and any(isinstance(n, ast.Call) and ctx.pointe(n.func).endswith("sleep") for n in ast.walk(noeud)):
                yield cellule, noeud, "`while True` avec `sleep` bloque le noyau."


@regle("AG107", "global", "avertissement",
       "L'instruction `global` dans une cellule.",
       "Les variables d'une cellule sont déjà globales pour marimo ; `global` contourne le graphe et cache une "
       "dépendance.",
       "Retourne la nouvelle valeur sous un nouveau nom, ou passe par la cellule qui définit la variable.")
def _global(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Global):
                yield cellule, noeud, f"`global {', '.join(noeud.names)}`."


@regle("AG108", "travail-lourd-sur-ui", "avertissement",
       "Un calcul lourd (`fit`, `pm.sample`, requête réseau) dans une cellule qui lit un curseur ou un champ.",
       "Chaque mouvement du curseur relance tout le calcul : l'interface rame et l'utilisateur attend.",
       "Sépare le calcul lourd en amont, ou déclenche-le par `mo.ui.run_button` (avec `mo.stop`) ou un formulaire "
       "(`mo.ui.slider(…).form()`) ; `@mo.cache` évite de refaire un calcul déjà fait.")
def _lourd(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        lit = sorted({n.value.id for n in premier_niveau(cellule.instructions)
                      if isinstance(n, ast.Attribute) and n.attr == "value" and isinstance(n.value, ast.Name)
                      and ctx.ui.get(n.value.id) in UI_CONTINUS})
        if not lit:
            continue
        for noeud in premier_niveau(cellule.instructions):
            if not isinstance(noeud, ast.Call):
                continue
            nom = ctx.module_de(ctx.pointe(noeud.func))
            dernier = nom.rsplit(".", 1)[-1] if nom else (noeud.func.attr if isinstance(noeud.func, ast.Attribute) else "")
            racine = nom.split(".", 1)[0]
            lourd = dernier in LOURDS or (dernier == "sample" and racine in MODULES_BAYES) or \
                (racine in ("requests", "httpx") and dernier in ("get", "post", "request"))
            if lourd:
                yield cellule, noeud, f"`{ctx.pointe(noeud.func) or dernier}(…)` est relancé à chaque changement de `{lit[0]}`."
                break


@regle("AG109", "except-large", "conseil",
       "`except Exception:` ou `except:` qui avale l'erreur.",
       "marimo affiche une erreur proprement sous la cellule et arrête les cellules qui en dépendent ; une erreur "
       "avalée donne un résultat faux sans signe.",
       "Laisse l'erreur remonter, ou n'attrape que l'exception attendue (`except FileNotFoundError:`).")
def _except(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in premier_niveau(cellule.instructions):
            large = isinstance(noeud, ast.ExceptHandler) and (noeud.type is None or (
                isinstance(noeud.type, ast.Name) and noeud.type.id in ("Exception", "BaseException")))
            if large and not any(isinstance(n, ast.Raise) for n in ast.walk(noeud)):
                yield cellule, noeud, "Toute erreur est avalée ici."


@regle("AG110", "arguments-de-ligne", "conseil",
       "`sys.argv` ou `argparse` dans un notebook.",
       "Dans l'éditeur, `sys.argv` contient les arguments de marimo, pas ceux du notebook.",
       "Lis les arguments avec `mo.cli_args()` (`python notebook.py -- --n 10`).")
def _argv(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            nom = ctx.module_de(ctx.pointe(noeud)) if isinstance(noeud, ast.Attribute) else ""
            if nom == "sys.argv" or (isinstance(noeud, ast.Call) and ctx.module_de(ctx.pointe(noeud.func)) == "argparse.ArgumentParser"):
                yield cellule, noeud, f"`{ctx.pointe(noeud if isinstance(noeud, ast.Attribute) else noeud.func)}`."


IMPORT_VERS_PAQUET = {
    "sklearn": "scikit-learn", "cv2": "opencv-python", "PIL": "pillow", "yaml": "pyyaml", "bs4": "beautifulsoup4",
    "skimage": "scikit-image", "dateutil": "python-dateutil", "dotenv": "python-dotenv", "jwt": "pyjwt",
    "attr": "attrs", "Crypto": "pycryptodome", "serial": "pyserial", "fitz": "pymupdf", "docx": "python-docx",
    "pptx": "python-pptx", "umap": "umap-learn", "mpl_toolkits": "matplotlib", "IPython": "ipython",
    "OpenSSL": "pyopenssl", "MySQLdb": "mysqlclient", "git": "gitpython", "magic": "python-magic",
    "multipart": "python-multipart", "google.protobuf": "protobuf", "sentence_transformers": "sentence-transformers",
    "pydantic_ai": "pydantic-ai", "psycopg2": "psycopg2", "win32com": "pywin32", "xlwings": "xlwings",
    "duckdb": "duckdb", "pymc": "pymc", "arviz": "arviz", "lightning": "lightning", "torch": "torch",
}


def _normaliser(nom: str) -> str:
    return re.sub(r"[-_.]+", "-", nom).lower()


def dependances_declarees(entete: str) -> set[str] | None:
    try:
        import tomllib
    except ModuleNotFoundError:  # Python 3.10
        return None
    try:
        donnees = tomllib.loads(entete)
    except tomllib.TOMLDecodeError:
        return None
    noms = set()
    for exigence in donnees.get("dependencies", []):
        trouve = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", exigence)
        if trouve:
            noms.add(_normaliser(trouve.group(1)))
    pixi = donnees.get("tool", {}).get("pixi", {})
    for cle in ("dependencies", "pypi-dependencies"):
        noms.update(_normaliser(n) for n in pixi.get(cle, {}))
    return noms


@regle("AG111", "dependance-non-declaree", "avertissement",
       "Un module importé qui manque à l'en-tête PEP 723 du notebook.",
       "`marimo edit --sandbox` et `uv run notebook.py` installent l'en-tête, pas plus : l'import échouera chez "
       "quiconque ouvre le notebook.",
       "Ajoute le paquet à `dependencies` dans l'en-tête `# /// script`, ou, dans une session marimo pair, "
       "`ctx.packages.add(\"paquet\")`.",
       modes=("fichier",))
def _dependances(carnet: Carnet, ctx: Contexte):
    if not carnet.entete:
        return
    declarees = dependances_declarees(carnet.entete)
    if declarees is None:
        return
    dossier = carnet.chemin.parent if carnet.chemin else None
    vus = set()
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            modules = []
            if isinstance(noeud, ast.Import):
                modules = [a.name for a in noeud.names]
            elif isinstance(noeud, ast.ImportFrom) and noeud.level == 0 and noeud.module:
                modules = [noeud.module]
            for module in modules:
                tete = module.split(".")[0]
                if tete in sys.stdlib_module_names or tete in ("marimo", "__future__") or tete in vus:
                    continue
                if dossier and ((dossier / f"{tete}.py").exists() or (dossier / tete).is_dir()):
                    continue
                paquet = IMPORT_VERS_PAQUET.get(module, IMPORT_VERS_PAQUET.get(tete, tete))
                voulu = _normaliser(paquet)
                if not any(d == voulu or d.startswith(voulu + "-") for d in declarees):
                    vus.add(tete)
                    yield cellule, noeud, f"`{tete}` est importé mais `{paquet}` n'est pas dans l'en-tête PEP 723."


# ---------------------------------------------------------------- conseils

@regle("AG201", "plt-show", "conseil",
       "`plt.show()` pour afficher une figure matplotlib.",
       "Dans marimo, la figure doit être la sortie de la cellule pour apparaître dans une app et dans un export.",
       "Termine la cellule par `plt.gca()` ou par la figure (`fig`).")
def _plt_show(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call) and ctx.module_de(ctx.pointe(noeud.func)) == "matplotlib.pyplot.show":
                yield cellule, noeud, "`plt.show()`."


@regle("AG202", "print-comme-sortie", "conseil",
       "Une cellule qui ne montre son résultat que par `print(f\"…\")`.",
       "`print` écrit dans la console, sous la cellule ; la sortie de la cellule, celle que montre une app, reste vide.",
       "Termine par `mo.md(f\"…\")` pour un texte, ou par l'objet lui-même.")
def _print(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        if not cellule.instructions:
            continue
        derniere = cellule.instructions[-1]
        if isinstance(derniere, ast.Expr) and isinstance(derniere.value, ast.Call) and \
                isinstance(derniere.value.func, ast.Name) and derniere.value.func.id == "print" and \
                any(isinstance(a, ast.JoinedStr) for a in derniere.value.args):
            yield cellule, derniere, "Le résultat n'apparaît qu'en console."


NOMBRE_RECOPIE = re.compile(r"(?<![\w.,/$\\-])(\d{1,3}[.,]\d+\s?%?|\d+\s?%)(?![\w.,]*\d)")
RENVOI = re.compile(r"(?i)(sections?|§|chap\w*|fig\w*|éq\w*|eq\w*|tableau|table|version|v)\.?\s*$")
LIENS = re.compile(r"\[[^\]]*\]\([^)]*\)|https?://\S+|<[^>]+>")


@regle("AG203", "valeur-recopiee", "conseil",
       "Un nombre décimal ou un pourcentage écrit en dur dans un texte `mo.md` sans interpolation.",
       "Si ce nombre vient d'un calcul, le texte mentira dès que les données changent.",
       "Interpole la valeur : `mo.md(f\"La moyenne vaut {moyenne:.2f}\")`.")
def _valeur_recopiee(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if not (isinstance(noeud, ast.Call) and ctx.est_mo(ctx.pointe(noeud.func), "md") and noeud.args):
                continue
            argument = noeud.args[0]
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                texte = LIENS.sub(" ", texte_hors_maths(argument.value))
                trouves = [m.group(1) for m in NOMBRE_RECOPIE.finditer(texte)
                           if not RENVOI.search(texte[max(0, m.start() - 14):m.start()])]
                if trouves:
                    yield cellule, noeud, f"« {trouves[0].strip()} » est écrit en dur : vient-il d'un calcul ?"


@regle("AG204", "trop-de-prives", "conseil",
       "Cinq noms privés (`_x`) ou plus dans une même cellule.",
       "Beaucoup de `_` cachent une étape utile ou une cellule qui fait trop de choses ; les agents en abusent pour "
       "contourner la règle d'un seul propriétaire par nom.",
       "Donne un nom public aux résultats utiles, ou range le calcul dans une fonction.")
def _prives(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        prives = sorted(n for n in cellule.definitions if n.startswith("_") and n != "_")
        if len(prives) >= 5:
            yield cellule, cellule.instructions[0] if cellule.instructions else None, f"{len(prives)} noms privés."


@regle("AG205", "sans-entete-pep723", "conseil",
       "Pas d'en-tête PEP 723 (`# /// script`) en tête du notebook.",
       "Sans lui, `uvx marimo edit --sandbox notebook.py` ne sait pas quoi installer.",
       "Ajoute l'en-tête avec `requires-python` et `dependencies` (marimo compris) ; `marimo edit --sandbox` le tient "
       "à jour ensuite.",
       modes=("fichier",))
def _entete(carnet: Carnet, ctx: Contexte):
    if carnet.entete is None and carnet.cellules:
        yield None, None, "Le notebook ne déclare pas ses dépendances."


@regle("AG206", "imports-disperses", "conseil",
       "Des imports répartis dans trois cellules ou plus.",
       "Le lecteur cherche d'où vient un nom ; deux cellules qui importent le même module sous le même nom font "
       "échouer le notebook.",
       "Regroupe les imports dans la première cellule, ou dans `with app.setup:` (cellule `setup`, sans dépendance).")
def _imports(carnet: Carnet, ctx: Contexte):
    avec = [c for c in cellules_de_code(carnet) if c.genre == "cell" and c.index > 0
            and any(isinstance(i, (ast.Import, ast.ImportFrom)) for i in c.instructions)]
    if len(avec) >= 3:
        yield avec[0], None, f"Imports dans {len(avec)} cellules : " + ", ".join(c.etiquette for c in avec[:4]) + "."


@regle("AG207", "cellule-longue", "conseil",
       "Une cellule de plus de 60 lignes de code (chaînes longues non comptées).",
       "Une cellule est une frontière de recalcul : une longue cellule refait tout pour le moindre changement, et "
       "se lit mal.",
       "Coupe en amont le calcul coûteux et réutilisable, en aval la présentation.")
def _longue(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        if not cellule.instructions:
            continue
        lignes = set()
        for instruction in cellule.instructions:
            lignes.update(range(instruction.lineno, (instruction.end_lineno or instruction.lineno) + 1))
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str) and (noeud.end_lineno or 0) > noeud.lineno:
                lignes -= set(range(noeud.lineno + 1, noeud.end_lineno + 1))
        if len(lignes) > 60:
            yield cellule, cellule.instructions[0], f"{len(lignes)} lignes de code."


CHEMIN_ABSOLU = re.compile(r"^(/home/|/Users/|/tmp/|/mnt/|/var/|/opt/|[A-Za-z]:[\\/])")


@regle("AG208", "chemin-absolu", "conseil",
       "Un chemin absolu propre à une machine (`/home/…`, `C:\\…`, `/tmp/…`).",
       "Le notebook ne tournera pas ailleurs, ni dans un bac à sable, ni chez un collègue.",
       "Pars du dossier du notebook : `mo.notebook_dir() / \"donnees\" / \"fichier.csv\"`.")
def _chemin(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str) and CHEMIN_ABSOLU.match(noeud.value) \
                    and "\n" not in noeud.value and len(noeud.value) < 200:
                yield cellule, noeud, f"« {noeud.value[:50]} »."


@regle("AG209", "mo-state-sans-rappel", "conseil",
       "`mo.state` sans aucun `on_change` dans le notebook.",
       "Pour 99 % des cas, les variables et les éléments d'interface suffisent ; `mo.state` ajoute des mises à jour "
       "difficiles à suivre.",
       "Garde une variable ordinaire et un élément d'interface ; réserve `mo.state` aux rappels `on_change` ou à un "
       "état accumulé.")
def _state(carnet: Carnet, ctx: Contexte):
    rappels = any(isinstance(n, ast.keyword) and n.arg == "on_change" for c in carnet.cellules for n in tous(c.instructions))
    if rappels:
        return
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call) and ctx.est_mo(ctx.pointe(noeud.func), "state"):
                yield cellule, noeud, "`mo.state(…)` sans `on_change`."
                return


@regle("AG210", "ui-sans-etiquette", "conseil",
       "Un curseur, un champ ou un bouton sans `label`.",
       "Le lecteur voit un curseur sans savoir ce qu'il règle.",
       "Ajoute `label=\"…\"` (le Markdown est permis), ou compose le texte avec `mo.md(\"… {x}\").batch(x=…)`.")
def _etiquette(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in premier_niveau(cellule.instructions):
            genre = ctx.genre_ui(noeud) if isinstance(noeud, ast.Call) else ""
            if genre not in UI_A_ETIQUETTE or any(m.arg == "label" for m in noeud.keywords):
                continue
            haut = ctx.parent(noeud)
            dans_enveloppe = False
            while haut is not None and not isinstance(haut, ast.stmt):
                if isinstance(haut, ast.Call) and ctx.genre_ui(haut) in UI_ENVELOPPES | {"batch"}:
                    dans_enveloppe = True
                haut = ctx.parent(haut)
            if not dans_enveloppe:
                yield cellule, noeud, f"`mo.ui.{genre}(…)` sans `label`."


# ---------------------------------------------------------------- moteur

def appliquer(carnet: Carnet, selection: set[str] | None = None, ignorer: set[str] | None = None) -> list[Diagnostic]:
    ctx = Contexte(carnet)
    resultat: list[Diagnostic] = []
    for code, r in REGLES.items():
        if carnet.mode not in r.modes:
            continue
        if selection and not any(code.startswith(s) for s in selection):
            continue
        if ignorer and any(code.startswith(s) for s in ignorer):
            continue
        for cellule, noeud, message in r.fonction(carnet, ctx):
            ligne = getattr(noeud, "lineno", None) if noeud is not None else None
            if ligne is None and cellule is not None:
                ligne = cellule.ligne if carnet.mode == "fichier" else 1
            resultat.append(Diagnostic(
                code=code, nom=r.nom, gravite=r.gravite, message=message, correction=r.correction,
                cellule=cellule.index if cellule is not None else None,
                etiquette=cellule.etiquette if cellule is not None else "notebook", ligne=ligne))
    for cellule in carnet.cellules:
        if cellule.erreur_syntaxe:
            resultat.append(Diagnostic(code="AG000", nom="syntaxe", gravite="erreur",
                                       message=f"Le code ne se lit pas : {cellule.erreur_syntaxe}.",
                                       correction="Corrige la syntaxe avant tout le reste.", cellule=cellule.index,
                                       etiquette=cellule.etiquette, ligne=cellule.ligne))
    ordre = {g: i for i, g in enumerate(GRAVITES)}
    resultat.sort(key=lambda d: (ordre[d.gravite], d.cellule if d.cellule is not None else -1, d.ligne or 0, d.code))
    return resultat
