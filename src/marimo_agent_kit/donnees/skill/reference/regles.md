# Règles de marimo-agent-kit

Fichier généré par `mak regles --reference` : ne pas le modifier à la main.

Ces règles complètent `marimo check` : elles visent ce qu'un agent écrit souvent de travers et que le
linter de marimo ne voit pas. Elles ne lisent que la syntaxe ; une règle qui se trompe sur un notebook
se désactive par `--ignorer CODE`.

| Gravité | Ce que l'agent en fait |
|---|---|
| erreur | La cellule plante ou affiche un résultat faux : corriger avant de rendre la main. |
| avertissement | Le notebook tourne mais la réactivité ou la lecture en souffre : corriger, ou dire pourquoi pas. |
| conseil | Lisibilité : appliquer aux cellules que l'on vient d'écrire. |

## AG001 `valeur-ui-meme-cellule` — erreur

Lire `.value` d'un élément d'interface dans la cellule qui le crée.

**Pourquoi.** marimo lève `RuntimeError: Accessing the value of a UIElement in the cell that created it is not allowed`.

**Correction.** Crée l'élément dans une cellule, lis `.value` dans une autre.

## AG002 `asyncio-run` — erreur

Appeler `asyncio.run()` ou `run_until_complete()` dans une cellule.

**Pourquoi.** Le noyau de marimo tourne déjà dans une boucle d'événements : l'appel échoue dans l'éditeur, une app et un export (`asyncio.run() cannot be called from a running event loop`), alors qu'il passe avec `python notebook.py`.

**Correction.** Écris `resultat = await coroutine()` directement dans la cellule : marimo accepte `await` au premier niveau.

## AG003 `habitude-jupyter` — erreur

`display()`, `get_ipython()` ou `IPython.display` dans une cellule.

**Pourquoi.** Ces noms n'existent pas dans marimo : `display(df)` lève `NameError`.

**Correction.** Mets l'objet en dernière expression de la cellule, ou `mo.output.append(objet)` pour plusieurs sorties ; `mo.md`, `mo.Html`, `mo.image` remplacent `IPython.display`.

## AG004 `md-sans-f` — erreur

`mo.md("… {variable} …")` sans le préfixe `f`.

**Pourquoi.** Sans `f`, marimo affiche les accolades telles quelles : le lecteur voit `{moyenne}` au lieu du nombre.

