# Exporter : site statique, PDF, PPTX

Essayé sur `exemples/meteo-seattle` avec marimo-studio 0.4.1, sous Windows. Choisis le runtime
avant de concevoir les contrôles : `references/docs/guide/run-and-share.md` les compare.

## Site interactif sans Python : l'export Prepared

L'export Prepared (`zero-python`) exécute le notebook une fois par état préparé, puis écrit un
site statique : la vue construite, les résultats de chaque état, aucun code du notebook. Changer
un contrôle charge l'état préparé qui correspond.

1. Décris les états dans `states.yaml`, dans le dossier de la vue. Les clés sont les noms des
   contrôles, les valeurs leur valeur côté navigateur : la liste d'un libellé pour un menu
   déroulant, un nombre pour un curseur.

   ```yaml
   schema: marimo-export.states.v1
   default_state: matrix-000001
   matrix:
     annee: [[Toutes], ["2012"], ["2013"], ["2014"], ["2015"]]
     seuil: [["0,1 mm"], ["1 mm"], ["5 mm"]]
   ```

   Cette matrice prépare 15 états. Sans `states.yaml`, seul l'état initial est préparé.

2. Exporte :

   ```bash
   pixi run marimo-studio view export grand-public --target notebook.py --output "$HOME/.mxo/grand-public" --prepare-timeout 300 --force
   ```

   Durées mesurées : 25 s à 1 min 35 s par vue, 15 états compris. Le site de la page React pèse
   21 Mo pour 264 fichiers.

3. Sers le dossier en HTTP et vérifie-le comme une vue en direct, contrôle changé compris :

   ```bash
   uv run --no-project python -m http.server --bind 127.0.0.1 2792 --directory $HOME/.mxo
   uv run --no-project --with playwright python scripts/capturer.py http://127.0.0.1:2792/grand-public/ --sortie export.png --choisir 0=2013 --choisir "1=5 mm" --attendre-texte "En 2013"
   ```

Ce que l'on obtient, et ce que l'on n'obtient pas :

- Le site marche sur tout hébergement statique, sans serveur Python. Seul 404 constaté :
  `/favicon.ico`.
- Il ne s'ouvre pas en `file://` : le navigateur bloque les modules et les feuilles de style
  (`Access to script at 'file:///.../zero-python.js' from origin 'null' has been blocked by CORS
  policy`). Studio 0.4.1 ne produit pas de page HTML en un seul fichier : la section suivante
  en donne une.
- Le site n'est pas hors ligne : polices Google et scripts distants restent des requêtes.
- Limite des valeurs JSON : un état ne peut pas porter une liste de 1 461 objets. L'erreur est
  `exceeds the maximum JSON value count`. Projette la série en DataFrame, elle voyage en Arrow.
- Sous Windows, régle d'abord les chemins (`references/environnement.md`), et exporte vers un
  dossier court.

## Page autonome qui garde l'interaction : une photo interactive

Pour un fichier qu'on envoie, qu'on ouvre depuis le disque et qui marche sans réseau, la recette
fait ce que fait l'export Prepared, en plus simple : exécuter le notebook une fois par
combinaison des contrôles, figer chaque résultat, et laisser le navigateur choisir lequel montrer.
Modèle : `exemples/meteo-seattle/page_autonome.py`, 135 lignes.

1. Importe le notebook comme un module et exécute-le avec les valeurs par défaut :
   `_, initial = app.run()`. `initial["annee"].options` donne les options de chaque contrôle.
2. Pour chaque combinaison, remplace la cellule des contrôles par de vrais éléments `mo.ui`, avec
   toutes ses définitions, sinon marimo lève `IncompleteRefsError` :

   ```python
   _, d = app.run(defs={
       "annees_disponibles": initial["annees_disponibles"],
       "annee": mo.ui.dropdown(options=annees, value=annee),
       "seuil": mo.ui.dropdown(options=initial["seuil"].options, value=seuil),
   })
   ```

3. Écris pour chaque état une `<section data-etat="2014|5 mm" hidden>` : les `messages` du
   notebook, les chiffres clés formatés par ses fonctions, et les figures Altair en SVG par
   `vl_convert.vegalite_to_svg(graphique.to_json())`. Échappe chaque texte (`html.escape`).
