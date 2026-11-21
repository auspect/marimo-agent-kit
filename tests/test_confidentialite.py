import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from marimo_agent_kit.confidentialite import diagnostiquer, lignes_a_poser  # noqa: E402
from marimo_agent_kit.environnement import ENV_SOBRE, env_sobre  # noqa: E402

PROPRE = {"ddgs": False, "markdownify": False, "presets_mcp": [], "serveurs_mcp": ["marimo_agent_kit"],
          "copilot": "custom", "consentement_new": None, "version": "0.25.2"}


def etats(env, infos):
    return {c.sujet: c.etat for c in diagnostiquer(env, infos)}


class Diagnostic(unittest.TestCase):
    def test_poste_sobre(self):
        resultat = etats({"MARIMO_SKIP_UPDATE_CHECK": "1", "PYDANTIC_AI_NO_BANNER": "1"}, PROPRE)
        self.assertNotIn("à régler", resultat.values())
        self.assertNotIn("attention", resultat.values())
        self.assertEqual(lignes_a_poser({"MARIMO_SKIP_UPDATE_CHECK": "1", "PYDANTIC_AI_NO_BANNER": "1"}),
                         ["Rien à poser : les variables sont déjà là."])

    def test_poste_bavard(self):
        env = {"MARIMO_TRACING": "true", "OTEL_EXPORTER_OTLP_ENDPOINT": "https://traces.exemple"}
        infos = {**PROPRE, "ddgs": True, "presets_mcp": ["context7"], "copilot": "github", "consentement_new": "2026-01-02"}
        constats = {c.sujet: c for c in diagnostiquer(env, infos)}
        self.assertEqual(constats["vérification de version"].etat, "à régler")
        self.assertIn("https://traces.exemple", constats["traces de l'assistant"].detail)
        for sujet in ("recherche web du chat", "MCP context7", "complétion de code", 'marimo new "invite"'):
            self.assertEqual(constats[sujet].etat, "attention", sujet)
        lignes = "\n".join(lignes_a_poser(env))
        self.assertIn('[Environment]::SetEnvironmentVariable("MARIMO_SKIP_UPDATE_CHECK", "1", "User")', lignes)
        self.assertIn("export MARIMO_SKIP_UPDATE_CHECK=1", lignes)
        self.assertIn("retire MARIMO_TRACING", lignes)

    def test_sans_marimo_on_le_dit(self):
        self.assertEqual(etats({}, None)["environnement de marimo"], "non vérifié")

    def test_le_kit_pose_les_variables_sur_ce_qu_il_lance(self):
        self.assertEqual(ENV_SOBRE["MARIMO_SKIP_UPDATE_CHECK"], "1")
        self.assertEqual(env_sobre()["PYDANTIC_AI_NO_BANNER"], "1")


if __name__ == "__main__":
    unittest.main()
