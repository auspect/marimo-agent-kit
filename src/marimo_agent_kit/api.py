from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

from .environnement import env_sobre

SCRIPT = r'''
import difflib, inspect, json, sys
import marimo

demande = sys.argv[1].strip()
mode = sys.argv[2]
ESPACES = {"": marimo}
for nom in ("ui", "output", "status", "cache", "persistent_cache"):
    objet = getattr(marimo, nom, None)
    if objet is not None and (inspect.ismodule(objet) or nom in ("ui", "output", "status")):
        ESPACES[nom + "."] = objet

def premiere_ligne(objet):
    doc = inspect.getdoc(objet) or ""
    return doc.strip().splitlines()[0] if doc.strip() else ""

def catalogue():
    noms = {}
    for prefixe, espace in ESPACES.items():
        for nom in dir(espace):
            if nom.startswith("_"):
                continue
            try:
                noms["mo." + prefixe + nom] = getattr(espace, nom)
            except Exception:
                pass
    return noms

def signature(objet):
    try:
        cible = objet.__init__ if inspect.isclass(objet) else objet
        texte = str(inspect.signature(cible))
        return texte.replace("(self, ", "(").replace("(self)", "()")
    except (TypeError, ValueError):
        return ""

resultat = {"version": marimo.__version__}
if mode == "chercher":
    motif = demande.lower()
    trouves = []
    for nom, objet in sorted(catalogue().items()):
        ligne = premiere_ligne(objet)
        if motif in nom.lower() or motif in ligne.lower():
            trouves.append({"nom": nom, "resume": ligne[:120]})
    resultat["trouves"] = trouves[:60]
else:
    chemin = demande
    for prefixe in ("marimo.", "mo."):
        if chemin.startswith(prefixe):
            chemin = chemin[len(prefixe):]
    objet, ok = marimo, True
    for morceau in [m for m in chemin.split(".") if m]:
        if not hasattr(objet, morceau):
            ok = False
            break
        objet = getattr(objet, morceau)
    if not ok or not chemin:
        tous = list(catalogue())
        cible = "mo." + chemin
        resultat["introuvable"] = cible
        resultat["proches"] = difflib.get_close_matches(cible, tous, n=8, cutoff=0.6) or \
            [n for n in tous if chemin.split(".")[-1].lower() in n.lower()][:8]
    else:
        resultat["nom"] = "mo." + chemin
        resultat["genre"] = "module" if inspect.ismodule(objet) else "classe" if inspect.isclass(objet) else \
            "fonction" if callable(objet) else type(objet).__name__
        resultat["signature"] = signature(objet)
        doc = inspect.getdoc(objet) or ""
        lignes = doc.splitlines()
        resultat["doc"] = "\n".join(lignes[:60]) + ("\n[…]" if len(lignes) > 60 else "")
        if inspect.ismodule(objet) or inspect.isclass(objet):
            membres = []
            for nom in dir(objet):
                if nom.startswith("_"):
                    continue
                try:
                    membre = getattr(objet, nom)
                except Exception:
                    continue
                membres.append({"nom": nom, "resume": premiere_ligne(membre)[:100]})
            resultat["membres"] = membres[:120]
print(json.dumps(resultat, ensure_ascii=False))
'''


def python_avec_marimo(depuis: Path | None = None) -> list[str] | None:
    depart = (depuis or Path.cwd()).resolve()
    for dossier in [depart, *depart.parents]:
        for candidat in (dossier / ".venv" / "bin" / "python", dossier / ".venv" / "Scripts" / "python.exe"):
            if candidat.exists() and (candidat.parent / ("marimo.exe" if candidat.suffix else "marimo")).exists():
                return [str(candidat)]
    if importlib.util.find_spec("marimo") is not None:
        return [sys.executable]
    if shutil.which("uv"):
        return ["uv", "run", "--no-project", "--with", "marimo", "python"]
    return None


def interroger(demande: str, mode: str = "decrire", depuis: Path | None = None) -> dict:
    python = python_avec_marimo(depuis)
    if python is None:
        return {"erreur": "aucun Python avec marimo, et uv est absent"}
    try:
        sortie = subprocess.run([*python, "-c", SCRIPT, demande, mode], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=120, env=env_sobre())
    except (OSError, subprocess.SubprocessError) as erreur:
        return {"erreur": f"{type(erreur).__name__} : {erreur}"}
    try:
        return json.loads(sortie.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"erreur": (sortie.stderr or sortie.stdout).strip()[-600:]}


def en_texte(resultat: dict) -> str:
    if "erreur" in resultat:
        return f"Impossible de lire l'API : {resultat['erreur']}"
    tete = f"marimo {resultat['version']}"
    if "trouves" in resultat:
        if not resultat["trouves"]:
            return f"{tete} : aucun nom ne correspond."
        return tete + "\n" + "\n".join(f"  {t['nom']:<32} {t['resume']}" for t in resultat["trouves"])
    if "introuvable" in resultat:
        proches = ", ".join(resultat["proches"]) or "aucun"
        return f"{tete} : `{resultat['introuvable']}` n'existe pas. Noms proches : {proches}."
    lignes = [f"{resultat['nom']}, {resultat['genre']} de {tete}"]
    if resultat.get("signature"):
        lignes.append(f"{resultat['nom']}{resultat['signature']}")
    if resultat.get("doc"):
        lignes += ["", resultat["doc"]]
    if resultat.get("membres"):
        lignes += ["", "Membres :"] + [f"  {m['nom']:<24} {m['resume']}" for m in resultat["membres"]]
    return "\n".join(lignes)
