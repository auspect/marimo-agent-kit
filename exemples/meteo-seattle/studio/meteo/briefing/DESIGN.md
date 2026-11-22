# Point climat, diaporama reveal.js

## Public et tâche

Une équipe en réunion décide d'un calendrier d'activités en plein air. Elle a
dix minutes : la réponse d'abord, puis la saison, l'intensité, les années, une
démonstration des réglages et la méthode.

## Une diapositive, un constat

Le titre de chaque diapositive est un message du notebook
(`donnees_vues.messages`), jamais une phrase écrite dans la vue. Le surtitre
nomme le thème. Le pied rappelle la période et le seuil courants.

## Système visuel

- Canevas 1440 × 810, mis à l'échelle par Reveal, transition en fondu.
- Couverture nuit `#142130` avec le calendrier des quatre années, puis papier
  `#f6f4ef`.
- Mêmes bleus et même terre cuite que la page grand public : les graphiques
  sont la même copie de `src/components/`.
- Fraunces pour les titres et les grands chiffres, Inter pour le reste.

## Interaction

Flèches et barre de progression de Reveal. La diapositive « À vous de régler »
projette `controles` avec `zoom: 1.6`. Changer un contrôle met à jour tout le
diaporama. Sur un écran étroit tenu droit, les mêmes diapositives se lisent à la
suite, sans Reveal (`.lecteur`), comme dans l'exemple officiel Earthquake watch.

## Contraintes vérifiées

Chaque diapositive capturée à 1440 × 810. Le PDF de partage se fait par
captures successives (`capturer.py --diapos 7 --pdf`) : l'impression
`?print-pdf` de Reveal laisse blanches les diapositives au-delà de la première
dans Studio 0.4.1.
