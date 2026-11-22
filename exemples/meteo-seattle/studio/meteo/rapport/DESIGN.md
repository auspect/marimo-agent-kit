# Note technique, PDF Typst

## Public et tâche

Un lecteur technique archive la note ou en vérifie les chiffres. Il lit le
résumé, puis va aux tableaux. Tout ce qui est affirmé doit se retrouver dans un
tableau de la note.

## Structure

Bandeau, titre, résumé fait des messages du notebook, quatre chiffres clés,
puis cinq sections numérotées : données et méthode, saisonnalité, intensité,
variabilité annuelle, limites. Deux pages A4.

## Typographie

Libertinus Serif 10,5 pt, justifié. Titres de section en gras 13 pt. Tableaux
à filets horizontaux seulement. Le mois le plus humide et le plus sec sont en
bleu `#2b5f9f`. Légendes en gris `#6b7680`.

## Figures

`figure_saison` et `figure_pluie` sont les graphiques Altair du notebook à
largeur fixe. Studio les redessine en PDF vectoriel à la largeur où ils sont
placés.

## Traçabilité

Les chiffres clés et les cellules des tableaux sont enveloppés dans
`marimo_region()` pour qu'une sélection Lens remonte à la cellule du notebook.
