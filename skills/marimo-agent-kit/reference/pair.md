# Travailler dans un notebook ouvert (marimo pair)

Quand un serveur marimo tient le notebook, le noyau est la source de vérité : le fichier est
ce que le noyau écrit. Une modification du fichier n'atteint ni le noyau ni l'utilisateur, et
peut être écrasée à la prochaine sauvegarde. On écrit donc par `marimo._code_mode` (`cm`), dans
le bloc-notes temporaire de `marimo pair execute`.

Ce fichier ajoute au mode d'emploi officiel (`marimo pair --help`, `marimo pair docs <sujet>`)
ce que le kit contrôle. Lis l'officiel d'abord : il suit la version installée.

## Le cycle

1. **Trouver la session** : `marimo pair notebook list` donne l'URL et le `session_id`.
2. **Lire l'API une fois** : `marimo pair execute --url URL --session ID -c "import marimo._code_mode as cm; help(cm)"`.
3. **Regarder avant d'écrire** : le code des cellules (`ctx.cells`), ce que chacune définit
   (`ctx.graph.cells[cid].defs`), les données réelles (`print(df.schema)`, `df.head()`), dans le
   bloc-notes : rien n'y est gardé.
4. **Vérifier les corps avant de les soumettre** : écris-les dans une liste JSON, puis
   `mak cellules --notebook notebook.py < proposees.json`. Le fichier reflète le noyau après sa
   sauvegarde automatique ; c'est assez pour juger les noms et les mutations. Corrige les erreurs.
5. **Soumettre en un lot** : `async with cm.get_context() as ctx:` puis `create_cell`,
   `edit_cell`, `run_cell`. marimo refuse le lot entier s'il casse le graphe (nom défini deux
   fois, cycle, nom retiré qui sert ailleurs) : lis le refus, corrige, resoumets.
6. **Lire le résultat** : `ctx.cells[cid].status`, `.errors`, `.console_outputs`. Une cellule
   « errored » se corrige avant de passer à la suite.
7. **Relire tout le notebook** : `mak verifier notebook.py --sans-execution` (le noyau a déjà
   exécuté) pour ce que `cm` ne contrôle pas : mutation entre cellules, élément non lié, `mo.md`
   sans `f`, sortie perdue, lisibilité.

## Ce que le kit ajoute aux consignes officielles

- **Montre le code.** `create_cell` replie le code par défaut (`hide_code=True`). L'utilisateur
  lit le code et ses sorties côte à côte : passe `hide_code=False`, sauf pour une cellule qui
  n'est que du Markdown.
- **Une cellule Markdown avant chaque étape** créée, en une ou deux phrases : ce qu'on va voir.
- **Paquets** : `ctx.packages.add("paquet")`, jamais `uv add` ou `pip` à côté ; demande avant
  d'ajouter une dépendance que l'utilisateur n'a pas demandée.
- **Supprimer** retire les noms de la cellule : regarde `ctx.graph.descendants(cid)` et
  demande avant.
- **Pas de chemin temporaire** (`/tmp/…`) dans une cellule gardée.

## Pièges vus

- Le bloc-notes copie les variables du notebook *avant* l'appel : après un `run_cell` dans le
  même appel, lis `ctx.globals["x"]`, pas `x`.
- Les méthodes de `ctx` ne s'attendent pas (`ctx.run_cell(cid)`, sans `await`) ; seul
  `async with` est asynchrone. Pas d'`asyncio.run` autour.
- `import marimo._code_mode` reste dans le bloc-notes, jamais dans une cellule (règle AG006).
