"""Recopier la documentation de wigglystuff dans le skill, lisible sans réseau.

À lancer avec un Python où la version voulue de wigglystuff est installée, en donnant une copie
du dépôt koaning/wigglystuff au commit de la version publiée (« Release 0.6.0 ») : la branche
principale peut décrire des fonctions qui ne sont pas encore publiées.

    git -C ../wigglystuff checkout 3b58e91   # « Release 0.6.0 »
    uv run --no-project --with "wigglystuff==0.6.0" python outils/importer_wigglystuff.py ../wigglystuff

Ce qui est écrit dans `skills/wigglystuff/references/` :

- `widgets/<page>.md` : chaque page de référence du site, sans les blocs HTML de démonstration ;
  la directive `::: module.Classe` est remplacée par la signature, la docstring et les traitlets
  synchronisés lus dans le paquet installé ;
- `demos/<nom>.py` : les notebooks marimo de démonstration du dépôt ;
- `catalogue.json` et `catalogue.md` : une ligne par widget, pour choisir et pour `mak widgets` ;
- `SOURCE.md` et `LICENSE-wigglystuff` : version, commit, licence MIT, écarts doc/paquet.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import inspect
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CIBLE = RACINE / "skills" / "wigglystuff" / "references"
BLOC_HTML = re.compile(r"<!-- no-md -->.*?<!-- /no-md -->\n?", re.S)
DIRECTIVE = re.compile(r"^::: ([\w.]+)\s*$", re.M)
ENTETE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)\n?")
DEMO = re.compile(r'data-demo="([^"]+)"')


def traits_de_base() -> set[str]:
    try:
        import anywidget

        return set(anywidget.AnyWidget.class_traits(sync=True))
    except ImportError:
        return set()


BASE = traits_de_base()


def bloc_api(chemin: str, ecarts: list[str], page: str, table: set[str]) -> tuple[str, dict]:
    module, _, nom = chemin.rpartition(".")
    objet = getattr(importlib.import_module(module), nom)
    infos = {"nom": nom, "module": module, "import": f"from {module.split('.')[0]} import {nom}"}
    lignes = [f"### `{nom}`", "", f"`from {module} import {nom}`", ""]
    cible = objet.__init__ if inspect.isclass(objet) else objet
    try:
        signature = str(inspect.signature(cible)).replace("(self, ", "(").replace("(self)", "()")
    except (TypeError, ValueError):
        signature = "(…)"
    infos["signature"] = f"{nom}{signature}"
    lignes += ["```python", f"{nom}{signature}", "```", ""]
    doc = inspect.getdoc(objet) or ""
    if doc:
        lignes += [doc, ""]
    traits = []
    if inspect.isclass(objet) and hasattr(objet, "class_traits"):
        for nom_trait, trait in sorted(objet.class_traits(sync=True).items()):
            if nom_trait in BASE or nom_trait.startswith("_"):
                continue
            defaut = getattr(trait, "default_value", None)
            texte = repr(defaut)
            texte = "" if "Undefined" in texte or "Sentinel" in texte else (texte if len(texte) <= 40 else texte[:37] + "…")
            traits.append({"nom": nom_trait, "type": type(trait).__name__, "defaut": texte})
        if traits:
            lignes += ["Traitlets synchronisés dans le paquet installé :", "", "| Traitlet | Type | Défaut |", "|---|---|---|"]
            lignes += [f"| `{t['nom']}` | {t['type']} | `{t['defaut']}` |" if t["defaut"] else f"| `{t['nom']}` | {t['type']} | |"
                       for t in traits]
            lignes.append("")
        reels = {t["nom"] for t in traits}
        if table:
            absents = sorted(table - reels - BASE)
            if absents:
                ecarts.append(f"{page} : {', '.join(absents)} ne sont pas des traitlets du paquet "
                              "(champs d'un dict, propriétés, ou doc en retard : vérifier avant usage)")
    infos["traitlets"] = [t["nom"] for t in traits]
    return "\n".join(lignes), infos


def traitlets_documentes(texte: str) -> set[str]:
    """Les noms de la table « Synced traitlets » d'une page."""
    section = texte.split("## Synced traitlets", 1)
    if len(section) < 2:
        return set()
    return set(re.findall(r"^\| `(\w+)` \|", section[1].split("\n## ", 1)[0], re.M))


