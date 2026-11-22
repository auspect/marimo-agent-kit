import importlib.util
import json
import re
import sys
import tempfile
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
                entete = re.match(r"---\nname: (.+)\ndescription: >-\n((?:  .+\n)+)---\n", texte)
                self.assertIsNotNone(entete, "en-tête name, puis description en bloc replié `>-`, attendu")
                self.assertEqual(entete.group(1), nom)
                description = " ".join(ligne.strip() for ligne in entete.group(2).splitlines())
                self.assertLessEqual(len(description), 1024, "description trop longue pour les agents")
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
                    casses.append(f"{page.name} vers {cible}")
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


class StudioVues(unittest.TestCase):
    """Le skill marimo-studio-vues, sa doc recopiée et l'exemple qui lui sert de preuve."""

    SKILL = dossier_skill("marimo-studio-vues")
    EXEMPLE = RACINE / "exemples" / "meteo-seattle"

    def version(self) -> str:
        source = (self.SKILL / "references" / "SOURCE.md").read_text(encoding="utf-8")
        return re.search(r"marimo-studio (\d+\.\d+\.\d+)", source).group(1)

    def test_doc_recopiee_avec_sa_source_et_sa_licence(self):
        references = self.SKILL / "references"
        source = (references / "SOURCE.md").read_text(encoding="utf-8")
        self.assertTrue((references / "LICENSE-marimo-studio").exists())
        pages = sorted((references / "docs").rglob("*.md"))
        self.assertEqual(f"{len(pages)} pages", re.search(r"(\d+ pages)", source).group(1))
        for page in pages:
            with self.subTest(page=page.name):
                self.assertTrue(page.read_text(encoding="utf-8").startswith(f"<!-- marimo-studio {self.version()}, recopié de"))
        self.assertIn("importer_marimo_studio.py", source)
        self.assertTrue((RACINE / "outils" / "importer_marimo_studio.py").exists())

    def test_une_seule_version_de_studio(self):
        version = self.version()
        self.assertIn(f"marimo-studio {version}", (self.SKILL / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn(f'"marimo-studio[deno,typst]=={version}"', (self.EXEMPLE / "pyproject.toml").read_text(encoding="utf-8"))

    def test_exemple_est_un_projet_pixi_comme_le_kit_le_conseille(self):
        import tomllib

        projet = tomllib.loads((self.EXEMPLE / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("workspace", projet["tool"]["pixi"])
        self.assertEqual(projet["tool"]["marimo"]["package_management"]["manager"], "pixi")
        self.assertEqual(projet["tool"]["marimo-studio"]["notebook"], "meteo.py")
        self.assertFalse((self.EXEMPLE / "pixi.toml").exists())
        self.assertNotIn("# /// script", (self.EXEMPLE / "meteo.py").read_text(encoding="utf-8"))

    def test_exemple_a_quatre_vues_de_formats_differents(self):
        vues = {p.parent.name: p.read_text(encoding="utf-8") for p in (self.EXEMPLE / "studio" / "meteo").glob("*/view.toml")}
        self.assertEqual(set(vues), {"grand-public", "briefing", "rapport", "article"})
        self.assertIn("marimo-studio/react", vues["grand-public"])
        self.assertIn("marimo-studio/react", vues["briefing"])
        self.assertIn("marimo-studio/typst", vues["rapport"])
        self.assertIn("marimo-studio/quarto", vues["article"])
        self.assertIn("@revealjs/react", (self.EXEMPLE / "studio" / "meteo" / "briefing" / "deno.json").read_text(encoding="utf-8"))
        for nom in vues:
            with self.subTest(vue=nom):
                self.assertTrue((self.EXEMPLE / "studio" / "meteo" / nom / "DESIGN.md").exists())

    def test_composants_partages_identiques(self):
        vues = self.EXEMPLE / "studio" / "meteo"
        for relatif in ("src/components/Graphiques.tsx", "src/components/graphiques.css", "src/lib/format.ts", "src/lib/donnees.ts"):
            with self.subTest(fichier=relatif):
                self.assertEqual((vues / "grand-public" / relatif).read_bytes(), (vues / "briefing" / relatif).read_bytes())

    def charger(self, nom: str):
        spec = importlib.util.spec_from_file_location(nom, self.SKILL / "scripts" / f"{nom}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_controle_des_vues_de_l_exemple(self):
        rapport = self.charger("controler_vues").controler(self.EXEMPLE / "meteo.py")
        self.assertEqual(rapport["erreurs"], 0, rapport["constats"])
        self.assertEqual(rapport["formats"], ["marimo-studio/quarto", "marimo-studio/react", "marimo-studio/typst"])

    def test_controle_signale_le_gabarit_et_les_chiffres(self):
        with tempfile.TemporaryDirectory() as dossier:
            notebook = Path(dossier) / "analyse.py"
            notebook.write_text("import marimo\n", encoding="utf-8")
            vue = Path(dossier) / "studio" / "analyse" / "tableau"
            (vue / "src").mkdir(parents=True)
            (vue / "view.toml").write_text('schema = 1\nprovider = "marimo-studio/react"\n', encoding="utf-8")
            (vue / "AGENTS.md").write_text("## Project intent\n\nKeep this section current with the user's audience.\n", encoding="utf-8")
            (vue / "src" / "App.tsx").write_text(
                'export const App = () => (\n  <main>\n    <marimo-cell name="cell-3" />\n    <p>Il pleut 35 % des jours.</p>\n  </main>\n);\n',
                encoding="utf-8")
            rapport = self.charger("controler_vues").controler(notebook)
        messages = " ".join(c["message"] for c in rapport["constats"])
        self.assertGreaterEqual(rapport["erreurs"], 1)
        self.assertIn("cell-N", messages)
        self.assertIn("DESIGN.md", messages)
        self.assertIn("« 35 % »", messages)
        self.assertIn("Project intent", messages)

    def test_scripts_valides(self):
        for script in (self.SKILL / "scripts" / "capturer.py", self.SKILL / "scripts" / "controler_vues.py",
                       self.EXEMPLE / "diapos_pptx.py", RACINE / "outils" / "importer_marimo_studio.py"):
            with self.subTest(script=script.name):
                compile(script.read_text(encoding="utf-8"), str(script), "exec")


if __name__ == "__main__":
    unittest.main()
