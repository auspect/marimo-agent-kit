---
name: marimo-lens
description: >-
  Savoir quand marimo-lens aide et le mettre en place, avec sa documentation 0.2.4 sans réseau.
  Lens sert quand un analyste montre une barre, une ligne ou une zone d'un résultat et demande une
  explication ou une modification, et pour une visite guidée d'un notebook. Pour le travail
  lui-même, le skill renvoie au mode d'emploi livré dans le paquet. À utiliser quand une tâche
  cite Lens, une sélection, "ce point-là", "cette barre" ou une visite guidée appelée Trail, ou
  demande de rendre une sortie ou un widget sélectionnable. Use for: marimo lens, visual
  selection, point at output, guided tour, selectable widgets.
---

# marimo-lens, pour montrer du doigt un résultat

Lens ajoute au notebook une barre appelée le dock. L'analyste y marque un point ou une zone d'une
sortie et écrit une note. L'agent reçoit cinq choses : la sélection, une image de la zone
marquée, la cellule qui a produit la sortie, ses cellules amont et la valeur des contrôles. Il
corrige, vérifie, puis remet le résultat sous les yeux de l'analyste.

## Quand utiliser Lens

| Situation | Lens | Raison |
|---|---|---|
| "Ce pic, d'où vient-il ?", "Cette ligne est fausse." | Oui | Montrer la sortie est plus précis que la décrire. Lens remonte à la cellule qui l'a produite. |
| Expliquer un notebook à un collègue, étape par étape | Oui | Une visite, appelée Trail, révèle les cellules clés avec un message chacune. |
| Relire un graphique ou un tableau de bord | Oui | L'analyste pose plusieurs sélections. L'agent les traite, puis les résout avec un résumé. |
| La demande se dit bien en mots, par exemple "renomme la colonne" | Non | Le chat suffit. |
| Aucun agent ne tourne dans le noyau, ou la page est exportée | Non | Lens n'agit pas seul. Il lui faut marimo pair ou le Code Mode de l'assistant. |

## Mettre Lens en place

- Lens demande Python 3.10 à 3.14 et marimo 0.25.2 ou plus. Il lui faut aussi un agent qui
  exécute du Python dans le noyau. marimo pair convient, avec Claude Code, Codex ou OpenCode. Le
  Code Mode de l'assistant intégré convient aussi. Avec un LLM interne, le Code Mode demande
  l'appel d'outils, que `mak sonde-llm` teste.
- Ajoute `"marimo-lens==0.2.4"` à l'en-tête PEP 723, ou lance `uv add marimo-lens`. marimo monte
  le dock dès qu'une cellule qui importe marimo a tourné. Sinon, l'agent l'ajoute avec
  `marimo_lens.agent.add_lens_cell(ctx)`, comme le décrit le mode d'emploi.

## Lire le mode d'emploi livré dans le paquet

Le paquet livre les instructions pour agents de sa version. Lis-les avant d'agir, depuis
l'environnement du notebook, où marimo-lens est déjà installé : `marimo_lens.agent.skill().body`
dans le noyau, ou cette commande.

```
python -c "import marimo_lens.agent as a; print(a.skill().body)"
```

Si marimo-lens n'est pas installé, ajoute-le par uv, selon `mak contexte`. Ne le télécharge pas
autrement. Pour une référence, lis par
exemple `marimo_lens.agent.skill().file("references/targets.md").read_text(encoding="utf-8")`.
Ces instructions couvrent trois tâches : ajouter Lens, faire une visite, traiter une sélection.

## Ce que ce skill ajoute

- La sélection part chez le fournisseur du modèle. Elle contient l'image de la zone marquée, le
  code des cellules et la valeur des contrôles. Avec un fournisseur extérieur, ne sélectionne pas
  de données confidentielles. Lens garde les sélections et les images dans la mémoire du noyau,
  et résoudre une sélection libère son image. `references/docs/data-and-trust.md` donne le détail.
- Les sorties de marimo, comme les tableaux et les graphiques altair, sont déjà sélectionnables.
  Pour du HTML ou un anywidget que tu écris, pose ces attributs sur les zones qui ont un sens.
  `data-marimo-lens-target` marque la zone. `data-marimo-lens-label` dit ce qu'elle montre.
  `data-marimo-lens-detail` donne les unités, le regroupement ou le filtre.
  `references/docs/reference/attributes.md` et `references/docs/custom-targets.md` donnent la
  liste complète.
- Après une modification demandée par une sélection, vérifie le notebook par
  `mak verifier notebook.py --sans-execution`, car le noyau a déjà exécuté les cellules. Suis
  ensuite le mode d'emploi pour révéler le résultat et résoudre la sélection avec un résumé.

## Documentation sans réseau

`references/docs/` contient les 19 pages de la documentation de marimo-lens 0.2.4, sous licence
Apache-2.0 et sans les images. Ces pages servent à ces besoins :

- `overview.md` et `how-lens-works.md` expliquent le fonctionnement ;
- `getting-started.md` décrit le démarrage ;
- `selections.md`, `custom-targets.md` et le dossier `reference/` donnent les détails ;
- `troubleshooting.md` aide quand le dock n'apparaît pas.

`references/SOURCE.md` donne la version et le commit. La documentation en ligne suit la branche
principale, qui décrit des fonctions absentes de la version 0.2.4, comme `Lens(record=True)`.
