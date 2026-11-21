import sys
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "src"))
sys.path.insert(0, str(ICI))

import faux_llm  # noqa: E402

from marimo_agent_kit.sonde_llm import bloc_configuration, en_texte, sonder  # noqa: E402


def lancer(**capacites):
    serveur = faux_llm.demarrer(**capacites)
    try:
        essais = sonder(f"http://127.0.0.1:{serveur.server_address[1]}/v1", "mon-llm", "cle", {"X-Equipe": "ia"}, delai=10)
    finally:
        serveur.shutdown()
        serveur.server_close()
    return {e.fonction.split(" (")[0]: e for e in essais}, serveur.journal


class Sonde(unittest.TestCase):
    def test_tout_passe_et_les_requetes_ont_la_forme_de_celles_de_marimo(self):
        essais, journal = lancer()
        self.assertTrue(all(e.ok for e in essais.values()), essais)
        self.assertEqual({r["chemin"] for r in journal}, {"/v1/chat/completions"})
        entetes = {k.lower(): v for k, v in journal[0]["entetes"].items()}
        self.assertEqual((entetes["authorization"], entetes["api-key"], entetes["x-equipe"]), ("Bearer cle", "cle", "ia"))
        self.assertEqual(journal[2]["corps"]["tool_choice"], "required")
        self.assertEqual(journal[3]["corps"]["tool_choice"], "auto")

    def test_sans_appel_d_outils_le_mode_manual_reste(self):
        essais, _ = lancer(outils=False)
        self.assertTrue(essais["chat, mode Manual"].ok)
        self.assertFalse(essais["génération de cellule"].ok)
        self.assertIn("enable-auto-tool-choice", essais["modes Ask et Agent, outils MCP"].detail)
        texte = en_texte(list(essais.values()), "")
        self.assertIn("Utilisable en mode Manual", texte)

    def test_max_completion_tokens_refuse(self):
        essais, _ = lancer(max_completion=False)
        self.assertFalse(essais["autocomplétion"].ok)
        self.assertIn("max_completion_tokens", essais["autocomplétion"].detail)
        self.assertTrue(essais["génération de cellule"].ok)

    def test_point_d_acces_injoignable(self):
        essais = sonder("http://127.0.0.1:9/v1", "m", delai=3)
        self.assertEqual(len(essais), 1)
        self.assertFalse(essais[0].ok)

    def test_configuration_proposee(self):
        bloc = bloc_configuration("interne", "https://llm.interne/v1", "mon-llm", "LLM_CLE", {"X-Equipe": "ia"}, None)
        self.assertIn('api_key = "env:LLM_CLE"', bloc)
        self.assertIn('chat_model = "interne/mon-llm"', bloc)
        if sys.version_info >= (3, 11):
            import tomllib

            donnees = tomllib.loads(bloc)
            self.assertEqual(donnees["tool"]["marimo"]["ai"]["custom_providers"]["interne"]["extra_headers"], {"X-Equipe": "ia"})


if __name__ == "__main__":
    unittest.main()
