from __future__ import annotations

from pathlib import Path

from .carnet import joindre, lire_corps, lire_fichier
from .regles import appliquer
from .verifier import Etape, Rapport, nombre


def verifier_cellules(cellules: list[str], notebook: Path | None = None, selection: set[str] | None = None,
                      ignorer: set[str] | None = None) -> Rapport:
    if notebook is not None and notebook.exists():
        base = lire_fichier(notebook)
        carnet = joindre(base, cellules)
        depart = len(base.cellules)
        contexte = f"dans le contexte de {notebook}, qui a {nombre(depart, 'cellule')}"
    else:
        carnet = lire_corps(cellules, noms=[f"proposée {i + 1}" for i in range(len(cellules))], complet=False)
        depart = 0
        contexte = "sans le notebook, donc sans juger les noms inconnus"
    proposees = set(range(depart, depart + len(cellules)))
    diagnostics = [d for d in appliquer(carnet, selection, ignorer) if d.cellule in proposees]
    for d in diagnostics:
        d.cellule = d.cellule - depart
    rapport = Rapport(chemin=f"{nombre(len(cellules), 'cellule')} {'proposées' if len(cellules) > 1 else 'proposée'}", diagnostics=diagnostics)
    rapport.etapes = [
        Etape("règles marimo-agent-kit", "fait", contexte),
        Etape("marimo check", "sauté", "cellules pas encore dans un fichier"),
        Etape("exécution", "sauté", "cellules pas encore dans le notebook"),
    ]
    return rapport
