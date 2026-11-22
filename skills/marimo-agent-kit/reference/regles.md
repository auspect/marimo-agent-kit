# Règles de marimo-agent-kit

`mak regles --reference` génère ce fichier. Ne le modifie pas à la main.

Ces règles complètent `marimo check`. Elles visent ce qu'un agent écrit souvent de travers et que le
linter de marimo ne voit pas. Elles ne lisent que la syntaxe. Une règle qui se trompe sur un notebook
se désactive par `--ignorer CODE`.

| Gravité | Ce que l'agent en fait |
|---|---|
| erreur | La cellule plante ou affiche un résultat faux. Corrige avant de rendre la main. |
| avertissement | Le notebook tourne, mais la réactivité ou la lecture en souffre. Corrige, ou dis pourquoi tu ne le fais pas. |
| conseil | La lisibilité en souffre. Applique le conseil aux cellules que tu viens d'écrire. |

Les règles `AG3xx` touchent à la sécurité du poste : commande du shell, `eval`, chargement de pickle, HTML
construit à partir de données, adresse externe, identifiants du poste. Elles aident la relecture humaine et
ne bloquent rien. Avant d'en ignorer une, dis à l'utilisateur pourquoi le code en a besoin.

## AG001 `valeur-ui-meme-cellule`, erreur

Lire `.value` d'un élément d'interface dans la cellule qui le crée.

**Pourquoi.** marimo lève `RuntimeError: Accessing the value of a UIElement in the cell that created it is not allowed`.

**Correction.** Crée l'élément dans une cellule, puis lis `.value` dans une autre.

## AG002 `asyncio-run`, erreur

Appeler `asyncio.run()` ou `run_until_complete()` dans une cellule.

**Pourquoi.** Le noyau de marimo tourne déjà dans une boucle d'événements. L'appel échoue dans l'éditeur, dans une app et dans un export avec `asyncio.run() cannot be called from a running event loop`. Il passe pourtant avec `python notebook.py`.

**Correction.** Écris `resultat = await coroutine()` directement dans la cellule. marimo accepte `await` au premier niveau.

## AG003 `habitude-jupyter`, erreur

Utiliser `display()`, `get_ipython()` ou `IPython.display` dans une cellule.

**Pourquoi.** Ces noms n'existent pas dans marimo. `display(df)` lève `NameError`.

**Correction.** Mets l'objet en dernière expression de la cellule. Pour plusieurs sorties, utilise `mo.output.append(objet)`. `mo.md`, `mo.Html` et `mo.image` remplacent `IPython.display`.

## AG004 `md-sans-f`, erreur

Écrire `mo.md("... {variable} ...")` sans le préfixe `f`.

**Pourquoi.** Sans `f`, marimo affiche les accolades telles quelles. Le lecteur voit `{moyenne}` au lieu du nombre.

**Correction.** Ajoute le préfixe, par exemple `mo.md(f"... {variable} ...")`. Avec des antislashs LaTeX, écris `rf"..."`.

## AG005 `secret-en-clair`, erreur

Écrire une clé d'API, un jeton ou un mot de passe dans le code.

**Pourquoi.** Le code d'un notebook voyage avec lui, dans git, dans un export HTML ou WASM et dans le contexte envoyé à l'assistant.

**Correction.** Lis la valeur dans l'environnement par `os.environ["NOM"]`, ou demande-la par `mo.ui.text(kind="password")`.

## AG006 `code-mode-dans-cellule`, erreur

Importer `marimo._code_mode` dans une cellule.

**Pourquoi.** C'est une API privée, réservée au bloc-notes temporaire de marimo pair. Elle change sans préavis.

**Correction.** Garde `import marimo._code_mode as cm` dans `marimo pair execute`, jamais dans le notebook.

## AG007 `nom-indefini`, erreur

Lire un nom qu'aucune cellule ne définit, ou un nom privé comme `_x` défini dans une autre cellule.

**Pourquoi.** La cellule lèvera `NameError`. Un nom qui commence par `_` reste local à sa cellule.

**Correction.** Définis le nom dans une cellule, corrige la faute de frappe, ou retire le `_` du nom partagé.

## AG008 `corps-au-format-fichier`, erreur, seulement en mode corps

