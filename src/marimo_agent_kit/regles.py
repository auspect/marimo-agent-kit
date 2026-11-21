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
    cellule: int | None = None
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


BUILTINS = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__builtins__", "__spec__", "__loader__", "__package__"}

NOMS_JUPYTER = ("display", "get_ipython")
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
MUTANTES_AMBIGUES = {"sort", "reverse", "update", "pop"}


class Contexte:
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
        self.genres_ui: dict[str, str] = {}
        for cellule in carnet.cellules:
            for instruction in cellule.instructions:
                if isinstance(instruction, ast.Assign) and len(instruction.targets) == 1:
                    cible = instruction.targets[0]
                    genre = self.genre_ui(instruction.value)
                    if isinstance(cible, ast.Name) and genre:
                        self.genres_ui[cible.id] = genre
        self.lectures_ailleurs: dict[int, set[str]] = {}
        for cellule in carnet.cellules:
            autres = set().union(*(c.lectures for c in carnet.cellules if c is not cellule)) if len(carnet.cellules) > 1 else set()
            self.lectures_ailleurs[cellule.index] = autres

    def parent(self, noeud: ast.AST) -> ast.AST | None:
        return self.parents.get(id(noeud))

    def nom_pointe(self, noeud: ast.AST) -> str:
        morceaux = []
        while isinstance(noeud, ast.Attribute):
            morceaux.append(noeud.attr)
            noeud = noeud.value
        if isinstance(noeud, ast.Name):
            morceaux.append(noeud.id)
            return ".".join(reversed(morceaux))
        return ""

    def nom_complet(self, nom_pointe: str) -> str:
        tete, _, reste = nom_pointe.partition(".")
        base = self.resolution.get(tete)
        if base is None:
            return nom_pointe
        return f"{base}.{reste}" if reste else base

    def est_mo(self, nom_pointe: str, *suite: str) -> bool:
        tete, _, reste = nom_pointe.partition(".")
        return tete in self.mo and (not suite or reste in suite)

    def genre_ui(self, noeud: ast.AST) -> str:
        if not isinstance(noeud, ast.Call):
            return ""
        fonction = noeud.func
        if isinstance(fonction, ast.Attribute) and fonction.attr in ("form", "batch") and self.genre_ui(fonction.value):
            return fonction.attr
        if isinstance(fonction, ast.Attribute) and fonction.attr == "batch" and isinstance(fonction.value, ast.Call) \
                and self.est_mo(self.nom_pointe(fonction.value.func), "md"):
            return "batch"
        nom = self.nom_pointe(fonction)
        tete, _, reste = nom.partition(".")
        if tete in self.mo and reste.startswith("ui.") and reste.count(".") == 1:
            return reste[3:]
        return ""

    def racine(self, noeud: ast.AST) -> ast.Name | None:
        while isinstance(noeud, (ast.Attribute, ast.Subscript, ast.Call)):
            noeud = noeud.func if isinstance(noeud, ast.Call) else noeud.value
        return noeud if isinstance(noeud, ast.Name) else None


def premier_niveau(instructions: list[ast.stmt]) -> Iterator[ast.AST]:
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


def masquer_maths_et_code(texte: str) -> str:
    def blanc(m: re.Match) -> str:
        return " " * len(m.group(0))

    for motif in (r"```.*?```", r"`[^`\n]*`", r"\$\$.*?\$\$", r"\\\[.*?\\\]", r"\\\(.*?\\\)", r"(?<!\\)\$[^$\n]+?(?<!\\)\$"):
        texte = re.sub(motif, blanc, texte, flags=re.S)
    return texte


@regle("AG001", "valeur-ui-meme-cellule", "erreur",
       "Lire `.value` d'un élément d'interface dans la cellule qui le crée.",
       "marimo lève `RuntimeError: Accessing the value of a UIElement in the cell that created it is not allowed`.",
       "Crée l'élément dans une cellule, puis lis `.value` dans une autre.")
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
       "Le noyau de marimo tourne déjà dans une boucle d'événements. L'appel échoue dans l'éditeur, dans une app et dans un export avec `asyncio.run() cannot be called from a running event loop`. Il passe pourtant avec `python notebook.py`.",
       "Écris `resultat = await coroutine()` directement dans la cellule. marimo accepte `await` au premier niveau.")
