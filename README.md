# marimo-agent-kit

Le kit aide un agent à écrire des notebooks marimo justes et lisibles. Il sert avec Claude Code,
Copilot, OpenCode, Codex et l'assistant intégré de marimo. Il contient ces éléments :

- un contrat d'écriture, et des contrôles qui trouvent ce que `marimo check` ne voit pas ;
- l'API de marimo lue dans la version installée ;
- quatre skills, `marimo-agent-kit`, `wigglystuff`, `marimo-lens` et `marimo-studio-vues` ;
- un rapport qui s'affiche dans le notebook lui-même ;
- deux commandes pour brancher un LLM interne sans rien laisser sortir du poste ;
- pixi comme gestionnaire de paquets par défaut : le bouton d'installation de l'éditeur ajoute
  le paquet manquant au projet, et un fichier `mak.env` porte le proxy, les certificats et les
  consignes pour l'agent.

La commande `mak` n'a pas de dépendance. Elle demande Python 3.10 ou plus, et marimo dans
l'environnement pixi du projet, dans son `.venv`, ou par `uvx`.

## Pourquoi

Le fichier `tests/exemples/mauvais.py` contient dix erreurs typiques d'un agent qui connaît mal
marimo. Voici ce que chaque contrôle y trouve.

| Contrôle | Résultat |
|---|---|
| `marimo check --strict` (0.25.2) | Aucun problème trouvé. |
| `python mauvais.py` | La première erreur, puis l'arrêt. |
| `mak verifier mauvais.py` | Les dix erreurs avant l'exécution, soit 4 erreurs et 6 avertissements. L'exécution confirme les trois cellules qui plantent. |

Les règles `AG001` à `AG210` visent les erreurs qui reviennent, et les règles `AG301` à `AG306`
ce qui touche à la sécurité du poste. En voici quelques-unes :

- lire `.value` dans la cellule qui crée l'élément d'interface ;
- écrire `mo.md("{x}")` sans le préfixe `f` ;
- modifier un objet qu'une autre cellule a créé ;
- ranger des éléments d'interface dans une liste Python ;
- écrire `if bouton.value:`, qui laisse des noms indéfinis ;
- appeler `asyncio.run`, qui passe en script et échoue dans l'éditeur ;
- appeler `display()`, ou laisser un secret en clair ;
- lancer une commande du shell, charger un pickle, ou construire `mo.Html` à partir de données
  sans les échapper.

Le fichier [`skills/marimo-agent-kit/reference/regles.md`](skills/marimo-agent-kit/reference/regles.md)
donne la liste complète et la raison de chaque règle.

Sur 21 notebooks de cours écrits par des agents puis relus, le kit ne trouve aucune erreur et un
seul avertissement. C'est un `AG304` sur un tableau HTML assemblé à partir de morceaux déjà
échappés, que la règle ne sait pas suivre. Le reste est fait de conseils de lisibilité.

## Contenu

| Élément | Utilisateur | Rôle |
|---|---|---|
| `mak verifier` | Tout agent, la CI, l'utilisateur | Lance `marimo check` et lit tous ses constats en JSON, applique les règles, puis exécute chaque cellule par `marimo export session`. |
| `mak cellules` | Un agent qui va insérer des cellules | Applique les règles aux cellules proposées, dans le contexte du notebook. |
| `mak api` | Tout agent | Affiche la signature et la documentation d'un symbole de marimo installé. `--chercher` trouve un nom. |
| `mak widgets` | Tout agent | Affiche la doc de wigglystuff 0.6.0 sans réseau et la compare à la version installée. |
| `mak regles` | L'assistant de marimo, les agents | Affiche le contrat de quatorze règles que `[tool.marimo.ai] rules` transmet à l'assistant. |
| `mak mcp` | L'assistant de marimo en modes Ask et Agent, Claude Code, Copilot | Sert six outils MCP. |
| `skills/` | Les agents qui lisent des skills | Contient `marimo-agent-kit`, `wigglystuff`, `marimo-lens` et `marimo-studio-vues`. |
| `mak hook` | Claude Code, Copilot | Vérifie chaque notebook que l'agent écrit. Une erreur bloque l'agent, un avertissement lui est signalé. Au démarrage, donne le gestionnaire de paquets du projet et ses consignes. |
| `mak.audit()` | L'utilisateur, dans le notebook | Affiche le rapport et le message à renvoyer à l'agent. |
| `mak sonde-llm`, `mak confidentialite` | L'utilisateur | Testent ce qu'un LLM interne accepte, et ce qui sort du poste. |
| `mak contexte`, `mak marimo` | Les agents, l'utilisateur | Disent le gestionnaire de paquets du projet et ses consignes, et lancent le marimo du projet. |
| `mak garde` | L'utilisateur | Fait le bilan de la garde avant outil, ou juge une commande à l'essai. |
| `mak lancer -- commande` | L'utilisateur | Lance un outil, par exemple safeagents, avec le proxy et les certificats du kit. |

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

