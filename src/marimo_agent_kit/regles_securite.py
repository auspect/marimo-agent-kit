"""Règles AG3xx : ce qui touche à la sécurité du poste. Elles aident la relecture et ne bloquent pas."""

from __future__ import annotations

import ast
import ipaddress
import re
import urllib.parse

from .carnet import Carnet
from .regles import Contexte, regle, tous

SHELL_TOUJOURS = {"os.system", "os.popen", "subprocess.getoutput", "subprocess.getstatusoutput"}
SOUS_PROCESSUS = {"subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output",
                  "subprocess.Popen", "asyncio.create_subprocess_shell", "asyncio.create_subprocess_exec"}
CHARGEMENTS = {"pickle.load", "pickle.loads", "cloudpickle.load", "cloudpickle.loads", "dill.load", "dill.loads",
               "joblib.load", "pandas.read_pickle", "marshal.load", "marshal.loads", "shelve.open"}
LECTURES_RESEAU = re.compile(r"^(requests|httpx)\.(get|post|put|patch|delete|head|request|stream)$"
                             r"|^urllib\.request\.(urlopen|urlretrieve)$"
                             r"|^(pandas|polars)\.(read|scan)_\w+$")
SURS_DANS_HTML = {"html.escape", "markupsafe.escape", "len", "int", "float", "round", "abs"}
FICHIERS_IDENTIFIANTS = re.compile(r"(^|[\\/~])(\.ssh|\.netrc|_netrc|\.aws[\\/]credentials|\.git-credentials|\.pypirc"
                                   r"|\.docker[\\/]config\.json|\.kube[\\/]config|id_rsa|id_ed25519|id_ecdsa)\b")
AFFICHAGES = {"print", "repr", "str", "dict", "list", "sorted", "json.dumps", "pandas.DataFrame", "polars.DataFrame",
              "pprint.pprint"}


def _nom(ctx: Contexte, appel: ast.Call) -> str:
    return ctx.nom_complet(ctx.nom_pointe(appel.func))


def _appels(carnet: Carnet):
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Call):
                yield cellule, noeud


def _mot_cle(appel: ast.Call, nom: str) -> ast.expr | None:
    return next((m.value for m in appel.keywords if m.arg == nom), None)


def _vrai(noeud: ast.expr | None) -> bool:
    return isinstance(noeud, ast.Constant) and noeud.value is True


@regle("AG301", "commande-shell", "avertissement",
       "Lancer une commande du système depuis une cellule : `subprocess`, `os.system`, `os.popen`.",
       "La commande tourne avec les droits de la personne qui ouvre le notebook. Avec `shell=True` ou un texte "
       "assemblé, une valeur venue de données peut ajouter une commande.",
       "Fais-le en Python quand une bibliothèque existe. Sinon, passe une liste d'arguments sans `shell=True`, et "
       "dis à l'utilisateur pourquoi la commande est nécessaire.")
def _shell(carnet: Carnet, ctx: Contexte):
    for cellule, appel in _appels(carnet):
        nom = _nom(ctx, appel)
        if nom in SHELL_TOUJOURS or (nom in SOUS_PROCESSUS and _vrai(_mot_cle(appel, "shell"))) \
                or nom == "asyncio.create_subprocess_shell":
            yield cellule, appel, f"`{nom}` passe par le shell."
        elif nom in SOUS_PROCESSUS:
            yield cellule, appel, f"`{nom}` lance un programme du poste."


@regle("AG302", "eval-exec", "avertissement",
       "Appeler `eval` ou `exec` sur un texte qui n'est pas écrit dans le code.",
       "Le texte s'exécute comme du code. S'il vient d'un fichier, d'une page, d'un modèle ou d'un contrôle, il peut "
       "faire n'importe quoi sur le poste.",
       "Lis la donnée avec un analyseur, par exemple `json.loads` ou `ast.literal_eval`.")
def _eval(carnet: Carnet, ctx: Contexte):
    for cellule, appel in _appels(carnet):
        if isinstance(appel.func, ast.Name) and appel.func.id in ("eval", "exec") and appel.func.id not in ctx.resolution \
                and appel.args and not isinstance(appel.args[0], ast.Constant):
            yield cellule, appel, f"`{appel.func.id}(...)` exécute un texte calculé."


