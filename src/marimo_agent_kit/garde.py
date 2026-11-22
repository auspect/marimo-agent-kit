"""Garde avant outil : un paquet passe par le gestionnaire du projet et sa configuration.

Elle juge les commandes du shell de l'agent. `pip install`, une option d'index, une source `git+`
ou `npx` contournent pixi ou uv, et les dépôts que leur configuration choisit. `MAK_GARDE` choisit
ce qu'elle fait : `observer` (défaut) note ce qu'elle aurait refusé, `agir` refuse, `off` ne
regarde rien.
"""

from __future__ import annotations

import datetime
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .environnement import Configuration, dossier_etat, masquer

OUTILS_SHELL = {"bash", "powershell", "shell", "run_in_terminal", "runinterminal", "terminal"}
MODES_GARDE = ("observer", "agir", "off")

# Début d'une commande : après un séparateur du shell, et après d'éventuelles affectations NOM=valeur.
# Un mot cité dans un message de commit ne compte donc pas.
DEBUT = r"(?:^|[;&|(`\n]|\$\()\s*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"
PIP = re.compile(DEBUT + r"(?:(?:python3?|py)(?:\.exe)?\s+-m\s+)?pip3?(?:\.exe)?\s+install\b")
OUTIL_PAQUETS = re.compile(DEBUT + r"(?:uvx?|pip3?|pixi|python3?|py|conda|mamba)(?:\.exe)?\s")
INDEX = re.compile(r"(?:--(?:extra-)?index-url|--default-index|--index|(?<![\w-])-i)[=\s]+[\"']?https?://[^\s\"']+"
                   r"|\b(?:UV_DEFAULT_INDEX|UV_INDEX_URL|UV_INDEX|UV_EXTRA_INDEX_URL|PIP_INDEX_URL|PIP_EXTRA_INDEX_URL)"
                   r"=[\"']?https?://[^\s\"']+")
SOURCE_GIT = re.compile(r"git\+(?:https?|ssh)://[^\s\"']+")
NPX = re.compile(DEBUT + r"(npx|bunx|pnpm\s+dlx|npm\s+exec)(?:\.cmd|\.exe)?(?![\w-])")


@dataclass
class Refus:
    regle: str
    raison: str
    extrait: str


def juger_commande(commande: str) -> list[Refus]:
    refus: list[Refus] = []
    if PIP.search(commande):
        refus.append(Refus("pip-install", "`pip install` contourne le gestionnaire du projet. Utilise `pixi add`, "
                                          "ou `uv add` dans un projet uv.", "pip install"))
    if OUTIL_PAQUETS.search(commande):
        for trouve in INDEX.finditer(commande):
            refus.append(Refus("option-index", "La configuration de pixi ou de uv choisit les dépôts. Retire l'option "
                                               "d'index.", masquer(trouve.group(0))))
        for trouve in SOURCE_GIT.finditer(commande):
            refus.append(Refus("source-git", "Une source `git+` prend le code hors des dépôts du gestionnaire. "
                                             "Demande le paquet publié.", masquer(trouve.group(0))))
    if npx := NPX.search(commande):
        refus.append(Refus("npx", "Cette commande télécharge et lance un paquet npm. Demande à l'utilisateur de "
                                  "l'installer.", npx.group(1)))
    return refus


def juger(outil: str, args: dict) -> list[Refus]:
    if outil.lower() not in OUTILS_SHELL:
        return []
    return juger_commande(str(args.get("command") or args.get("cmd") or ""))


def mode_garde(config: Configuration) -> str:
    mode = config.env.get("MAK_GARDE", "observer").strip().lower()
    return mode if mode in MODES_GARDE else "observer"


def chemin_journal(config: Configuration) -> Path:
    return Path(config.env.get("MAK_GARDE_JOURNAL") or dossier_etat(config.env) / "garde.jsonl")


def noter(config: Configuration, outil: str, refus: list[Refus], decision: str) -> None:
    chemin = chemin_journal(config)
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with chemin.open("a", encoding="utf-8") as journal:
            for r in refus:
                journal.write(json.dumps({"date": datetime.datetime.now().isoformat(timespec="seconds"),
                                          "decision": decision, "regle": r.regle, "outil": outil,
                                          "extrait": r.extrait[:120]}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def bilan(config: Configuration) -> str:
    chemin = chemin_journal(config)
    try:
        entrees = [json.loads(ligne) for ligne in chemin.read_text(encoding="utf-8").splitlines() if ligne.strip()]
    except (OSError, ValueError):
        entrees = []
    tete = f"Garde : mode {mode_garde(config)}. Journal : {chemin}"
    if not entrees:
        return tete + "\n\nRien de noté."
    lignes = [tete, ""]
    for regle in sorted({e["regle"] for e in entrees}):
        siennes = [e for e in entrees if e["regle"] == regle]
        refusees = sum(e["decision"] == "refusé" for e in siennes)
        lignes.append(f"{regle} : {len(siennes)} fois, dont {refusees} {'refusées' if refusees > 1 else 'refusée'}")
        lignes += [f"  {e['date']}  {e['outil']}  {e['extrait']}" for e in siennes[-3:]]
    lignes += ["", "Si chaque ligne est un vrai écart, passe en `agir` : MAK_GARDE=agir dans mak.env."]
    return "\n".join(lignes)
