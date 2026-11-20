# marimo-agent-kit

Ce qu'il faut à un agent (Claude Code, Copilot, OpenCode, Codex, ou l'assistant intégré de
marimo) pour écrire des notebooks marimo justes et lisibles : un contrat d'écriture, des
contrôles qui voient ce que `marimo check` ne voit pas, l'API de marimo lue dans la version
installée, et le rapport rendu dans le notebook lui-même.

Une commande, `mak`, sans dépendance : Python 3.10 ou plus, et marimo dans le projet (ou `uvx`).

## Pourquoi

Sur `tests/exemples/mauvais.py`, dix erreurs typiques d'un agent peu habitué à marimo :

| Contrôle | Ce qu'il voit |
|---|---|
| `marimo check --strict` (0.25.2) | rien : 0 problème |
| `python mauvais.py` | la première erreur seulement, puis s'arrête |
| `mak verifier mauvais.py` | les dix, avant exécution (4 erreurs, 6 avertissements) ; l'exécution confirme les trois cellules qui plantent |

Les règles (`AG001`…) visent ce qui revient : `.value` lu dans la cellule qui crée l'élément,
`mo.md("{x}")` sans `f`, mutation d'un objet d'une autre cellule, élément d'interface rangé dans
une liste Python, `if bouton.value:` qui laisse des noms indéfinis, `asyncio.run` (qui passe en
script et casse dans l'éditeur), `display()`, secret en clair, dépendance absente de l'en-tête
PEP 723… La liste et la raison de chacune : [`reference/regles.md`](src/marimo_agent_kit/donnees/skill/reference/regles.md).

Sur les 21 notebooks de ce dépôt, relus par leur auteur : aucune erreur, aucun avertissement ;
des conseils de lisibilité seulement.

## Ce qu'il y a dedans

| Couche | Pour qui | Comment |
|---|---|---|
| `mak verifier` | tout agent, la CI, toi | `marimo check --strict`, les règles, puis l'exécution de chaque cellule par `marimo export session` |
| `mak cellules` | un agent avant d'insérer des cellules (marimo pair, assistant) | les règles sur les corps proposés, dans le contexte du notebook |
| `mak api` | tout agent | signature et documentation de la version installée ; `--chercher` pour trouver un nom |
| Contrat (`mak regles`) | l'assistant de marimo, les agents | quatorze règles courtes, posées dans `[tool.marimo.ai] rules` |
| Serveur MCP (`mak mcp`) | l'assistant de marimo (modes Ask et Agent), Claude Code, Copilot | cinq outils : `verifier_notebook`, `verifier_cellules`, `api_marimo`, `chercher_api_marimo`, `regles_marimo` |
| Skill `marimo-agent-kit` | agents à skills | où écrire (noyau ou fichier), le contrat, la boucle de vérification |
| Hook (`mak hook`) | Claude Code, Copilot | après chaque écriture d'un notebook : erreur → l'agent doit corriger ; avertissement → contexte |
| `mak.audit()` | toi, dans le notebook | une cellule qui montre le rapport et le message à renvoyer à l'agent |

Le kit complète les outils de marimo-team, il ne les refait pas : le skill officiel
`marimo-notebook` pour le format, `marimo pair` pour travailler dans le noyau, `marimo check`
pour la structure. Ce qu'ils couvrent est résumé dans `veille/2026-11-20-marimo-agents.md`.

## Installer

Depuis ce dépôt (copie locale) :

```bash
uv tool install ./marimo-agent-kit
```

Sans rien installer :

```bash
uvx --from ./marimo-agent-kit mak verifier notebook.py
```

Depuis GitHub, quand le dépôt est accessible au poste :

```bash
uv tool install "git+https://github.com/auspect/amelioration-continue#subdirectory=marimo-agent-kit"
```

Puis, dans un projet, l'installateur dit ce qu'il ferait, et `--appliquer` l'écrit (rien n'est
écrasé) :

```bash
mak installer --skill agents --marimo --hook-claude
```

```bash
mak installer --skill agents --marimo --hook-claude --appliquer
```

- `--skill agents|claude|github` : le skill dans `.agents/skills/`, `.claude/skills/` ou `.github/skills/`.
- `--marimo` : le contrat et le serveur MCP dans `pyproject.toml`. Le serveur MCP de l'assistant
  demande `marimo[mcp]` dans l'environnement qui lance marimo.
