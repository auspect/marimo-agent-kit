import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ICI = Path(__file__).resolve().parent
SRC = ICI.parent / "src"
sys.path.insert(0, str(SRC))

from marimo_agent_kit import cli  # noqa: E402
from marimo_agent_kit.contrat import contrat_court, reference_regles  # noqa: E402
from marimo_agent_kit.hook import principal  # noqa: E402
from marimo_agent_kit.installer import fichiers_du_skill, installer  # noqa: E402
from marimo_agent_kit.mcp_serveur import traiter  # noqa: E402

MAUVAIS = ICI / "exemples" / "mauvais.py"
PROPRE = ICI / "exemples" / "propre.py"
AVEC_MARIMO = importlib.util.find_spec("marimo") is not None
AVEC_POLARS = importlib.util.find_spec("polars") is not None


def lancer_cli(*args: str, entree: str = "") -> tuple[int, str]:
    sortie, erreur = io.StringIO(), io.StringIO()
    ancien = sys.stdin
    sys.stdin = io.StringIO(entree)
    try:
        with redirect_stdout(sortie), redirect_stderr(erreur):
            code = cli.main(list(args))
    finally:
        sys.stdin = ancien
    return code, sortie.getvalue() + erreur.getvalue()


class SansMarimo(unittest.TestCase):
    def setUp(self):
        self.ancien = os.environ.get("MAK_MARIMO")
        os.environ["MAK_MARIMO"] = "commande-qui-n-existe-pas"

    def tearDown(self):
        if self.ancien is None:
            os.environ.pop("MAK_MARIMO", None)
        else:
            os.environ["MAK_MARIMO"] = self.ancien

    def test_verifier_dit_ce_qui_n_a_pas_tourne(self):
        code, texte = lancer_cli("verifier", str(MAUVAIS), "--json")
        self.assertEqual(code, 1)
        rapport = json.loads(texte)[0]
        self.assertEqual(rapport["statut"], "non vérifié")
        etats = {e["nom"]: e["etat"] for e in rapport["etapes"]}
        self.assertEqual(etats["marimo check"], "échec")
        self.assertEqual(etats["règles marimo-agent-kit"], "fait")
        self.assertGreaterEqual(rapport["compte"]["erreur"], 4)

    def test_hook_claude_bloque_sur_une_erreur(self):
        evenement = {"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": str(MAUVAIS)}}
        erreur = io.StringIO()
        with redirect_stderr(erreur):
            code = principal(io.StringIO(json.dumps(evenement)))
        self.assertEqual(code, 2)
        self.assertIn("AG001", erreur.getvalue())

    def test_hook_laisse_passer_ce_qui_n_est_pas_un_notebook(self):
        for evenement in ({"tool_name": "Read", "tool_input": {"file_path": str(MAUVAIS)}},
                          {"tool_name": "Write", "tool_input": {"file_path": str(ICI / "test_outils.py")}},
                          {"toolName": "edit", "toolArgs": "pas du json"}):
            with self.subTest(evenement=evenement):
                self.assertEqual(principal(io.StringIO(json.dumps(evenement))), 0)
        self.assertEqual(principal(io.StringIO("illisible")), 0)


class LigneDeCommande(unittest.TestCase):
    def test_cellules_proposees(self):
        code, texte = lancer_cli("cellules", "--notebook", str(PROPRE), "--json",
                                 entree=json.dumps(["ventes['c'] = 1", "total = inconnu + 1"]))
        self.assertEqual(code, 1)
        trouves = {(d["code"], d["cellule"]) for d in json.loads(texte)["diagnostics"]}
        self.assertIn(("AG101", 1), trouves)
        self.assertIn(("AG007", 2), trouves)

    def test_cellule_en_texte_sans_notebook(self):
        code, texte = lancer_cli("cellules", "--texte", entree="x = 1\nreturn (x,)")
        self.assertEqual(code, 1)
        self.assertIn("AG008", texte)

    def test_regles(self):
        self.assertEqual(lancer_cli("regles"), (0, contrat_court()))
        code, texte = lancer_cli("regles", "--reference")
        self.assertIn("## AG101", texte)


