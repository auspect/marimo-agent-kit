# marimo-agent-kit

Le kit aide un agent à écrire des notebooks marimo justes et lisibles. Il sert avec Claude Code,
Copilot, OpenCode, Codex et l'assistant intégré de marimo. Il contient ces éléments :

- un contrat d'écriture, et des contrôles qui trouvent ce que `marimo check` ne voit pas ;
- l'API de marimo lue dans la version installée ;
- trois skills, `marimo-agent-kit`, `wigglystuff` et `marimo-lens` ;
- un rapport qui s'affiche dans le notebook lui-même ;
- deux commandes pour brancher un LLM interne sans rien laisser sortir du poste.

La commande `mak` n'a pas de dépendance. Elle demande Python 3.10 ou plus, et marimo dans le
projet ou par `uvx`.

## Pourquoi

Le fichier `tests/exemples/mauvais.py` contient dix erreurs typiques d'un agent qui connaît mal
marimo. Voici ce que chaque contrôle y trouve.

| Contrôle | Résultat |
|---|---|
| `marimo check --strict` (0.25.2) | Aucun problème trouvé. |
| `python mauvais.py` | La première erreur, puis l'arrêt. |
| `mak verifier mauvais.py` | Les dix erreurs avant l'exécution, soit 4 erreurs et 6 avertissements. L'exécution confirme les trois cellules qui plantent. |

Les règles `AG001` à `AG210` visent les erreurs qui reviennent. En voici quelques-unes :

- lire `.value` dans la cellule qui crée l'élément d'interface ;
- écrire `mo.md("{x}")` sans le préfixe `f` ;
- modifier un objet qu'une autre cellule a créé ;
- ranger des éléments d'interface dans une liste Python ;
- écrire `if bouton.value:`, qui laisse des noms indéfinis ;
- appeler `asyncio.run`, qui passe en script et échoue dans l'éditeur ;
- appeler `display()`, ou laisser un secret en clair.

Le fichier [`skills/marimo-agent-kit/reference/regles.md`](skills/marimo-agent-kit/reference/regles.md)
donne la liste complète et la raison de chaque règle.

Sur 21 notebooks de cours écrits par des agents puis relus, le kit ne trouve ni erreur ni
avertissement. Il ne donne que des conseils de lisibilité.

## Contenu

| Élément | Utilisateur | Rôle |
|---|---|---|
| `mak verifier` | Tout agent, la CI, toi | Lance `marimo check` et lit tous ses constats en JSON, applique les règles, puis exécute chaque cellule par `marimo export session`. |
| `mak cellules` | Un agent qui va insérer des cellules | Applique les règles aux cellules proposées, dans le contexte du notebook. |
| `mak api` | Tout agent | Affiche la signature et la documentation d'un symbole de marimo installé. `--chercher` trouve un nom. |
| `mak widgets` | Tout agent | Affiche la doc de wigglystuff 0.6.0 sans réseau et la compare à la version installée. |
| `mak regles` | L'assistant de marimo, les agents | Affiche le contrat de quatorze règles que `[tool.marimo.ai] rules` transmet à l'assistant. |
| `mak mcp` | L'assistant de marimo en modes Ask et Agent, Claude Code, Copilot | Sert six outils MCP. |
| `skills/` | Les agents qui lisent des skills | Contient `marimo-agent-kit`, `wigglystuff` et `marimo-lens`. |
| `mak hook` | Claude Code, Copilot | Vérifie chaque notebook que l'agent écrit. Une erreur bloque l'agent, un avertissement lui est signalé. |
| `mak.audit()` | Toi, dans le notebook | Affiche le rapport et le message à renvoyer à l'agent. |
| `mak sonde-llm`, `mak confidentialite` | Toi, au travail | Testent ce qu'un LLM interne accepte, et ce qui sort du poste. |

Les six outils MCP sont `verifier_notebook`, `verifier_cellules`, `api_marimo`,
`chercher_api_marimo`, `widgets_wigglystuff` et `regles_marimo`.

