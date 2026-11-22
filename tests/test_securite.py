import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "src"))

from marimo_agent_kit.carnet import lire_corps  # noqa: E402
from marimo_agent_kit.environnement import charger  # noqa: E402
from marimo_agent_kit.garde import bilan, juger  # noqa: E402
from marimo_agent_kit.hook import principal  # noqa: E402
from marimo_agent_kit.regles import appliquer  # noqa: E402

IMPORTS = "import os, subprocess, pickle, yaml, html\nimport marimo as mo\nimport pandas as pd\nimport requests\nimport torch"


class Poste(unittest.TestCase):
    def setUp(self):
        self._dossier = tempfile.TemporaryDirectory()
        self.racine = Path(self._dossier.name)
        self.journal = self.racine / "garde.jsonl"
        self.env = {"HOME": str(self.racine), "USERPROFILE": str(self.racine), "XDG_CONFIG_HOME": str(self.racine / "c"),
                    "APPDATA": str(self.racine / "c"), "MAK_GARDE_JOURNAL": str(self.journal), "PATH": "/usr/bin"}

    def tearDown(self):
        self._dossier.cleanup()

    def config(self, **env):
        return charger(self.racine, {**self.env, **env})

    def regles(self, commande: str, outil: str = "Bash") -> set[str]:
        return {r.regle for r in juger(outil, {"command": commande})}


class Garde(Poste):
    def test_ce_qui_contourne_le_gestionnaire_est_refuse(self):
        cas = {
            "pip install requests": {"pip-install"},
            "python -m pip install -U x": {"pip-install"},
            "uv pip install --index-url https://pypi.org/simple x": {"option-index"},
            "pixi add --pypi x --index https://depot.exemple.interne/simple": {"option-index"},
            "uvx --from git+https://github.com/a/b mak": {"source-git"},
            "cd outils && npx skills add x": {"npx"},
        }
        for commande, attendu in cas.items():
            with self.subTest(commande=commande):
                self.assertEqual(self.regles(commande), attendu)

    def test_ce_qui_passe(self):
        for commande in ("git commit -m 'retire pip install et npx'", "grep -i https://pypi.org notes.md",
                         "pixi add polars", "pixi add --pypi humanize", "uv add polars", "uv --version",
                         "curl https://exemple.com/donnees.csv", "echo npx"):
            with self.subTest(commande=commande):
                self.assertEqual(self.regles(commande), set())

    def test_seules_les_commandes_du_shell_sont_jugees(self):
        self.assertEqual(self.regles("pip install x", "PowerShell"), {"pip-install"})
        self.assertEqual(self.regles("pip install x", "WebFetch"), set())


