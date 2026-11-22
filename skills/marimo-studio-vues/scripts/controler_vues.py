"""Contrôler les vues Studio d'un notebook contre les critères d'une restitution de qualité.

    python controler_vues.py notebook.py
    python controler_vues.py notebook.py --json

Le script lit les sources, sans rien construire ni exécuter. Il complète `marimo-studio validate`,
qui vérifie déjà les cibles projetées. Il rend 1 s'il trouve une erreur, 0 sinon. Les conseils
sont des points à relire, pas des fautes certaines.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXTE = {".qmd", ".md", ".markdown", ".typ", ".tex", ".tsx", ".ts", ".jsx", ".js", ".html", ".svelte"}
GABARIT = ("Keep this section current", "Connect a notebook value", "Define `report` in the notebook")
CIBLE_ANONYME = re.compile(r"""["'=]cell-\d+["'\s>]""")
# Un nombre suivi d'une unité ou d'un pourcentage, ou une année : ce qu'une vue ne devrait pas écrire elle-même.
CHIFFRE = re.compile(r"(?<![\w.#-])(\d+(?:[.,]\d+)?\s?(?:%|mm|°C|jours?\b|ans\b|années\b)|(?:19|20)\d\d\b)")
CHAINE = re.compile(r"""(["'`])((?:(?!\1).)*)\1""")
TEXTE_JSX = re.compile(r">([^<>{}]+)<")
IGNORE_LIGNE = re.compile(r"^\s*(import|//|/\*|\*|#let|#set|#show|#import|<link|<meta|@|--)|className=|style=|viewBox|width|height")


def suspects(chemin: Path) -> list[tuple[int, str]]:
    trouves = []
    entete = code = False
    for numero, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        if chemin.suffix in {".qmd", ".md", ".markdown"}:
            if ligne.strip() == "---" and (numero == 1 or entete):
                entete = not entete if numero == 1 or entete else entete
                continue
            if ligne.lstrip().startswith("```"):
                code = not code
            if entete or code:
                continue
            morceaux = [re.sub(r"\{\{<.*?>\}\}", "", ligne)]
        elif chemin.suffix in {".tsx", ".ts", ".jsx", ".js", ".svelte", ".html"}:
            if IGNORE_LIGNE.search(ligne):
                continue
            morceaux = [m.group(2) for m in CHAINE.finditer(ligne)] + TEXTE_JSX.findall(ligne)
        else:
            if IGNORE_LIGNE.search(ligne):
                continue
            morceaux = [re.sub(r"#\w+\([^)]*\)", "", ligne)]
        for morceau in morceaux:
            for trouve in CHIFFRE.findall(morceau):
                trouves.append((numero, trouve.strip()))
    return trouves


def controler(notebook: Path) -> dict:
    racine = notebook.parent / "studio" / notebook.stem
    constats: list[dict] = []
    vues = sorted(p.parent for p in racine.glob("*/view.toml")) if racine.exists() else []
    if not vues:
        constats.append({"gravite": "erreur", "vue": None, "message": f"aucune vue sous {racine}"})
    fournisseurs = set()
    for vue in vues:
        manifeste = (vue / "view.toml").read_text(encoding="utf-8")
        fournisseur = re.search(r'provider\s*=\s*"([^"]+)"', manifeste)
        fournisseurs.add(fournisseur.group(1) if fournisseur else "?")
        if not (vue / "DESIGN.md").exists():
            constats.append({"gravite": "conseil", "vue": vue.name,
                             "message": "pas de DESIGN.md : public, tâche du lecteur et système visuel non écrits"})
        agents = vue / "AGENTS.md"
        if agents.exists() and any(g in agents.read_text(encoding="utf-8") for g in GABARIT):
            constats.append({"gravite": "conseil", "vue": vue.name,
                             "message": "AGENTS.md garde le texte du gabarit dans « Project intent »"})
        fichiers = [p for p in vue.rglob("*") if p.is_file() and p.suffix in TEXTE
                    and p.name not in {"AGENTS.md", "DESIGN.md"} and not {".artifacts", "node_modules"} & set(p.parts)
                    and p.name not in {"marimo.typ", "use-marimo-value.ts", "marimo-studio.d.ts"}]
        projette_controles = False
        for fichier in fichiers:
            texte = fichier.read_text(encoding="utf-8")
            relatif = fichier.relative_to(vue).as_posix()
            for gabarit in GABARIT:
                if gabarit in texte:
                    constats.append({"gravite": "erreur", "vue": vue.name, "fichier": relatif,
                                     "message": f"texte du gabarit resté en place : « {gabarit} »"})
            if CIBLE_ANONYME.search(texte):
                constats.append({"gravite": "erreur", "vue": vue.name, "fichier": relatif,
                                 "message": "cible `cell-N` du gabarit : nommez la cellule dans le notebook"})
            if re.search(r'marimo-cell[^>]*name=|marimo cell=', texte):
                projette_controles = True
            for ligne, trouve in suspects(fichier):
                constats.append({"gravite": "conseil", "vue": vue.name, "fichier": relatif, "ligne": ligne,
                                 "message": f"« {trouve} » écrit dans la vue : vient-il du notebook ?"})
        if projette_controles and not (vue / "states.yaml").exists():
            constats.append({"gravite": "conseil", "vue": vue.name,
                             "message": "la vue projette une cellule, peut-être un contrôle, sans states.yaml : "
                                        "un export Prepared ne préparera que l'état initial"})
    if len(vues) > 1 and len(fournisseurs) == 1:
        constats.append({"gravite": "conseil", "vue": None,
                         "message": "toutes les vues ont le même format : chaque public a-t-il le bon support ?"})
    return {"notebook": str(notebook), "vues": [v.name for v in vues], "formats": sorted(fournisseurs),
            "erreurs": sum(c["gravite"] == "erreur" for c in constats), "constats": constats}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rapport = controler(args.notebook.resolve())
    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
    else:
        print(f"{rapport['notebook']} : {len(rapport['vues'])} vues ({', '.join(rapport['formats'])}), "
              f"{rapport['erreurs']} erreur(s)")
        for c in rapport["constats"]:
            ou = ":".join(str(x) for x in (c.get("vue"), c.get("fichier"), c.get("ligne")) if x)
            print(f"  {c['gravite'].upper()} {ou} {c['message']}")
    return 1 if rapport["erreurs"] else 0


if __name__ == "__main__":
    sys.exit(main())