Le kit complète les outils de marimo-team sans les remplacer. Le skill officiel `marimo-notebook`
décrit le format. `marimo pair` sert à travailler dans le noyau. `marimo check` contrôle la
structure. Le paquet `marimo-lens` livre son propre mode d'emploi pour agents.

## Installer

Pour installer les skills seuls dans un agent qui lit le format Agent Skills, lance cette commande :

```bash
npx skills add auspect/marimo-agent-kit
```

Pour installer le greffon de Claude Code, tape ces commandes dans une session :

```text
/plugin marketplace add auspect/marimo-agent-kit
/plugin install marimo-agent-kit@marimo-agent-kit
```

Pour installer la commande `mak`, lance cette commande :

```bash
uv tool install "git+https://github.com/auspect/marimo-agent-kit"
```

Pour l'utiliser sans l'installer, lance cette commande :

```bash
uvx --from "git+https://github.com/auspect/marimo-agent-kit" mak verifier notebook.py
```

Dans un projet, l'installateur affiche d'abord ce qu'il ferait :

```bash
mak installer --skill agents --marimo --hook-claude
```

L'option `--appliquer` écrit les fichiers. L'installateur n'écrase jamais un fichier existant.

```bash
mak installer --skill agents --marimo --hook-claude --appliquer
```

Les options choisissent ce que l'installateur pose :

- `--skill agents`, `--skill claude` ou `--skill github` pose les trois skills dans `.agents/skills/`,
  `.claude/skills/` ou `.github/skills/`. `--seulement wigglystuff,marimo-lens` restreint la liste.
- `--marimo` ajoute le contrat et le serveur MCP à `pyproject.toml`. Le serveur MCP de l'assistant
  demande `marimo[mcp]` dans l'environnement qui lance marimo.
- `--hook-claude` ajoute le hook à `.claude/settings.json`.
- `--mcp-claude` ajoute le serveur MCP à `.mcp.json`. Un serveur MCP lance du code chez toute
  personne qui ouvre le projet. Ne pose cette option qu'en connaissance de cause.

## Utiliser

Voici les commandes courantes :

```bash
mak verifier notebook.py
mak verifier notebook.py --sans-execution
mak verifier notebook.py --conseils --json
mak api mo.ui.table
mak api --chercher cache
mak widgets TangleDistribution
mak widgets --chercher lasso
echo '["df[\"c\"] = 1"]' | mak cellules --notebook notebook.py
```

`mak verifier` rend 0 sans erreur et 1 sinon. Le rapport dit quelles étapes ont tourné. Une étape
sautée ne compte pas comme une vérification.

Le rapport numérote les cellules dans l'ordre du fichier. La cellule setup, `with app.setup:`,
porte le numéro 0, et les autres cellules partent de 1. Le champ `cellule` du JSON et le texte
« cellule 2 » donnent le même numéro. `mak cellules` numérote les cellules proposées de 1 à n,
dans l'ordre de la liste.

Pour voir le rapport dans le notebook, ajoute cette cellule. Le kit doit être dans
l'environnement du notebook, par exemple avec
`uvx --with "git+https://github.com/auspect/marimo-agent-kit" marimo edit notebook.py`.

```python
import marimo_agent_kit as mak
mak.audit()
```

`mak.audit("autre.py", executer=True)` vérifie un autre notebook et exécute ses cellules.