def _asyncio_run(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call):
                nom = ctx.nom_complet(ctx.nom_pointe(noeud.func))
                if nom == "asyncio.run" or (isinstance(noeud.func, ast.Attribute) and noeud.func.attr == "run_until_complete"):
                    yield cellule, noeud, f"`{ctx.nom_pointe(noeud.func) or 'run_until_complete'}(...)` échouera dans le noyau de marimo."


@regle("AG003", "habitude-jupyter", "erreur",
       "Utiliser `display()`, `get_ipython()` ou `IPython.display` dans une cellule.",
       "Ces noms n'existent pas dans marimo. `display(df)` lève `NameError`.",
       "Mets l'objet en dernière expression de la cellule. Pour plusieurs sorties, utilise `mo.output.append(objet)`. `mo.md`, `mo.Html` et `mo.image` remplacent `IPython.display`.")
def _jupyter(carnet: Carnet, ctx: Contexte):
    definis = carnet.definitions
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Name) and noeud.func.id in NOMS_JUPYTER:
                if noeud.func.id not in definis:
                    yield cellule, noeud, f"`{noeud.func.id}(...)` n'existe pas dans marimo."
            elif isinstance(noeud, ast.ImportFrom) and (noeud.module or "").startswith("IPython"):
                yield cellule, noeud, f"`from {noeud.module} import ...` vient de Jupyter."
            elif isinstance(noeud, ast.Import) and any(a.name.startswith("IPython") for a in noeud.names):
                yield cellule, noeud, "`import IPython` : une habitude de Jupyter."


PLACEHOLDER = re.compile(r"(?<![\\\w^_{$])\{([A-Za-z_][A-Za-z0-9_]*)((?:\.[A-Za-z_]\w*|\[[^\]{}]*\])*)(?:![rsa])?(?::[^{}]*)?\}")


@regle("AG004", "md-sans-f", "erreur",
       "Écrire `mo.md(\"... {variable} ...\")` sans le préfixe `f`.",
       "Sans `f`, marimo affiche les accolades telles quelles. Le lecteur voit `{moyenne}` au lieu du nombre.",
       "Ajoute le préfixe, par exemple `mo.md(f\"... {variable} ...\")`. Avec des antislashs LaTeX, écris `rf\"...\"`.")
def _md_sans_f(carnet: Carnet, ctx: Contexte):
    definis = carnet.definitions
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if not (isinstance(noeud, ast.Call) and ctx.est_mo(ctx.nom_pointe(noeud.func), "md") and noeud.args):
                continue
            argument = noeud.args[0]
            if not (isinstance(argument, ast.Constant) and isinstance(argument.value, str)):
                continue
            parent = ctx.parent(noeud)
            if isinstance(parent, ast.Attribute) and parent.attr in ("batch", "format"):
                continue
            noms = [m.group(1) for m in PLACEHOLDER.finditer(masquer_maths_et_code(argument.value)) if m.group(1) in definis]
            if noms:
                liste = ", ".join(f"`{{{n}}}`" for n in dict.fromkeys(noms))
                yield cellule, noeud, f"{liste} sera affiché tel quel, car la chaîne n'est pas une f-string."


SECRETS = re.compile(r"\b(sk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|"
                     r"glpat-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|hf_[A-Za-z0-9]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|"
                     r"AIza[0-9A-Za-z_-]{35})\b")
NOM_SECRET = re.compile(r"(?i)(api_?key|apikey|token|secret|password|passwd|mot_?de_?passe|mdp|credential)")
FACTICE = re.compile(r"(?i)(<|>|xxx|\.\.\.|changeme|votre|your|exemple|example|placeholder|dummy|\$\{|todo)")


