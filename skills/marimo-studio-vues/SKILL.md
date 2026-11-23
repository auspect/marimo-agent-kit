---
name: marimo-studio-vues
description: >-
  Faire d'une analyse marimo plusieurs restitutions soignées avec marimo Studio 0.4.1 : page React,
  diaporama reveal.js, rapport PDF Typst, article Quarto, et leurs exports (site statique sans
  Python, PDF, PPTX). Dit comment cadrer chaque public, structurer le notebook pour qu'il serve
  toutes les vues, construire, regarder et contrôler chaque vue, puis l'exporter, avec un exemple
  complet essayé sous Windows. À utiliser quand on demande « un Studio », des vues, une page, un
  tableau de bord, des slides, un rapport PDF, un article ou un export d'un notebook marimo, ou
  quand un dossier `studio/` ou un `view.toml` est en jeu. Use for: marimo studio views, react
  view, reveal.js deck, typst report, quarto article, static export, pptx from notebook.
---

# marimo Studio : plusieurs restitutions d'une seule analyse

Studio tire d'un notebook des vues nommées. Le notebook garde les données, les calculs, les
contrôles et les phrases qui affirment quelque chose. La vue ne fait que la présentation. Un
notebook « un peu amélioré » n'est pas une restitution : chaque vue sert un public précis, dans le
format de ce public, et elle a été construite, regardée et exportée pour de vrai.

## 0. Créer l'environnement, avant toute autre commande

Chaque commande qui suit passe par `pixi run` et cherche un projet pixi en remontant les
dossiers. Sans lui, la première échoue (`found pyproject.toml without tool.pixi section`). pixi
gère le projet, comme partout dans le kit, au format `pyproject.toml`. Depuis le dossier du
notebook :

```bash
pixi init --format pyproject
pixi add "python=3.13.*" "quarto>=1.9.38" "typst>=0.15"
pixi add --pypi "marimo-studio[deno,typst]==0.4.1" polars altair vl-convert-python
pixi run marimo-studio status --target notebook.py
```

Ajoute ensuite `[tool.marimo.package_management]`, `[tool.marimo-studio]` et, sous Windows, deux
variables d'activation : `references/environnement.md` donne le fichier essayé. Sans ces
variables, les constructions React et Quarto et l'export Prepared échouent sur la limite de 260
caractères des chemins. Le notebook n'a alors pas d'en-tête PEP 723. `pixi run marimo-studio
starters --target notebook.py` liste les starters : seuls ceux des formats choisis doivent être
`available` ; Quarto manque tant qu'il n'est pas installé, LaTeX demande Tectonic.

## 1. Lire les instructions du paquet

Ce skill est écrit pour marimo-studio 0.4.1 et marimo 0.25.2, que Studio épingle. Les instructions
pour agents livrées dans le paquet installé font foi pour tout ce qui change d'une version à
l'autre : `pixi run agent-plugins read marimo-studio`. Lis ensuite l'`AGENTS.md` de chaque vue
avant de la modifier. `references/docs/` contient la documentation de Studio 0.4.1 sans réseau,
`references/exemples/` des sources d'exemples officiels, et `references/SOURCE.md` la version.

## 2. Cadrer : un public, une tâche, un format

Avant toute ligne de code, écris pour chaque vue le public, ce qu'il doit faire après lecture, et
le format. Note-le dans le `DESIGN.md` de la vue, avec le système visuel.

| Public | Tâche du lecteur | Format | Starter |
|---|---|---|---|
| Grand public, lien partagé | Comprendre vite, explorer | Page React | `marimo-studio/react:default` |
| Décideur, suivi régulier | Comparer, trier, situer un élément | Tableau de bord React | `marimo-studio/react:default` |
| Réunion, comité | Décider en dix minutes | Diaporama | `marimo-studio/react:reveal` |
| Lecteur technique, archive | Vérifier les chiffres | PDF Typst | `marimo-studio/typst:default` |
| Lecteur de magazine, blog | Lire un récit argumenté | Article Quarto | `marimo-studio/quarto:default` |

