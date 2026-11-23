"""Écrire une page HTML autonome qui garde l'interaction : une « photo interactive » du notebook.

    pixi run python page_autonome.py

Studio 0.4.1 n'exporte pas de page en un seul fichier : son site Prepared se sert en HTTP et
charge des modules qu'un navigateur refuse en `file://`. Ce script exécute le notebook comme un
module, une fois par combinaison des contrôles, et fige chaque état dans la page : messages du
notebook, chiffres clés et figures en SVG. Les deux menus de la page affichent l'état choisi, par
quelques lignes de JavaScript. Le fichier s'ouvre depuis le disque, sans réseau, et sort dans
`dist/page/meteo.html`.
"""

from __future__ import annotations

import html
import itertools
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
SORTIE = ICI / "dist" / "page" / "meteo.html"


def svg(graphique) -> str:
    import vl_convert

    return vl_convert.vegalite_to_svg(graphique.properties(background="transparent").to_json())


def etat(definitions: dict) -> str:
    s, m = definitions["synthese"], definitions["messages"]
    nombre, pourcent = definitions["nombre"], definitions["pourcent"]
    chiffres = [
        (pourcent(s["part_pluie"]), "des jours sont pluvieux"),
        (f"{nombre(s['hauteur_annuelle_mm'])} mm", "de pluie par an"),
        (f"{s['serie_pluie']['jours']} jours", "de pluie d'affilée, au plus"),
        (f"{s['serie_seche']['jours']} jours", "secs d'affilée, au plus"),
    ]
    e = html.escape
    return f"""
  <h1>{e(m['titre'])}</h1>
  <p class="chapeau">{e(m['chapeau'])}</p>
  <div class="chiffres">{''.join(f'<p><strong>{e(v)}</strong>{e(t)}</p>' for v, t in chiffres)}</div>
  <h2>La saison fait tout</h2>
  <p>{e(m['saison'])}</p>
  <figure>{svg(definitions['figure_saison'])}</figure>
  <h2>Souvent, mais peu à la fois</h2>
  <p>{e(m['intensite'])} {e(m['series'])}</p>
  <figure>{svg(definitions['figure_pluie'])}</figure>
  <h2>D'une année à l'autre</h2>
  <p>{e(m['hauteur'])}</p>"""


def page(etats: dict[str, str], annees: list[str], seuils: list[str], initial: tuple[str, str], source: dict) -> str:
    def menu(nom: str, libelle: str, options: list[str], choisie: str) -> str:
        items = "".join(f'<option{" selected" if o == choisie else ""}>{html.escape(o)}</option>' for o in options)
        return f'<label>{libelle} <select id="{nom}">{items}</select></label>'

    sections = "".join(
        f'<section data-etat="{html.escape(cle)}"{"" if cle == "|".join(initial) else " hidden"}>{corps}</section>'
        for cle, corps in etats.items()
    )
    return f"""<!doctype html>
<html lang="fr">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seattle sous la pluie</title>
<style>
  :root {{
    --papier: #f6f4ef; --encre: #17202a; --texte: #36414b; --discret: #6b7680; --filet: #dcd8cf;
    --titre: "Iowan Old Style", "Palatino Linotype", Palatino, "URW Palladio L", P052, "Book Antiqua", Georgia, serif;
    --corps: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans", "Helvetica Neue", Arial, sans-serif;
  }}
  body {{ margin: 0; background: var(--papier); color: var(--texte); font: 17px/1.55 var(--corps); }}
  main {{ max-width: 46rem; margin: auto; padding: 0 1rem 3rem; }}
  .reglages {{ position: sticky; top: 0; display: flex; flex-wrap: wrap; gap: .5rem 1.5rem; padding: .75rem 0;
    background: var(--papier); border-bottom: 1px solid var(--filet); }}
  .reglages label {{ font-weight: 600; color: var(--encre); }}
  select {{ font: inherit; margin-inline-start: .4rem; }}
  h1, h2 {{ font-family: var(--titre); color: var(--encre); line-height: 1.08; }}
  h1 {{ font-size: clamp(2.2rem, 7vw, 3.6rem); margin: 2.5rem 0 1rem; }}
  h2 {{ font-size: 1.6rem; margin: 2.5rem 0 .5rem; }}
  .chiffres {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr)); gap: 1rem; }}
  .chiffres p {{ margin: 0; border-top: 2px solid var(--encre); padding-top: .4rem; color: var(--discret); font-size: .85rem; }}
  .chiffres strong {{ display: block; font: 2rem/1.2 var(--titre); color: var(--encre); font-variant-numeric: tabular-nums; }}
  figure {{ margin: 1rem 0; overflow-x: auto; }}
  figure svg {{ max-width: 100%; height: auto; }}
  footer {{ margin-top: 3rem; font-size: .85rem; color: var(--discret); }}
</style>
<main>
  <div class="reglages">{menu("annee", "Année", annees, initial[0])}{menu("seuil", "Seuil d'un jour de pluie", seuils, initial[1])}</div>
  <div aria-live="polite">{sections}</div>
  <footer>Source : {html.escape(source['nom'])}. Calculs du notebook marimo <code>meteo.py</code>, figés à
  l'écriture de cette page pour chaque réglage.</footer>
</main>
<script>
  const menus = [document.getElementById("annee"), document.getElementById("seuil")];
  const afficher = () => {{
    const cle = menus.map((m) => m.value).join("|");
    document.querySelectorAll("section[data-etat]").forEach((s) => {{ s.hidden = s.dataset.etat !== cle; }});
  }};
  menus.forEach((m) => m.addEventListener("change", afficher));
</script>
</html>
"""


def main() -> int:
    sys.path.insert(0, str(ICI))
    import marimo as mo
    from meteo import app

    _, initial = app.run()
    annees = list(initial["annee"].options)
    seuils = list(initial["seuil"].options)
    etats = {}
    for annee, seuil in itertools.product(annees, seuils):
        # Remplacer une cellule demande toutes ses définitions, même celles que le script ne change pas.
        _, definitions = app.run(defs={
            "annees_disponibles": initial["annees_disponibles"],
            "annee": mo.ui.dropdown(options=annees, value=annee),
            "seuil": mo.ui.dropdown(options=initial["seuil"].options, value=seuil),
        })
        etats[f"{annee}|{seuil}"] = etat(definitions)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    choix = (initial["annee"].value, initial["seuil"].selected_key)
    SORTIE.write_text(page(etats, annees, seuils, choix, initial["donnees_vues"]["source"]), encoding="utf-8")
    print(f"{SORTIE} : {len(etats)} états, {SORTIE.stat().st_size // 1024} Ko")
    print(json.dumps({"etat_initial": "|".join(choix)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