**Correction.** Ajoute le préfixe : `mo.md(f"… {variable} …")` (et `rf"…"` s'il y a des antislashs LaTeX).

## AG005 `secret-en-clair` — erreur

Une clé d'API, un jeton ou un mot de passe écrit dans le code.

**Pourquoi.** Le code d'un notebook part avec lui : dans git, dans un export HTML ou WASM, dans le contexte envoyé à l'assistant d'IA.

**Correction.** Lis-le dans l'environnement (`os.environ["NOM"]`), ou demande-le par `mo.ui.text(kind="password")`.

## AG006 `code-mode-dans-cellule` — erreur

Importer `marimo._code_mode` dans une cellule.

**Pourquoi.** C'est une API privée réservée au bloc-notes temporaire de marimo pair ; elle change sans préavis.

**Correction.** Garde `import marimo._code_mode as cm` dans `marimo pair execute`, jamais dans le notebook.

## AG007 `nom-indefini` — erreur

Lire un nom qu'aucune cellule ne définit, ou un nom privé (`_x`) défini dans une autre cellule.

**Pourquoi.** La cellule lèvera `NameError`. Un nom qui commence par `_` reste local à sa cellule.

**Correction.** Définis le nom dans une cellule, corrige la faute de frappe, ou retire le `_` du nom partagé.

## AG008 `corps-au-format-fichier` — erreur *(seulement en mode corps)*

Un corps de cellule envoyé à code mode contient `return`, `@app.cell` ou `app = marimo.App`.

**Pourquoi.** `create_cell` et `edit_cell` prennent le contenu de la cellule, pas l'enveloppe du fichier.

**Correction.** Envoie seulement les instructions de la cellule ; marimo calcule les entrées et les sorties.

## AG009 `nom-redefini` — erreur *(seulement en mode corps)*

Un nom public défini par deux cellules.

**Pourquoi.** marimo refuse le notebook (`Multiply-defined names`) ; en code mode, tout le lot de modifications est rejeté.

**Correction.** Modifie la cellule propriétaire, ou donne un nouveau nom au résultat (`propre = df.dropna()`).

## AG101 `mutation-inter-cellules` — avertissement

Modifier en place un objet défini dans une autre cellule (`df["c"] = …`, `liste.append`, `inplace=True`).

**Pourquoi.** marimo suit les noms, pas les mutations : les cellules qui lisent l'objet ne sont pas relancées, et relancer cette cellule applique la mutation une seconde fois.

**Correction.** Crée un nouvel objet (`df2 = df.assign(c=…)`, `df.with_columns(…)`, `liste2 = [*liste, x]`) ou fais la modification dans la cellule qui définit l'objet.

## AG102 `ui-non-liee` — avertissement

Un élément d'interface qui n'est pas affecté à un nom public (dans une liste, dans `mo.hstack`, ou `_nom`).

**Pourquoi.** marimo ne relance les cellules qu'à partir d'un élément lié à une variable globale : toucher ce curseur ne fera rien, et sa valeur n'est lisible nulle part.

**Correction.** Affecte-le à un nom public (`seuil = mo.ui.slider(…)`) dans sa propre instruction ; pour une liste ou un dictionnaire d'éléments, utilise `mo.ui.array([...])` ou `mo.ui.dictionary({...})`.

## AG103 `bouton-sans-action` — avertissement

Lire `.value` d'un `mo.ui.button` créé sans `on_click`.

**Pourquoi.** La valeur d'un `mo.ui.button` sans `on_click` reste `None` : `if bouton.value:` n'est jamais vrai.

**Correction.** Pour lancer un calcul : `lancer = mo.ui.run_button(label="…")`, puis `mo.stop(not lancer.value)` dans la cellule du calcul. Pour compter des clics : `on_click=lambda n: n + 1, value=0`.

## AG104 `garde-if-valeur` — avertissement

Un `if element.value:` qui définit un nom lu par d'autres cellules, sans `else`.

**Pourquoi.** Quand la condition est fausse, le nom n'existe pas : les cellules qui le lisent affichent une erreur (`Name … is not defined`) au lieu d'attendre.

**Correction.** En tête de cellule : `mo.stop(not lancer.value, mo.md("Clique sur **Lancer** pour calculer."))`, puis le calcul sans `if`.

## AG105 `sortie-perdue` — avertissement

Une expression d'affichage (`mo.md(…)`, `df`, `df.head()`) qui n'est pas la dernière de la cellule.

**Pourquoi.** marimo n'affiche que la dernière expression : celle-ci ne sera jamais vue.

**Correction.** Mets-la en dernier, regroupe plusieurs sorties avec `mo.vstack([...])`, ou utilise `mo.output.append(…)`.

## AG106 `boucle-bloquante` — avertissement

Une boucle `while True` avec `sleep` dans une cellule.

**Pourquoi.** Elle bloque le noyau : plus aucune cellule ni aucun élément d'interface ne répond.

**Correction.** Rafraîchis avec `mo.ui.refresh(default_interval="5s")` lu dans une cellule, ou lance le travail dans `mo.Thread`.

## AG107 `global` — avertissement

L'instruction `global` dans une cellule.

**Pourquoi.** Les variables d'une cellule sont déjà globales pour marimo ; `global` contourne le graphe et cache une dépendance.

**Correction.** Retourne la nouvelle valeur sous un nouveau nom, ou passe par la cellule qui définit la variable.

## AG108 `travail-lourd-sur-ui` — avertissement

Un calcul lourd (`fit`, `pm.sample`, requête réseau) dans une cellule qui lit un curseur ou un champ.

**Pourquoi.** Chaque mouvement du curseur relance tout le calcul : l'interface rame et l'utilisateur attend.

**Correction.** Sépare le calcul lourd en amont, ou déclenche-le par `mo.ui.run_button` (avec `mo.stop`) ou un formulaire (`mo.ui.slider(…).form()`) ; `@mo.cache` évite de refaire un calcul déjà fait.

## AG111 `dependance-non-declaree` — avertissement *(seulement en mode fichier)*

Un module importé qui manque à l'en-tête PEP 723 du notebook.

**Pourquoi.** `marimo edit --sandbox` et `uv run notebook.py` installent l'en-tête, pas plus : l'import échouera chez quiconque ouvre le notebook.

**Correction.** Ajoute le paquet à `dependencies` dans l'en-tête `# /// script`, ou, dans une session marimo pair, `ctx.packages.add("paquet")`.

## AG109 `except-large` — conseil

`except Exception:` ou `except:` qui avale l'erreur.

**Pourquoi.** marimo affiche une erreur proprement sous la cellule et arrête les cellules qui en dépendent ; une erreur avalée donne un résultat faux sans signe.

**Correction.** Laisse l'erreur remonter, ou n'attrape que l'exception attendue (`except FileNotFoundError:`).

## AG110 `arguments-de-ligne` — conseil

`sys.argv` ou `argparse` dans un notebook.

**Pourquoi.** Dans l'éditeur, `sys.argv` contient les arguments de marimo, pas ceux du notebook.

**Correction.** Lis les arguments avec `mo.cli_args()` (`python notebook.py -- --n 10`).

## AG201 `plt-show` — conseil

`plt.show()` pour afficher une figure matplotlib.

**Pourquoi.** Dans marimo, la figure doit être la sortie de la cellule pour apparaître dans une app et dans un export.

**Correction.** Termine la cellule par `plt.gca()` ou par la figure (`fig`).

## AG202 `print-comme-sortie` — conseil

Une cellule qui ne montre son résultat que par `print(f"…")`.

**Pourquoi.** `print` écrit dans la console, sous la cellule ; la sortie de la cellule, celle que montre une app, reste vide.

**Correction.** Termine par `mo.md(f"…")` pour un texte, ou par l'objet lui-même.

## AG203 `valeur-recopiee` — conseil

Un nombre décimal ou un pourcentage écrit en dur dans un texte `mo.md` sans interpolation.

**Pourquoi.** Si ce nombre vient d'un calcul, le texte mentira dès que les données changent.

**Correction.** Interpole la valeur : `mo.md(f"La moyenne vaut {moyenne:.2f}")`.

## AG204 `trop-de-prives` — conseil

Cinq noms privés (`_x`) ou plus dans une même cellule.

**Pourquoi.** Beaucoup de `_` cachent une étape utile ou une cellule qui fait trop de choses ; les agents en abusent pour contourner la règle d'un seul propriétaire par nom.

**Correction.** Donne un nom public aux résultats utiles, ou range le calcul dans une fonction.

## AG205 `sans-entete-pep723` — conseil *(seulement en mode fichier)*

Pas d'en-tête PEP 723 (`# /// script`) en tête du notebook.

**Pourquoi.** Sans lui, `uvx marimo edit --sandbox notebook.py` ne sait pas quoi installer.

**Correction.** Ajoute l'en-tête avec `requires-python` et `dependencies` (marimo compris) ; `marimo edit --sandbox` le tient à jour ensuite.

## AG206 `imports-disperses` — conseil

Des imports répartis dans trois cellules ou plus.

**Pourquoi.** Le lecteur cherche d'où vient un nom ; deux cellules qui importent le même module sous le même nom font échouer le notebook.

**Correction.** Regroupe les imports dans la première cellule, ou dans `with app.setup:` (cellule `setup`, sans dépendance).

## AG207 `cellule-longue` — conseil

Une cellule de plus de 60 lignes de code (chaînes longues non comptées).

**Pourquoi.** Une cellule est une frontière de recalcul : une longue cellule refait tout pour le moindre changement, et se lit mal.

**Correction.** Coupe en amont le calcul coûteux et réutilisable, en aval la présentation.

## AG208 `chemin-absolu` — conseil

Un chemin absolu propre à une machine (`/home/…`, `C:\…`, `/tmp/…`).

**Pourquoi.** Le notebook ne tournera pas ailleurs, ni dans un bac à sable, ni chez un collègue.

**Correction.** Pars du dossier du notebook : `mo.notebook_dir() / "donnees" / "fichier.csv"`.

## AG209 `mo-state-sans-rappel` — conseil

`mo.state` sans aucun `on_change` dans le notebook.

**Pourquoi.** Pour 99 % des cas, les variables et les éléments d'interface suffisent ; `mo.state` ajoute des mises à jour difficiles à suivre.

**Correction.** Garde une variable ordinaire et un élément d'interface ; réserve `mo.state` aux rappels `on_change` ou à un état accumulé.

## AG210 `ui-sans-etiquette` — conseil

Un curseur, un champ ou un bouton sans `label`.

**Pourquoi.** Le lecteur voit un curseur sans savoir ce qu'il règle.

**Correction.** Ajoute `label="…"` (le Markdown est permis), ou compose le texte avec `mo.md("… {x}").batch(x=…)`.