def main(depot: Path) -> None:
    version = importlib.metadata.version("wigglystuff")
    version_depot = re.search(r'^version = "([^"]+)"', (depot / "pyproject.toml").read_text(encoding="utf-8"), re.M)
    if not version_depot or version_depot.group(1) != version:
        sys.exit(f"Le dépôt est en {version_depot and version_depot.group(1)}, le paquet installé en {version}.")
    commit = subprocess.run(["git", "-C", str(depot), "log", "-1", "--format=%h %cs"], capture_output=True, text=True).stdout.strip()
    if CIBLE.exists():
        shutil.rmtree(CIBLE)
    (CIBLE / "widgets").mkdir(parents=True)
    (CIBLE / "demos").mkdir()
    demos = {p.stem for p in (depot / "demos").glob("*.py")}
    for demo in sorted(demos):
        shutil.copy2(depot / "demos" / f"{demo}.py", CIBLE / "demos" / f"{demo}.py")
    catalogue, ecarts = [], []
    for page in sorted((depot / "docs" / "reference").glob("*.md")):
        texte = page.read_text(encoding="utf-8")
        entete = ENTETE.match(texte)
        meta = dict(re.findall(r'^(\w+): "?(.*?)"?$', entete.group(1), re.M)) if entete else {}
        demo = next(iter(DEMO.findall(texte)), None)
        corps = IMAGE.sub("", BLOC_HTML.sub("", texte[entete.end():] if entete else texte))
        table = traitlets_documentes(corps)
        directives = DIRECTIVE.findall(corps)
        for chemin in directives:
            bloc, infos = bloc_api(chemin, ecarts, page.name, table if len(directives) == 1 else set())
            corps = corps.replace(f"::: {chemin}", bloc, 1)
            infos.update(page=f"widgets/{page.name}", titre=meta.get("title", ""), resume=meta.get("description", ""),
                         demo=f"demos/{demo}.py" if demo in demos else None)
            catalogue.append(infos)
        pied = f"\n---\nDémo : [`../demos/{demo}.py`](../demos/{demo}.py)\n" if demo in demos else ""
        tete = f"<!-- wigglystuff {version}, recopié de docs/reference/{page.name} (MIT) -->\n"
        (CIBLE / "widgets" / page.name).write_text(tete + corps.lstrip() + pied, encoding="utf-8")
    (CIBLE / "catalogue.json").write_text(json.dumps({"version": version, "commit": commit, "widgets": catalogue},
                                                     ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    lignes = [f"# Catalogue wigglystuff {version}", "",
              "Généré par `outils/importer_wigglystuff.py`. Une ligne par classe ou fonction documentée ; le "
              "détail est dans la page, l'exemple dans la démo.", "",
              "| Widget | Page | Démo | Ce qu'il fait |", "|---|---|---|---|"]
    for infos in catalogue:
        demo = f"[{Path(infos['demo']).name}]({infos['demo']})" if infos["demo"] else ""
        resume = infos["resume"].replace("|", "\\|")
        lignes.append(f"| `{infos['nom']}` | [{Path(infos['page']).name}]({infos['page']}) | {demo} | {resume} |")
    (CIBLE / "catalogue.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    shutil.copy2(depot / "LICENSE", CIBLE / "LICENSE-wigglystuff")
    source = ["# Source de cette documentation", "",
              f"- wigglystuff {version} (paquet installé), dépôt koaning/wigglystuff au commit {commit}.",
              "- Pages : `docs/reference/*.md`, démos : `demos/*.py`, sous licence MIT (`LICENSE-wigglystuff`).",
              "- Signatures, docstrings et traitlets : lus dans le paquet installé, pas sur le site.",
              f"- {len(catalogue)} classes ou fonctions, {len(list((CIBLE / 'widgets').glob('*.md')))} pages, {len(demos)} démos.", "",
              "## Écarts entre la doc et le paquet", ""]
    source += [f"- {e}" for e in ecarts] or ["Aucun : chaque traitlet cité par une page existe dans le paquet."]
    (CIBLE / "SOURCE.md").write_text("\n".join(source) + "\n", encoding="utf-8")
    print(f"wigglystuff {version} ({commit}) : {len(catalogue)} entrées, {len(demos)} démos, {len(ecarts)} écart(s)")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
