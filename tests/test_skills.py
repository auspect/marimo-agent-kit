"""Les skills (en-tête, liens internes), les manifestes de greffon, et la doc hors ligne de wigglystuff.

    python -m unittest discover -s marimo-agent-kit/tests
"""

import json
import re
import sys
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
sys.path.insert(0, str(RACINE / "src"))

from marimo_agent_kit.ressources import SKILLS, dossier_skill  # noqa: E402
from marimo_agent_kit.widgets import catalogue, chercher, en_texte, proches, trouver  # noqa: E402

LIEN = re.compile(r"\]\((?!https?://|#)([^)#\s]+)")


class Skills(unittest.TestCase):
    def test_en_tete_et_taille(self):
        for nom in SKILLS:
            with self.subTest(skill=nom):
                texte = (dossier_skill(nom) / "SKILL.md").read_text(encoding="utf-8")
                entete = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", texte)
                self.assertIsNotNone(entete, "en-tête name/description manquant")
                self.assertEqual(entete.group(1), nom)
                self.assertLessEqual(len(entete.group(2)), 1024, "description trop longue pour les agents")
                self.assertLess(len(texte.splitlines()), 200, "un SKILL.md se lit d'un coup : le détail va dans references/")

    def test_les_chemins_cites_existent(self):
        for nom in SKILLS:
            racine = dossier_skill(nom)
            texte = (racine / "SKILL.md").read_text(encoding="utf-8")
            for chemin in re.findall(r"`(references?/[\w./-]+\.(?:md|json|py))`", texte):
                with self.subTest(skill=nom, chemin=chemin):
                    self.assertTrue((racine / chemin).exists() or (racine / "references" / "docs" / Path(chemin).name).exists(), chemin)

    def test_liens_des_pages_wigglystuff(self):
        widgets = dossier_skill("wigglystuff") / "references" / "widgets"
        casses = []
        for page in widgets.glob("*.md"):
            for cible in LIEN.findall(page.read_text(encoding="utf-8")):
                if cible.endswith((".md", ".py")) and not (page.parent / cible).resolve().exists():
                    casses.append(f"{page.name} → {cible}")
        self.assertLessEqual(len(casses), 5, casses)

    def test_manifestes_de_greffon(self):
        claude = json.loads((RACINE / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(claude["plugins"][0]["skills"], ["./skills"])
        codex = json.loads((RACINE / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        version = re.search(r'^version = "([^"]+)"', (RACINE / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1)
        self.assertEqual(codex["version"], version)
        self.assertEqual(claude["metadata"]["version"], version)


class DocWigglystuff(unittest.TestCase):
    def test_catalogue_et_pages(self):
        cat = catalogue()
        self.assertEqual(cat["version"], "0.6.0")
        self.assertGreater(len(cat["widgets"]), 60)
        for entree in cat["widgets"]:
            with self.subTest(widget=entree["nom"]):
                self.assertTrue((dossier_skill("wigglystuff") / "references" / entree["page"]).exists())
                if entree["demo"]:
                    self.assertTrue((dossier_skill("wigglystuff") / "references" / entree["demo"]).exists())

    def test_les_widgets_du_guide_existent(self):
        guide = (dossier_skill("wigglystuff") / "SKILL.md").read_text(encoding="utf-8")
        section = guide.split("## 1. Choisir", 1)[1].split("## 2.", 1)[0]
        noms = {n for n in re.findall(r"`([A-Z]\w+|shape_display)`", section)}
        noms = {n for n in noms if not n.startswith(("ChartSelect",)) or trouver(n)}
        absents = sorted(n for n in noms if trouver(n) is None)
        self.assertEqual(absents, [], "le guide cite des widgets absents du catalogue")

    def test_recherche_et_noms_proches(self):
        self.assertIn("ChartSelect", [e["nom"] for e in chercher("lasso")])
        self.assertIn("Slider2D", proches("Slidr2D"))
        page = en_texte("tangledistribution", verifier_installe=False)
        self.assertIn('params: Optional[Dict[str, float]]', page)
        self.assertIn("n'est pas dans", en_texte("Inexistant", verifier_installe=False))


if __name__ == "__main__":
    unittest.main()