Envoyer à code mode un corps de cellule qui contient `return`, `@app.cell` ou `app = marimo.App`.

**Pourquoi.** `create_cell` et `edit_cell` prennent le contenu de la cellule, pas l'enveloppe du fichier.

**Correction.** Envoie seulement les instructions de la cellule. marimo calcule ses entrées et ses sorties.

## AG009 `nom-redefini`, erreur, seulement en mode corps

Définir un même nom public dans deux cellules.

**Pourquoi.** marimo refuse le notebook avec `Multiply-defined names`. En code mode, il rejette tout le lot de modifications.

**Correction.** Modifie la cellule propriétaire, ou donne un nouveau nom au résultat, par exemple `propre = df.dropna()`.

## AG101 `mutation-inter-cellules`, avertissement

Modifier en place un objet défini dans une autre cellule, par exemple par `df["c"] = ...`, `liste.append` ou `inplace=True`.

**Pourquoi.** marimo suit les noms, pas les mutations. Les cellules qui lisent l'objet ne repartent pas. Relancer cette cellule applique la mutation une seconde fois.

**Correction.** Crée un nouvel objet, par exemple `df2 = df.assign(c=...)`, `df.with_columns(...)` ou `liste2 = [*liste, x]`. Sinon, fais la modification dans la cellule qui définit l'objet.

## AG102 `ui-non-liee`, avertissement

Créer un élément d'interface sans l'affecter à un nom public, par exemple dans une liste, dans `mo.hstack` ou sous un nom `_nom`.

**Pourquoi.** marimo ne relance les cellules qu'à partir d'un élément lié à une variable globale. Toucher ce curseur ne fera rien, et sa valeur n'est lisible nulle part.

**Correction.** Affecte l'élément à un nom public dans sa propre instruction, par exemple `seuil = mo.ui.slider(...)`. Pour une liste ou un dictionnaire d'éléments, utilise `mo.ui.array([...])` ou `mo.ui.dictionary({...})`.

## AG103 `bouton-sans-action`, avertissement

Lire `.value` d'un `mo.ui.button` créé sans `on_click`.

**Pourquoi.** La valeur d'un `mo.ui.button` sans `on_click` reste `None`, donc `if bouton.value:` n'est jamais vrai.

**Correction.** Pour lancer un calcul, crée `lancer = mo.ui.run_button(label="...")`, puis écris `mo.stop(not lancer.value)` dans la cellule du calcul. Pour compter des clics, passe `on_click=lambda n: n + 1, value=0`.

## AG104 `garde-if-valeur`, avertissement

Écrire un `if element.value:` qui définit sans `else` un nom que d'autres cellules lisent.

**Pourquoi.** Quand la condition est fausse, le nom n'existe pas. Les cellules qui le lisent affichent alors `Name ... is not defined` au lieu d'attendre.

**Correction.** Écris en tête de cellule `mo.stop(not lancer.value, mo.md("Clique sur **Lancer** pour calculer."))`, puis le calcul sans `if`.

## AG105 `sortie-perdue`, avertissement

Écrire une expression d'affichage, comme `mo.md(...)`, `df` ou `df.head()`, ailleurs qu'en dernière position dans la cellule.

**Pourquoi.** marimo n'affiche que la dernière expression. Celle-ci ne sera jamais vue.

**Correction.** Mets-la en dernier, regroupe plusieurs sorties avec `mo.vstack([...])`, ou utilise `mo.output.append(...)`.

## AG106 `boucle-bloquante`, avertissement

Écrire une boucle `while True` avec `sleep` dans une cellule.

**Pourquoi.** La boucle bloque le noyau. Plus aucune cellule ni aucun élément d'interface ne répond.

**Correction.** Lis un `mo.ui.refresh(default_interval="5s")` dans une cellule, ou lance le travail dans un `mo.Thread`.

## AG107 `global`, avertissement

Utiliser l'instruction `global` dans une cellule.

**Pourquoi.** Les variables d'une cellule sont déjà globales pour marimo. `global` contourne le graphe et cache une dépendance.

**Correction.** Retourne la nouvelle valeur sous un nouveau nom, ou modifie la cellule qui définit la variable.

## AG108 `travail-lourd-sur-ui`, avertissement