@regle("AG303", "chargement-non-sur", "avertissement",
       "Charger un fichier par `pickle`, `joblib`, `pandas.read_pickle`, `torch.load` sans `weights_only=True`, "
       "`numpy.load(allow_pickle=True)` ou `yaml.load` sans chargeur sûr.",
       "Ces formats peuvent contenir du code, qui s'exécute au chargement. Un fichier reçu ou téléchargé suffit.",
       "Préfère Parquet, CSV, JSON ou safetensors. Pour un fichier que tu n'as pas produit, demande d'abord à "
       "l'utilisateur.")
def _chargement(carnet: Carnet, ctx: Contexte):
    for cellule, appel in _appels(carnet):
        nom = _nom(ctx, appel)
        if nom in CHARGEMENTS:
            yield cellule, appel, f"`{nom}` exécute le code que le fichier contient."
        elif nom == "torch.load" and not _vrai(_mot_cle(appel, "weights_only")):
            yield cellule, appel, "`torch.load` sans `weights_only=True` peut exécuter du code."
        elif nom == "numpy.load" and _vrai(_mot_cle(appel, "allow_pickle")):
            yield cellule, appel, "`numpy.load(allow_pickle=True)` peut exécuter du code."
        elif nom == "yaml.load":
            chargeur = _mot_cle(appel, "Loader") or (appel.args[1] if len(appel.args) > 1 else None)
            if chargeur is None or not ctx.nom_pointe(chargeur).endswith(("SafeLoader", "CSafeLoader")):
                yield cellule, appel, "`yaml.load` sans `SafeLoader` peut construire des objets Python."


def _parametres(noeud: ast.AST, ctx: Contexte) -> set[str]:
    while noeud is not None and not isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        noeud = ctx.parent(noeud)
    if noeud is None:
        return set()
    arguments = noeud.args
    return {a.arg for a in [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]}


def _texte_fixe(nom: str, ctx: Contexte) -> bool:
    valeurs = [i.value for c in ctx.carnet.cellules for i in tous(c.instructions)
               if isinstance(i, ast.Assign) and any(isinstance(t, ast.Name) and t.id == nom for t in i.targets)]
    return bool(valeurs) and all(isinstance(v, ast.Constant) and isinstance(v.value, str) for v in valeurs)


def _valeur_sure(valeur: ast.expr, ctx: Contexte, parametres: set[str]) -> bool:
    # Un paramètre transmis tel quel est le gabarit d'une fonction d'affichage : le risque est chez l'appelant.
    return (isinstance(valeur, ast.Constant)
            or (isinstance(valeur, ast.Call) and _nom(ctx, valeur) in SURS_DANS_HTML)
            or (isinstance(valeur, ast.Name) and (valeur.id in parametres or _texte_fixe(valeur.id, ctx))))


def _interpolation_risquee(noeud: ast.expr, ctx: Contexte) -> bool:
    parametres = _parametres(noeud, ctx)
    if isinstance(noeud, ast.JoinedStr):
        return any(isinstance(m, ast.FormattedValue) and m.format_spec is None
                   and not _valeur_sure(m.value, ctx, parametres) for m in noeud.values)
    if isinstance(noeud, ast.BinOp) and isinstance(noeud.op, ast.Add):
        return _interpolation_risquee(noeud.left, ctx) or _interpolation_risquee(noeud.right, ctx) \
            or any(not isinstance(c, (ast.BinOp, ast.JoinedStr)) and not _valeur_sure(c, ctx, parametres)
                   for c in (noeud.left, noeud.right))
    if isinstance(noeud, ast.BinOp) and isinstance(noeud.op, ast.Mod):
        elements = noeud.right.elts if isinstance(noeud.right, ast.Tuple) else [noeud.right]
        return any(not _valeur_sure(e, ctx, parametres) for e in elements)
    return isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute) and noeud.func.attr == "format"


