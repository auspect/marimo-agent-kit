"""Capturer une vue Studio, ou une page exportée, dans un vrai navigateur.

    uv run --no-project --with playwright python capturer.py URL --sortie vue.png
    uv run --no-project --with playwright python capturer.py URL --sortie vue.png --largeur 390 --hauteur 844
    uv run --no-project --with playwright python capturer.py URL --pdf deck.pdf --largeur 1440 --hauteur 810

Le script pilote Chrome ou Edge déjà installés (canal `chrome`, puis `msedge`) : il ne télécharge
aucun navigateur. Il attend `html[data-marimo-studio-state="ready"]` quand la page vient de
Studio, puis `--attendre`, un sélecteur CSS propre à la vue, comme un graphique dessiné. Il écrit
sur la sortie standard l'état Studio, la révision affichée et les erreurs de la console : une
capture seule ne prouve pas que la vue a reçu ses valeurs.

`--hors-ligne` bloque toute requête vers un autre hôte que celui de la page, toutes pour une page
ouverte en `file://`, et les rend dans `requetes_bloquees`.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from urllib.parse import urlsplit


def hors_page(url_page: str, url: str) -> bool:
    """Vrai pour une requête qui sortirait du poste : un autre hôte que la page, ou tout hôte depuis `file://`."""
    cible = urlsplit(url)
    if cible.scheme in ("data", "blob", "file", "about"):
        return False
    return urlsplit(url_page).scheme == "file" or cible.netloc != urlsplit(url_page).netloc


def ouvrir_navigateur(playwright, canal: str | None):
    from playwright.sync_api import Error

    canaux = [canal] if canal else ["chrome", "msedge"]
    erreurs = []
    for nom in canaux:
        try:
            return playwright.chromium.launch(channel=nom)
        except Error as erreur:
            erreurs.append(f"{nom} : {str(erreur).splitlines()[0]}")
    sys.exit("Aucun navigateur trouvé. " + " ; ".join(erreurs))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url")
    parser.add_argument("--sortie", help="capture PNG de toute la page")
    parser.add_argument("--pdf", help="impression PDF de la page, par exemple un diaporama ?print-pdf")
    parser.add_argument("--largeur", type=int, default=1280)
    parser.add_argument("--hauteur", type=int, default=900)
    parser.add_argument("--attendre", help="sélecteur CSS à attendre en plus de l'état Studio")
    parser.add_argument("--choisir", action="append", default=[], metavar="RANG=OPTION",
                        help="choisir OPTION dans la liste déroulante numéro RANG (0 pour la première), "
                             "comme un lecteur qui change un contrôle du notebook")
    parser.add_argument("--hors-ligne", action="store_true",
                        help="bloquer les requêtes vers un autre hôte que la page, et les lister")
    parser.add_argument("--attendre-texte", help="texte qui doit apparaître après les choix")
    parser.add_argument("--touche", action="append", default=[],
                        help="touche à presser avant la capture, par exemple ArrowRight pour la diapositive suivante")
    parser.add_argument("--diapos", type=int, default=0, metavar="N",
                        help="diaporama : capturer N diapositives en passant de l'une à l'autre par ArrowRight, "
                             "puis les réunir dans le PDF de --pdf, une page par diapositive")
    parser.add_argument("--studio", choices=["oui", "non", "auto"], default="auto",
                        help="attendre l'état Studio : auto l'attend s'il apparaît")
    parser.add_argument("--delai", type=float, default=60, help="secondes d'attente au plus")
    parser.add_argument("--pause", type=float, default=1.5, help="secondes laissées aux transitions")
    parser.add_argument("--canal", help="chrome, msedge ou chromium")
    parser.add_argument("--ecran", action="store_true", help="ne capturer que l'écran visible")
    args = parser.parse_args()
    if not args.sortie and not args.pdf:
        parser.error("donne --sortie, --pdf ou les deux")

    from playwright.sync_api import Error, sync_playwright

    erreurs_console: list[str] = []
    bloquees: list[str] = []
    with sync_playwright() as playwright:
        navigateur = ouvrir_navigateur(playwright, args.canal)
        page = navigateur.new_page(viewport={"width": args.largeur, "height": args.hauteur})
        page.on("console", lambda m: erreurs_console.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: erreurs_console.append(str(e)))
        if args.hors_ligne:
            def filtrer(route):
                if hors_page(args.url, route.request.url):
                    bloquees.append(route.request.url)
                    return route.abort()
                return route.continue_()

            page.route("**/*", filtrer)
        page.goto(args.url, wait_until="load", timeout=args.delai * 1000)
        etat = None
        if args.studio != "non":
            try:
                page.wait_for_function(
                    "() => document.documentElement.dataset.marimoStudioState !== undefined",
                    timeout=(args.delai if args.studio == "oui" else 5) * 1000)
                page.wait_for_selector('html[data-marimo-studio-state="ready"], html[data-marimo-studio-state="error"]',
                                       state="attached", timeout=args.delai * 1000)
            except Error:
                if args.studio == "oui":
                    raise
            etat = page.evaluate("document.documentElement.dataset.marimoStudioState ?? null")
        attente_echouee = None
        if args.attendre:
            try:
                page.wait_for_selector(args.attendre, timeout=args.delai * 1000)
            except Error:
                attente_echouee = args.attendre
        for choix in args.choisir:
            rang, _, option = choix.partition("=")
            page.locator("select").nth(int(rang)).select_option(label=option)
            page.wait_for_timeout(500)
        if args.attendre_texte:
            page.get_by_text(args.attendre_texte).filter(visible=True).first.wait_for(timeout=args.delai * 1000)
        for touche in args.touche:
            page.keyboard.press(touche)
            page.wait_for_timeout(400)
        page.wait_for_timeout(args.pause * 1000)
        if args.diapos:
            images = []
            for rang in range(args.diapos):
                if rang:
                    page.keyboard.press("ArrowRight")
                    page.wait_for_timeout(args.pause * 1000)
                images.append(base64.b64encode(page.screenshot()).decode())
            if args.sortie:
                page.screenshot(path=args.sortie, full_page=not args.ecran)
            if args.pdf:
                feuille = navigateur.new_page()
                feuille.set_content(
                    "<style>@page{margin:0}body{margin:0}img{display:block;width:100%;"
                    "break-after:page}</style>"
                    + "".join(f'<img src="data:image/png;base64,{image}">' for image in images))
                feuille.pdf(path=args.pdf, width=f"{args.largeur}px", height=f"{args.hauteur}px",
                            print_background=True)
            args.pdf = None
            args.sortie = None
        if args.sortie:
            page.screenshot(path=args.sortie, full_page=not args.ecran)
        if args.pdf:
            page.emulate_media(media="print")
            page.pdf(path=args.pdf, width=f"{args.largeur}px", height=f"{args.hauteur}px",
                     print_background=True)
        rapport = {
            "url": page.url,
            "etat_studio": etat,
            "revision": page.evaluate("document.documentElement.dataset.marimoStudioRevision ?? null"),
            "titre": page.title(),
            "selecteur_absent": attente_echouee,
            "diagnostics": page.evaluate(
                "globalThis.marimoStudio?.diagnostics ? JSON.parse(JSON.stringify(marimoStudio.diagnostics())) : null"),
            "erreurs_console": erreurs_console,
            "requetes_bloquees": bloquees,
        }
        navigateur.close()
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 1 if etat == "error" or attente_echouee else 0


if __name__ == "__main__":
    raise SystemExit(main())
