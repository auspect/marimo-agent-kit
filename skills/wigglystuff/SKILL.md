---
name: wigglystuff
description: >-
  Choisir et utiliser un widget wigglystuff dans un notebook marimo, par exemple Slider2D,
  TangleDistribution, ChartPuck, PairPlot, StateViewer, FitProgress, TraceView, Paint ou
  FloatingPanel. Le skill embarque la documentation de la version 0.6.0 sans réseau, avec les
  pages, les signatures, les traitlets et les démos. À utiliser quand une interaction dépasse
  mo.ui, comme régler deux paramètres d'un geste, glisser un nombre dans une phrase, sélectionner
  sur un graphique matplotlib, dessiner, suivre un algorithme ou suivre un entraînement. À
  utiliser aussi quand une tâche cite wigglystuff, anywidget ou un de ses widgets. Use for:
  wigglystuff widgets, anywidget in marimo, interactive explanations, choosing a widget.
---

# Widgets wigglystuff dans marimo

wigglystuff est une bibliothèque de Vincent Warmerdam, sous licence MIT. Elle rassemble environ 70
widgets AnyWidget. Ils servent quand l'interaction aide à comprendre. Un geste règle deux
paramètres, un nombre se glisse dans une phrase, un algorithme se rejoue ligne à ligne. Pour un
réglage ordinaire, `mo.ui` suffit et reste le premier choix.

## 1. Choisir

| Besoin | Widget | Idéal pour | Préfère autre chose si |
|---|---|---|---|
| Régler deux paramètres liés d'un geste | `Slider2D` | Le point de départ d'une optimisation, un couple (μ, σ) | Une grille discrète demande `HeatmapSelect`, un seul paramètre `mo.ui.slider`. |
| Parcourir une grille précalculée | `HeatmapSelect` | Des résultats par couple (a, b), une ligne ou une colonne épinglée | Des valeurs continues demandent `Slider2D`. |
| Régler un nombre dans le texte | `TangleSlider`, `TangleChoice`, `TangleSelect` | Les explications à la manière de Bret Victor | Un formulaire de réglages demande `mo.ui` et `.form()`. |
| Régler une loi de probabilité | `TangleDistribution` | Un a priori bayésien. Le widget connaît 14 familles et fournit `sample` et `cdf` sans scipy. | |
| Manipuler une formule | `TangleLatex`, `FormulaDAG`, `FormulaAnimation` | Un cours, avec des paramètres, une chaîne de calcul ou une dérivation pas à pas | Une formule fixe demande `mo.md` avec `$$`. |
| Appeler une fonction typée | `TangleFunction` | Explorer une fonction annotée, avec les bornes de pydantic | |
| Animer un paramètre ou des images | `PlaySlider`, `FramePlayer` | Parcourir le temps ou une simulation | |
| Saisir une matrice ou un ordre | `Matrix`, `SortableList` | Des poids, des transformations, des priorités | Un tableau de données demande `mo.ui.data_editor`. |
| Sélectionner sur un graphique matplotlib | `ChartPuck` pour un point, `ChartMultiSelect` pour plusieurs classes | Des régions étiquetées, un point dans l'espace des données | Une région simple dans marimo demande `mo.ui.matplotlib`. `ChartSelect` sert à Jupyter. |
| Explorer beaucoup de données ou de dimensions | `PairPlot`, `ParallelCoordinates` | Plus d'un million de lignes en WebGL, des filtres Keep et Exclude, des axes à brosser | Deux variables et quelques milliers de points demandent `mo.ui.altair_chart`. |
| Faire suivre un curseur à un graphique altair | `AltairWidget` | Une mise à jour sans scintillement | Une sélection dans le graphique demande `mo.ui.altair_chart`. |
| Dessiner des données ou un croquis | `ScatterWidget`, `Paint`, `SplineDraw`, `GridDraw`, `Excalidraw` | Des jeux de données jouets, l'étiquetage, un schéma | `Excalidraw` exige le réseau. |
| Montrer un graphe | `GraphWidget` depuis Python, `EdgeDraw` à la main, `Neo4jWidget` | Des réseaux, des dépendances | |
| Comprendre un algorithme | `StateViewer`, `LiveEdit`, `AsyncFlow` | Le backtracking, les boucles, asyncio. `AsyncFlow` demande Python 3.12 ou plus. | |
| Suivre un calcul | `FitProgress`, `TraceView`, `ProgressBar` | Un GridSearchCV en direct avec scikit-learn 1.9 ou plus, des traces OpenTelemetry ou W&B Weave | Une boucle simple demande `mo.status.progress_bar`. |
| Montrer une hiérarchie | `Treemap`, `NestedTable`, `ModuleTreeWidget` | Les parts d'un tout, des lignes dépliables, l'architecture d'un modèle PyTorch | |
| Montrer des formes plutôt que des nombres | `shape_display` | L'algèbre linéaire, `X @ W` | |
| Garder un contrôle visible, guider la lecture | `FloatingPanel`, `Pip`, `CellTour`, `Hint`, `WidgetDAG`, `WidgetFlow` | Les longues pages, les visites, les flèches explicatives | Dans un iframe comme molab, `Pip` ne marche pas. Prends `FloatingPanel`. |
| Lire le clavier, une manette, la voix ou la webcam | `KeystrokeWidget`, `GamepadWidget`, `WebkitSpeechToTextWidget`, `WebcamCapture`, `AnnotationWidget` | L'annotation rapide de données | |
| Utiliser une bibliothèque JavaScript | `EsmWidget`, `ObservablePlot`, `ManimWeb` | Une bibliothèque chargée depuis un CDN | Sans réseau, écris un anywidget avec le skill `anywidget` de marimo. |