@regle("AG304", "html-interpole", "avertissement",
       "Construire `mo.Html` ou `mo.iframe` en y insérant des valeurs calculées sans les échapper.",
       "Le HTML s'affiche dans l'éditeur, qui peut lancer du code. Une valeur venue d'un fichier, d'une page ou d'une "
       "API peut y glisser un script.",
       "Échappe chaque valeur par `html.escape(...)`, ou affiche les données par `mo.ui.table`, `mo.md` ou un "
       "graphique.")
def _html(carnet: Carnet, ctx: Contexte):
    for cellule, appel in _appels(carnet):
        nom = ctx.nom_pointe(appel.func)
        if ctx.est_mo(nom, "Html", "iframe") and appel.args and _interpolation_risquee(appel.args[0], ctx):
            yield cellule, appel, f"`{nom}(...)` reçoit des valeurs insérées sans échappement."


def _hote_local(hote: str) -> bool:
    hote = hote.lower().strip("[]")
    if hote == "localhost":
        return True
    try:
        adresse = ipaddress.ip_address(hote)
    except ValueError:
        return False
    return adresse.is_private or adresse.is_loopback


def _adresse(appel: ast.Call) -> str:
    candidats = [*appel.args[:1], *(m.value for m in appel.keywords if m.arg in ("url", "source", "io", "path_or_buf",
                                                                                  "filepath_or_buffer"))]
    for noeud in candidats:
        if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
            return noeud.value
        if isinstance(noeud, ast.JoinedStr) and noeud.values and isinstance(noeud.values[0], ast.Constant):
            return str(noeud.values[0].value)
    return ""


@regle("AG305", "adresse-externe", "avertissement",
       "Lire depuis une adresse écrite en dur dont l'hôte n'est pas local.",
       "La cellule sort de la machine à chaque exécution : elle échoue hors ligne ou sur un réseau restreint, et ses "
       "données changent sans prévenir.",
       "Télécharge le fichier une fois, par un moyen que l'utilisateur valide, puis lis la copie locale. Si l'adresse "
       "est voulue, passe `--ignorer AG305` et dis pourquoi.")
def _adresse_externe(carnet: Carnet, ctx: Contexte):
    for cellule, appel in _appels(carnet):
        nom = _nom(ctx, appel)
        if not LECTURES_RESEAU.match(nom):
            continue
        adresse = _adresse(appel)
        if not adresse.startswith(("http://", "https://")):
            continue
        hote = urllib.parse.urlsplit(adresse).hostname or ""
        if not _hote_local(hote):
            yield cellule, appel, f"`{nom}` contacte {hote} à chaque exécution."


def _est_environ(noeud: ast.AST, ctx: Contexte) -> bool:
    if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute) \
            and noeud.func.attr in ("items", "keys", "values", "copy"):
        noeud = noeud.func.value
    return ctx.nom_complet(ctx.nom_pointe(noeud)) == "os.environ"


@regle("AG306", "identifiants-du-poste", "avertissement",
       "Lire un fichier d'identifiants du poste (`~/.ssh`, `.netrc`, `.aws/credentials`…) ou afficher tout "
       "`os.environ`.",
       "La sortie d'une cellule part dans le notebook, ses exports et le contexte de l'assistant. Les variables "
       "d'environnement contiennent souvent des jetons.",
       "Lis seulement la variable utile, par `os.environ[\"NOM\"]`, et n'affiche pas sa valeur.")
def _identifiants(carnet: Carnet, ctx: Contexte):
    for cellule in carnet.cellules:
        for noeud in tous(cellule.instructions):
            if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str) and FICHIERS_IDENTIFIANTS.search(noeud.value):
                yield cellule, noeud, f"`{noeud.value[:60]}` désigne un fichier d'identifiants."
            elif isinstance(noeud, ast.Expr) and _est_environ(noeud.value, ctx):
                yield cellule, noeud, "La cellule affiche tout `os.environ`."
            elif isinstance(noeud, ast.Call) and (_nom(ctx, noeud) in AFFICHAGES or ctx.est_mo(ctx.nom_pointe(noeud.func))) \
                    and any(_est_environ(a, ctx) for a in noeud.args):
                yield cellule, noeud, f"`{ctx.nom_pointe(noeud.func)}(...)` reçoit tout `os.environ`."
