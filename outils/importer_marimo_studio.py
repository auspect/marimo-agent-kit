"""Recopier la documentation de marimo Studio et une partie de ses exemples dans le skill.

    git clone --depth 1 --branch v0.4.1 https://github.com/marimo-team/marimo-studio ../marimo-studio-0.4.1
    uv run --no-project --python 3.13 --with "marimo-studio==0.4.1" python outils/importer_marimo_studio.py ../marimo-studio-0.4.1

Le mode d'emploi pour agents voyage déjà avec le paquet (`agent-plugins read marimo-studio`) : on
ne le recopie pas, on vérifie seulement que le dépôt cloné est bien celui de la version installée.
On recopie la documentation pour humains (`docs/**/*.md`, Apache-2.0), sans les images ni les
composants du site, et les sources d'exemples qui montrent le niveau visé.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CIBLE = RACINE / "skills" / "marimo-studio-vues" / "references"
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?\n?")
COMPOSANT = re.compile(r"<llm-exclude>.*?</llm-exclude>\n?", re.S)
EXEMPLES = [
    "examples/earthquakes.py",
    "examples/studio/earthquakes/briefing/DESIGN.md",
    "examples/studio/earthquakes/briefing/src/App.tsx",
    "examples/studio/earthquakes/bulletin/index.qmd",
    "examples/studio/earthquakes/operations/DESIGN.md",
    "examples/studio/earthquakes/story/DESIGN.md",
    "examples/quadratic_program.py",
    "examples/studio/quadratic_program/report/main.typ",
]


def lire(chemin: Path) -> str:
    return chemin.read_text(encoding="utf-8").replace("\r\n", "\n")


def main(depot: Path) -> None:
    version = importlib.metadata.version("marimo-studio")
    declaree = re.search(r'^version = "([^"]+)"', lire(depot / "packages" / "marimo-studio" / "pyproject.toml"), re.M)
    if not declaree or declaree.group(1) != version:
        sys.exit(f"Le dépôt est en {declaree and declaree.group(1)}, le paquet installé en {version}.")
    livre = Path(importlib.util.find_spec("marimo_studio").origin).parent.parent / f"marimo_studio-{version}.agent-plugin"
    for fichier in (livre / "skills" / "marimo-studio").rglob("*.md"):
        relatif = fichier.relative_to(livre)
        if lire(fichier) != lire(depot / relatif):
            sys.exit(f"{relatif} diffère entre le paquet installé et le dépôt : prends le tag de la version publiée.")
    commit = subprocess.run(["git", "-C", str(depot), "log", "-1", "--format=%h %cs"], capture_output=True, text=True).stdout.strip()

    for dossier in ("docs", "exemples"):
        if (CIBLE / dossier).exists():
            shutil.rmtree(CIBLE / dossier)
    pages = sorted(p for p in (depot / "docs").rglob("*.md") if "node_modules" not in p.parts and ".vitepress" not in p.parts)
    for page in pages:
        relatif = page.relative_to(depot / "docs")
        sortie = CIBLE / "docs" / relatif
        sortie.parent.mkdir(parents=True, exist_ok=True)
        texte = COMPOSANT.sub("", IMAGE.sub("", lire(page)))
        sortie.write_text(f"<!-- marimo-studio {version}, recopié de docs/{relatif.as_posix()} (Apache-2.0) -->\n{texte}",
                          encoding="utf-8", newline="\n")
    for chemin in EXEMPLES:
        sortie = CIBLE / "exemples" / Path(chemin).relative_to("examples")
        sortie.parent.mkdir(parents=True, exist_ok=True)
        sortie.write_text(lire(depot / chemin), encoding="utf-8", newline="\n")
    shutil.copy2(depot / "LICENSE", CIBLE / "LICENSE-marimo-studio")
    (CIBLE / "SOURCE.md").write_text(
        "# Source de cette documentation\n\n"
        f"- marimo-studio {version}, dépôt marimo-team/marimo-studio au commit {commit}.\n"
        f"- {len(pages)} pages de `docs/`, sans les images ni les composants du site, sous licence Apache-2.0"
        " (`LICENSE-marimo-studio`).\n"
        f"- {len(EXEMPLES)} fichiers d'exemples dans `exemples/`, recopiés tels quels depuis `examples/`.\n"
        "- Le mode d'emploi pour agents n'est pas recopié : il est dans le paquet installé "
        "(`uvx --with marimo-studio agent-plugins read marimo-studio`). Le script a vérifié qu'il est identique"
        " à celui du dépôt à ce commit.\n"
        "- Régénérer : `outils/importer_marimo_studio.py`, mode d'emploi en tête du script.\n",
        encoding="utf-8", newline="\n")
    print(f"marimo-studio {version} ({commit}) : {len(pages)} pages, {len(EXEMPLES)} exemples")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
