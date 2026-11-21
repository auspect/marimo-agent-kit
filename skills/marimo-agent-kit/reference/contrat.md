# Contrat d'écriture marimo (marimo-agent-kit)

## Justesse
1. Un nom public n'a qu'une cellule propriétaire. Pour l'étape suivante, un nouveau nom (`ventes_2024 = ventes.filter(...)`), jamais une réaffectation, jamais un `_` pour contourner : `_nom` n'existe que dans sa cellule.
2. Ne modifie jamais en place un objet d'une autre cellule (`df["c"] = ...`, `.append`, `inplace=True`) : marimo ne relance pas ceux qui le lisent.
3. Un élément `mo.ui.*` est affecté à un nom public ; sa `.value` se lit dans une autre cellule. Plusieurs éléments : `mo.ui.array`, `mo.ui.dictionary`.
4. Seule la dernière expression s'affiche ; plusieurs sorties : `mo.vstack([...])`.
5. Toute valeur calculée citée dans un texte est interpolée : `mo.md(f"... {valeur:.2f} ...")`.
6. Calcul lancé par un bouton : `mo.ui.run_button(label=...)`, puis `mo.stop(not bouton.value, mo.md("..."))` en tête de la cellule de calcul, jamais `if bouton.value:`.
7. `await` directement dans la cellule, jamais `asyncio.run`. Ni `display()`, ni `!pip`, ni `%magic` : ce n'est pas Jupyter.

## Lisibilité
8. Une cellule, une idée : le calcul coûteux en amont, la présentation en aval ; les imports regroupés en tête.
9. Une courte cellule Markdown annonce chaque étape (ce qu'on va voir, pourquoi) ; une conclusion cite des valeurs interpolées.
10. Chaque contrôle a un `label` ; les contrôles d'un même réglage sont groupés, au-dessus de ce qu'ils pilotent.
11. Un calcul lourd lié à un curseur passe par `.form()`, un `run_button` ou `@mo.cache`.
12. Une figure est la dernière expression (`fig`, `plt.gca()`, graphique altair), avec un titre et des axes nommés.

## Vérification
13. Avant d'écrire un appel marimo dont tu n'es pas sûr, lis sa signature (outil `api_marimo`, ou `mak api mo.ui.slider`) : n'invente pas de paramètre.
14. Après chaque modification, vérifie (outil `verifier_notebook`, ou `mak verifier notebook.py`) et corrige toutes les erreurs ; dis ce qui n'a pas pu être vérifié.