`references/catalogue.md` donne une ligne par classe.

## 2. Brancher dans marimo

```python
with app.setup:
    import marimo as mo
    from wigglystuff import Slider2D

@app.cell
def _():
    depart = mo.ui.anywidget(Slider2D(x=0.5, y=-0.5, x_bounds=(-2.0, 2.0), y_bounds=(-2.0, 2.0)))
    depart
    return (depart,)

@app.cell
def _(depart):
    mo.md(f"Départ en ({depart.x:.2f}, {depart.y:.2f})")
```

- Enveloppe chaque widget et lie-le à un nom public par `nom = mo.ui.anywidget(Widget(...))`.
  Crée et affiche le widget dans une cellule. Lis `nom.x` ou `nom.value["x"]` dans une autre. Sans
  enveloppe ni nom public, bouger le widget ne relance aucune cellule.
- Pour un calcul lourd, lis la valeur validée quand le widget en a une. Ce sont
  `committed_amount`, `committed_values` ou `params` pour `TangleDistribution`. La valeur en
  direct, `amount`, `values` ou `live_params`, change à chaque pixel.
- `FloatingPanel`, `Hint`, `WidgetDAG`, `WidgetFlow` et `shape_display` ne sont pas des AnyWidget.
  Ne les enveloppe pas. Mets-les en dernière expression de la cellule. Le widget qu'ils portent
  garde son propre nom.
- Pour glisser un widget dans une phrase, écris `mo.md(f"... {tangle} ...")` avec le widget déjà
  enveloppé.
- Épingle `wigglystuff==<version>` dans l'en-tête PEP 723, car l'API change entre les versions 0.5
  et 0.6. Vérifie ensuite le notebook par `mak verifier notebook.py`, qui exécute les cellules.

Le dépôt du kit contient un exemple complet et vérifié, `tests/exemples/widgets.py`.

## 3. La documentation sans réseau

Ne devine pas une signature. Un paramètre inventé fait planter la cellule à l'exécution. Par
exemple, `TangleDistribution(params=[0, 1])` plante, alors que
`TangleDistribution(params={"loc": 0, "scale": 1})` passe.

```
mak widgets
mak widgets TangleDistribution
mak widgets --chercher lasso
```

La première commande affiche le catalogue et compare la version installée à celle de la doc. La
deuxième affiche la page d'un widget, avec son usage, sa signature, ses traitlets et sa démo. La
troisième cherche un mot dans les noms et les résumés.

Sans `mak`, lis ces fichiers :

- `references/widgets/<page>.md` est la page du site pour la version 0.6.0. Elle contient la
  signature, la docstring et les traitlets lus dans le paquet.
- `references/demos/<nom>.py` est le notebook de démonstration. Le lien est en bas de la page.
- `references/SOURCE.md` donne la version, le commit, la licence et les rares écarts entre la doc
  et le paquet.

Dans le noyau, par marimo pair, `help(Widget)` et `Widget.class_traits(sync=True)` font foi pour
la version installée.

## 4. Avec marimo-lens

Le skill `marimo-lens` explique comment rendre une zone d'un widget sélectionnable. Un analyste
peut alors la montrer et demander une modification.