Lancer un calcul lourd, comme `fit`, `pm.sample` ou une requête réseau, dans une cellule qui lit un curseur ou un champ.

**Pourquoi.** Chaque mouvement du curseur relance tout le calcul. L'interface rame et l'utilisateur attend.

**Correction.** Place le calcul lourd en amont, ou déclenche-le par un `mo.ui.run_button` avec `mo.stop`, ou par un formulaire comme `mo.ui.slider(...).form()`. `@mo.cache` évite de refaire un calcul déjà fait.

## AG111 `dependance-non-declaree`, avertissement, seulement en mode fichier

Importer un module qui manque à l'en-tête PEP 723 du notebook.

**Pourquoi.** `marimo edit --sandbox` et `uv run notebook.py` n'installent que l'en-tête. L'import échouera chez toute personne qui ouvre le notebook.

**Correction.** Ajoute le paquet à `dependencies` dans l'en-tête `# /// script`. Dans une session marimo pair, utilise `ctx.packages.add("paquet")`.

## AG301 `commande-shell`, avertissement

Lancer une commande du système depuis une cellule : `subprocess`, `os.system`, `os.popen`.

**Pourquoi.** La commande tourne avec les droits de la personne qui ouvre le notebook. Avec `shell=True` ou un texte assemblé, une valeur venue de données peut ajouter une commande.

**Correction.** Fais-le en Python quand une bibliothèque existe. Sinon, passe une liste d'arguments sans `shell=True`, et dis à l'utilisateur pourquoi la commande est nécessaire.

## AG302 `eval-exec`, avertissement

Appeler `eval` ou `exec` sur un texte qui n'est pas écrit dans le code.

**Pourquoi.** Le texte s'exécute comme du code. S'il vient d'un fichier, d'une page, d'un modèle ou d'un contrôle, il peut faire n'importe quoi sur le poste.

**Correction.** Lis la donnée avec un analyseur, par exemple `json.loads` ou `ast.literal_eval`.

## AG303 `chargement-non-sur`, avertissement

Charger un fichier par `pickle`, `joblib`, `pandas.read_pickle`, `torch.load` sans `weights_only=True`, `numpy.load(allow_pickle=True)` ou `yaml.load` sans chargeur sûr.

**Pourquoi.** Ces formats peuvent contenir du code, qui s'exécute au chargement. Un fichier reçu ou téléchargé suffit.

**Correction.** Préfère Parquet, CSV, JSON ou safetensors. Pour un fichier que tu n'as pas produit, demande d'abord à l'utilisateur.

## AG304 `html-interpole`, avertissement

Construire `mo.Html` ou `mo.iframe` en y insérant des valeurs calculées sans les échapper.

**Pourquoi.** Le HTML s'affiche dans l'éditeur, qui peut lancer du code. Une valeur venue d'un fichier, d'une page ou d'une API peut y glisser un script.

**Correction.** Échappe chaque valeur par `html.escape(...)`, ou affiche les données par `mo.ui.table`, `mo.md` ou un graphique.

## AG305 `adresse-externe`, avertissement

Lire depuis une adresse écrite en dur dont l'hôte n'est pas local.

**Pourquoi.** La cellule sort de la machine à chaque exécution : elle échoue hors ligne ou sur un réseau restreint, et ses données changent sans prévenir.

**Correction.** Télécharge le fichier une fois, par un moyen que l'utilisateur valide, puis lis la copie locale. Si l'adresse est voulue, passe `--ignorer AG305` et dis pourquoi.

## AG306 `identifiants-du-poste`, avertissement

Lire un fichier d'identifiants du poste (`~/.ssh`, `.netrc`, `.aws/credentials`…) ou afficher tout `os.environ`.

**Pourquoi.** La sortie d'une cellule part dans le notebook, ses exports et le contexte de l'assistant. Les variables d'environnement contiennent souvent des jetons.

**Correction.** Lis seulement la variable utile, par `os.environ["NOM"]`, et n'affiche pas sa valeur.

## AG109 `except-large`, conseil

Écrire `except Exception:` ou `except:` qui avale l'erreur.

**Pourquoi.** marimo affiche une erreur sous la cellule et arrête les cellules qui en dépendent. Une erreur avalée donne un résultat faux sans aucun signe.

