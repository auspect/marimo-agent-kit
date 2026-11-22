import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "src"))

from marimo_agent_kit.environnement import (  # noqa: E402
    charger,
    contexte_agent,
    detail_configuration,
    lanceur,
    lire_fichier_env,
    trouver_projet,
)
from marimo_agent_kit.hook import principal  # noqa: E402
from marimo_agent_kit.installer import poser_hooks, poser_mcp  # noqa: E402

INTERNE = "https://artifactory.exemple.interne/api/pypi/pypi/simple"


class Poste(unittest.TestCase):
    """Un dossier personnel et un projet jetables : le vrai poste n'est jamais lu."""

    def setUp(self):
        self._dossier = tempfile.TemporaryDirectory()
        self.racine = Path(self._dossier.name)
        self.accueil = self.racine / "accueil"
        self.projet = self.racine / "projet" / "notebooks"
        self.projet.mkdir(parents=True)
        self.env = {"HOME": str(self.accueil), "USERPROFILE": str(self.accueil),
                    "XDG_CONFIG_HOME": str(self.accueil / ".config"), "APPDATA": str(self.accueil / ".config"),
                    "PATH": "/usr/bin"}

    def tearDown(self):
        self._dossier.cleanup()

    def ecrire(self, relatif: str, texte: str) -> Path:
        chemin = self.racine / relatif
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(texte, encoding="utf-8")
        return chemin

    def charger(self, **env):
        return charger(self.projet, {**self.env, **env})


class FichierEnv(Poste):
    def test_format_et_lignes_illisibles(self):
        chemin = self.ecrire("a.env", "# commentaire\n\nexport A=1\nB = \"deux mots\"\nC='C:\\certs\\ca.pem'\nfaux\n")
        paires, problemes = lire_fichier_env(chemin)
        self.assertEqual(paires, [("A", "1"), ("B", "deux mots"), ("C", "C:\\certs\\ca.pem")])
        self.assertEqual(len(problemes), 1)
        self.assertIn(":6 :", problemes[0])

    def test_ordre_des_fichiers_et_le_shell_gagne(self):
        self.ecrire("accueil/.config/marimo-agent-kit/mak.env",
                    "HTTPS_PROXY=http://proxy.utilisateur:8080\nOUTIL=utilisateur\nMAK_CONTEXTE=phrase un\n")
        self.ecrire("projet/mak.env", "OUTIL=projet\nMAK_CONTEXTE=phrase deux\n")
        explicite = self.ecrire("explicite.env", "OUTIL=explicite\nDEJA=fichier\n")
        config = self.charger(MAK_CONFIG=str(explicite), DEJA="shell")
        self.assertEqual(config.env["HTTPS_PROXY"], "http://proxy.utilisateur:8080")
        self.assertEqual(config.env["OUTIL"], "explicite")
        self.assertEqual(config.env["DEJA"], "shell")
        self.assertIn("shell", config.origines["DEJA"])
        self.assertEqual(config.contexte, ["phrase un", "phrase deux"])
        self.assertEqual([o for o, _ in config.fichiers], ["utilisateur", "projet", "MAK_CONFIG"])

    def test_mak_config_absent_est_signale(self):
        config = self.charger(MAK_CONFIG=str(self.racine / "absent.env"))
        self.assertTrue(any("absent.env" in p for p in config.problemes))


class Reseau(Poste):
    def test_le_kit_laisse_le_reseau_aux_gestionnaires(self):
        config = self.charger(UV_DEFAULT_INDEX=INTERNE)
        for nom in ("UV_OFFLINE", "UV_PYTHON_DOWNLOADS"):
            self.assertNotIn(nom, config.env)
        self.assertEqual(config.env["UV_DEFAULT_INDEX"], INTERNE)
        self.assertEqual(config.env["MARIMO_SKIP_UPDATE_CHECK"], "1")


class Projets(Poste):
    def test_gestionnaire_du_projet(self):
        cas = {
            "pixi.toml": ("[workspace]\nchannels = ['conda-forge']\n", "pixi"),
            "pyproject.toml": ("[project]\nname = 'x'\n\n[tool.pixi.workspace]\nchannels = ['conda-forge']\n", "pixi"),
        }
        for nom, (texte, attendu) in cas.items():
            with self.subTest(nom=nom):
                manifeste = self.ecrire(f"{nom}/projet/{nom}", texte)
                projet = trouver_projet(manifeste.parent / "notebooks")
                self.assertEqual((projet.manifeste, projet.gestionnaire), (manifeste.resolve(), attendu))
        self.ecrire("uv/pyproject.toml", "[project]\nname = 'x'\n")
        self.assertIsNone(trouver_projet(self.racine / "uv").gestionnaire)
        self.ecrire("uv/uv.lock", "")
        self.assertEqual(trouver_projet(self.racine / "uv").gestionnaire, "uv")

    def test_contexte_donne_la_commande_du_gestionnaire(self):
        self.assertIn("`pixi init --format pyproject`", contexte_agent(self.charger(), None))
        self.ecrire("projet/pixi.toml", "[workspace]\n")
        texte = contexte_agent(self.charger(), trouver_projet(self.projet))
        self.assertIn("Paquets du projet", texte)
        self.assertIn("`pixi add <paquet>`", texte)
        self.assertIn("`pip install`", texte)

    def test_lanceur_prefere_l_environnement_pixi(self):
        manifeste = self.ecrire("projet/pixi.toml", "[workspace]\n")
        for env in (".pixi/envs/default", ".venv"):
            for relatif in ("bin/marimo", "bin/python", "Scripts/marimo.exe", "Scripts/python.exe"):
                self.ecrire(f"projet/{env}/{relatif}", "")
        with mock.patch("marimo_agent_kit.environnement.shutil.which", return_value="pixi"):
            self.assertEqual(lanceur("marimo", self.projet / "nb.py"),
                             ["pixi", "run", "--manifest-path", str(manifeste.resolve()), "marimo"])
            self.assertEqual(lanceur("python", self.projet)[-1], "python")
        with mock.patch("marimo_agent_kit.environnement.shutil.which", return_value=None):
            self.assertEqual(Path(lanceur("python", self.projet)[0]).parent.parent, (self.racine / "projet" / ".venv").resolve())


