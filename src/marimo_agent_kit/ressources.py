"""Où sont les skills : dans le paquet installé, ou à la racine du dépôt quand on travaille sur les sources."""

from __future__ import annotations

from pathlib import Path

ICI = Path(__file__).resolve().parent
SKILLS = ("marimo-agent-kit", "wigglystuff", "marimo-lens")


def dossier_skills() -> Path:
    for candidat in (ICI / "skills", ICI.parent.parent / "skills"):
        if (candidat / "marimo-agent-kit" / "SKILL.md").exists():
            return candidat
    raise FileNotFoundError("skills introuvables : ni dans le paquet, ni à la racine du dépôt")


def dossier_skill(nom: str) -> Path:
    return dossier_skills() / nom