class HookAvantOutil(Poste):
    def lancer(self, donnees: dict, evenement: str | None = None, **env) -> tuple[int, str]:
        import os

        anciennes = {n: os.environ.get(n) for n in [*self.env, *env]}
        os.environ.update({**self.env, **env})
        erreur = io.StringIO()
        try:
            with redirect_stderr(erreur):
                code = principal(io.StringIO(json.dumps({"cwd": str(self.racine), **donnees})), evenement=evenement)
        finally:
            for nom, valeur in anciennes.items():
                if valeur is None:
                    os.environ.pop(nom, None)
                else:
                    os.environ[nom] = valeur
        return code, erreur.getvalue()

    def test_observer_note_sans_refuser_puis_agir_refuse(self):
        claude = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "pip install x"}}
        self.assertEqual(self.lancer(claude), (0, ""))
        self.assertIn("aurait refusé", self.journal.read_text(encoding="utf-8"))
        code, raison = self.lancer(claude, MAK_GARDE="agir")
        self.assertEqual(code, 2)
        self.assertIn("pip install", raison)
        copilot = {"toolName": "bash", "toolArgs": json.dumps({"command": "npx x"})}
        self.assertEqual(self.lancer(copilot, "preToolUse", MAK_GARDE="agir")[0], 2)
        self.assertEqual(self.lancer(copilot, "preToolUse", MAK_GARDE="off"), (0, ""))
        self.assertIn("pip-install", bilan(self.config()))

    def test_une_entree_illisible_laisse_passer(self):
        self.assertEqual(self.lancer({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": "texte"},
                                     MAK_GARDE="agir"), (0, ""))
        self.assertEqual(self.lancer({"toolName": "bash", "toolArgs": "{pas du json"}, "preToolUse", MAK_GARDE="agir"),
                         (0, ""))


class Safeagents(Poste):
    def test_fournisseurs_compares_a_safeagents(self):
        from marimo_agent_kit.confidentialite import constats_safeagents

        infos = {"fournisseurs": {"custom_providers.interne": "http://localhost:8790/v1",
                                  "custom_providers.direct": "https://llm.exemple.interne/v1"}}
        etats = {c.detail.split(" ")[0]: c.etat for c in constats_safeagents(
            self.config(MAK_SAFEAGENTS="http://127.0.0.1:8790"), infos)}
        self.assertEqual(etats, {"custom_providers.interne": "ok", "custom_providers.direct": "attention"})
        self.assertEqual([c.etat for c in constats_safeagents(self.config(), infos)], ["info"])
        self.assertEqual(constats_safeagents(self.config(), {"fournisseurs": {}}), [])

    def test_lancer_donne_l_environnement_du_kit(self):
        from marimo_agent_kit import cli

        sortie = self.racine / "env.txt"
        code = cli.main(["lancer", "--", sys.executable, "-c",
                         f"import os, pathlib; pathlib.Path({str(sortie)!r}).write_text(os.environ['MARIMO_SKIP_UPDATE_CHECK'])"])
        self.assertEqual((code, sortie.read_text()), (0, "1"))


class ReglesDeSecurite(unittest.TestCase):
    def codes(self, *cellules: str) -> list[tuple[str, int]]:
        return [(d.code, d.ligne) for d in appliquer(lire_corps([IMPORTS, *cellules]), selection={"AG3"})]

    def test_signale(self):
        cas = {
            "subprocess.run('ls', shell=True)": "AG301", "os.system('dir')": "AG301",
            "x = eval(texte)": "AG302", "d = pickle.load(f)": "AG303", "m = torch.load('m.pt')": "AG303",
            "c = yaml.load(t)": "AG303", "nom = lu()\nh = mo.Html(f'<b>{nom}</b>')": "AG304",
            "h = mo.Html('<td>' + ligne['nom'] + '</td>')": "AG304",
            "r = requests.get('https://api.exemple.com/x')": "AG305",
            "df = pd.read_csv('https://raw.githubusercontent.com/a/b.csv')": "AG305",
            "k = open('~/.ssh/id_rsa').read()": "AG306", "print(os.environ)": "AG306", "os.environ": "AG306",
        }
        for cellule, code in cas.items():
            with self.subTest(cellule=cellule):
                self.assertIn(code, [c for c, _ in self.codes(cellule)])

    def test_laisse_passer(self):
        for cellule in ("y = eval('1 + 1')", "m = torch.load('m.pt', weights_only=True)",
                        "c = yaml.load(t, Loader=yaml.SafeLoader)", "h = mo.Html(f'<b>{html.escape(nom)}</b> {x:.2f}')",
                        "h = mo.Html('<pre>' + html.escape(code) + '</pre>')",
                        "def cadre(svg):\n    return mo.Html(f'<div>{svg}</div>')",
                        "LOGO = '<svg></svg>'\nh = mo.Html('<p>' + LOGO + '</p>')",
                        "r = requests.get('http://localhost:8000/x')", "r = requests.get('http://192.168.1.10/x')",
                        "df = pd.read_csv('local.csv')",
                        "v = os.environ['HOME']", "env = {**os.environ, 'A': '1'}"):
            with self.subTest(cellule=cellule):
                self.assertEqual(self.codes(cellule), [])


if __name__ == "__main__":
    unittest.main()
