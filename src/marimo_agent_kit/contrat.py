"""Le contrat d'écriture : une version courte pour les prompts, une référence complète des règles.

La version courte part dans chaque requête de l'assistant de marimo (`[tool.marimo.ai] rules`) :
elle doit rester brève. La référence est générée à partir des règles elles-mêmes, pour ne pas
avoir deux textes à garder d'accord.
"""

from __future__ import annotations

from pathlib import Path

from .regles import GRAVITES, REGLES

CONTRAT = Path(__file__).resolve().parent / "donnees" / "skill" / "reference" / "contrat.md"


def contrat_court() -> str:
    """Le contrat sans son titre Markdown : il part tel quel dans un prompt."""
    return CONTRAT.read_text(encoding="utf-8").removeprefix("# ")


def reference_regles() -> str:
    lignes = [
        "# Règles de marimo-agent-kit",
        "",
        "Fichier généré par `mak regles --reference` : ne pas le modifier à la main.",
        "",
        "Ces règles complètent `marimo check` : elles visent ce qu'un agent écrit souvent de travers et que le",
        "linter de marimo ne voit pas. Elles ne lisent que la syntaxe ; une règle qui se trompe sur un notebook",
        "se désactive par `--ignorer CODE`.",
        "",
        "| Gravité | Ce que l'agent en fait |",
        "|---|---|",
        "| erreur | La cellule plante ou affiche un résultat faux : corriger avant de rendre la main. |",
        "| avertissement | Le notebook tourne mais la réactivité ou la lecture en souffre : corriger, ou dire pourquoi pas. |",
        "| conseil | Lisibilité : appliquer aux cellules que l'on vient d'écrire. |",
        "",
    ]
    for gravite in GRAVITES:
        for code, regle in REGLES.items():
            if regle.gravite != gravite:
                continue
            portee = "" if regle.modes == ("fichier", "corps") else f" *(seulement en mode {', '.join(regle.modes)})*"
            lignes += [
                f"## {code} `{regle.nom}` — {gravite}{portee}",
                "",
                regle.resume,
                "",
                f"**Pourquoi.** {regle.pourquoi}",
                "",
                f"**Correction.** {regle.correction}",
                "",
            ]
    return "\n".join(lignes).rstrip() + "\n"