Quatre vues pour quatre publics valent mieux que quatre fois la même page.

## 3. Structurer le notebook pour qu'il serve toutes les vues

`references/notebook.md` donne le détail. L'essentiel :

- une cellule nommée par étape, et des contrôles natifs (`mo.ui.dropdown`, `mo.ui.slider`) dans
  une cellule nommée, par exemple `controles` ;
- une valeur JSON unique pour les vues, par exemple `donnees_vues`, avec une synthèse chiffrée,
  les tableaux agrégés et des `messages` : les phrases qui affirment, rédigées par le notebook ;
- les séries longues à part, en DataFrame : elles voyagent en Arrow, alors qu'un export Prepared
  refuse un JSON trop gros (`exceeds the maximum JSON value count`) ;
- deux versions d'un graphique Altair : `width="container"` pour l'écran, une largeur fixe pour
  le PDF, sinon le rapport Typst grossit le texte du graphique.

Vérifie le notebook avant toute vue : `mak verifier notebook.py`, depuis le dossier du projet.
`mak` s'installe hors du projet (`uv tool install`, voir le skill `marimo-agent-kit`) et trouve
seul le marimo de l'environnement pixi. Ne l'ajoute pas au projet pour le lancer par `pixi run
mak` : un essai y a vu pixi réinstaller `mak.exe` pendant qu'il tournait (`failed to remove
file .../Scripts/mak.exe`). Plus besoin de `--marimo` ni de `--bac-a-sable`.

## 4. Créer les vues

```bash
pixi run marimo-studio view create grand-public --target notebook.py --starter marimo-studio/react:default
pixi run marimo-studio view create briefing --target notebook.py --starter marimo-studio/react:reveal
pixi run marimo-studio view create rapport --target notebook.py --starter marimo-studio/typst:default
pixi run marimo-studio view create article --target notebook.py --starter marimo-studio/quarto:default --setting toc=true
```

Le starter place chaque cellule qui affiche quelque chose. C'est un point de départ, pas une
restitution : remplace-le entièrement.

## 5. Écrire chaque vue

Une recette par format, chacune tirée de l'exemple :

- `references/react.md` : `useMarimoValue`, tableaux Arrow, graphiques SVG sans bibliothèque,
  composants partagés, états de chargement et d'erreur, Lens, mise en page responsive ;
- `references/revealjs.md` : canevas 1440 × 810, un message du notebook par titre de diapositive,
  contrôles en direct, lecture verticale sur téléphone ;
- `references/typst.md` : `marimo_value`, `marimo_output`, `marimo_region`, mise en forme
  française, tableaux complets, PDF hors Studio ;
- `references/quarto.md` : shortcodes `value`, `output` et `cell`, thème SCSS, encadrés, notes en
  marge, Quarto de conda-forge.

## 6. Construire, regarder, contrôler

Lance le notebook avec Studio, puis travaille dans le noyau par `marimo pair` :

```bash
mak marimo edit notebook.py --watch --no-token --headless --port 2791
pixi run marimo pair notebook list
pixi run marimo pair execute --url http://localhost:2791 --session <SESSION_ID> --code-file etape.py
```

Une session n'existe qu'une fois l'éditeur ouvert dans un navigateur : avant, `notebook list`
rend `"notebooks": []`. Ouvre `http://localhost:2791/`, relance la liste, et prends
`notebooks[].sessions[].session_id`. Avec `--watch`, une modification du fichier rend les
cellules touchées « stale » sans les relancer : relance-les dans le noyau
(`references/notebook.md`). Après chaque modification d'une vue :

```bash
pixi run marimo-studio view build grand-public --target notebook.py --profile production
pixi run marimo-studio validate --target notebook.py --level static
```

