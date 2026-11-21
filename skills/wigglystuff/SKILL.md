---
name: wigglystuff
description: Choisir et utiliser un widget wigglystuff (Slider2D, Tangle, TangleDistribution, ChartPuck, PairPlot, StateViewer, FitProgress, TraceView, Paint, FloatingPanel…) dans un notebook marimo, avec la documentation de la version 0.6.0 lisible hors ligne (pages, signatures, traitlets, démos). À utiliser quand une interaction dépasse mo.ui (deux paramètres d'un geste, nombre réglable dans une phrase, sélection sur un graphique matplotlib, dessin, trace d'algorithme, progression d'un entraînement), ou quand une tâche cite wigglystuff, anywidget ou un de ses widgets. Use for: wigglystuff widgets, anywidget in marimo, interactive explanations, choosing a widget.
---

# Widgets wigglystuff dans marimo

wigglystuff (Vincent Warmerdam, MIT) rassemble environ 70 widgets AnyWidget. Ils servent quand
l'interaction elle-même aide à comprendre : un geste qui règle deux paramètres, un nombre
qu'on tire dans une phrase, un algorithme qu'on rejoue ligne à ligne. Pour un réglage ordinaire,
`mo.ui` suffit et reste le premier choix.

## 1. Choisir

| Besoin | Widget | Idéal pour | Plutôt autre chose si… |
|---|---|---|---|
| Deux paramètres liés d'un geste | `Slider2D` | point de départ d'une optimisation, couple (μ, σ) | grille discrète → `HeatmapSelect` ; un seul → `mo.ui.slider` |
| Parcourir une grille précalculée | `HeatmapSelect` | résultats par (a, b), épingler une ligne ou une colonne | valeurs continues → `Slider2D` |
| Un nombre réglable dans le texte | `TangleSlider`, `TangleChoice`, `TangleSelect` | explications « à la Bret Victor » | formulaire de réglages → `mo.ui` + `.form()` |
| Une loi de probabilité | `TangleDistribution` | a priori bayésien (14 familles, `sample`, `cdf`…) sans scipy | — |
| Une formule qui se manipule | `TangleLatex`, `FormulaDAG`, `FormulaAnimation` | cours : paramètres, chaîne de calcul, dérivation pas à pas | formule fixe → `mo.md` avec `$$` |
| Appeler une fonction typée | `TangleFunction` | explorer une fonction annotée (bornes pydantic) | — |
| Animer un paramètre ou des images | `PlaySlider`, `FramePlayer` | parcourir le temps, une simulation | — |
| Saisir une matrice ou un ordre | `Matrix`, `SortableList` | poids, transformations ; priorités | tableau de données → `mo.ui.data_editor` |
| Sélectionner sur matplotlib | `ChartPuck` (un point), `ChartMultiSelect` (plusieurs classes) | régions étiquetées, un point dans l'espace des données | une région simple dans marimo → `mo.ui.matplotlib` ; `ChartSelect` est pour Jupyter |
| Beaucoup de données, beaucoup de dimensions | `PairPlot`, `ParallelCoordinates` | 1M+ lignes en WebGL, filtres Keep/Exclude ; brosser des axes | deux variables et quelques milliers de points → `mo.ui.altair_chart` |
| Un graphique altair qui suit un curseur | `AltairWidget` | mise à jour sans scintillement | sélection dans le graphique → `mo.ui.altair_chart` |
| Dessiner des données ou un croquis | `ScatterWidget`, `Paint`, `SplineDraw`, `GridDraw`, `Excalidraw` | jeux jouets, étiquetage, schéma | `Excalidraw` exige le réseau |
| Graphes | `GraphWidget` (depuis Python), `EdgeDraw` (à la main), `Neo4jWidget` | réseaux, dépendances | — |
| Comprendre un algorithme | `StateViewer`, `LiveEdit`, `AsyncFlow` | backtracking, boucles, asyncio (`AsyncFlow` : Python 3.12+) | — |
| Suivre un calcul | `FitProgress` (scikit-learn ≥ 1.9), `TraceView` (OpenTelemetry, W&B Weave), `ProgressBar` | GridSearchCV en direct, traces d'agent | boucle simple → `mo.status.progress_bar` |
| Hiérarchies | `Treemap`, `NestedTable`, `ModuleTreeWidget` (PyTorch) | parts d'un tout, lignes dépliables, architecture d'un modèle | — |
| Montrer des formes plutôt que des nombres | `shape_display` | algèbre linéaire, `X @ W` | — |
| Garder un contrôle visible, guider la lecture | `FloatingPanel`, `Pip`, `CellTour`, `Hint`, `WidgetDAG`, `WidgetFlow` | longues pages, visites, flèches explicatives | dans un iframe (molab) : `FloatingPanel`, pas `Pip` |
| Clavier, manette, voix, webcam | `KeystrokeWidget`, `GamepadWidget`, `WebkitSpeechToTextWidget`, `WebcamCapture`, `AnnotationWidget` | annotation rapide de données | — |
| Rien ne convient | `EsmWidget`, `ObservablePlot`, `ManimWeb` | une bibliothèque JS d'un CDN | sans réseau : écrire un anywidget (skill `anywidget` de marimo) |

Le catalogue complet (une ligne par classe) : `references/catalogue.md`.

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

- **Envelopper et lier** : `nom = mo.ui.anywidget(Widget(...))`, nom public, une cellule pour le
  créer et l'afficher, une autre pour lire `nom.x` ou `nom.value["x"]`. Sans enveloppe ni nom
  public, bouger le widget ne relance rien.
- **Calcul lourd** : lire la valeur « validée » quand elle existe (`committed_amount`,
  `committed_values`, `params` de `TangleDistribution`) plutôt que la valeur en direct
  (`amount`, `values`, `live_params`), qui change à chaque pixel.
- **Aides d'affichage** : `FloatingPanel`, `Hint`, `WidgetDAG`, `WidgetFlow` et `shape_display`
  ne sont pas des AnyWidget. Pas d'enveloppe : ils sont la dernière expression de la cellule, et
  le widget qu'ils portent garde son propre nom.
- **Un widget dans une phrase** : `mo.md(f"… {tangle} …")` avec le widget déjà enveloppé.
- **Version** : épingler `wigglystuff==<version>` dans l'en-tête PEP 723 ; l'API bouge entre les
  versions (0.5 → 0.6). Vérifier ensuite par `mak verifier notebook.py`, qui exécute les cellules.

Exemple complet et vérifié : `tests/exemples/widgets.py` du dépôt du kit.

## 3. La documentation, sans réseau

Ne devine pas une signature : un paramètre inventé fait planter la cellule à l'exécution
(`TangleDistribution(params=[0, 1])` au lieu de `params={"loc": 0, "scale": 1}`).

```
mak widgets                    # le catalogue, et la version installée comparée à celle de la doc
mak widgets TangleDistribution # la page : usage, signature, traitlets, démo
mak widgets --chercher lasso   # chercher dans les noms et les résumés
```

Sans `mak`, lire directement :

- `references/widgets/<page>.md` : la page du site (version 0.6.0), avec la signature, la
  docstring et les traitlets lus dans le paquet ;
- `references/demos/<nom>.py` : le notebook de démonstration (le lien est en bas de la page) ;
- `references/SOURCE.md` : version, commit, licence, et les rares écarts doc/paquet ;
- dans le noyau (marimo pair) : `help(Widget)` et `Widget.class_traits(sync=True)`, qui font foi
  pour la version installée.

## 4. Avec marimo-lens

Pour qu'un analyste puisse montrer une zone d'un widget et demander une modification, le
skill `marimo-lens` explique comment rendre un widget sélectionnable.
