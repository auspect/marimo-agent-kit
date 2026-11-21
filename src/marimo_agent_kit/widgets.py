from __future__ import annotations

import difflib
import json
import subprocess
from pathlib import Path

from .api import python_avec_marimo
from .environnement import env_sobre
from .ressources import dossier_skill

SCRIPT_INSTALLE = r'''
import importlib.metadata, inspect, json, sys
try:
    r = {"version": importlib.metadata.version("wigglystuff")}
except importlib.metadata.PackageNotFoundError:
    print(json.dumps({"version": None}))
    sys.exit(0)
nom = sys.argv[1]
if nom:
    import wigglystuff
    objet = getattr(wigglystuff, nom, None)
    if objet is not None:
        cible = objet.__init__ if inspect.isclass(objet) else objet
        try:
            r["signature"] = nom + str(inspect.signature(cible)).replace("(self, ", "(").replace("(self)", "()")
        except (TypeError, ValueError):
            pass
        if inspect.isclass(objet) and hasattr(objet, "class_traits"):
            base = set()
            try:
                import anywidget
                base = set(anywidget.AnyWidget.class_traits(sync=True))
            except ImportError:
                pass
            r["traitlets"] = sorted(n for n in objet.class_traits(sync=True) if n not in base and not n.startswith("_"))
print(json.dumps(r))
'''


def references() -> Path:
    return dossier_skill("wigglystuff") / "references"


def catalogue() -> dict:
    return json.loads((references() / "catalogue.json").read_text(encoding="utf-8"))


def installe(nom: str = "", depuis: Path | None = None) -> dict | None:
    python = python_avec_marimo(depuis)
    if python is None:
        return None
    if python[0] == "uv":
        python = [*python[:-1], "--with", "wigglystuff", python[-1]]
    try:
        sortie = subprocess.run([*python, "-c", SCRIPT_INSTALLE, nom], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=120, env=env_sobre())
        return json.loads(sortie.stdout.strip().splitlines()[-1])
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def trouver(nom: str) -> dict | None:
    cle = nom.lower().removeprefix("wigglystuff.")
    for entree in catalogue()["widgets"]:
        if cle in (entree["nom"].lower(), Path(entree["page"]).stem.lower()):
            return entree
    return None


def proches(nom: str) -> list[str]:
    noms = [e["nom"] for e in catalogue()["widgets"]]
    return difflib.get_close_matches(nom, noms, n=6, cutoff=0.5)


def chercher(motif: str) -> list[dict]:
    motif = motif.lower()
    return [e for e in catalogue()["widgets"]
            if motif in e["nom"].lower() or motif in e["resume"].lower() or motif in e["titre"].lower()]


def ligne_version(doc: str, local: dict | None) -> str:
    if local is None:
        return f"Doc : wigglystuff {doc}. Version installée : inconnue (aucun Python avec marimo trouvé)."
    if local.get("version") is None:
        return f"Doc : wigglystuff {doc}. Le Python du projet n'a pas wigglystuff : ajoute `wigglystuff=={doc}` à l'en-tête PEP 723."
    if local.get("version") == doc:
        return f"Doc et paquet installé : wigglystuff {doc}."
    return (f"Attention : la doc est celle de wigglystuff {doc}, le projet a {local.get('version')}. "
            "La signature et les traitlets ci-dessous viennent du paquet installé ; ils font foi.")


def en_texte(nom: str | None = None, motif: str | None = None, verifier_installe: bool = True) -> str:
    cat = catalogue()
    if motif:
        trouves = chercher(motif)
        if not trouves:
            return f'Aucun widget ne parle de "{motif}".'
        return "\n".join(f"{e['nom']:<26} {e['resume']}" for e in trouves)
    if not nom:
        local = installe() if verifier_installe else None
        lignes = [ligne_version(cat["version"], local) if verifier_installe else f"Doc : wigglystuff {cat['version']}.", ""]
        lignes += [f"{e['nom']:<26} {e['resume']}" for e in cat["widgets"]]
        lignes += ["", "`mak widgets <Nom>` affiche une page. La section \"Choisir\" du skill wigglystuff aide à choisir."]
        return "\n".join(lignes)
    entree = trouver(nom)
    if entree is None:
        suggestion = ", ".join(proches(nom)) or "aucun"
        return f"`{nom}` n'est pas dans wigglystuff {cat['version']}. Noms proches : {suggestion}."
    page = (references() / entree["page"]).read_text(encoding="utf-8")
    lignes = [page]
    if verifier_installe:
        local = installe(entree["nom"])
        lignes.insert(0, ligne_version(cat["version"], local) + "\n")
        if local and local.get("version") not in (None, cat["version"]):
            if local.get("signature"):
                lignes += ["", "## Dans le paquet installé", "", "```python", local["signature"], "```"]
            if local.get("traitlets"):
                lignes += ["", "Traitlets : " + ", ".join(f"`{t}`" for t in local["traitlets"])]
    return "\n".join(lignes)
