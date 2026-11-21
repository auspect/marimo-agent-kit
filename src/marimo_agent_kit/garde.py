"""Garde avant outil : ce qu'un agent ne lance pas quand le poste est hors ligne.

`MAK_GARDE` choisit ce qu'elle fait : `observer` (défaut) note ce qu'elle aurait refusé, `agir`
refuse, `off` ne regarde rien. En mode réseau `public`, elle ne juge rien. Un hôte est permis
s'il est déclaré interne (voir `Configuration.hote_interne`), et en mode `aucun` seulement la
boucle locale.
"""

from __future__ import annotations

import datetime
import json
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from .environnement import Configuration, dossier_etat, masquer

OUTILS_SHELL = {"bash", "powershell", "shell", "run_in_terminal", "runinterminal", "terminal"}
OUTILS_LECTURE_WEB = {"webfetch", "web_fetch", "fetch", "fetch_webpage"}
OUTILS_RECHERCHE_WEB = {"websearch", "web_search"}
MODES_GARDE = ("observer", "agir", "off")

# Début d'une commande : après un séparateur du shell, et après d'éventuelles affectations NOM=valeur.
# Un mot cité dans un message de commit ne compte donc pas.
DEBUT = r"(?:^|[;&|(`\n]|\$\()\s*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"
PIP = re.compile(DEBUT + r"(?:(?:python3?|py)(?:\.exe)?\s+-m\s+)?pip3?(?:\.exe)?\s+install\b")
OUTIL_PAQUETS = re.compile(DEBUT + r"(?:uvx?|pip3?|pixi|python3?|py|conda|mamba)(?:\.exe)?\s")
INDEX = re.compile(r"(?:--(?:extra-)?index-url|--default-index|--index|(?<![\w-])-i)[=\s]+[\"']?(https?://[^\s\"']+)"
                   r"|\b(?:UV_DEFAULT_INDEX|UV_INDEX_URL|UV_INDEX|UV_EXTRA_INDEX_URL|PIP_INDEX_URL|PIP_EXTRA_INDEX_URL)"
                   r"=[\"']?(https?://[^\s\"']+)")
SOURCE_GIT = re.compile(r"git\+(?:https?|ssh)://(?:[^\s\"'/@]+@)?([^\s\"'/:]+)")
TELECHARGEMENT = re.compile(DEBUT + r"(curl|wget|Invoke-WebRequest|iwr|Invoke-RestMethod|irm|Start-BitsTransfer)"
                            r"(?:\.exe)?(?![\w-])", re.I)
URL = re.compile(r"https?://([^\s\"'/:?#]+)")
NPX = re.compile(DEBUT + r"(npx|bunx|pnpm\s+dlx|npm\s+exec)(?:\.cmd|\.exe)?(?![\w-])")
UV = re.compile(DEBUT + r"(uvx|uv)(?:\.exe)?\s+(?!--version|-V\b|help\b|version\b|self\b)")


@dataclass
class Refus:
    regle: str
    raison: str
    extrait: str


def _hote(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def juger_commande(commande: str, config: Configuration) -> list[Refus]:
    refus: list[Refus] = []
    if PIP.search(commande):
        refus.append(Refus("pip-install", "`pip install` contourne la configuration de uv et de pixi. "
                                          "Utilise `uv add` ou `uv pip install`, ou `pixi add`.", "pip install"))
    if OUTIL_PAQUETS.search(commande):
        for trouve in INDEX.finditer(commande):
            url = trouve.group(1) or trouve.group(2)
            if not config.hote_permis(_hote(url)):
                refus.append(Refus("index-externe", f"Le dépôt {_hote(url)} n'est pas déclaré interne. Garde le dépôt "
                                                    "configuré pour uv ou pixi, sans option d'index.", masquer(trouve.group(0))))
        for trouve in SOURCE_GIT.finditer(commande):
            if not config.hote_permis(trouve.group(1)):
                refus.append(Refus("source-git", f"Une source `git+` va chercher le code sur {trouve.group(1)}. "
                                                 "Demande le paquet sur le dépôt interne.", masquer(trouve.group(0))))
    if telechargement := TELECHARGEMENT.search(commande):
        for hote in sorted({h.lower() for h in URL.findall(commande)}):
            if not config.hote_permis(hote):
                refus.append(Refus("telechargement", f"{hote} n'est pas un hôte interne déclaré : le poste n'y va pas. "
                                                     "Dis à l'utilisateur ce qui manque.", f"{telechargement.group(1)} {hote}"))
    if npx := NPX.search(commande):
        refus.append(Refus("npx", "Cette commande télécharge et lance un paquet npm. Demande à l'utilisateur de "
                                  "l'installer.", npx.group(1)))
    uv = UV.search(commande)
    if uv and config.env.get("UV_OFFLINE") == "1" and "--offline" not in commande and "UV_OFFLINE=1" not in commande:
        refus.append(Refus("uv-en-ligne", "Le kit a coupé uv du réseau sur ce poste. Ajoute `--offline` à la "
                                          "commande uv ou uvx.", uv.group(1)))
    return refus


def juger(outil: str, args: dict, config: Configuration) -> list[Refus]:
    if config.mode == "public":
        return []
    outil = outil.lower()
    if outil in OUTILS_SHELL:
        return juger_commande(str(args.get("command") or args.get("cmd") or ""), config)
    if outil in OUTILS_RECHERCHE_WEB:
        return [Refus("recherche-web", "La recherche web sort du poste. La documentation est sur le poste : "
                                       "`mak api`, `mak widgets`, les références des skills.", outil)]
    if outil in OUTILS_LECTURE_WEB:
        hote = _hote(str(args.get("url") or ""))
        if not config.hote_permis(hote):
            return [Refus("lecture-web", f"{hote or 'cette adresse'} n'est pas un hôte interne déclaré. "
                                         "Lis la documentation sur le poste : `mak api`, `mak widgets`, les "
                                         "références des skills.", hote)]
    return []


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
    tete = f"Garde : mode {mode_garde(config)}, réseau {config.mode}. Journal : {chemin}"
    if not entrees:
        return tete + "\n\nRien de noté."
    lignes = [tete, ""]
    for regle in sorted({e["regle"] for e in entrees}):
        siennes = [e for e in entrees if e["regle"] == regle]
        refusees = sum(e["decision"] == "refusé" for e in siennes)
        lignes.append(f"{regle} : {len(siennes)} fois, dont {refusees} refusées")
        lignes += [f"  {e['date']}  {e['outil']}  {e['extrait']}" for e in siennes[-3:]]
    lignes += ["", "Si chaque ligne est un vrai écart, passe en `agir` : MAK_GARDE=agir dans mak.env."]
    return "\n".join(lignes)
