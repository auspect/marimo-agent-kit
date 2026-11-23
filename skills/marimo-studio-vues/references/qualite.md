# Ce qui distingue une restitution d'un notebook amélioré

Chaque critère se contrôle. `scripts/controler_vues.py notebook.py` en relit les sources ; les
autres demandent une construction, une capture ou un export.

| # | Critère | Comment le contrôler |
|---|---|---|
| 1 | Chaque vue a un public et une tâche écrits | `DESIGN.md` présent et rempli ; `AGENTS.md` sans le texte « Keep this section current » du gabarit (`controler_vues.py`) |
| 2 | Les vues ont des formats différents, choisis pour leur public | `controler_vues.py` liste les fournisseurs ; un seul format pour plusieurs vues est signalé |
| 3 | Plus rien du starter | Ni cible `cell-N`, ni texte du gabarit (`controler_vues.py`, erreur) ; ni la liste de toutes les cellules du starter |
| 4 | Le titre est une réponse, pas un intitulé | Lis le titre : « Il pleut un jour sur 2,9 à Seattle », pas « Analyse de la pluie » |
| 5 | Aucun chiffre ni constat écrit dans la vue | `controler_vues.py` signale chaque nombre suivi d'une unité, d'un `%` ou chaque année écrite dans la vue ; chacun doit venir du notebook ou être un fait externe assumé |
| 6 | Un même chiffre s'écrit pareil partout | Compare les captures des vues : même arrondi, même format |
| 7 | La vue a son propre système visuel | Couleurs, polices et mise en page décrites dans `DESIGN.md`, visibles sur la capture ; pas la page grise du starter |
| 8 | Les graphiques sont faits pour la vue | Graphiques de la vue (SVG, CSS, ou une bibliothèque), ou sorties du notebook à la bonne largeur ; pas un tableau brut à la place d'un graphique |
| 9 | Lisible à 1280 et à 390 pixels | `capturer.py --largeur 1280` et `--largeur 390`, puis lire les images : texte lisible, contrôles utilisables, pas de débordement de page |
| 10 | Changer un contrôle met tout à jour | `capturer.py --choisir 2014 --attendre-texte "En 2014"` : le texte attendu apparaît |
| 11 | États de chargement et d'erreur | La vue affiche un message pendant `aria-busy="true"` et un `role="alert"` en cas d'erreur de valeur |
| 12 | Traçable | Les régions dessinées portent `data-marimo-lens-inputs`, un libellé et une source de rendu ; les PDF Typst, des `marimo_region()` |
| 13 | Construite, validée, sans erreur | `view build` réussi, `validate --level static` en `PASS`, `etat_studio` à `ready` et `erreurs_console` vide dans le rapport de `capturer.py` |
| 14 | Chaque export ouvert et regardé | Site servi en HTTP et capturé avec un contrôle changé ; PDF et PPTX ouverts, page par page ; page autonome ouverte en `file://` avec `capturer.py --hors-ligne`, `requetes_bloquees` vide |
| 15 | Hiérarchie au premier écran | À 1280 × 800, sans défiler : le titre-réponse, le périmètre actif (période, seuil, zone) et l'objet principal ; pour un tableau de bord, aussi les cartes d'indicateurs |
| 16 | Chiffres alignés | `font-variant-numeric: tabular-nums` sur les indicateurs, tableaux et légendes ; unité et période écrites à côté de chaque chiffre |

Un tableau de bord, en plus des seize critères :

| # | Critère | Comment le contrôler |
|---|---|---|
| T1 | Trois ou quatre cartes d'indicateurs, chacune avec son écart à une référence venu du notebook | Lis la capture ; `controler_vues.py` ne signale aucun chiffre écrit dans la vue |
| T2 | Un classement qui se trie par colonne et dont une ligne se sélectionne au clavier | Capture après un clic sur un en-tête puis sur une ligne : l'ordre et le panneau de détail changent |
| T3 | Un filtre de page, nommé comme tel, avec un état vide | Capture filtre actif ; le seuil du filtre vient du notebook |
| T4 | La sélection se compare à une moyenne du périmètre, à la même échelle | La courbe de l'élément choisi et celle de la moyenne sont sur le même graphique |

`references/react.md` donne les quatre patrons. Une page grand public ou un diaporama n'en a
pas besoin : un tri ou une sélection sans tâche de lecteur derrière ne fait qu'ajouter du bruit.

Un critère non vérifié se dit comme tel dans le compte rendu, avec la raison.