Regarde ensuite la vue dans un vrai navigateur, à deux largeurs, et change un contrôle. `marimo
run` sert chaque vue à `http://127.0.0.1:<port>/<vue>/` dans un cadre ; l'URL de la vue seule
vient de `pixi run marimo-studio view preview <vue> --target notebook.py --runtime server
--server http://127.0.0.1:<port> --exact`, qui demande une construction `--profile production`.
Cette URL porte la révision construite : redemande-la après chaque construction, sinon la page
reste sur « Chargement ».
`scripts/capturer.py` pilote le Chrome ou l'Edge installé, attend
`html[data-marimo-studio-state="ready"]`, et rend l'état Studio, les diagnostics et les erreurs de
la console :

```bash
uv run --no-project --with playwright python scripts/capturer.py "<URL>" --sortie vue-1280.png --attendre ".graphique"
uv run --no-project --with playwright python scripts/capturer.py "<URL>" --sortie vue-390.png --largeur 390 --hauteur 844
uv run --no-project --with playwright python scripts/capturer.py "<URL>" --sortie vue-2014.png --attendre ".graphique" --choisir 2014 --attendre-texte "En 2014"
```

`--choisir 2014` prend le seul menu qui propose « 2014 », Shadow DOM des contrôles compris, et
échoue si aucun ou plusieurs le proposent. Attends d'abord un élément dessiné (`--attendre`) : un
choix fait avant l'arrivée des valeurs se perd. Lance les captures l'une après l'autre. Une vue
Typst n'a pas de menu : le PDF suit les contrôles du notebook, qui se changent dans le cadre du
notebook de l'éditeur ; compare alors deux PDF. Ouvre chaque capture avec un outil qui lit les
images : enregistrer un PNG ne prouve rien.

Enfin, `scripts/controler_vues.py notebook.py` relit les sources des vues contre les critères de
`references/qualite.md` : texte du gabarit resté en place, cibles `cell-N`, `DESIGN.md` absent,
chiffre écrit dans la vue au lieu de venir du notebook.

## 7. Exporter

`references/exports.md` donne les commandes essayées et leurs limites. Exporte une vue à la
fois, ne touche à aucun fichier du dossier du projet pendant l'export, et ne capture l'export
qu'une fois la commande finie. Exporte tôt dès qu'une vue lit un tableau Arrow : un export peut
casser ce que le direct montrait.

| Livrable | Chemin | Remarque |
|---|---|---|
| Site interactif sans Python | `view export --runtime zero-python` et `states.yaml` | Dossier à servir en HTTP ; ne s'ouvre pas en `file://` |
| PDF du rapport | Le PDF rendu dans l'export Prepared de la vue Typst | Un PDF par état préparé |
| PDF du diaporama | `capturer.py --diapos N --pdf` sur l'export | Pages en images ; `?print-pdf` laisse des pages blanches |
| PPTX | Script qui exécute le notebook, écrit un `.qmd`, puis `quarto render --to pptx` | Studio n'exporte pas de PPTX |
| Page autonome interactive | Script qui exécute le notebook pour chaque réglage et fige les résultats dans un HTML | S'ouvre en `file://`, hors ligne ; les menus changent le résultat |
| Notebook en un fichier | `marimo export html` | Un seul fichier, sans interaction |

## 8. Critères d'une restitution de qualité

`references/qualite.md` les détaille, chacun avec sa façon de le contrôler. En bref : un public
et une tâche écrits dans `DESIGN.md` ; le titre de chaque vue est une réponse, pas un intitulé ;
aucun chiffre ni constat écrit dans la vue ; un système visuel propre à la vue, pas le starter ;
lisible à 1280 et à 390 pixels ; un contrôle changé met tout à jour ; états de chargement et
d'erreur ; chaque export ouvert et regardé.

## 9. L'exemple complet

Le dépôt marimo-agent-kit contient `exemples/meteo-seattle/` : un notebook sur la pluie à Seattle
et quatre vues, React, reveal.js, Typst et Quarto, avec leurs `DESIGN.md`, le `pyproject.toml` et le
script PPTX. Copie ses motifs plutôt que de repartir des starters. Son `README.md` donne les
commandes, dans l'ordre.
