# Environnement : pixi, Quarto et Typst depuis conda-forge

Essayé sous Windows 11 avec pixi 0.84.2, le 22 novembre 2026. Le `pixi.toml` de
`exemples/meteo-seattle/` est la référence.

## Le projet pixi

```toml
[workspace]
channels = ["conda-forge"]
platforms = ["win-64", "linux-64", "osx-arm64"]

[dependencies]
python = "3.13.*"
quarto = ">=1.9.38"
typst = ">=0.15"

[pypi-dependencies]
marimo-studio = { version = "==0.4.1", extras = ["deno", "typst"] }
polars = ">=1.33"
altair = ">=5.5"
vl-convert-python = ">=1.8"

[target.win-64.activation.env]
MARIMO_STUDIO_STATE_DIR = '%USERPROFILE%\.mss'
MARIMO_EXPORT_REPOSITORY = '\\?\%USERPROFILE%\.mxr'
```

```bash
pixi install
pixi run quarto --version
pixi run typst --version
pixi run marimo-studio starters --target notebook.py
```

Ce que donne ce canal sous Windows :

| Outil | Source | Version obtenue | Résultat |
|---|---|---|---|
| Python | conda-forge | 3.13.18 | Marche. Garde 3.13 : des règles du kit ne se déclenchent pas en 3.14. |
| Quarto | conda-forge | 1.11.9 | Marche par `pixi run` : Studio le trouve et rend la vue Quarto. Le paquet tire aussi Deno 2.9.8 de conda-forge. |
| Typst (CLI) | conda-forge | 0.15.1 | Marche : `typst compile main.typ` compose le document avec les valeurs par défaut. Studio, lui, n'utilise pas ce binaire. |
| Typst (Studio) | PyPI, extra `typst` | 0.15.2 | Marche : c'est le compilateur que Studio appelle. |
| Deno (React, reveal.js) | PyPI, extra `deno` | 2.9.8 | Marche. Il cohabite avec le Deno de Quarto, de même version ici. La documentation de Studio prévient qu'une version différente remplacerait celui de Quarto ; dans ce cas, installe Quarto à part. |
| Tectonic (LaTeX) | non installé | — | Le starter LaTeX reste `unavailable`. `pixi add tectonic` le fournirait ; non essayé ici. |

Lance tout par `pixi run` : Quarto de conda-forge trouve Pandoc par l'activation de
l'environnement, et Studio le déclare indisponible sans elle.

Studio voit le `pixi.toml` : il exécute ses commandes dans l'environnement pixi et affiche les
commandes de lancement sous la forme `pixi run --manifest-path ... -x marimo edit ... --no-sandbox`.
Il ajoute tout de même un en-tête PEP 723 au notebook, avec `marimo-studio` et la section
`[tool.marimo-studio]`.

## Windows sans chemins longs

Par défaut, Windows limite un chemin à 260 caractères (`LongPathsEnabled` vaut 0). Studio écrit
son état de construction et ses exports dans des dossiers profonds, nommés par des empreintes de
32 à 64 caractères. Sans réglage, dans un projet un peu profond :

| Étape | Message obtenu |
|---|---|
| Construction React | `React provider could not normalize browser output: [WinError 3] Le chemin d’accès spécifié est introuvable` |
| Construction Quarto | `FileNotFoundError: [WinError 206] Nom de fichier ou extension trop long` puis `unable to open database file` |
| Export Prepared | `Could not prepare notebook states for the Prepared runtime: [WinError 3] ...\marimo-export\repository\prepared-states\...` |
| Export dans un dossier profond | `prepared export materialization failed: [Errno 2] No such file or directory: ...\dist\.rapport.staging-...` |
| `view preflight` | même erreur, dans `%TEMP%\marimo-studio-preflight-...` |

Ce qui marche, sans toucher au registre :

1. `MARIMO_STUDIO_STATE_DIR` vers un dossier court, par exemple `%USERPROFILE%\.mss`. Un dossier
   sous `%TEMP%` est encore trop long pour Quarto.
2. `MARIMO_EXPORT_REPOSITORY` avec le préfixe de chemin étendu `\\?\`, par exemple
   `\\?\%USERPROFILE%\.mxr`. Sans ce préfixe, même un dossier court dépasse la limite : les
   états préparés s'emboîtent sur quatre niveaux d'empreintes de 64 caractères.
3. `--output` d'un export vers un dossier court, par exemple `$HOME/.mxo/grand-public`.
   Le préfixe `\\?\` n'est pas accepté par `--output`.
4. Pas de `view preflight` : `view export` fait le même contrôle avant d'écrire le dossier.

Les deux variables vont dans `[target.win-64.activation.env]` de `pixi.toml` : pixi les pose à
chaque `pixi run`, et seulement sous Windows. Autre solution, qui demande les droits
d'administration : activer les chemins longs de Windows.

## Encodage de la console

Sous Windows, un `print` de texte accentué ou d'un tableau polars vers la console peut lever
`UnicodeEncodeError: 'charmap' codec`. Pose `PYTHONIOENCODING=utf-8` dans le shell qui lance la
commande, pas dans le notebook.

## Lancer le notebook

```bash
pixi run marimo edit notebook.py --no-sandbox --watch --no-token --headless --port 2791
```

`--no-token` rend la session visible de `marimo pair notebook list`. `--headless` n'ouvre pas de
navigateur : ouvre `http://localhost:2791/` toi-même, sinon aucune session n'existe. L'éditeur
affiche alors l'onglet Studio et la vue par défaut à côté du notebook.
