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

## 0. Lire d'abord les instructions du paquet

Ce skill est écrit pour marimo-studio 0.4.1 et marimo 0.25.2, que Studio épingle. Les instructions
pour agents livrées dans le paquet installé font foi pour tout ce qui change d'une version à
l'autre, API Python et options de commande comprises. Lis-les depuis l'environnement du notebook :

```bash
pixi run agent-plugins read marimo-studio
```

Lis ensuite l'`AGENTS.md` de chaque vue avant de la modifier. `references/docs/` contient la
documentation de Studio 0.4.1 sans réseau, et `references/exemples/` des sources d'exemples
officiels, comme le briefing reveal.js et le bulletin Quarto. `references/SOURCE.md` donne la
version et le commit.

## 1. Cadrer : un public, une tâche, un format

Avant toute ligne de code, écris pour chaque vue le public, ce qu'il doit faire après lecture, et
le format. Note-le dans le `DESIGN.md` de la vue, avec le système visuel.

| Public | Tâche du lecteur | Format | Starter |
|---|---|---|---|
| Grand public, lien partagé | Comprendre vite, explorer | Page React | `marimo-studio/react:default` |
| Réunion, comité | Décider en dix minutes | Diaporama | `marimo-studio/react:reveal` |
| Lecteur technique, archive | Vérifier les chiffres | PDF Typst | `marimo-studio/typst:default` |
| Lecteur de magazine, blog | Lire un récit argumenté | Article Quarto | `marimo-studio/quarto:default` |

Quatre vues pour quatre publics valent mieux que quatre fois la même page.

## 2. Structurer le notebook pour qu'il serve toutes les vues

`references/notebook.md` donne le détail. L'essentiel :

- une cellule nommée par étape, et des contrôles natifs (`mo.ui.dropdown`, `mo.ui.slider`) dans
  une cellule nommée, par exemple `controles` ;
- une valeur JSON unique pour les vues, par exemple `donnees_vues`, avec une synthèse chiffrée,
  les tableaux agrégés et des `messages` : les phrases qui affirment, rédigées par le notebook ;
- les séries longues à part, en DataFrame : elles voyagent en Arrow, alors qu'un export Prepared
  refuse un JSON trop gros (`exceeds the maximum JSON value count`) ;
- deux versions d'un graphique Altair : `width="container"` pour l'écran, une largeur fixe pour
  le PDF, sinon le rapport Typst grossit le texte du graphique.

Vérifie le notebook avant toute vue, avec le skill `marimo-agent-kit` :
`mak verifier notebook.py --marimo "pixi run marimo" --bac-a-sable non`.

## 3. Installer l'environnement

`references/environnement.md` donne la recette pixi essayée, avec Quarto et Typst depuis
conda-forge, et les réglages indispensables sous Windows : sans eux, les constructions React et
Quarto et l'export Prepared échouent sur la limite de 260 caractères des chemins.

```bash
pixi install
pixi run marimo-studio starters --target notebook.py
```

Chaque starter doit être `available`, sauf LaTeX si tu n'en as pas besoin.

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
pixi run marimo edit notebook.py --no-sandbox --watch --no-token --headless --port 2791
pixi run marimo pair notebook list
pixi run marimo pair execute --url http://localhost:2791 --session <SESSION_ID> --code-file etape.py
```

Une session n'existe qu'une fois l'éditeur ouvert dans un navigateur. Avec `--watch`, une
modification du fichier rend les cellules touchées « stale » sans les relancer : relance-les
dans le noyau (`references/notebook.md`). Après chaque modification d'une vue :

```bash
pixi run marimo-studio view build grand-public --target notebook.py
pixi run marimo-studio validate --target notebook.py --level static
```

Regarde ensuite la vue dans un vrai navigateur, à deux largeurs, et change un contrôle.
`scripts/capturer.py` pilote le Chrome ou l'Edge installé, attend
`html[data-marimo-studio-state="ready"]`, et rend l'état Studio, les diagnostics et les erreurs de
la console :

```bash
uv run --no-project --with playwright python scripts/capturer.py "<URL d'aperçu>" --sortie vue-1280.png --attendre ".graphique"
uv run --no-project --with playwright python scripts/capturer.py "<URL d'aperçu>" --sortie vue-390.png --largeur 390 --hauteur 844
uv run --no-project --with playwright python scripts/capturer.py "<URL>" --sortie vue-2014.png --choisir 0=2014 --attendre-texte "En 2014"
```

L'URL d'aperçu vient du noyau : `await workspace.view("grand-public").preview_url(runtime="server")`.
Ouvre chaque capture avec un outil qui lit les images : enregistrer un PNG ne prouve rien.

Enfin, `scripts/controler_vues.py notebook.py` relit les sources des vues contre les critères de
`references/qualite.md` : texte du gabarit resté en place, cibles `cell-N`, `DESIGN.md` absent,
chiffre écrit dans la vue au lieu de venir du notebook.

## 7. Exporter

`references/exports.md` donne les commandes essayées et leurs limites :

| Livrable | Chemin | Remarque |
|---|---|---|
| Site interactif sans Python | `view export --runtime zero-python` et `states.yaml` | Dossier à servir en HTTP ; ne s'ouvre pas en `file://` |
| PDF du rapport | Le PDF rendu dans l'export Prepared de la vue Typst | Un PDF par état préparé |
| PDF du diaporama | `capturer.py --diapos N --pdf` sur l'export | Pages en images ; `?print-pdf` laisse des pages blanches |
| PPTX | Script qui exécute le notebook, écrit un `.qmd`, puis `quarto render --to pptx` | Studio n'exporte pas de PPTX |
| Notebook en un fichier | `marimo export html` | Un seul fichier, sans interaction |

## 8. Critères d'une restitution de qualité

`references/qualite.md` les détaille, chacun avec sa façon de le contrôler. En bref : un public
et une tâche écrits dans `DESIGN.md` ; le titre de chaque vue est une réponse, pas un intitulé ;
aucun chiffre ni constat écrit dans la vue ; un système visuel propre à la vue, pas le starter ;
lisible à 1280 et à 390 pixels ; un contrôle changé met tout à jour ; états de chargement et
d'erreur ; chaque export ouvert et regardé.

## 9. L'exemple complet

Le dépôt marimo-agent-kit contient `exemples/meteo-seattle/` : un notebook sur la pluie à Seattle
et quatre vues, React, reveal.js, Typst et Quarto, avec leurs `DESIGN.md`, le `pixi.toml` et le
script PPTX. Copie ses motifs plutôt que de repartir des starters. Son `README.md` donne les
commandes, dans l'ordre.
