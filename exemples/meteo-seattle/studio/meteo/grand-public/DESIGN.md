# Seattle sous la pluie, page grand public

## Public et tâche

Un lecteur curieux, sans formation en climatologie, arrive par un lien. Il
veut savoir en une minute si la réputation de Seattle est méritée, puis
explorer une année ou un autre seuil s'il en a envie.

## Ce que la page affirme

Le titre et chaque paragraphe viennent de `donnees_vues.messages`, rédigés par
le notebook. La page n'écrit aucun chiffre de l'analyse. Elle met en forme les
nombres en français et choisit les couleurs.

Ordre : la réponse (titre et quatre chiffres), le calendrier des jours, la
saison, l'intensité, la comparaison des années, la source.

## Système visuel

- Papier `#f6f4ef`, encre `#17202a`, filets `#dcd8cf`.
- Une échelle de bleus pour la hauteur de pluie, du plus clair (moins de 1 mm)
  au plus foncé (20 mm et plus). Les jours secs sont beige.
- Le volume tombé est en terre cuite `#c8553d`, la seule couleur chaude, pour
  opposer « nombre de jours » et « volume ».
- Fraunces pour les titres et les chiffres clés, Inter pour le texte, avec des
  polices de repli système si Google Fonts ne répond pas.

## Interaction

Les deux contrôles du notebook (`controles`) restent collés en haut de page.
Changer l'année ou le seuil met à jour le titre, les chiffres et tous les
graphiques. Aucun filtre ne vit seulement dans le navigateur.

## Contraintes vérifiées

- 1280 px et 390 px de large, sans débordement de page. Le calendrier défile
  horizontalement sous 52rem, les étiquettes des mois restent lisibles.
- Chaque graphique porte `data-marimo-lens-inputs="donnees"`, un libellé et sa
  source de rendu.
