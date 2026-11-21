# Contrat d'écriture marimo de marimo-agent-kit

## Justesse
1. Un nom public n'a qu'une cellule propriétaire. Pour l'étape suivante, crée un nouveau nom, par exemple `ventes_2024 = ventes.filter(...)`. Ne réaffecte jamais un nom. N'utilise jamais un `_` pour contourner la règle, car `_nom` n'existe que dans sa cellule.
2. Ne modifie jamais en place un objet d'une autre cellule, que ce soit par `df["c"] = ...`, `.append` ou `inplace=True`. marimo ne relance pas les cellules qui lisent cet objet.
3. Affecte chaque élément `mo.ui.*` à un nom public, et lis sa `.value` dans une autre cellule. Pour plusieurs éléments, utilise `mo.ui.array` ou `mo.ui.dictionary`.
4. Seule la dernière expression s'affiche. Pour plusieurs sorties, utilise `mo.vstack([...])`.
5. Interpole chaque valeur calculée qu'un texte cite, par exemple `mo.md(f"... {valeur:.2f} ...")`.
6. Pour un calcul lancé par un bouton, crée `mo.ui.run_button(label=...)`, puis écris `mo.stop(not bouton.value, mo.md("..."))` en tête de la cellule de calcul. N'écris jamais `if bouton.value:`.
7. Écris `await` directement dans la cellule, jamais `asyncio.run`. N'utilise ni `display()`, ni `!pip`, ni `%magic`, qui viennent de Jupyter.

## Lisibilité
8. Une cellule porte une idée. Place le calcul coûteux en amont et la présentation en aval. Mets les imports dans la cellule setup, que marimo exécute avant toutes les autres. Dans le fichier, elle s'écrit `with app.setup:`, juste après `app = marimo.App()`. N'y mets que des imports : si elle définit aussi des valeurs, la modifier relance tout le notebook.
9. Une courte cellule Markdown annonce chaque étape et dit pourquoi elle compte. Une conclusion cite des valeurs interpolées.
10. Chaque contrôle a un `label`. Groupe les contrôles d'un même réglage au-dessus de ce qu'ils pilotent.
11. Un calcul lourd lié à un curseur passe par `.form()`, par un `run_button` ou par `@mo.cache`.
12. Termine une cellule de figure par la figure, par exemple `fig`, `plt.gca()` ou un graphique altair. Donne-lui un titre et des axes nommés.

## Vérification
13. Avant d'écrire un appel marimo dont tu n'es pas sûr, lis sa signature par l'outil `api_marimo` ou par `mak api mo.ui.slider`. N'invente pas de paramètre.
14. Après chaque modification, vérifie le notebook par l'outil `verifier_notebook` ou par `mak verifier notebook.py`. Corrige toutes les erreurs. Dis ce qui n'a pas pu être vérifié.
