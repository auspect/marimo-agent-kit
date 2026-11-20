"""Vérifier des cellules avant de les insérer, seules ou dans le contexte d'un notebook."""

from __future__ import annotations

from pathlib import Path

from .carnet import joindre, lire_corps, lire_fichier
from .regles import appliquer
from .verifier import Etape, Rapport


def verifier_cellules(cellules: list[str], notebook: Path | None = None, selection: set[str] | None = None,
                      ignorer: set[str] | None = None) -> Rapport:
    if notebook is not None and notebook.exists():
        base = lire_fichier(notebook)
        carnet = joindre(base, cellules)
        depart = len(base.cellules)
        contexte = f"dans le contexte de {notebook} ({depart} cellule(s))"
    else:
        carnet = lire_corps(cellules, noms=[f"proposée {i + 1}" for i in range(len(cellules))], complet=False)
        depart = 0
        contexte = "sans le notebook : les noms inconnus ne sont pas jugés"
    proposees = set(range(depart, depart + len(cellules)))
    diagnostics = [d for d in appliquer(carnet, selection, ignorer) if d.cellule in proposees]
    for d in diagnostics:
        d.cellule = d.cellule - depart  # index dans la liste proposée
    rapport = Rapport(chemin=f"{len(cellules)} cellule(s) proposée(s)", diagnostics=diagnostics)
    rapport.etapes = [
        Etape("règles marimo-agent-kit", "fait", contexte),
        Etape("marimo check --strict", "sauté", "cellules pas encore dans un fichier"),
        Etape("exécution", "sauté", "cellules pas encore dans le notebook"),
    ]
    return rapport
