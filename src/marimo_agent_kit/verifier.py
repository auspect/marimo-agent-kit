from __future__ import annotations

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .carnet import Carnet, lire_fichier
from .environnement import env_sobre
from .regles import GRAVITES, Diagnostic, appliquer

MARGE_HORLOGE_S = 1


def nombre(n: int, mot: str) -> str:
    return f"{n} {mot}{'s' if n > 1 else ''}"

GRAVITE_MARIMO = {"breaking": "erreur", "runtime": "erreur", "formatting": "conseil"}


@dataclass
class Etape:
    nom: str
    etat: Literal["fait", "sauté", "échec"]
    detail: str = ""


@dataclass
class Rapport:
    chemin: str
    diagnostics: list[Diagnostic] = field(default_factory=list)
    etapes: list[Etape] = field(default_factory=list)

    def compte(self) -> dict[str, int]:
        return {g: sum(1 for d in self.diagnostics if d.gravite == g) for g in GRAVITES}

    @property
    def ok(self) -> bool:
        return self.compte()["erreur"] == 0 and not any(e.etat == "échec" for e in self.etapes)

    @property
    def statut(self) -> str:
        if any(e.etat == "échec" for e in self.etapes):
            return "non vérifié"
        if self.compte()["erreur"]:
            return "à corriger"
        return "propre" if all(e.etat == "fait" for e in self.etapes) else "propre, vérification partielle"

    def en_dict(self, conseils: bool = True) -> dict:
        return {
            "chemin": self.chemin,
            "statut": self.statut,
            "compte": self.compte(),
            "etapes": [vars(e) for e in self.etapes],
            "diagnostics": [d.en_dict() for d in self.diagnostics if conseils or d.gravite != "conseil"],
        }

    def en_texte(self, conseils: bool = False) -> str:
        compte = self.compte()
        lignes = [f"{self.chemin}, {self.statut}. {nombre(compte['erreur'], 'erreur')}, "
                  f"{nombre(compte['avertissement'], 'avertissement')}, {nombre(compte['conseil'], 'conseil')}."]
        for etape in self.etapes:
            lignes.append(f"  [{etape.etat}] {etape.nom}" + (f". {etape.detail}" if etape.detail else ""))
        for d in self.diagnostics:
            if d.gravite == "conseil" and not conseils:
                continue
            ou = f"{d.etiquette}, ligne {d.ligne}" if d.ligne else d.etiquette
            lignes.append(f"\n{d.gravite.upper()} {d.code} {d.nom}, {ou}, source {d.source}\n  {d.message}\n  Correction. {d.correction}")
        if compte["conseil"] and not conseils:
            lignes.append(f"\n{nombre(compte['conseil'], 'conseil')} de lisibilité. `--conseils` les affiche.")
        return "\n".join(lignes)


def commande_marimo(chemin: Path | None = None, imposee: str | None = None) -> list[str]:
    imposee = imposee or os.environ.get("MAK_MARIMO")
    if imposee:
        return shlex.split(imposee)
    if chemin is not None:
        for dossier in [chemin.resolve().parent, *chemin.resolve().parents]:
            for candidat in (dossier / ".venv" / "bin" / "marimo", dossier / ".venv" / "Scripts" / "marimo.exe"):
                if candidat.exists():
                    return [str(candidat)]
    if importlib.util.find_spec("marimo") is not None:
        return [sys.executable, "-m", "marimo"]
    if shutil.which("marimo"):
        return ["marimo"]
    if shutil.which("uvx"):
        return ["uvx", "marimo"]
    return []


def _cellule_de_ligne(carnet: Carnet, ligne: int | None):
    if ligne is None:
        return None
    candidate = None
    for cellule in carnet.cellules:
        if cellule.ligne <= ligne:
            candidate = cellule
    return candidate