- `--hook-claude` : le hook dans `.claude/settings.json`.
- `--mcp-claude` : le serveur MCP dans `.mcp.json` (un serveur lance du code chez quiconque ouvre
  le projet : à poser en connaissance de cause).

## S'en servir

```bash
mak verifier notebook.py                  # tout : structure, règles, exécution
mak verifier notebook.py --sans-execution # rapide
mak verifier notebook.py --conseils --json
mak api mo.ui.table
mak api --chercher cache
echo '["df[\"c\"] = 1"]' | mak cellules --notebook notebook.py
```

Dans un notebook, une cellule montre le rapport du notebook lui-même, avec le message à
renvoyer à l'agent (le kit doit être dans l'environnement du notebook, par exemple
`uvx --with ./marimo-agent-kit marimo edit notebook.py`) :

```python
import marimo_agent_kit as mak
mak.audit()          # le notebook courant ; mak.audit("autre.py", executer=True)
```

| Sans le kit : marimo montre les cellules qui plantent | Avec `mak.audit()` en dernière cellule |
|---|---|
| ![Fin de mauvais.py dans l'éditeur : deux cellules « Ancestor raised »](captures/audit-avant-1280.png) | ![La même fin de notebook, avec le rapport : gravité, règle, cellule, constat, correction](captures/audit-apres-1280.png) |

Les deux captures : `mauvais.py` dans l'éditeur marimo 0.25.2, toutes les cellules lancées,
fenêtre de 1 280 px, la dernière cellule en haut de l'écran. Les erreurs silencieuses (`mo.md`
sans `f`, mutation, case à cocher non liée, bouton sans effet) n'apparaissent que dans la seconde.

### Brancher un LLM interne dans l'assistant de marimo

marimo appelle un fournisseur personnalisé en API OpenAI (`/chat/completions`). La sonde rejoue
les requêtes de marimo 0.25.2 contre ton point d'accès et dit ce qui passe : chat (mode Manual),
autocomplétion (`max_completion_tokens`), génération de cellule (`tool_choice: "required"`),
modes Ask et Agent avec les outils du kit (`tool_choice: "auto"`). Elle propose ensuite le bloc
de configuration.

```bash
mak sonde-llm https://llm.interne/v1 mon-modele --cle-env LLM_INTERNE_CLE --ca /chemin/ca-entreprise.pem
```

L'environnement qui lance marimo a besoin de `pydantic-ai-slim[openai]` (extra
`marimo[recommended]`). Détail : `savoir/marimo/v0.25/editor-features/llm-interne-en-fournisseur-personnalise.md`.

### Ce qui sort du poste

marimo n'a pas de télémétrie d'usage, mais `marimo edit` contacte marimo.io une fois par jour
pour la version, et quelques fonctions sortent sur demande (recherche web du chat, préréglage
MCP `context7`, complétion Copilot, `marimo new "invite"`). Le bilan du poste, et les lignes à
poser en PowerShell ou en bash :

```bash
mak confidentialite
```

Le kit pose lui-même `MARIMO_SKIP_UPDATE_CHECK=1` et `PYDANTIC_AI_NO_BANNER=1` sur les marimo
qu'il lance. Mesures : `savoir/marimo/v0.25/configuration/ce-qui-sort-du-poste.md`.

Code de sortie de `mak verifier` : 0 si aucune erreur, 1 sinon. Le rapport dit quelles étapes
ont tourné ; une étape sautée n'est pas une vérification.

## Limites

- Les règles lisent la syntaxe, pas les types : `df.sort(…)` seul dans une cellule est signalé
  comme ambigu (liste modifiée en place, ou résultat de DataFrame perdu).
- `AG203` (nombre écrit en dur dans un texte) est bruyant sur des notebooks de cours : c'est un
  conseil, à lire, pas à appliquer partout.
- L'exécution écrit `__marimo__/session/<notebook>.json` à côté du notebook (le dossier
  `__marimo__/` est d'ordinaire ignoré par git).
- Écrit pour marimo 0.25.2 ; `marimo._code_mode` et les outils de l'assistant changent d'une
  version à l'autre.