| Sans le kit, marimo montre les cellules qui plantent | Avec `mak.audit()` en dernière cellule |
|---|---|
| ![Fin de mauvais.py dans l'éditeur, avec deux cellules "Ancestor raised"](captures/audit-avant-1280.png) | ![La même fin de notebook, avec le rapport des constats et des corrections](captures/audit-apres-1280.png) |

Les deux captures montrent `mauvais.py` dans l'éditeur de marimo 0.25.2, toutes cellules lancées,
dans une fenêtre de 1 280 pixels. Les erreurs silencieuses n'apparaissent que dans la seconde.
Ce sont le `mo.md` sans `f`, la mutation, la case à cocher non liée et le bouton sans effet.

### Widgets wigglystuff et marimo-lens sans réseau

Le skill `wigglystuff` aide à choisir un widget selon le besoin. Il embarque la doc de
wigglystuff 0.6.0, soit 71 pages et 93 démos, avec la signature et les traitlets lus dans le
paquet.

Le skill `marimo-lens` dit quand Lens aide et comment le monter. Il embarque les 19 pages de la
doc de marimo-lens 0.2.4. Le mode d'emploi pour agents reste celui du paquet, que cette commande
affiche :

```bash
uvx --with marimo-lens==0.2.4 agent-plugins read marimo-lens
```

Les deux docs viennent du commit de la version publiée. La branche principale de chaque projet
décrit déjà des fonctions qui ne sont pas publiées. Les scripts `outils/importer_wigglystuff.py`
et `outils/importer_marimo_lens.py` régénèrent ces docs. Leur mode d'emploi est en tête de chaque
script.

### Brancher un LLM interne dans l'assistant de marimo

marimo appelle un fournisseur personnalisé par l'API OpenAI `/chat/completions`. Il envoie la
clé dans les en-têtes `Authorization` et `api-key`. La sonde rejoue contre ton point d'accès les
quatre requêtes que marimo 0.25.2 envoie :

- le chat en mode Manual ;
- l'autocomplétion, avec `max_completion_tokens` ;
- la génération de cellule, avec `tool_choice: "required"` ;
- les modes Ask et Agent avec les outils du kit, avec `tool_choice: "auto"`.

La sonde dit ensuite quelles fonctions marcheront et affiche le bloc de configuration.

```bash
mak sonde-llm https://llm.interne/v1 mon-modele --cle-env LLM_INTERNE_CLE --ca /chemin/ca-entreprise.pem
```

L'environnement qui lance marimo a besoin de `pydantic-ai-slim[openai]`, que l'extra
`marimo[recommended]` installe. Il lui faut aussi une clé non vide, même factice.

### Ce qui sort du poste

marimo n'envoie aucune télémétrie d'usage. `marimo edit` contacte marimo.io une fois par jour pour
la version, et `MARIMO_SKIP_UPDATE_CHECK=1` coupe cet appel. Quatre fonctions envoient des données
dehors quand on les active : la recherche web du chat, le préréglage MCP `context7`, la
complétion Copilot et `marimo new "invite"`. Avec la variable posée, un proxy qui notait chaque
hôte n'a vu aucune connexion sortante, ni du serveur, ni du navigateur, ni de l'assistant branché
sur un LLM local.

```bash
mak confidentialite
```

Cette commande fait le bilan du poste et affiche les lignes à poser en PowerShell ou en bash. Le
kit pose lui-même `MARIMO_SKIP_UPDATE_CHECK=1` et `PYDANTIC_AI_NO_BANNER=1` sur chaque marimo
qu'il lance.

## Limites

- Les règles lisent la syntaxe, pas les types. `df.sort(...)` seul dans une cellule reçoit un
  avertissement ambigu, car c'est une liste modifiée en place ou un résultat de DataFrame perdu.
- La règle `AG203` signale un nombre écrit en dur dans un texte. Elle se trompe souvent sur des
  notebooks de cours. C'est un conseil à lire, pas une correction à appliquer partout.
- L'exécution écrit `__marimo__/session/<notebook>.json` à côté du notebook. Le dossier
  `__marimo__/` est d'ordinaire ignoré par git.
- Le kit vise marimo 0.25.2, wigglystuff 0.6.0 et marimo-lens 0.2.4. `marimo._code_mode` et les
  outils de l'assistant changent d'une version à l'autre.

## Développer

```bash
uv run --no-project --with marimo --with polars python -m unittest discover -s tests
uvx ruff check .
```

Le kit est sous licence Apache-2.0. Les docs recopiées gardent leur licence. wigglystuff est sous
MIT, voir `skills/wigglystuff/references/LICENSE-wigglystuff`. marimo-lens est sous Apache-2.0,
voir `skills/marimo-lens/references/LICENSE-marimo-lens`.
