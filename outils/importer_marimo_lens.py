"""Recopier la documentation de marimo-lens dans le skill, lisible sans réseau.

    git clone --depth 1 --branch v0.2.4 https://github.com/marimo-team/marimo-lens ../marimo-lens-0.2.4
    uv run --no-project --with "marimo-lens==0.2.4" python outils/importer_marimo_lens.py ../marimo-lens-0.2.4

Le mode d'emploi pour agents voyage déjà avec le paquet (`agent-plugins read marimo-lens`) : on
ne le recopie pas. On recopie la documentation pour humains (`docs/**/*.md`, Apache-2.0), qui
dit à quoi sert Lens, ce qu'il expose et comment rendre une zone sélectionnable.
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
CIBLE = RACINE / "skills" / "marimo-lens" / "references"
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)\n?")


def main(depot: Path) -> None:
    version = importlib.metadata.version("marimo-lens")
    declaree = re.search(r'^version = "([^"]+)"', (depot / "packages" / "marimo-lens" / "pyproject.toml").read_text(encoding="utf-8"), re.M)
    if not declaree or declaree.group(1) != version:
        sys.exit(f"Le dépôt est en {declaree and declaree.group(1)}, le paquet installé en {version}.")
    livre = Path(importlib.util.find_spec("marimo_lens").origin).parent.parent / f"marimo_lens-{version}.agent-plugin"
    skill_livre = livre / "skills" / "marimo-lens" / "SKILL.md"
    skill_depot = depot / "skills" / "marimo-lens" / "SKILL.md"
    if skill_livre.exists() and skill_livre.read_text(encoding="utf-8") != skill_depot.read_text(encoding="utf-8"):
        sys.exit("Le skill du dépôt diffère de celui du paquet installé : prends le tag de la version publiée.")
    commit = subprocess.run(["git", "-C", str(depot), "log", "-1", "--format=%h %cs"], capture_output=True, text=True).stdout.strip()
    if CIBLE.exists():
        shutil.rmtree(CIBLE)
    pages = sorted(p for p in (depot / "docs").rglob("*.md") if "node_modules" not in p.parts)
    for page in pages:
        relatif = page.relative_to(depot / "docs")
        sortie = CIBLE / "docs" / relatif
        sortie.parent.mkdir(parents=True, exist_ok=True)
        texte = IMAGE.sub("", page.read_text(encoding="utf-8"))
        sortie.write_text(f"<!-- marimo-lens {version}, recopié de docs/{relatif} (Apache-2.0) -->\n{texte}", encoding="utf-8")
    shutil.copy2(depot / "LICENSE", CIBLE / "LICENSE-marimo-lens")
    (CIBLE / "SOURCE.md").write_text(
        "# Source de cette documentation\n\n"
        f"- marimo-lens {version}, dépôt marimo-team/marimo-lens au commit {commit}.\n"
        f"- {len(pages)} pages de `docs/`, sans les images, sous licence Apache-2.0 (`LICENSE-marimo-lens`).\n"
        "- Le mode d'emploi pour agents n'est pas recopié : il est dans le paquet installé "
        "(`uvx --with marimo-lens agent-plugins read marimo-lens`).\n", encoding="utf-8")
    print(f"marimo-lens {version} ({commit}) : {len(pages)} pages")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