**Correction.** Laisse l'erreur remonter, ou n'attrape que l'exception attendue, par exemple `except FileNotFoundError:`.

## AG110 `arguments-de-ligne`, conseil

Utiliser `sys.argv` ou `argparse` dans un notebook.

**Pourquoi.** Dans l'éditeur, `sys.argv` contient les arguments de marimo, pas ceux du notebook.

**Correction.** Lis les arguments avec `mo.cli_args()`, puis lance `python notebook.py -- --n 10`.

## AG201 `plt-show`, conseil

Afficher une figure matplotlib par `plt.show()`.

**Pourquoi.** Dans marimo, la figure doit être la sortie de la cellule pour apparaître dans une app et dans un export.

**Correction.** Termine la cellule par `plt.gca()` ou par la figure, par exemple `fig`.

## AG202 `print-comme-sortie`, conseil

Montrer le résultat d'une cellule seulement par `print(f"...")`.

**Pourquoi.** `print` écrit dans la console, sous la cellule. La sortie de la cellule, celle qu'une app montre, reste vide.

**Correction.** Termine par `mo.md(f"...")` pour un texte, ou par l'objet lui-même.

## AG203 `valeur-recopiee`, conseil

Écrire en dur un nombre décimal ou un pourcentage dans un texte `mo.md` sans interpolation.

**Pourquoi.** Si ce nombre vient d'un calcul, le texte sera faux dès que les données changent.

**Correction.** Interpole la valeur, par exemple `mo.md(f"La moyenne vaut {moyenne:.2f}")`.

## AG204 `trop-de-prives`, conseil

Définir cinq noms privés `_x` ou plus dans une même cellule.

**Pourquoi.** Beaucoup de `_` cachent une étape utile ou une cellule qui fait trop de choses. Les agents en abusent pour contourner la règle d'un seul propriétaire par nom.

**Correction.** Donne un nom public aux résultats utiles, ou range le calcul dans une fonction.

## AG205 `sans-entete-pep723`, conseil, seulement en mode fichier

Omettre l'en-tête PEP 723 `# /// script` en tête du notebook.

**Pourquoi.** Sans lui, `uvx marimo edit --sandbox notebook.py` ne sait pas quoi installer.

**Correction.** Ajoute l'en-tête avec `requires-python` et `dependencies`, marimo compris. `marimo edit --sandbox` le tient à jour ensuite.

## AG206 `imports-disperses`, conseil

Répartir les imports dans trois cellules ou plus.

**Pourquoi.** Le lecteur cherche d'où vient un nom. Deux cellules qui importent le même module sous le même nom font échouer le notebook.

**Correction.** Regroupe les imports dans la cellule setup, `with app.setup:`, que marimo exécute avant toutes les autres. N'y mets que des imports.

## AG207 `cellule-longue`, conseil

Écrire une cellule de plus de 60 lignes de code, sans compter les longues chaînes.

**Pourquoi.** Une cellule est une frontière de recalcul. Une longue cellule refait tout pour le moindre changement, et se lit mal.

**Correction.** Place en amont le calcul coûteux et réutilisable, et en aval la présentation.

## AG208 `chemin-absolu`, conseil

Écrire un chemin absolu propre à une machine, comme `/home/...`, `C:\...` ou `/tmp/...`.

**Pourquoi.** Le notebook ne tournera pas ailleurs, ni dans un bac à sable, ni chez un collègue.

**Correction.** Pars du dossier du notebook, par exemple `mo.notebook_dir() / "donnees" / "fichier.csv"`.

## AG209 `mo-state-sans-rappel`, conseil

Utiliser `mo.state` sans aucun `on_change` dans le notebook.

**Pourquoi.** Le plus souvent, des variables et des éléments d'interface suffisent. `mo.state` ajoute des mises à jour difficiles à suivre.

**Correction.** Garde une variable ordinaire et un élément d'interface. Réserve `mo.state` aux rappels `on_change` ou à un état accumulé.

## AG210 `ui-sans-etiquette`, conseil

Créer un curseur, un champ ou un bouton sans `label`.

**Pourquoi.** Le lecteur voit un curseur sans savoir ce qu'il règle.

**Correction.** Ajoute `label="..."`, qui accepte le Markdown. Sinon, compose le texte avec `mo.md("... {x}").batch(x=...)`.
