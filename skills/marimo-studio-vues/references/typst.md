# Recette : un rapport PDF Typst

Modèle : `exemples/meteo-seattle/studio/meteo/rapport/main.typ` dans le dépôt, et l'exemple
officiel `exemples/studio/quadratic_program/report/main.typ` de ce dossier.

Studio compile `main.typ` avec le compilateur Typst de l'extra `marimo-studio[typst]`, à chaque
changement d'une valeur lue. La page de la vue montre le PDF avec un lien de téléchargement.
`references/docs/reference/built-in-providers.md` décrit les fonctions en détail.

## Lire les valeurs

```typst
#import "marimo.typ": marimo_output, marimo_region, marimo_value

#let synthese = marimo_value("donnees_vues.synthese", default: none)
#let messages = marimo_value("donnees_vues.messages", default: none)
#let mois = marimo_value("donnees_vues.mois", default: ())
#let pret = synthese != none and messages != none
```

- Chaque sélecteur est une chaîne littérale : Studio ne fournit que les valeurs qu'il voit lues.
- Chaque lecture a un `default`. Le document doit compiler sans valeurs : Studio le vérifie à la
  construction, et `typst compile main.typ` hors Studio le compose avec les défauts.
- Un DataFrame arrive comme une liste de lignes, une date comme un texte ISO 8601.
- Enveloppe le corps dans `#if not pret { ... } else [ ... ]` avec un message d'attente lisible.

## Mise en forme française

Typst n'a pas de format de nombre localisé. L'exemple définit deux fonctions et n'écrit aucun
nombre à la main :

```typst
#let fr(x, chiffres: 0) = {
  let texte = str(calc.round(float(x), digits: chiffres))
  if chiffres > 0 and not texte.contains(".") { texte += "." + "0" * chiffres }
  texte.replace(".", ",")
}
#let pct(part) = fr(100 * part) + sym.space.nobreak + "%"
```

Avec `#set text(lang: "fr")`, les renvois s'écrivent « Tableau 1 », « Fig. 1 » : accorde le
texte autour (« le @tab-mois », « la @fig-saison »).

## Figures

```typst
#figure(
  marimo_output("figure_saison", width: 100%),
  caption: [Part des jours de pluie par mois, seuil #synthese.seuil.],
) <fig-saison>
```

Studio redessine un graphique Altair en PDF vectoriel à la largeur où il est placé. Il lui faut
`vl-convert-python` dans l'environnement du notebook. Donne-lui un graphique à largeur fixe : un
graphique `width="container"`, fait pour une page web, est sorti avec un texte énorme. L'exemple
garde donc deux versions dans le notebook, `graphique_saison` pour l'écran et `figure_saison`
pour le papier.

## Tableaux et traçabilité

Les tableaux se construisent depuis les lignes lues, avec des filets horizontaux seulement. Les
chiffres clés et les cellules qui portent un résultat sont enveloppés dans `marimo_region()` :
une sélection Lens dans le PDF remonte ainsi à la cellule du notebook.

```typst
marimo_region("donnees_vues.mois[" + str(rang) + "].part_pluie", pct(m.part_pluie))
```

## Polices et reproductibilité

Studio compose avec les polices embarquées de Typst (Libertinus Serif, New Computer Modern,
DejaVu Sans Mono) et celles du dossier `fonts/` de la vue, avec une horloge fixée au 1er janvier
1970 : passe les dates par le notebook.

## Compiler hors Studio

```bash
pixi run typst compile main.typ rapport-sans-valeurs.pdf
```

Avec le Typst de conda-forge, depuis le dossier de la vue. Le PDF ne contient que les valeurs par
défaut : il sert à vérifier la mise en page d'attente, pas à livrer. Le PDF à livrer vient de
l'export (`references/exports.md`).
