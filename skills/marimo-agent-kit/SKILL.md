---
name: marimo-agent-kit
description: Écrire, modifier ou relire un notebook marimo sans les erreurs habituelles des agents, et le rendre lisible pour un humain. Le skill choisit entre le noyau ouvert, par marimo pair, et le fichier. Il applique un contrat d'écriture, vérifie chaque changement par `mak verifier` et lit l'API installée par `mak api`. À utiliser dès qu'une tâche touche un fichier marimo (`@app.cell`, `marimo.App`, `mo.ui`, `mo.md`), un notebook ouvert dans marimo, ou l'assistant intégré de marimo. Use for: marimo notebook, reactive cells, mo.ui, marimo pair, marimo check.
---

# Écrire des notebooks marimo justes et lisibles

marimo n'est pas Jupyter. Chaque cellule est un nœud d'un graphe de noms. Un nom n'a qu'une
cellule propriétaire. Seule la dernière expression d'une cellule s'affiche. Une mutation ne
relance aucune cellule. Presque toutes les erreurs d'un agent viennent de ces quatre règles, et
`marimo check` n'en trouve qu'une petite partie. Ce skill ajoute un contrat d'écriture, des
contrôles et la lecture de l'API installée.

`mak` est la commande du paquet `marimo-agent-kit`. Sans installation, lance
`uvx --from "git+https://github.com/auspect/marimo-agent-kit" mak ...`.

## 1. Choisir où écrire

| Situation | Où écrire | Contrôle |
|---|---|---|
| Un serveur marimo tient le notebook. | Dans le noyau, par marimo pair. Jamais dans le fichier. | `cm` refuse un lot invalide. Lance ensuite `mak verifier --sans-execution`. |
| Aucun serveur ne tourne, ou l'utilisateur veut un fichier. | Le fichier `.py`, au format marimo. | `mak verifier notebook.py` |
| L'utilisateur parle dans le chat de marimo. | Rien à écrire. `mak installer --marimo` donne le contrat et les outils à l'assistant. | Les outils MCP du kit. |

`marimo pair notebook list` dit si un notebook est ouvert. La commande existe depuis marimo
0.22.5 et liste les serveurs lancés avec `--no-token`. Lis une fois par session
`marimo pair --help` et `marimo pair docs gotchas`, qui suivent la version installée. Le travail
dans le noyau est détaillé dans `reference/pair.md`.

## 2. Écrire selon le contrat

Lis `reference/contrat.md` avant la première cellule. Ses quatorze règles se lisent en une
minute. Voici les cinq pièges les plus fréquents.

1. Un nom a une seule cellule. Pour l'étape suivante, crée un nouveau nom, par exemple
   `propre = df.dropna()`. N'écris jamais `df = ...` dans une autre cellule. N'utilise jamais
   `_df` pour contourner la règle, car un nom en `_` reste privé à sa cellule.
2. Ne modifie pas un objet d'une autre cellule. `df["c"] = ...`, `.append` et `inplace=True` ne
   relancent pas les cellules qui lisent cet objet.
3. Lie chaque élément d'interface à un nom public, et lis sa `.value` dans une autre cellule.
   Pour plusieurs éléments, utilise `mo.ui.array` et non une liste Python.
4. Seule la dernière expression s'affiche. Pour plusieurs sorties, utilise `mo.vstack([...])`.
   Écris `mo.md(f"... {valeur} ...")` avec le `f`, pour que le texte suive le calcul.
5. Pour un bouton de calcul, crée un `mo.ui.run_button`, puis écris
   `mo.stop(not bouton.value, mo.md("..."))` en tête de la cellule de calcul. N'écris pas
   `if bouton.value:`, car les noms définis dans le `if` manquent aux autres cellules.

Un humain lira le notebook. Mets une courte cellule Markdown avant chaque étape. Donne un
`label` à chaque contrôle et place-le au-dessus de ce qu'il pilote. Place le calcul coûteux en
amont de la présentation. Termine une cellule de figure par la figure, avec un titre et des axes
nommés.

## 3. Lire l'API installée

```
mak api mo.ui.table
mak api --chercher cache
```

La première commande affiche la signature, la documentation et les membres. La seconde liste les
noms qui contiennent le mot, par exemple `mo.cache` et `mo.persistent_cache`. Les listes d'API des
prompts vieillissent, et un paramètre inventé fait planter la cellule. Pour un symbole hors de
marimo, applique le skill `notes-doc` s'il existe dans le projet.

## 4. Vérifier avant de rendre la main

```
mak verifier notebook.py
mak verifier notebook.py --conseils
mak cellules --notebook notebook.py < proposees.json
```

`mak verifier` lance `marimo check --strict`, applique les règles et exécute chaque cellule.
`--conseils` ajoute les conseils de lisibilité. `mak cellules` juge des cellules avant leur
insertion.

- Corrige chaque erreur et chaque avertissement. Une erreur est une cellule qui plante ou un
  résultat faux. Un avertissement est une réactivité cassée. Si tu laisses un avertissement,
  dis pourquoi à l'utilisateur.
- Applique les conseils aux cellules que tu viens d'écrire, pas au reste.
- Le rapport dit quelles étapes ont tourné. Une étape sautée ou en échec n'est pas une
  vérification. Dis-le dans ton compte rendu et n'annonce pas un notebook vérifié.
- `reference/regles.md` ou `mak regles --reference` explique chaque règle. Si une règle se trompe
  sur un cas précis, passe `--ignorer AG203` et dis pourquoi.

## Les autres skills du kit

- `wigglystuff` aide à choisir un widget quand `mo.ui` ne suffit pas, et donne sa doc sans réseau.
  Exemples de besoins : régler deux paramètres d'un geste, glisser un nombre dans une phrase,
  sélectionner sur un graphique, suivre un algorithme.
- `marimo-lens` sert quand l'analyste montre une zone d'un résultat, ou pour une visite guidée.

## Ce que ce skill ne refait pas

Les skills officiels de marimo couvrent le format du fichier, les conversions depuis Jupyter ou
Streamlit, WASM et anywidget. Installe-les par `npx skills add marimo-team/skills`. marimo pair
couvre le travail dans le noyau. Ce skill s'ajoute à eux.