Ces commandes vont sur GitHub. Sur un réseau restreint, construis plutôt la roue une fois,
dépose-la sur le dépôt interne, puis installe-la depuis ce dépôt. Un fichier
`src/marimo_agent_kit/mak.env` posé avant `uv build` voyage dans la roue et sert de configuration
par défaut à toutes ses installations. La section [Le fichier mak.env](#le-fichier-makenv) le
décrit.

```bash
uv build --wheel
```

```bash
uv tool install marimo-agent-kit
```

pixi est le gestionnaire de paquets par défaut. Crée le projet au format `pyproject.toml`, que
pixi et marimo lisent tous deux, et ajoute marimo à son environnement :

```bash
pixi init --format pyproject
pixi add marimo
```

Dans le projet, l'installateur affiche d'abord ce qu'il ferait :

```bash
mak installer --skill agents --marimo --hooks
```

L'option `--appliquer` écrit les fichiers. L'installateur n'écrase jamais un fichier existant.

```bash
mak installer --skill agents --marimo --hooks --appliquer
```

Les options choisissent ce que l'installateur pose :

- `--skill agents`, `--skill claude` ou `--skill github` pose les quatre skills dans `.agents/skills/`,
  `.claude/skills/` ou `.github/skills/`. `--seulement wigglystuff,marimo-lens` restreint la liste.
- `--marimo` ajoute à `pyproject.toml` le contrat, le serveur MCP et
  `[tool.marimo.package_management] manager = "pixi"`, ou `"uv"` dans un projet uv. Le serveur
  MCP de l'assistant demande `marimo[mcp]` dans l'environnement qui lance marimo. marimo ne lit
  sa configuration de projet que dans `pyproject.toml` : un projet en `pixi.toml` seul reçoit le
  bloc à recopier.
- `--hooks` pose trois hooks. Le premier relit chaque notebook écrit. Le deuxième donne à l'agent
  le gestionnaire de paquets du projet au démarrage de la session. Le troisième est la garde
  avant outil.
  Par défaut, ils vont dans `.claude/settings.json`, que lisent Claude Code et Copilot.
  `--hooks github` les met dans `.github/hooks/marimo-agent-kit.json`, que lit Copilot seul. Ne
  pose qu'un des deux, sinon Copilot lancerait chaque hook deux fois ; l'installateur refuse le
  second.
- `--mcp` ajoute le serveur MCP à `.mcp.json`, que lisent Claude Code et Copilot. Un serveur MCP
  lance du code chez toute personne qui ouvre le projet. Ne pose cette option qu'en connaissance
  de cause.

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
python -c "import marimo_lens.agent as a; print(a.skill().body)"
```

Les deux docs viennent du commit de la version publiée. La branche principale de chaque projet
décrit déjà des fonctions qui ne sont pas publiées. Les scripts `outils/importer_wigglystuff.py`
et `outils/importer_marimo_lens.py` régénèrent ces docs. Leur mode d'emploi est en tête de chaque
script.

### Restitutions avec marimo Studio

Le skill `marimo-studio-vues` fait d'une analyse plusieurs restitutions pour des publics
différents, avec marimo Studio 0.4.1 : une page React, un diaporama reveal.js, un rapport PDF
Typst et un article Quarto. Il dit comment structurer le notebook pour qu'il serve toutes les
vues, comment les construire, les regarder et les exporter en site statique, en PDF et en PPTX.
Il donne quatorze critères de qualité et deux scripts : `capturer.py` capture une vue dans un vrai
navigateur, `controler_vues.py` relit les sources des vues.

Il embarque les 34 pages de la doc de marimo-studio 0.4.1 et huit fichiers d'exemples officiels,
que `outils/importer_marimo_studio.py` régénère. Le mode d'emploi pour agents reste celui du
paquet, que cette commande affiche :

```bash
uvx --with marimo-studio agent-plugins read marimo-studio
```

L'exemple `exemples/meteo-seattle/` sert de référence : un notebook sur la pluie à Seattle et ses
quatre vues. Son `pyproject.toml` est un projet pixi, comme le kit le conseille : il installe
Quarto et Typst depuis conda-forge, et porte la configuration de marimo et de Studio. Sous
Windows, il contourne la limite de 260 caractères des chemins, que Studio dépasse sans réglage.

### Brancher un LLM interne dans l'assistant de marimo

marimo appelle un fournisseur personnalisé par l'API OpenAI `/chat/completions`. Il envoie la
clé dans les en-têtes `Authorization` et `api-key`. La sonde rejoue contre le point d'accès les
quatre requêtes que marimo 0.25.2 envoie :

- le chat en mode Manual ;
- l'autocomplétion, avec `max_completion_tokens` ;
- la génération de cellule, avec `tool_choice: "required"` ;
- les modes Ask et Agent avec les outils du kit, avec `tool_choice: "auto"`.

La sonde dit ensuite quelles fonctions marcheront et affiche le bloc de configuration.

```bash
mak sonde-llm https://llm.interne/v1 mon-modele --cle-env LLM_INTERNE_CLE --ca /chemin/ca-interne.pem
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

### pixi par défaut, et installer un paquet depuis marimo

pixi gère les paquets du projet. `mak installer --marimo` règle marimo pour qu'il passe par lui :
quand une cellule importe un paquet absent, l'éditeur propose de l'installer, lance
`pixi add <paquet>`, et le paquet arrive dans `pyproject.toml`, `pixi.lock` et l'environnement.
La cellule repart ensuite.

`mak marimo`, `mak verifier`, `mak api` et `mak widgets` cherchent marimo dans cet ordre : la
commande de `MAK_MARIMO`, l'environnement pixi du projet, son `.venv`, le Python de `mak`, puis
`uvx marimo`. L'environnement pixi se lance par `pixi run --manifest-path`, qui l'active : marimo
y trouve pixi, et `pixi add` vise le bon projet même si marimo tourne depuis un autre dossier.

```bash
mak marimo edit notebook.py
```

Le kit ne règle pas le réseau. pixi et uv suivent leur propre configuration. Sur un réseau
restreint, déclare le miroir conda ou le dépôt PyPI interne dans la configuration de pixi, par
exemple `[mirrors]` ou `[pypi-config]` dans `~/.pixi/config.toml`. Le bouton de marimo, les
commandes du kit et l'agent passent alors tous par lui.

### Le fichier mak.env

Le fichier `mak.env` porte le proxy, l'autorité de certification, les variables propres au kit
et des consignes pour l'agent. Il contient une variable par ligne, au format `NOM=valeur`.

```bash
HTTPS_PROXY=http://proxy.exemple.interne:8080
NO_PROXY=localhost,127.0.0.1,.exemple.interne
SSL_CERT_FILE=C:\certs\ca-interne.pem
MAK_CONTEXTE=Les données de production restent sur le partage réseau. Ne les copie pas.
```

Le kit lit jusqu'à quatre fichiers. Le dernier l'emporte :

1. le `mak.env` livré dans le paquet, pour une roue construite pour une équipe ;
2. `~/.config/marimo-agent-kit/mak.env`, ou `%APPDATA%\marimo-agent-kit\mak.env` sous Windows ;
3. le `mak.env` le plus proche du notebook ;
4. le fichier que nomme `MAK_CONFIG`.

Une variable déjà posée dans le shell garde sa valeur. Chaque ligne `MAK_CONTEXTE` ajoute une
consigne. Les variables vont à tout ce que le kit lance : `marimo check`, l'exécution, `mak api`,
la sonde LLM et `mak marimo`, donc aussi au `pixi add` que lance le bouton de marimo. Le kit
masque l'identifiant et le mot de passe d'une adresse de proxy dans ce qu'il affiche, mais le
fichier reste en clair. N'y mets pas de mot de passe.

L'agent reçoit le contexte du projet de trois façons. Le hook de démarrage le lui donne, dans
Claude Code comme dans Copilot. L'outil MCP `regles_marimo` le rend avec le contrat, et le skill
lui demande de lancer `mak contexte`. Ce contexte nomme le gestionnaire du projet et la commande
qui ajoute un paquet. Il interdit `pip install`, les options d'index, les sources `git+` et
`npx`, et renvoie vers `mak api`, `mak widgets` et les références des skills pour la
documentation. `mak contexte --detail` montre d'où vient chaque réglage, le projet trouvé et le
marimo que le kit lancera.

```bash
mak contexte --detail
```

### Garde avant outil

La garde juge chaque commande du shell de l'agent avant qu'elle tourne, dans Claude Code comme
dans Copilot, Windows compris. Elle vise ce qui contourne le gestionnaire du projet et les
dépôts que sa configuration choisit :

- `pip install` ;
- une option d'index, comme `--index-url`, ou une variable `UV_INDEX_URL` posée sur la commande ;
- une source `git+` ;
- `npx`.

`MAK_GARDE` règle son action. `observer`, le défaut, note ce qu'elle aurait refusé sans rien
bloquer. `agir` refuse et donne la raison à l'agent. `off` l'éteint. Le journal ne garde que la
règle, l'outil et un court extrait, dans `~/.local/state/marimo-agent-kit/garde.jsonl` ou
`%LOCALAPPDATA%\marimo-agent-kit\garde.jsonl`. Après quelques jours, lis le bilan. Si chaque
ligne est un vrai écart, passe en `agir`.

```bash
mak garde bilan
mak garde essai "uv pip install --index-url https://pypi.org/simple polars"
```

### Inspecter les appels d'outils de l'assistant avec safeagents (option)

safeagents, de Hugging Face, est un proxy entre l'assistant et l'API du modèle. Il juge chaque
appel d'outil avant qu'il tourne. Le mode Agent de l'assistant de marimo peut exécuter du Python
sur le poste : safeagents se place donc entre lui et le LLM interne. Le projet en est à la version
0.0, sans version publiée. Garde-le en option, jamais en réglage par défaut.

1. Construis la roue d'un commit que tu as relu, sur un poste qui a le droit d'aller sur GitHub.
   Dépose-la sur le dépôt interne, puis installe-la depuis lui par `uv tool install safeagents`.
   Le 15 novembre 2026, le commit `a8ee22d` a été essayé sous Windows avec un faux modèle.
2. Lance-le avec l'environnement du kit, pour qu'il passe par le proxy et lise l'autorité de
   certification. Garde son journal hors du dépôt, car il contient les arguments des appels.
   N'active aucun greffon `hf://`, car un greffon s'exécute dans le proxy.

   ```bash
   mak lancer -- safeagents https://llm.exemple.interne 8790 --journal ~/journaux/safeagents.jsonl
   ```

3. Fais pointer le fournisseur personnalisé de marimo sur `http://127.0.0.1:8790/v1`, et garde
   `127.0.0.1` dans `NO_PROXY`. Déclare `MAK_SAFEAGENTS=http://127.0.0.1:8790` dans `mak.env`.
   `mak confidentialite` signale alors chaque fournisseur qui ne passe pas par safeagents.
4. Vérifie la chaîne : les quatre essais doivent passer à travers safeagents.

   ```bash
   mak sonde-llm http://127.0.0.1:8790/v1 mon-modele --cle-env LLM_INTERNE_CLE
   ```

Sans modèle juge, safeagents laisse passer les constats de gravité moyenne. Il ne voit ni les
modèles servis par Copilot, ni les API Responses d'OpenAI et Gemini. La forme exacte de l'adresse
amont, avec ou sans `/v1`, n'a pas été vérifiée : la sonde le dira.

## Limites

- Les règles lisent la syntaxe, pas les types. `df.sort(...)` seul dans une cellule reçoit un
  avertissement ambigu, car c'est une liste modifiée en place ou un résultat de DataFrame perdu.
- La règle `AG203` signale un nombre écrit en dur dans un texte. Elle se trompe souvent sur des
  notebooks de cours. C'est un conseil à lire, pas une correction à appliquer partout.
- L'exécution écrit `__marimo__/session/<notebook>.json` à côté du notebook. Le dossier
  `__marimo__/` est d'ordinaire ignoré par git.
- La garde lit le texte des commandes. Une commande déguisée, par exemple un script Python qui
  installe un paquet, lui échappe. Elle ne remplace pas un bac à sable.
- Les règles `AG3xx` ne suivent pas les données d'une cellule à l'autre. `AG304` ne voit pas qu'un
  morceau de HTML a été échappé avant d'être assemblé ailleurs.
- Le kit ne lance que l'environnement pixi `default`. Pour un autre, donne la commande par
  `MAK_MARIMO`, par exemple `pixi run -e cpu marimo`.
- Le bouton de marimo installe le paquet par son nom conda. Un paquet absent de conda-forge
  s'ajoute à la main par `pixi add --pypi`.
- Huit widgets wigglystuff chargent du JavaScript depuis un CDN dans le navigateur. Le skill
  `wigglystuff` les écarte sur un réseau restreint, mais le kit ne le contrôle pas.
- Le kit vise marimo 0.25.2, wigglystuff 0.6.0, marimo-lens 0.2.4 et marimo-studio 0.4.1.
  `marimo._code_mode`, les outils de l'assistant et l'API de Studio changent d'une version à
  l'autre.
- Studio 0.4.1 n'exporte ni PPTX, ni page interactive en un seul fichier. Le skill
  `marimo-studio-vues` donne le chemin essayé pour chacun.

## Développer

```bash
uv run --no-project --python 3.13 --with marimo --with polars python -m unittest discover -s tests
uvx ruff check .
```

Le dépôt utilise [prek](https://prek.j178.dev) pour les contrôles avant commit et avant push. Le
fichier `prek.toml` ne lance que des hooks livrés dans prek, donc sans téléchargement. Ils
refusent l'en-tête PEM d'une clé privée, une clé d'API sans afficher sa valeur, et un fichier
nommé `.env`, `mak.env`, `*.pem` ou `*.key`. Le dépôt est public : le hook `depot-public` refuse
les tournures sur un cadre professionnel ou adressées à l'auteur, que liste `prek.toml`, et
`prek run depot-public --all-files` relance cette recherche. Les hooks contrôlent aussi le JSON, le
TOML, les fins de ligne et les espaces en fin de ligne, sans rien réécrire. Pose les hooks une
fois par clone :

```bash
prek install --allow-missing-config
prek run --all-files
```

L'option `--allow-missing-config` laisse passer les commits des branches qui n'ont pas encore
`prek.toml`.

Le kit est sous licence Apache-2.0. Les docs recopiées gardent leur licence. wigglystuff est sous
MIT, voir `skills/wigglystuff/references/LICENSE-wigglystuff`. marimo-lens est sous Apache-2.0,
voir `skills/marimo-lens/references/LICENSE-marimo-lens`. marimo-studio est sous Apache-2.0, voir
`skills/marimo-studio-vues/references/LICENSE-marimo-studio`. Les relevés météo de l'exemple sont
dans le domaine public, voir `exemples/meteo-seattle/public/SOURCE.md`.