def lancer_marimo_check(carnet: Carnet, commande: list[str], delai: int = 120) -> tuple[Etape, list[Diagnostic]]:
    nom = "marimo check"
    if not commande:
        return Etape(nom, "échec", "marimo introuvable (ni dans le projet, ni dans ce Python, ni par uvx)"), []
    try:
        sortie = subprocess.run([*commande, "check", "--format", "json", str(carnet.chemin)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=delai,
                                env=env_sobre())
    except (OSError, subprocess.SubprocessError) as erreur:
        return Etape(nom, "échec", f"{type(erreur).__name__} : {erreur}"), []
    try:
        donnees = json.loads(sortie.stdout[sortie.stdout.index("{"):])
    except ValueError:
        return Etape(nom, "échec", (sortie.stderr or sortie.stdout).strip()[-400:] or f"code {sortie.returncode}"), []
    diagnostics = []
    for probleme in donnees.get("issues", []):
        if probleme.get("type") != "diagnostic":
            continue
        cellule = _cellule_de_ligne(carnet, probleme.get("line"))
        correction = "`marimo check --fix` le corrige." if probleme.get("fixable") else \
            f"Voir https://docs.marimo.io/guides/lint_rules/rules/{probleme.get('name', '').replace('-', '_')}/"
        diagnostics.append(Diagnostic(
            code=probleme.get("code", "M?"), nom=probleme.get("name", ""),
            gravite=GRAVITE_MARIMO.get(probleme.get("severity", ""), "avertissement"),
            message=probleme.get("message", ""), correction=correction,
            cellule=cellule.numero if cellule else None, etiquette=cellule.etiquette if cellule else "notebook",
            ligne=probleme.get("line"), source="marimo check"))
    return Etape(nom, "fait", nombre(len(diagnostics), "problème")), diagnostics


def lancer_execution(carnet: Carnet, commande: list[str], delai: int = 300, bac_a_sable: str | None = "auto"
                     ) -> tuple[Etape, list[Diagnostic]]:
    chemin = carnet.chemin
    nom = "exécution (marimo export session)"
    if not commande:
        return Etape(nom, "échec", "marimo introuvable"), []
    options = ["--no-sandbox"]
    if bac_a_sable == "auto" and carnet.entete is not None and shutil.which("uv"):
        options = ["--sandbox=pixi"] if "[tool.pixi" in carnet.entete and shutil.which("pixi") else ["--sandbox=uv"]
    elif bac_a_sable in ("uv", "pixi"):
        options = [f"--sandbox={bac_a_sable}"]
    instantane = chemin.parent / "__marimo__" / "session" / f"{chemin.name}.json"
    debut = time.time()
    try:
        sortie = subprocess.run([*commande, "export", "session", "--force-overwrite", *options, chemin.name],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=delai,
                                cwd=chemin.parent, env=env_sobre())
    except subprocess.TimeoutExpired:
        return Etape(nom, "échec", f"plus de {delai} s : une cellule attend peut-être une saisie, ou le calcul est trop long"), []
    except OSError as erreur:
        return Etape(nom, "échec", str(erreur)), []
    echec = Etape(nom, "échec", (sortie.stderr or sortie.stdout).strip()[-600:] or "aucun instantané écrit")
    if not instantane.exists() or instantane.stat().st_mtime < debut - MARGE_HORLOGE_S:
        return echec, []
    try:
        session = json.loads(instantane.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return echec, []
    cellules = session.get("cells", [])
    alignees = len(cellules) == len(carnet.cellules)
    diagnostics, bloquees, rang = [], 0, 0
    for index, cellule_session in enumerate(cellules):
        if cellule_session.get("id") == "setup":
            numero = 0
        else:
            rang += 1
            numero = rang
        for sortie_cellule in cellule_session.get("outputs", []):
            if sortie_cellule.get("type") != "error":
                continue
            valeur = (sortie_cellule.get("evalue") or "").strip()
            if valeur.startswith("An ancestor raised an exception"):
                bloquees += 1
                continue
            cellule = carnet.cellules[index] if alignees else None
            diagnostics.append(Diagnostic(
                code="EXEC", nom="execution", gravite="erreur", message=valeur or sortie_cellule.get("ename", "erreur"),
                correction="Corrige la cause dans cette cellule. Les cellules qui en dépendent repartiront.",
                cellule=numero, etiquette=cellule.etiquette if cellule else f"cellule {numero}",
                ligne=cellule.ligne if cellule else None, source="exécution"))
    detail = f"{nombre(len(cellules), 'cellule')}, {len(diagnostics)} en erreur"
    if bloquees:
        detail += f", {bloquees} {'bloquées' if bloquees > 1 else 'bloquée'} par une erreur en amont"
    detail += f", avec {' '.join(options)}"
    return Etape(nom, "fait", detail), diagnostics


def _confirmer_par_execution(statiques: list[Diagnostic], executes: list[Diagnostic]) -> list[Diagnostic]:
    restants = []
    for d in executes:
        cause = next((s for s in statiques if s.gravite == "erreur" and s.cellule == d.cellule), None)
        if cause is None:
            restants.append(d)
        else:
            cause.message += f" L'exécution le confirme : \"{d.message[:160]}\"."
    return restants


def verifier(chemin: str | Path, executer: bool = True, marimo: str | None = None, delai: int = 300,
             selection: set[str] | None = None, ignorer: set[str] | None = None, bac_a_sable: str | None = "auto"
             ) -> Rapport:
    chemin = Path(chemin)
    rapport = Rapport(chemin=str(chemin))
    try:
        carnet = lire_fichier(chemin)
    except SyntaxError as erreur:
        rapport.diagnostics.append(Diagnostic(code="AG000", nom="syntaxe", gravite="erreur",
                                              message=f"Le fichier ne se lit pas : {erreur.msg} (ligne {erreur.lineno}).",
                                              correction="Corrige la syntaxe.", ligne=erreur.lineno, etiquette="notebook"))
        rapport.etapes.append(Etape("lecture", "fait", "syntaxe invalide : rien d'autre n'a tourné"))
        return rapport
    if not carnet.cellules:
        rapport.etapes.append(Etape("lecture", "échec", "aucune cellule marimo dans ce fichier"))
        return rapport
    commande = commande_marimo(chemin, marimo)
    etape, diagnostics = lancer_marimo_check(carnet, commande)
    rapport.etapes.append(etape)
    rapport.diagnostics += diagnostics
    regles = appliquer(carnet, selection, ignorer)
    rapport.etapes.append(Etape("règles marimo-agent-kit", "fait", nombre(len(regles), "constat")))
    rapport.diagnostics += regles
    if executer:
        if any(d.source == "marimo check" and d.code.startswith("MB") for d in diagnostics):  # cassant
            rapport.etapes.append(Etape("exécution (marimo export session)", "sauté",
                                        "le notebook ne passe pas marimo check : corrige d'abord sa structure"))
        else:
            etape, diagnostics = lancer_execution(carnet, commande, delai, bac_a_sable)
            rapport.etapes.append(etape)
            rapport.diagnostics += _confirmer_par_execution(regles, diagnostics)
    else:
        rapport.etapes.append(Etape("exécution (marimo export session)", "sauté", "non demandée"))
    ordre = {g: i for i, g in enumerate(GRAVITES)}
    rapport.diagnostics.sort(key=lambda d: (ordre[d.gravite], d.cellule if d.cellule is not None else -1, d.ligne or 0))
    return rapport
