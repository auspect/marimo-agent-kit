---
name: marimo-lens
description: Savoir quand marimo-lens aide (un analyste montre une barre, une ligne ou une zone d'un résultat et demande une explication ou une modification ; visite guidée d'un notebook) et le mettre en place, avec sa documentation 0.2.4 lisible hors ligne. Renvoie au mode d'emploi livré dans le paquet pour le travail lui-même. À utiliser quand une tâche cite Lens, une sélection, « ce point-là », « cette barre », une visite guidée (Trail), ou demande de rendre une sortie ou un widget sélectionnable. Use for: marimo lens, visual selection, point at output, guided tour, selectable widgets.
---

# marimo-lens : montrer du doigt un résultat

Lens ajoute au notebook une barre (le « dock ») avec laquelle on marque un point ou une zone
d'une sortie et on écrit une note. L'agent reçoit la sélection, une image de la zone marquée,
la cellule qui a produit la sortie, ses cellules amont et la valeur des contrôles. Il corrige,
vérifie, puis remet le résultat sous les yeux de l'analyste.

## Quand

| Situation | Lens ? | Pourquoi |
|---|---|---|
| « Ce pic, d'où vient-il ? », « cette ligne est fausse » | Oui | Un doigt sur la sortie vaut mieux qu'une description ; Lens remonte à la cellule qui l'a produite |
| Expliquer un notebook à un collègue, étape par étape | Oui | Une visite (« Trail ») révèle les cellules clés avec un message chacune |
| Revue d'un graphique ou d'un tableau de bord | Oui | Plusieurs sélections, traitées puis résolues avec un résumé |
| La demande se dit bien en mots (« renomme la colonne ») | Non | Le chat suffit |
| Aucun agent dans le noyau, ou une page exportée | Non | Lens n'agit pas seul : il faut marimo pair ou le Code Mode de l'assistant |

## Mettre en place

- Prérequis : Python 3.10 à 3.14, marimo 0.25.2 ou plus, et un agent qui exécute du Python
  dans le noyau : marimo pair (Claude Code, Codex, OpenCode…) ou le Code Mode de l'assistant
  intégré. Avec un LLM interne, le Code Mode demande l'appel d'outils : `mak sonde-llm` le dit.
- Installation : `"marimo-lens==0.2.4"` dans l'en-tête PEP 723 (ou `uv add marimo-lens`).
  marimo monte le dock tout seul dès qu'une cellule qui importe marimo a tourné ; sinon, l'agent
  l'ajoute avec `marimo_lens.agent.add_lens_cell(ctx)` (voir le mode d'emploi).

## Le mode d'emploi est dans le paquet

Le paquet livre les instructions pour agents de sa version. Lis-les avant d'agir, ne les
devine pas :

```
uvx --with marimo-lens==0.2.4 agent-plugins read marimo-lens
```

Dans le noyau : `marimo_lens.agent.skill().body`, et
`marimo_lens.agent.skill().file("references/targets.md").read_text(encoding="utf-8")` pour
une référence. Elles couvrent trois gestes : ajouter Lens, faire une visite, traiter une sélection.

## Ce que ce skill ajoute

- **Ce qui part chez le modèle** : l'image de la zone marquée, le code des cellules, la valeur
  des contrôles. Avec un fournisseur extérieur, ne sélectionne pas de données confidentielles.
  Lens garde sélections et images en mémoire du noyau ; résoudre une sélection libère son image
  (`references/docs/data-and-trust.md`).
- **Rendre une sortie maison sélectionnable** : les sorties de marimo (tableaux, graphiques
  altair…) le sont déjà. Pour du HTML ou un anywidget écrit par toi, pose sur les zones qui ont
  un sens `data-marimo-lens-target`, `data-marimo-lens-label` (ce que c'est) et
  `data-marimo-lens-detail` (unités, regroupement, filtre) ; la liste complète est dans
  `references/docs/reference/attributes.md` et `custom-targets.md`.
- **Boucle de vérification** : après une modification demandée par une sélection, vérifie le
  notebook (`mak verifier notebook.py --sans-execution`, le noyau a déjà exécuté), puis suis le
  mode d'emploi pour révéler et résoudre avec un résumé.

## Documentation hors ligne

`references/docs/` contient les 19 pages de la documentation de marimo-lens 0.2.4 (Apache-2.0),
sans les images : `overview.md` et `how-lens-works.md` pour comprendre, `getting-started.md`
pour démarrer, `selections.md`, `custom-targets.md`, `reference/` pour les détails,
`troubleshooting.md` quand le dock n'apparaît pas. Version et commit : `references/SOURCE.md`.
La documentation en ligne suit la branche principale, qui décrit déjà des fonctions absentes
de 0.2.4 (par exemple `Lens(record=True)`).
