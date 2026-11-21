from __future__ import annotations

from .regles import GRAVITES, REGLES
from .ressources import dossier_skill


def contrat_court() -> str:
    contrat = dossier_skill("marimo-agent-kit") / "reference" / "contrat.md"
    return contrat.read_text(encoding="utf-8").removeprefix("# ")


def reference_regles() -> str:
    lignes = [
        "# Règles de marimo-agent-kit",
        "",
        "`mak regles --reference` génère ce fichier. Ne le modifie pas à la main.",
        "",
        "Ces règles complètent `marimo check`. Elles visent ce qu'un agent écrit souvent de travers et que le",
        "linter de marimo ne voit pas. Elles ne lisent que la syntaxe. Une règle qui se trompe sur un notebook",
        "se désactive par `--ignorer CODE`.",
        "",
        "| Gravité | Ce que l'agent en fait |",
        "|---|---|",
        "| erreur | La cellule plante ou affiche un résultat faux. Corrige avant de rendre la main. |",
        "| avertissement | Le notebook tourne, mais la réactivité ou la lecture en souffre. Corrige, ou dis pourquoi tu ne le fais pas. |",
        "| conseil | La lisibilité en souffre. Applique le conseil aux cellules que tu viens d'écrire. |",
        "",
        "Les règles `AG3xx` touchent à la sécurité du poste : commande du shell, `eval`, chargement de pickle, HTML",
        "construit à partir de données, adresse externe, identifiants du poste. Elles aident la relecture humaine et",
        "ne bloquent rien. Avant d'en ignorer une, dis à l'utilisateur pourquoi le code en a besoin.",
        "",
    ]
    for gravite in GRAVITES:
        for code, regle in REGLES.items():
            if regle.gravite != gravite:
                continue
            portee = "" if regle.modes == ("fichier", "corps") else f", seulement en mode {', '.join(regle.modes)}"
            lignes += [
                f"## {code} `{regle.nom}`, {gravite}{portee}",
                "",
                regle.resume,
                "",
                f"**Pourquoi.** {regle.pourquoi}",
                "",
                f"**Correction.** {regle.correction}",
                "",
            ]
    return "\n".join(lignes).rstrip() + "\n"