class ServeurMCP(unittest.TestCase):
    def test_echange_complet_par_l_entree_standard(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "regles_marimo", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "verifier_cellules", "arguments": {"cellules": ["mo.md('{x}')\nx = 1"]}}},
            {"jsonrpc": "2.0", "id": 5, "method": "inconnue"},
        ]
        entree = "".join(json.dumps(m) + "\n" for m in messages)
        sortie = subprocess.run([sys.executable, "-m", "marimo_agent_kit", "mcp"], input=entree, capture_output=True,
                                text=True, encoding="utf-8", timeout=60, env={**os.environ, "PYTHONPATH": str(SRC)})
        reponses = {r["id"]: r for r in map(json.loads, sortie.stdout.splitlines())}
        self.assertEqual(sorted(reponses), [1, 2, 3, 4, 5], "la notification ne reçoit pas de réponse")
        self.assertEqual(reponses[1]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(len(reponses[2]["result"]["tools"]), 6)
        self.assertIn("Contrat", reponses[3]["result"]["content"][0]["text"])
        self.assertIn("AG105", reponses[4]["result"]["content"][0]["text"])
        self.assertEqual(reponses[5]["error"]["code"], -32601)

    def test_outil_qui_echoue_ne_coupe_pas_la_connexion(self):
        reponse = traiter({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                           "params": {"name": "verifier_notebook", "arguments": {}}})
        self.assertTrue(reponse["result"]["isError"])


class Installateur(unittest.TestCase):
    def test_sans_appliquer_rien_n_est_ecrit_puis_tout_l_est_une_fois(self):
        with tempfile.TemporaryDirectory() as dossier:
            dossier = Path(dossier)
            (dossier / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0"\n', encoding="utf-8")
            avant = installer(dossier, "agents", True, "claude", True, appliquer=False, source="/kit", noms=("marimo-agent-kit",))
            self.assertTrue(all(a.etat == "à créer" for a in avant))
            self.assertEqual(sorted(p.name for p in dossier.iterdir()), ["pyproject.toml"])
            installer(dossier, "agents", True, "claude", True, appliquer=True, source="/kit", noms=("marimo-agent-kit",))
            apres = installer(dossier, "agents", True, "claude", True, appliquer=True, source="/kit", noms=("marimo-agent-kit",))
            self.assertTrue(all(a.etat == "déjà là" for a in apres), [(a.cible, a.etat) for a in apres])
            reglages = json.loads((dossier / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(reglages["hooks"]["PostToolUse"][0]["hooks"][0]["command"], "uvx --from /kit mak hook")
            if sys.version_info >= (3, 11):
                import tomllib

                marimo = tomllib.loads((dossier / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["marimo"]
                self.assertEqual(marimo["ai"]["rules"], contrat_court())
                self.assertEqual(marimo["mcp"]["mcpServers"]["marimo_agent_kit"]["args"], ["--from", "/kit", "mak", "mcp"])
                self.assertEqual(marimo["package_management"]["manager"], "pixi")

    def test_gestionnaire_du_bouton_d_installation(self):
        cas = {"[tool.pixi.workspace]\nchannels = ['conda-forge']\n": "pixi", "[tool.uv]\npackage = false\n": "uv",
               "": "pixi"}
        for section, attendu in cas.items():
            with self.subTest(attendu=attendu, section=section), tempfile.TemporaryDirectory() as dossier:
                pyproject = Path(dossier) / "pyproject.toml"
                pyproject.write_text(f'[project]\nname = "x"\nversion = "0"\n\n{section}', encoding="utf-8")
                installer(Path(dossier), None, True, None, False, appliquer=True, source="/kit")
                self.assertIn('[tool.marimo.package_management]\n# Le bouton', pyproject.read_text(encoding="utf-8"))
                self.assertIn(f'manager = "{attendu}"', pyproject.read_text(encoding="utf-8"))

    def test_un_projet_d_une_version_precedente_recoit_le_gestionnaire(self):
        with tempfile.TemporaryDirectory() as dossier:
            pyproject = Path(dossier) / "pyproject.toml"
            ancien = ('[project]\nname = "x"\n\n[tool.marimo.mcp.mcpServers.marimo_agent_kit]\ncommand = "mak"\n'
                      'args = ["mcp"]\n')
            pyproject.write_text(ancien, encoding="utf-8")
            self.assertEqual(installer(Path(dossier), None, True, None, False, appliquer=True)[0].etat, "créé")
            self.assertEqual(pyproject.read_text(encoding="utf-8").count("[tool.marimo"), 2)
            self.assertEqual(installer(Path(dossier), None, True, None, False, appliquer=True)[0].etat, "déjà là")

    def test_une_section_marimo_existante_n_est_pas_touchee(self):
        with tempfile.TemporaryDirectory() as dossier:
            dossier = Path(dossier)
            texte = '[project]\nname = "x"\n\n[tool.marimo.ai]\nrules = "les miennes"\n'
            (dossier / "pyproject.toml").write_text(texte, encoding="utf-8")
            actions = installer(dossier, None, True, None, False, appliquer=True)
            self.assertEqual(actions[0].etat, "à compléter à la main")
            self.assertEqual((dossier / "pyproject.toml").read_text(encoding="utf-8"), texte)


class FichiersGeneres(unittest.TestCase):
    def test_reference_des_regles_a_jour(self):
        livree = ICI.parent / "skills" / "marimo-agent-kit" / "reference" / "regles.md"
        self.assertEqual(livree.read_text(encoding="utf-8"), reference_regles(),
                         "régénère : mak regles --reference > skills/marimo-agent-kit/reference/regles.md")

    def test_copie_des_skills_dans_le_depot_parent_a_jour(self):
        from marimo_agent_kit.ressources import SKILLS

        copies = ICI.parent.parent / ".github" / "skills"
        presents = [n for n in SKILLS if (copies / n).exists()]
        if not presents:
            self.skipTest("pas de copie des skills dans un dépôt parent")
        for nom in presents:
            for relatif, contenu in fichiers_du_skill(nom).items():
                with self.subTest(skill=nom, fichier=relatif):
                    self.assertEqual((copies / nom / relatif).read_bytes(), contenu,
                                     "mets la copie à jour : mak installer --skill github --remplacer --appliquer")


@unittest.skipUnless(AVEC_MARIMO and AVEC_POLARS, "marimo ou polars absent de ce Python")
class AvecMarimo(unittest.TestCase):
    def test_exemple_mauvais_et_propre_de_bout_en_bout(self):
        from marimo_agent_kit.verifier import verifier

        mauvais = verifier(MAUVAIS, executer=True, bac_a_sable=None)
        self.assertEqual(mauvais.statut, "à corriger")
        confirmes = [d for d in mauvais.diagnostics if "L'exécution le confirme" in d.message]
        self.assertGreaterEqual(len(confirmes), 3, [d.message for d in mauvais.diagnostics])
        ancien = os.getcwd()
        os.chdir(ICI.parent)
        try:
            propre = verifier(Path("tests/exemples/propre.py"), executer=True, bac_a_sable=None)
        finally:
            os.chdir(ancien)
        self.assertEqual(propre.statut, "propre", propre.en_texte(conseils=True))

    def test_regle_de_marimo_check_lue_sur_le_poste(self):
        code, texte = lancer_cli("api", "MB002")
        self.assertEqual(code, 0, texte)
        self.assertIn("multiple-definitions", texte)

    def test_regle_de_marimo_check_renvoie_a_la_doc_installee(self):
        from marimo_agent_kit.verifier import verifier

        source = ("import marimo\n\napp = marimo.App()\n\n\n@app.cell\ndef _():\n    x = 1\n    return (x,)\n\n\n"
                  "@app.cell\ndef _():\n    x = 2\n    return (x,)\n")
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "double.py"
            chemin.write_text(source, encoding="utf-8")
            double = next(d for d in verifier(chemin, executer=False).diagnostics if d.code == "MB002")
            self.assertIn("`mak api MB002`", double.correction)


if __name__ == "__main__":
    unittest.main()