@regle("AG005", "secret-en-clair", "erreur",
       "Écrire une clé d'API, un jeton ou un mot de passe dans le code.",
       "Le code d'un notebook voyage avec lui, dans git, dans un export HTML ou WASM et dans le contexte envoyé à l'assistant.",
       "Lis la valeur dans l'environnement par `os.environ[\"NOM\"]`, ou demande-la par `mo.ui.text(kind=\"password\")`.")
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
       "C'est une API privée, réservée au bloc-notes temporaire de marimo pair. Elle change sans préavis.",
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
       "Lire un nom qu'aucune cellule ne définit, ou un nom privé comme `_x` défini dans une autre cellule.",
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
            if nom in BUILTINS or nom in NOMS_JUPYTER:
                continue
            noeud = next((n for n in tous(cellule.instructions) if isinstance(n, ast.Name) and n.id == nom), None)
            if nom not in definis:
                yield cellule, noeud, f"`{nom}` n'est défini par aucune cellule."
            elif nom.startswith("_") and nom != "_":
                proprietaire = carnet.proprietaire(nom)
                ou = proprietaire.etiquette if proprietaire else "une autre cellule"
                yield cellule, noeud, f"`{nom}` est privé à la {ou}. Il n'existe pas ici."


@regle("AG008", "corps-au-format-fichier", "erreur",
       "Envoyer à code mode un corps de cellule qui contient `return`, `@app.cell` ou `app = marimo.App`.",
       "`create_cell` et `edit_cell` prennent le contenu de la cellule, pas l'enveloppe du fichier.",
       "Envoie seulement les instructions de la cellule. marimo calcule ses entrées et ses sorties.",
       modes=("corps",))
def _corps_format_fichier(carnet: Carnet, ctx: Contexte):
    for cellule in carnet.cellules:
        if cellule.retour_au_premier_niveau:
            noeud = next((n for n in cellule.instructions if isinstance(n, ast.Return)), None)
            yield cellule, noeud, "`return` au premier niveau d'un corps de cellule."
        if "@app.cell" in cellule.code or "marimo.App(" in cellule.code:
            yield cellule, None, "Le corps contient l'enveloppe du fichier (`@app.cell` ou `marimo.App`)."


