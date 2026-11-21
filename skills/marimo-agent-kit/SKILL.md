---
name: marimo-agent-kit
description: Écrire, modifier ou relire un notebook marimo sans les erreurs habituelles des agents, et le rendre lisible pour un humain. Choisit entre le noyau vivant (marimo pair) et le fichier, applique un contrat d'écriture, vérifie chaque changement par `mak verifier` (marimo check --strict, règles d'agent, exécution de chaque cellule) et lit l'API installée par `mak api` au lieu de la deviner. À utiliser dès qu'une tâche touche un fichier marimo (`@app.cell`, `marimo.App`, `mo.ui`, `mo.md`), un notebook ouvert dans marimo, ou l'assistant intégré de marimo. Use for: marimo notebook, reactive cells, mo.ui, marimo pair, marimo check.
---

# Écrire des notebooks marimo justes et lisibles

marimo n'est pas Jupyter : chaque cellule est un nœud d'un graphe de noms, un nom n'a qu'une
cellule propriétaire, seule la dernière expression s'affiche, et une mutation ne relance rien.
Les erreurs d'un agent viennent presque toutes de là, et `marimo check` n'en voit qu'une
petite partie. Ce skill ajoute ce qui manque : un contrat, des contrôles, l'API réelle.

`mak` est la commande du paquet `marimo-agent-kit`. Sans installation :
`uvx --from <source du kit> mak …` (la source est dans le README du kit).

## 1. Choisir où écrire

| Situation | Où écrire | Ce qui vérifie |
|---|---|---|
| Le notebook est ouvert dans marimo (un serveur répond) | Dans le noyau, par **marimo pair** : jamais dans le fichier | `cm` refuse un lot invalide ; puis `mak verifier --sans-execution` |
| Aucun serveur, ou l'utilisateur veut un fichier | Le fichier `.py`, au format marimo | `mak verifier notebook.py` |
| L'utilisateur parle dans le chat de marimo | Rien à écrire ici : `mak installer --marimo` lui donne le contrat et les outils | Les outils MCP du kit |

Pour savoir si un notebook est ouvert : `marimo pair notebook list` (marimo ≥ 0.22.5 ; les
serveurs lancés avec `--no-token` y apparaissent). Le mode d'emploi de pair est dans
`marimo pair --help` et `marimo pair docs gotchas` : lis-les une fois par session, ils
suivent la version installée. Le détail du travail dans le noyau : `reference/pair.md`.

## 2. Écrire selon le contrat

Lis `reference/contrat.md` avant la première cellule (quatorze règles, une minute). Les cinq
pièges qui reviennent le plus :

1. **Un nom, une cellule.** Pour l'étape suivante, un nouveau nom (`propre = df.dropna()`) ;
   jamais `df = …` dans une autre cellule, jamais `_df` pour contourner (privé à sa cellule).
2. **Pas de mutation entre cellules** : `df["c"] = …`, `.append`, `inplace=True` sur un objet
   d'une autre cellule ne relancent pas ses lecteurs.
3. **Un élément d'interface est lié à un nom public** et sa `.value` se lit dans une *autre*
   cellule. Liste d'éléments : `mo.ui.array`, pas une liste Python.
4. **Seule la dernière expression s'affiche** : `mo.vstack([...])` pour plusieurs sorties ;
   `mo.md(f"…{valeur}…")` avec le `f`, pour que le texte suive le calcul.
5. **Un bouton de calcul** : `mo.ui.run_button` puis `mo.stop(not bouton.value, mo.md("…"))`,
   jamais `if bouton.value:` (les noms définis dessous manquent aux autres cellules).

Pour un humain qui lira le notebook : une courte cellule Markdown avant chaque étape, les
contrôles avec un `label` au-dessus de ce qu'ils pilotent, le calcul coûteux en amont de la
présentation, une figure en dernière expression avec titre et axes.

## 3. Lire l'API installée, pas celle de mémoire

```
mak api mo.ui.table          # signature, documentation, membres
mak api --chercher cache     # quels noms existent (mo.cache, mo.persistent_cache…)
```

Les listes d'API des prompts vieillissent ; un paramètre inventé fait planter la cellule.
Pour un symbole hors de marimo, le skill `notes-doc` s'applique s'il existe dans le projet.

## 4. Vérifier, puis seulement rendre la main

```
mak verifier notebook.py            # marimo check --strict, règles, exécution de chaque cellule
mak verifier notebook.py --conseils # avec les conseils de lisibilité
mak cellules --notebook notebook.py < proposees.json   # avant d'insérer des cellules
```

- Corrige chaque **erreur** (cellule qui plante, ou résultat faux) et chaque **avertissement**
  (réactivité cassée), ou dis à l'utilisateur pourquoi tu en laisses un.
- Applique les **conseils** aux cellules que tu viens d'écrire, pas au reste.
- Le rapport dit quelles étapes ont tourné. Une étape « sautée » ou « échec » n'est pas une
  vérification : dis-le dans ton compte rendu, n'annonce pas un notebook vérifié.
- La référence de chaque règle (`AG001`…) : `reference/regles.md`, ou `mak regles --reference`.
  Une règle qui se trompe sur un cas précis : `--ignorer AG203`, et dis pourquoi.

## Skills voisins du même kit

- `wigglystuff` : choisir un widget au-delà de `mo.ui` (deux paramètres d'un geste, nombre dans
  une phrase, sélection sur un graphique, trace d'algorithme) et lire sa doc hors ligne.
- `marimo-lens` : quand l'analyste montre une zone d'un résultat, ou pour une visite guidée.

## Ce que ce skill ne refait pas

Le format du fichier, les conversions depuis Jupyter ou Streamlit, WASM et anywidget sont
couverts par les skills officiels de marimo (`npx skills add marimo-team/skills`) ; le
travail dans le noyau par marimo pair. Ce skill s'ajoute à eux.