4. Ajoute les menus et dix lignes de JavaScript qui montrent la section de l'état choisi. Styles
   en ligne, polices du système, aucun lien vers l'extérieur.

```bash
pixi run python page_autonome.py
uv run --no-project --with playwright python scripts/capturer.py "file:///C:/.../dist/page/meteo.html" --studio non --hors-ligne --choisir 0=2014 --choisir "1=5 mm" --attendre-texte "En 2014" --sortie page-2014.png
```

Sur l'exemple : 15 états en 13 s, un fichier de 0,4 Mo. Ouvert en `file://` avec toute requête
réseau bloquée, la page affiche « Il pleut un jour sur 2,9 à Seattle » ; après 2014 et 5 mm,
« Il pleut un jour sur 4,9 à Seattle », 21 %, et `requetes_bloquees` reste vide.

Ce que la photo ne fait pas : elle ne connaît que les combinaisons calculées, et elle n'est pas
une vue Studio. Elle reprend le système visuel de la vue, pas son code : une page de plus à tenir
quand la vue change. Garde-la courte, et réserve-la aux contrôles à peu d'options ; à 10 options
par contrôle sur trois contrôles, mille états ne tiennent plus dans un fichier.

## Site qui calcule dans le navigateur : l'export Browser

```bash
pixi run marimo-studio view export grand-public --target notebook.py --runtime wasm --output "$HOME/.mxo/grand-public-wasm" --force
```

L'export réussit, mais la page échoue dans le navigateur : Pyodide installe les dépendances de
l'en-tête du notebook, et `vl-convert-python` n'a pas de roue pour lui (`ValueError: Can't find a
pure Python 3 wheel for 'vl-convert-python>=1.8'`). L'export Browser demande un notebook dont
toutes les dépendances existent pour Pyodide ; une vue Typst y affiche de toute façon
`render-results-unavailable`. Il publie aussi le code du notebook.

## PDF du rapport Typst

L'export Prepared d'une vue Typst contient un PDF par état préparé :

```bash
pixi run marimo-studio view export rapport --target notebook.py --output "$HOME/.mxo/rapport" --force
```

Le fichier est `_marimo-studio/views/rapport/renders/<empreinte>/main.pdf` dans le dossier
exporté. Sans `states.yaml`, il n'y en a qu'un, celui de l'état initial. Pendant l'édition, le
lien « Download » de la vue donne le même PDF.

## PDF du diaporama

```bash
uv run --no-project --with playwright python scripts/capturer.py http://127.0.0.1:2792/briefing/ --diapos 7 --pdf briefing.pdf --largeur 1440 --hauteur 810 --attendre ".reveal .slides section"
```

Une page par diapositive, en image. `?print-pdf` ne marche pas ici : voir
`references/revealjs.md`.

## PPTX : par Quarto

Studio 0.4.1 n'exporte pas de PowerPoint. Le chemin le plus court qui marche :
`exemples/meteo-seattle/diapos_pptx.py`.

```bash
pixi run python diapos_pptx.py
```

Le script importe le notebook comme un module : `app.run()` exécute toutes les cellules avec les
valeurs par défaut des contrôles et rend leurs définitions. Il enregistre les deux figures Altair
en PNG (`chart.save("saison.png", scale_factor=2)`, par vl-convert), écrit un `.qmd` dont chaque
diapositive porte un message du notebook, puis lance `quarto render diapos.qmd --to pptx`. Le
fichier sort dans `dist/pptx/diapos.pptx` en une dizaine de secondes : six diapositives, titres et
textes modifiables, deux images, un tableau. Le gabarit est celui de Pandoc ; un
`reference-doc` dans l'en-tête du `.qmd` y mettrait une charte.

Écarté : `marimo export ipynb --include-outputs` puis Quarto. L'export demande `nbformat`, et les
graphiques Altair y sont du JSON Vega-Lite, que le PPTX ignore.

## Le notebook lui-même

```bash
pixi run marimo export html notebook.py --no-sandbox -o notebook.html -f
```

Un seul fichier, qui s'ouvre en `file://`, avec code et sorties, mais sans interaction : les
contrôles ne répondent plus. Ce n'est pas une vue Studio.
