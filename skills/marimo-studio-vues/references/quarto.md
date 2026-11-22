# Recette : un article Quarto

Modèle : `exemples/meteo-seattle/studio/meteo/article/` dans le dépôt, et le bulletin officiel
`exemples/studio/earthquakes/bulletin/index.qmd` de ce dossier, avec citations, encadrés et
graphiques en JavaScript.

Studio rend `index.qmd` par `quarto render --no-execute` : aucun bloc `{python}` ne s'exécute.
Le calcul reste dans le notebook, l'article place ses résultats.

## Placer les résultats

| Shortcode | Rend | Où l'écrire |
|---|---|---|
| `{{< marimo value="donnees_vues.messages.saison" >}}` | Une valeur JSON dans le texte | Dans une phrase |
| `{{< marimo output="graphique_saison" >}}` | La sortie d'une variable, par exemple un graphique | Seul sur sa ligne, entre deux lignes vides |
| `{{< marimo cell="controles" >}}` | Une cellule complète, contrôles compris | Seul sur sa ligne, entre deux lignes vides |

Un shortcode dans l'en-tête YAML, dans du code ou dans un autre shortcode n'est pas relié. Le
titre, le sous-titre et le résumé de l'en-tête ne peuvent donc pas citer un résultat : écris-les
neutres, et laisse les constats aux shortcodes du corps.

## Mise en forme

```yaml
lang: fr
format:
  html:
    theme: [cosmo, article.scss]
    toc: true
    toc-title: "Dans cet article"
    toc-location: left
    reference-location: margin
    page-layout: article
    include-in-header:
      text: |
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Inter:wght@400;500;600&display=swap">
```

- Le thème SCSS (`/*-- scss:defaults --*/`, `/*-- scss:rules --*/`) porte les couleurs, les
  polices et le style des valeurs insérées : `[mo-value] { font-weight: 600; }`.
- Les encadrés (`::: {.callout-note appearance="simple"}`), les notes en marge
  (`::: {.column-margin}`) et les notes de bas de page (`^[...]`) donnent la texture d'un article.
- L'encadré du haut projette les contrôles : le lecteur règle l'article, et le texte suit.
- Studio enveloppe le corps dans `#app-shell` : n'utilise pas cet identifiant.

## Graphiques responsifs

Un graphique Altair avec `width="container"` prend la largeur de la colonne, sur téléphone
compris. Un graphique à largeur fixe est rogné à 390 pixels : l'exemple l'a constaté puis corrigé.

## Quarto dans l'environnement

Quarto de conda-forge (1.11.9 ici) marche par `pixi run`, qui active l'environnement. Sous
Windows, la construction échoue sur `unable to open database file` quand le chemin de l'état de
construction est trop long : voir `references/environnement.md`. Ajoute à la vue un `.gitignore`
pour `.quarto/`, `*_files/` et `index.html` si tu lances Quarto toi-même dans ce dossier.
