"""Construire un diaporama PowerPoint à partir du notebook, par Quarto.

    pixi run python diapos_pptx.py

Studio 0.4.1 n'exporte pas de PPTX. Le chemin le plus court : exécuter le notebook comme un
module (`app.run()` rend ses valeurs), écrire les figures en PNG et un document Quarto dont
chaque diapositive porte un message rédigé par le notebook, puis `quarto render --to pptx`.
Les contrôles gardent leur valeur par défaut. Le fichier sort dans `dist/pptx/`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
SORTIE = ICI / "dist" / "pptx"


def diapositives(v: dict) -> str:
    s, m = v["synthese"], v["messages"]
    annees = "\n".join(
        f"| {a['annee']} | {a['hauteur_mm']:.0f} | {a['jours_pluie']} |" for a in v["bilan_annuel"].to_dicts()
    )
    return f"""---
title: "Seattle sous la pluie"
subtitle: "Point climat, relevés quotidiens NOAA {m['periode']}"
lang: fr
---

## La réponse

{m['titre']}.

{m['chapeau']}

## {m['saison']}

![](saison.png)

## Souvent, mais peu à la fois

{m['intensite']}

![](intensite.png)

## D'une année à l'autre

{m['hauteur']} L'année la plus humide est {s['annee_plus_humide']}, la plus sèche {s['annee_plus_seche']}.

| Année | Hauteur (mm) | Jours de pluie |
|---|---:|---:|
{annees}

## Méthode

- Un jour est pluvieux à partir de {s['seuil']} de pluie.
- Source : {v['donnees_vues']['source']['nom']}.
- Calculs dans le notebook marimo `meteo.py`.
"""


def main() -> int:
    sys.path.insert(0, str(ICI))
    from meteo import app

    _, definitions = app.run()
    valeurs = {
        "synthese": definitions["synthese"],
        "messages": definitions["messages"],
        "bilan_annuel": definitions["bilan_annuel"],
        "donnees_vues": definitions["donnees_vues"],
    }
    SORTIE.mkdir(parents=True, exist_ok=True)
    definitions["figure_saison"].save(str(SORTIE / "saison.png"), scale_factor=2)
    definitions["figure_pluie"].save(str(SORTIE / "intensite.png"), scale_factor=2)
    (SORTIE / "diapos.qmd").write_text(diapositives(valeurs), encoding="utf-8")
    rendu = subprocess.run(["quarto", "render", "diapos.qmd", "--to", "pptx"], cwd=SORTIE, shell=sys.platform == "win32")
    if rendu.returncode == 0:
        print(SORTIE / "diapos.pptx")
    return rendu.returncode


if __name__ == "__main__":
    raise SystemExit(main())
