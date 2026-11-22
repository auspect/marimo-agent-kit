# Seattle sous la pluie : un notebook, quatre vues Studio

Exemple de référence du skill `marimo-studio-vues`. Le notebook `meteo.py` analyse quatre années
de relevés quotidiens à Seattle. Quatre vues marimo Studio 0.4.1 en tirent quatre restitutions :

| Vue | Format | Public |
|---|---|---|
| `grand-public` | Page React | Un lecteur curieux, sur ordinateur ou téléphone |
| `briefing` | Diaporama reveal.js | Une réunion de dix minutes |
| `rapport` | PDF Typst | Un lecteur technique qui vérifie les chiffres |
| `article` | Article Quarto | Le lecteur d'un magazine en ligne |

Chaque vue a son `DESIGN.md`. Les données sont dans `public/`, leur source dans
`public/SOURCE.md`.

## Commandes

```bash
pixi install
pixi run marimo-studio starters --target meteo.py
mak marimo edit meteo.py --watch --no-token --headless --port 2791
```

Ouvre ensuite `http://localhost:2791/` dans un navigateur. Pour construire et vérifier sans
l'éditeur :

```bash
pixi run marimo-studio view build grand-public --target meteo.py
pixi run marimo-studio validate --target meteo.py --level static
```

Pour exporter, vers un dossier court sous Windows :

```bash
pixi run marimo-studio view export grand-public --target meteo.py --output "$HOME/.mxo/grand-public" --prepare-timeout 300 --force
pixi run python diapos_pptx.py
```

Le `pyproject.toml` est un projet pixi. Il installe Python 3.13, Quarto et Typst depuis
conda-forge, et marimo-studio avec ses extras `deno` et `typst` depuis PyPI. Il dit aussi à
marimo d'installer un paquet manquant par pixi, et porte la configuration de Studio : le notebook
n'a pas d'en-tête PEP 723. Sous Windows, il pose deux variables qui contournent la limite de 260
caractères des chemins. Le skill explique pourquoi, dans
`skills/marimo-studio-vues/references/environnement.md`.