class Secrets(Poste):
    def test_identifiants_du_proxy_masques(self):
        self.ecrire("projet/mak.env", "HTTPS_PROXY=http://alice:motdepasse@proxy.exemple.interne:8080\n"
                                      "OUTIL_TOKEN=abc123\n")
        config = self.charger()
        self.assertEqual(config.env["HTTPS_PROXY"], "http://alice:motdepasse@proxy.exemple.interne:8080")
        for texte in (contexte_agent(config), detail_configuration(config)):
            self.assertNotIn("motdepasse", texte)
            self.assertNotIn("abc123", texte)
        self.assertIn("http://***@proxy.exemple.interne:8080", contexte_agent(config))

    def test_no_proxy_respecte(self):
        config = self.charger(HTTPS_PROXY="http://proxy.exemple.interne:8080", NO_PROXY=".exemple.interne")
        direct = config.ouvreur("https://llm.exemple.interne/v1")
        passe = config.ouvreur("https://ailleurs.exemple/v1")
        def proxys(ouvreur):
            return next((h.proxies for h in ouvreur.handlers if hasattr(h, "proxies")), {})

        self.assertEqual(proxys(direct), {})
        self.assertEqual(proxys(passe)["https"], "http://proxy.exemple.interne:8080")


class Branchements(Poste):
    def test_hook_de_demarrage(self):
        self.ecrire("projet/mak.env", "MAK_CONTEXTE=Les données restent sur le partage.\n")
        for evenement, entree, cle in (
            (None, {"hook_event_name": "SessionStart", "cwd": str(self.projet)}, "hookSpecificOutput"),
            ("sessionStart", {"cwd": str(self.projet)}, "additionalContext"),
        ):
            with self.subTest(evenement=evenement):
                sortie = io.StringIO()
                with redirect_stdout(sortie):
                    self.assertEqual(principal(io.StringIO(json.dumps(entree)), evenement=evenement), 0)
                reponse = json.loads(sortie.getvalue())
                texte = reponse[cle]["additionalContext"] if cle == "hookSpecificOutput" else reponse[cle]
                self.assertIn("Paquets du projet", texte)
                self.assertIn("Les données restent sur le partage.", texte)

    def test_installateur_pose_les_deux_hooks_une_fois(self):
        poser_hooks(self.racine, appliquer=True, source="marimo-agent-kit")
        poser_hooks(self.racine, appliquer=True, source="marimo-agent-kit")
        reglages = json.loads((self.racine / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(len(reglages["hooks"]["PostToolUse"]), 1)
        self.assertEqual(len(reglages["hooks"]["SessionStart"]), 1)
        self.assertNotIn("matcher", reglages["hooks"]["SessionStart"][0])
        self.assertEqual(len(reglages["hooks"]["PreToolUse"]), 1)
        refus = poser_hooks(self.racine, appliquer=True, source="marimo-agent-kit", cible="github")
        self.assertEqual(refus[0].etat, "à compléter à la main")
        self.assertFalse((self.racine / ".github" / "hooks" / "marimo-agent-kit.json").exists())

    def test_hooks_pour_copilot_seul(self):
        poser_hooks(self.racine, appliquer=True, source="marimo-agent-kit", cible="github")
        poser_hooks(self.racine, appliquer=True, source="marimo-agent-kit", cible="github")
        fichier = json.loads((self.racine / ".github" / "hooks" / "marimo-agent-kit.json").read_text(encoding="utf-8"))
        self.assertEqual(fichier["version"], 1)
        self.assertEqual({e: len(v) for e, v in fichier["hooks"].items()},
                         {"sessionStart": 1, "preToolUse": 1, "postToolUse": 1})
        avant = fichier["hooks"]["preToolUse"][0]
        self.assertEqual((avant["bash"], avant["powershell"]), ("uvx --from marimo-agent-kit mak hook preToolUse",) * 2)
        self.assertEqual(poser_hooks(self.racine, appliquer=True, source="marimo-agent-kit")[0].etat, "à compléter à la main")

    def test_mcp_dans_le_fichier_commun(self):
        poser_mcp(self.racine, appliquer=True, source="marimo-agent-kit")
        serveur = json.loads((self.racine / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["marimo_agent_kit"]
        self.assertEqual(serveur["args"][-1], "mcp")


if __name__ == "__main__":
    unittest.main()
