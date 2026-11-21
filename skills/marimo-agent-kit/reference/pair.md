# Travailler dans un notebook ouvert avec marimo pair

Quand un serveur marimo tient le notebook, le noyau fait foi. Le fichier n'est que ce que le
noyau écrit. Une modification du fichier n'atteint ni le noyau ni l'utilisateur, et la prochaine
sauvegarde peut l'écraser. Écris donc par `marimo._code_mode`, importé sous le nom `cm`, dans le
bloc-notes temporaire de `marimo pair execute`.

Le mode d'emploi officiel est dans `marimo pair --help` et `marimo pair docs <sujet>`. Il suit la
version installée. Lis-le d'abord. Ce fichier ajoute ce que le kit contrôle.

## Le cycle

1. Trouve la session. `marimo pair notebook list` donne l'URL et le `session_id`.
2. Lis l'API une fois :
   `marimo pair execute --url URL --session ID -c "import marimo._code_mode as cm; help(cm)"`.
3. Regarde avant d'écrire, dans le bloc-notes, qui ne garde rien. Lis le code des cellules dans
   `ctx.cells`, ce que chacune définit dans `ctx.graph.cells[cid].defs`, et les données réelles
   par `print(df.schema)` ou `df.head()`.
4. Vérifie les cellules avant de les soumettre. Écris leurs corps dans une liste JSON, puis lance
   `mak cellules --notebook notebook.py < proposees.json`. Le fichier reflète le noyau après la
   sauvegarde automatique, ce qui suffit pour juger les noms et les mutations. Corrige les erreurs.
5. Soumets un seul lot : ouvre `async with cm.get_context() as ctx:`, puis appelle `create_cell`,
   `edit_cell` et `run_cell`. marimo refuse tout le lot s'il casse le graphe, par exemple par un
   nom défini deux fois, un cycle ou un nom retiré qui sert ailleurs. Lis le refus, corrige, puis
   soumets de nouveau.
6. Lis le résultat dans `ctx.cells[cid].status`, `.errors` et `.console_outputs`. Corrige une
   cellule en état `errored` avant de passer à la suite.
7. Relis tout le notebook par `mak verifier notebook.py --sans-execution`, car le noyau a déjà
   exécuté les cellules. Cette commande trouve ce que `cm` ne contrôle pas : la mutation entre
   cellules, l'élément non lié, le `mo.md` sans `f`, la sortie perdue et les défauts de lisibilité.

## Ce que le kit ajoute aux consignes officielles

- Montre le code. `create_cell` replie le code par défaut avec `hide_code=True`. L'utilisateur lit
  le code à côté de ses sorties. Passe donc `hide_code=False`, sauf pour une cellule qui ne
  contient que du Markdown.
- Crée une cellule Markdown d'une ou deux phrases avant chaque étape. Elle dit ce que l'étape
  montre.
- Installe un paquet par `ctx.packages.add("paquet")`, jamais par `uv add` ou `pip`. Demande avant
  d'ajouter une dépendance que l'utilisateur n'a pas demandée.
- Supprimer une cellule retire ses noms. Regarde `ctx.graph.descendants(cid)` et demande avant.
- N'écris pas de chemin temporaire comme `/tmp/...` dans une cellule que tu gardes.

## Pièges connus

- Le bloc-notes copie les variables du notebook avant l'appel. Après un `run_cell` dans le même
  appel, lis `ctx.globals["x"]`, pas `x`.
- N'écris pas `await` devant les méthodes de `ctx`, par exemple `ctx.run_cell(cid)`. Seul
  `async with` est asynchrone. N'ajoute pas `asyncio.run` autour.
- `import marimo._code_mode` reste dans le bloc-notes, jamais dans une cellule. La règle AG006 le
  vérifie.