@regle("AG009", "nom-redefini", "erreur",
       "Définir un même nom public dans deux cellules.",
       "marimo refuse le notebook avec `Multiply-defined names`. En code mode, il rejette tout le lot de modifications.",
       "Modifie la cellule propriétaire, ou donne un nouveau nom au résultat, par exemple `propre = df.dropna()`.",
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


@regle("AG101", "mutation-inter-cellules", "avertissement",
       "Modifier en place un objet défini dans une autre cellule, par exemple par `df[\"c\"] = ...`, `liste.append` ou `inplace=True`.",
       "marimo suit les noms, pas les mutations. Les cellules qui lisent l'objet ne repartent pas. Relancer cette cellule applique la mutation une seconde fois.",
       "Crée un nouvel objet, par exemple `df2 = df.assign(c=...)`, `df.with_columns(...)` ou `liste2 = [*liste, x]`. Sinon, fais la modification dans la cellule qui définit l'objet.")
def _mutation(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        etrangers = {n for n in cellule.lectures if n not in BUILTINS and n not in ctx.resolution and n not in ctx.genres_ui}
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
                    yield cellule, noeud, (f"Sur une liste, `{appel}(...)` modifie en place un objet d'une autre "
                                           "cellule. Sur un DataFrame, son résultat est perdu.")
                elif en_place or (noeud.func.attr in MUTANTES and seule):
                    yield cellule, noeud, f"`{appel}(...)` modifie en place `{racine.id}`, un objet d'une autre cellule."


@regle("AG102", "ui-non-liee", "avertissement",
       "Créer un élément d'interface sans l'affecter à un nom public, par exemple dans une liste, dans `mo.hstack` ou sous un nom `_nom`.",
       "marimo ne relance les cellules qu'à partir d'un élément lié à une variable globale. Toucher ce curseur ne fera rien, et sa valeur n'est lisible nulle part.",
       "Affecte l'élément à un nom public dans sa propre instruction, par exemple `seuil = mo.ui.slider(...)`. Pour une liste ou un dictionnaire d'éléments, utilise `mo.ui.array([...])` ou `mo.ui.dictionary({...})`.")
def _ui_non_liee(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in premier_niveau(cellule.instructions):
            genre = ctx.genre_ui(noeud) if isinstance(noeud, ast.Call) else ""
            if not genre or genre in UI_AFFICHAGE or genre in ("form", "batch"):
                continue
            courant, haut, en_liste, dans_appel = noeud, ctx.parent(noeud), False, False
            while haut is not None and not isinstance(haut, ast.stmt):
                if isinstance(haut, ast.Call) and ctx.genre_ui(haut) in UI_ENVELOPPES | {"form", "batch"}:
                    courant = haut
                elif isinstance(haut, ast.IfExp) and courant in (haut.body, haut.orelse):
                    courant = haut  # `a = mo.ui.slider(...) if x else mo.ui.number(...)`
                elif isinstance(haut, ast.Call):
                    dans_appel = True
                elif isinstance(haut, (ast.List, ast.ListComp, ast.Dict, ast.DictComp, ast.Tuple, ast.SetComp)) and courant is noeud:
                    en_liste = True
                haut = ctx.parent(haut)
            cible = _cible_publique(haut, courant)
            if cible is True:
                continue
            if isinstance(cible, str):
                yield cellule, noeud, f"`mo.ui.{genre}` est lié à `{cible}`, un nom privé. Ses changements ne relancent rien."
            elif en_liste and not dans_appel:
                yield cellule, noeud, f"`mo.ui.{genre}(...)` est rangé dans une liste ou un dictionnaire ordinaire. Utilise `mo.ui.array` ou `mo.ui.dictionary`."
            else:
                yield cellule, noeud, f"`mo.ui.{genre}(...)` n'est affecté à aucun nom public. Il ne déclenchera rien."


def _cible_publique(instruction: ast.AST, valeur: ast.AST) -> bool | str:
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
       "La valeur d'un `mo.ui.button` sans `on_click` reste `None`, donc `if bouton.value:` n'est jamais vrai.",
       "Pour lancer un calcul, crée `lancer = mo.ui.run_button(label=\"...\")`, puis écris `mo.stop(not lancer.value)` dans la cellule du calcul. Pour compter des clics, passe `on_click=lambda n: n + 1, value=0`.")
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
                            yield cellule, instruction, f"`{cible.id}` est un `mo.ui.button` sans `on_click`, donc `{cible.id}.value` vaut toujours `None`."


@regle("AG104", "garde-if-valeur", "avertissement",
       "Écrire un `if element.value:` qui définit sans `else` un nom que d'autres cellules lisent.",
       "Quand la condition est fausse, le nom n'existe pas. Les cellules qui le lisent affichent alors `Name ... is not defined` au lieu d'attendre.",
       "Écris en tête de cellule `mo.stop(not lancer.value, mo.md(\"Clique sur **Lancer** pour calculer.\"))`, puis le calcul sans `if`.")
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
       "Écrire une expression d'affichage, comme `mo.md(...)`, `df` ou `df.head()`, ailleurs qu'en dernière position dans la cellule.",
       "marimo n'affiche que la dernière expression. Celle-ci ne sera jamais vue.",
       "Mets-la en dernier, regroupe plusieurs sorties avec `mo.vstack([...])`, ou utilise `mo.output.append(...)`.")
def _sortie_perdue(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for instruction in cellule.instructions[:-1]:
            if not isinstance(instruction, ast.Expr):
                continue
            valeur = instruction.value
            if isinstance(valeur, ast.Constant):
                continue
            perdue = isinstance(valeur, (ast.Name, ast.Attribute, ast.Subscript))
            if isinstance(valeur, ast.Call):
                nom = ctx.nom_pointe(valeur.func)
                tete, _, reste = nom.partition(".")
                perdue = (tete in ctx.mo and (reste in MO_AFFICHAGE or (reste.startswith("ui.") and reste.count(".") == 1))) \
                    or (isinstance(valeur.func, ast.Attribute) and valeur.func.attr in ("head", "tail", "describe")
                        and not valeur.keywords)
            if perdue:
                extrait = ast.unparse(valeur)
                extrait = extrait if len(extrait) <= 40 else extrait[:37] + "…"
                yield cellule, instruction, f"`{extrait}` ne sera pas affiché, car ce n'est pas la dernière expression."


@regle("AG106", "boucle-bloquante", "avertissement",
       "Écrire une boucle `while True` avec `sleep` dans une cellule.",
       "La boucle bloque le noyau. Plus aucune cellule ni aucun élément d'interface ne répond.",
       "Lis un `mo.ui.refresh(default_interval=\"5s\")` dans une cellule, ou lance le travail dans un `mo.Thread`.")
def _boucle(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in premier_niveau(cellule.instructions):
            infinie = isinstance(noeud, ast.While) and isinstance(noeud.test, ast.Constant) and noeud.test.value
            if infinie and any(isinstance(n, ast.Call) and ctx.nom_pointe(n.func).endswith("sleep") for n in ast.walk(noeud)):
                yield cellule, noeud, "`while True` avec `sleep` bloque le noyau."


@regle("AG107", "global", "avertissement",
       "Utiliser l'instruction `global` dans une cellule.",
       "Les variables d'une cellule sont déjà globales pour marimo. `global` contourne le graphe et cache une dépendance.",
       "Retourne la nouvelle valeur sous un nouveau nom, ou modifie la cellule qui définit la variable.")
def _global(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Global):
                yield cellule, noeud, f"`global {', '.join(noeud.names)}`."


@regle("AG108", "travail-lourd-sur-ui", "avertissement",
       "Lancer un calcul lourd, comme `fit`, `pm.sample` ou une requête réseau, dans une cellule qui lit un curseur ou un champ.",
       "Chaque mouvement du curseur relance tout le calcul. L'interface rame et l'utilisateur attend.",
       "Place le calcul lourd en amont, ou déclenche-le par un `mo.ui.run_button` avec `mo.stop`, ou par un formulaire comme `mo.ui.slider(...).form()`. `@mo.cache` évite de refaire un calcul déjà fait.")
def _lourd(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        lit = sorted({n.value.id for n in premier_niveau(cellule.instructions)
                      if isinstance(n, ast.Attribute) and n.attr == "value" and isinstance(n.value, ast.Name)
                      and ctx.genres_ui.get(n.value.id) in UI_CONTINUS})
        if not lit:
            continue
        for noeud in premier_niveau(cellule.instructions):
            if not isinstance(noeud, ast.Call):
                continue
            nom = ctx.nom_complet(ctx.nom_pointe(noeud.func))
            dernier = nom.rsplit(".", 1)[-1] if nom else (noeud.func.attr if isinstance(noeud.func, ast.Attribute) else "")
            racine = nom.split(".", 1)[0]
            lourd = dernier in LOURDS or (dernier == "sample" and racine in MODULES_BAYES) or \
                (racine in ("requests", "httpx") and dernier in ("get", "post", "request"))
            if lourd:
                yield cellule, noeud, f"`{ctx.nom_pointe(noeud.func) or dernier}(...)` est relancé à chaque changement de `{lit[0]}`."
                break


@regle("AG109", "except-large", "conseil",
       "Écrire `except Exception:` ou `except:` qui avale l'erreur.",
       "marimo affiche une erreur sous la cellule et arrête les cellules qui en dépendent. Une erreur avalée donne un résultat faux sans aucun signe.",
       "Laisse l'erreur remonter, ou n'attrape que l'exception attendue, par exemple `except FileNotFoundError:`.")
def _except(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in premier_niveau(cellule.instructions):
            large = isinstance(noeud, ast.ExceptHandler) and (noeud.type is None or (
                isinstance(noeud.type, ast.Name) and noeud.type.id in ("Exception", "BaseException")))
            if large and not any(isinstance(n, ast.Raise) for n in ast.walk(noeud)):
                yield cellule, noeud, "Toute erreur est avalée ici."


@regle("AG110", "arguments-de-ligne", "conseil",
       "Utiliser `sys.argv` ou `argparse` dans un notebook.",
       "Dans l'éditeur, `sys.argv` contient les arguments de marimo, pas ceux du notebook.",
       "Lis les arguments avec `mo.cli_args()`, puis lance `python notebook.py -- --n 10`.")
def _argv(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            nom = ctx.nom_complet(ctx.nom_pointe(noeud)) if isinstance(noeud, ast.Attribute) else ""
            if nom == "sys.argv" or (isinstance(noeud, ast.Call) and ctx.nom_complet(ctx.nom_pointe(noeud.func)) == "argparse.ArgumentParser"):
                yield cellule, noeud, f"`{ctx.nom_pointe(noeud if isinstance(noeud, ast.Attribute) else noeud.func)}`."


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
       "Importer un module qui manque à l'en-tête PEP 723 du notebook.",
       "`marimo edit --sandbox` et `uv run notebook.py` n'installent que l'en-tête. L'import échouera chez toute personne qui ouvre le notebook.",
       "Ajoute le paquet à `dependencies` dans l'en-tête `# /// script`. Dans une session marimo pair, utilise `ctx.packages.add(\"paquet\")`.",
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


@regle("AG201", "plt-show", "conseil",
       "Afficher une figure matplotlib par `plt.show()`.",
       "Dans marimo, la figure doit être la sortie de la cellule pour apparaître dans une app et dans un export.",
       "Termine la cellule par `plt.gca()` ou par la figure, par exemple `fig`.")
def _plt_show(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call) and ctx.nom_complet(ctx.nom_pointe(noeud.func)) == "matplotlib.pyplot.show":
                yield cellule, noeud, "`plt.show()`."


@regle("AG202", "print-comme-sortie", "conseil",
       "Montrer le résultat d'une cellule seulement par `print(f\"...\")`.",
       "`print` écrit dans la console, sous la cellule. La sortie de la cellule, celle qu'une app montre, reste vide.",
       "Termine par `mo.md(f\"...\")` pour un texte, ou par l'objet lui-même.")
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
       "Écrire en dur un nombre décimal ou un pourcentage dans un texte `mo.md` sans interpolation.",
       "Si ce nombre vient d'un calcul, le texte sera faux dès que les données changent.",
       "Interpole la valeur, par exemple `mo.md(f\"La moyenne vaut {moyenne:.2f}\")`.")
def _valeur_recopiee(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if not (isinstance(noeud, ast.Call) and ctx.est_mo(ctx.nom_pointe(noeud.func), "md") and noeud.args):
                continue
            argument = noeud.args[0]
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                texte = LIENS.sub(" ", masquer_maths_et_code(argument.value))
                trouves = [m.group(1) for m in NOMBRE_RECOPIE.finditer(texte)
                           if not RENVOI.search(texte[max(0, m.start() - 14):m.start()])]
                if trouves:
                    yield cellule, noeud, f"\"{trouves[0].strip()}\" est écrit en dur. Ce nombre vient-il d'un calcul ?"


@regle("AG204", "trop-de-prives", "conseil",
       "Définir cinq noms privés `_x` ou plus dans une même cellule.",
       "Beaucoup de `_` cachent une étape utile ou une cellule qui fait trop de choses. Les agents en abusent pour contourner la règle d'un seul propriétaire par nom.",
       "Donne un nom public aux résultats utiles, ou range le calcul dans une fonction.")
def _prives(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        prives = sorted(n for n in cellule.definitions if n.startswith("_") and n != "_")
        if len(prives) >= 5:
            yield cellule, cellule.instructions[0] if cellule.instructions else None, f"{len(prives)} noms privés."


@regle("AG205", "sans-entete-pep723", "conseil",
       "Omettre l'en-tête PEP 723 `# /// script` en tête du notebook.",
       "Sans lui, `uvx marimo edit --sandbox notebook.py` ne sait pas quoi installer.",
       "Ajoute l'en-tête avec `requires-python` et `dependencies`, marimo compris. `marimo edit --sandbox` le tient à jour ensuite.",
       modes=("fichier",))
def _entete(carnet: Carnet, ctx: Contexte):
    if carnet.entete is None and carnet.cellules:
        yield None, None, "Le notebook ne déclare pas ses dépendances."


@regle("AG206", "imports-disperses", "conseil",
       "Répartir les imports dans trois cellules ou plus.",
       "Le lecteur cherche d'où vient un nom. Deux cellules qui importent le même module sous le même nom font échouer le notebook.",
       "Regroupe les imports dans la première cellule, ou dans `with app.setup:`. Cette cellule `setup` ne dépend d'aucune autre.")
def _imports(carnet: Carnet, ctx: Contexte):
    avec = [c for c in cellules_de_code(carnet) if c.genre == "cell" and c.index > 0
            and any(isinstance(i, (ast.Import, ast.ImportFrom)) for i in c.instructions)]
    if len(avec) >= 3:
        yield avec[0], None, f"Imports dans {len(avec)} cellules, dont " + ", ".join(c.etiquette for c in avec[:4]) + "."


@regle("AG207", "cellule-longue", "conseil",
       "Écrire une cellule de plus de 60 lignes de code, sans compter les longues chaînes.",
       "Une cellule est une frontière de recalcul. Une longue cellule refait tout pour le moindre changement, et se lit mal.",
       "Place en amont le calcul coûteux et réutilisable, et en aval la présentation.")
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
       "Écrire un chemin absolu propre à une machine, comme `/home/...`, `C:\\...` ou `/tmp/...`.",
       "Le notebook ne tournera pas ailleurs, ni dans un bac à sable, ni chez un collègue.",
       "Pars du dossier du notebook, par exemple `mo.notebook_dir() / \"donnees\" / \"fichier.csv\"`.")
def _chemin(carnet: Carnet, ctx: Contexte):
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str) and CHEMIN_ABSOLU.match(noeud.value) \
                    and "\n" not in noeud.value and len(noeud.value) < 200:
                yield cellule, noeud, f"Le chemin \"{noeud.value[:50]}\" ne marche que sur cette machine."


@regle("AG209", "mo-state-sans-rappel", "conseil",
       "Utiliser `mo.state` sans aucun `on_change` dans le notebook.",
       "Le plus souvent, des variables et des éléments d'interface suffisent. `mo.state` ajoute des mises à jour difficiles à suivre.",
       "Garde une variable ordinaire et un élément d'interface. Réserve `mo.state` aux rappels `on_change` ou à un état accumulé.")
def _state(carnet: Carnet, ctx: Contexte):
    rappels = any(isinstance(n, ast.keyword) and n.arg == "on_change" for c in carnet.cellules for n in tous(c.instructions))
    if rappels:
        return
    for cellule in cellules_de_code(carnet):
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call) and ctx.est_mo(ctx.nom_pointe(noeud.func), "state"):
                yield cellule, noeud, "`mo.state(...)` sans `on_change`."
                return


@regle("AG210", "ui-sans-etiquette", "conseil",
       "Créer un curseur, un champ ou un bouton sans `label`.",
       "Le lecteur voit un curseur sans savoir ce qu'il règle.",
       "Ajoute `label=\"...\"`, qui accepte le Markdown. Sinon, compose le texte avec `mo.md(\"... {x}\").batch(x=...)`.")
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
                yield cellule, noeud, f"`mo.ui.{genre}(...)` sans `label`."


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
                                       message=f"Le code ne se lit pas. {cellule.erreur_syntaxe}.",
                                       correction="Corrige la syntaxe avant tout le reste.", cellule=cellule.index,
                                       etiquette=cellule.etiquette, ligne=cellule.ligne))
    ordre = {g: i for i, g in enumerate(GRAVITES)}
    resultat.sort(key=lambda d: (ordre[d.gravite], d.cellule if d.cellule is not None else -1, d.ligne or 0, d.code))
    return resultat
