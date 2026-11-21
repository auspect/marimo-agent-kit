import sys
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "src"))

from marimo_agent_kit.carnet import joindre, lire_corps, lire_fichier, lire_source  # noqa: E402
from marimo_agent_kit.regles import REGLES, appliquer  # noqa: E402

ENTETE = '# /// script\n# requires-python = ">=3.12"\n# dependencies = ["marimo", "polars"]\n# ///\n'


def codes(*cellules: str, complet: bool = True, regle: str | None = None) -> list[str]:
    carnet = lire_corps(["import marimo as mo", *cellules], complet=complet)
    return [d.code for d in appliquer(carnet, selection={regle} if regle else None)]


def fichier(corps_de_cellules: list[str], entete: str = ENTETE) -> str:
    morceaux = [entete, "import marimo\n\napp = marimo.App()\n"]
    for corps in corps_de_cellules:
        lignes = "\n".join("    " + ligne for ligne in corps.splitlines())
        morceaux.append(f"\n@app.cell\ndef _():\n{lignes}\n    return\n")
    morceaux.append('\nif __name__ == "__main__":\n    app.run()\n')
    return "".join(morceaux)


class Erreurs(unittest.TestCase):
    def test_valeur_lue_dans_la_cellule_qui_cree(self):
        self.assertIn("AG001", codes("s = mo.ui.slider(0, 9, label='n')\nprint(s.value)\ns"))
        self.assertNotIn("AG001", codes("s = mo.ui.slider(0, 9, label='n')\ns", "print(s.value)"))
        rappel = "s = mo.ui.slider(0, 9, label='n', on_change=lambda v: print(v))\ns"
        self.assertNotIn("AG001", codes(rappel))

    def test_asyncio_run(self):
        self.assertIn("AG002", codes("import asyncio", "async def f():\n    return 1\nr = asyncio.run(f())"))
        self.assertNotIn("AG002", codes("async def f():\n    return 1\nr = await f()"))

    def test_habitudes_de_jupyter(self):
        self.assertIn("AG003", codes("import polars as pl\ndf = pl.DataFrame()", "display(df)"))
        self.assertIn("AG003", codes("from IPython.display import HTML"))
        self.assertNotIn("AG003", codes("def display(x):\n    return x", "display(1)"))
        self.assertEqual(codes("display(1)").count("AG007"), 0, "AG003 suffit pour display")

    def test_md_sans_f(self):
        self.assertIn("AG004", codes("moyenne = 2.5", "mo.md('La moyenne vaut {moyenne}')"))
        self.assertNotIn("AG004", codes("moyenne = 2.5", "mo.md(f'La moyenne vaut {moyenne}')"))
        self.assertNotIn("AG004", codes("a = 1", r"mo.md(r'$\frac{a}{b}$ et `{a}`')"))
        self.assertNotIn("AG004", codes("a = 1", "s = mo.md('Seuil {a}').batch(a=mo.ui.slider(0, 1))"))
        self.assertNotIn("AG004", codes("mo.md('{inconnu}')"))

    def test_secret_en_clair(self):
        fausse_cle = "sk-" + "ant-api03-" + "abcdefghijklmnopqrstuvwxyz0123"
        self.assertIn("AG005", codes(f"cle = '{fausse_cle}'"))
        self.assertIn("AG005", codes("api" + "_key = " + "'a8f5f167f44f4964e6c998dee827110c'"))
        self.assertNotIn("AG005", codes("import os\napi_key = os.environ['CLE']"))
        self.assertNotIn("AG005", codes("api_key = '<ta-cle-ici>'"))

    def test_code_mode_dans_une_cellule(self):
        self.assertIn("AG006", codes("import marimo._code_mode as cm"))

    def test_nom_indefini_et_nom_prive_lu_ailleurs(self):
        self.assertIn("AG007", codes("x = y + 1"))
        self.assertIn("AG007", codes("_df = 1", "z = _df"))
        self.assertNotIn("AG007", codes("x = y + 1", complet=False), "carnet partiel : on ne conclut pas")
        self.assertNotIn("AG007", codes("x = [i for i in range(3)]\nf = lambda t: t + len(x)"))

    def test_corps_au_format_fichier(self):
        self.assertIn("AG008", codes("x = 1\nreturn (x,)"))
        self.assertNotIn("AG008", codes("x = 1"))


class Avertissements(unittest.TestCase):
    def test_mutation_inter_cellules(self):
        base = "import pandas as pd\ndf = pd.DataFrame({'a': [1]})"
        self.assertIn("AG101", codes(base, "df['b'] = df['a'] * 2"))
        self.assertIn("AG101", codes(base, "df.dropna(inplace=True)"))
        self.assertIn("AG101", codes("l = [1]", "l.append(2)"))
        self.assertNotIn("AG101", codes(base, "df2 = df.assign(b=1)"))
        self.assertNotIn("AG101", codes("import os", "os.environ['X'] = '1'"), "un module n'est pas un objet du notebook")
        self.assertNotIn("AG101", codes("import polars as pl\ndf = pl.DataFrame()", "df.sort('a')"), "dernière expression : affichage")

    def test_ui_non_liee(self):
        self.assertIn("AG102", codes("mo.hstack([mo.ui.slider(0, 1, label='a')])"))
        self.assertIn("AG102", codes("curseurs = [mo.ui.slider(0, 1, label='a') for _ in range(3)]"))
        self.assertIn("AG102", codes("_s = mo.ui.slider(0, 1, label='a')\n_s"))
        self.assertNotIn("AG102", codes("curseurs = mo.ui.array([mo.ui.slider(0, 1) for _ in range(3)])"))
        self.assertNotIn("AG102", codes("f = mo.ui.slider(0, 1, label='a').form()"))
        self.assertNotIn("AG102", codes("t = mo.ui.slider(0, 3, label='a') if True else mo.ui.number(0, 1, label='b')"))
        self.assertNotIn("AG102", codes("import polars as pl\ndf = pl.DataFrame()", "mo.ui.table(df)"), "affichage seul")

    def test_bouton_sans_action(self):
        self.assertIn("AG103", codes("b = mo.ui.button(label='Go')\nb", "x = 1 if b.value else 0"))
        self.assertNotIn("AG103", codes("b = mo.ui.run_button(label='Go')\nb", "mo.stop(not b.value)"))

    def test_garde_if_valeur(self):
        self.assertIn("AG104", codes("b = mo.ui.run_button(label='Go')\nb", "if b.value:\n    r = 1", "print(r)"))
        self.assertNotIn("AG104", codes("b = mo.ui.run_button(label='Go')\nb", "mo.stop(not b.value)\nr = 1", "print(r)"))

    def test_sortie_perdue(self):
        self.assertIn("AG105", codes("mo.md('Titre')\nx = 1"))
        self.assertIn("AG105", codes("import polars as pl\ndf = pl.DataFrame()", "df.head()\ny = 2"))
        self.assertNotIn("AG105", codes("x = 1\nmo.md('Titre')"))
        self.assertNotIn("AG105", codes("mo.output.append(mo.md('a'))\nx = 1"))

    def test_boucle_bloquante_et_global(self):
        self.assertIn("AG106", codes("import time", "while True:\n    time.sleep(1)"))
        self.assertIn("AG107", codes("x = 1", "def f():\n    global x\n    x = 2"))

    def test_travail_lourd_sur_ui(self):
        avant = "n = mo.ui.slider(1, 9, label='n')\nn"
        self.assertIn("AG108", codes(avant, "import pymc as pm", "trace = pm.sample(draws=n.value)"))
        self.assertNotIn("AG108", codes("n = mo.ui.slider(1, 9, label='n').form()\nn", "import pymc as pm",
                                        "trace = pm.sample(draws=n.value)"))

    def test_dependance_non_declaree(self):
        source = fichier(["import marimo as mo\nimport polars as pl\nimport sklearn\nimport json"])
        trouves = [d for d in appliquer(lire_source(source)) if d.code == "AG111"]
        self.assertEqual([d.message.split("`")[1] for d in trouves], ["sklearn"])

    def test_entete_lu_sans_tomllib(self):
        from marimo_agent_kit.regles import _lire_entete_sans_tomllib, dependances_declarees

        entete = 'requires-python = ">=3.12"\ndependencies = [\n  "marimo",\n  "scikit-learn>=1.5",\n]\n\n[tool.pixi.dependencies]\nffmpeg = "*"\n'
        lu = _lire_entete_sans_tomllib(entete)
        self.assertEqual(lu["dependencies"], ["marimo", "scikit-learn>=1.5"])
        self.assertEqual(sorted(lu["tool"]["pixi"]["dependencies"]), ["ffmpeg"])
        self.assertEqual(dependances_declarees(entete), {"marimo", "scikit-learn", "ffmpeg"})


class Conseils(unittest.TestCase):
    def test_conseils_principaux(self):
        self.assertIn("AG201", codes("import matplotlib.pyplot as plt", "plt.plot([1])\nplt.show()"))
        self.assertIn("AG202", codes("x = 1", "print(f'x = {x}')"))
        self.assertIn("AG203", codes("mo.md('La précision atteint 0,93 sur le test.')"))
        self.assertNotIn("AG203", codes("mo.md('Voir la section 3.1 et https://arxiv.org/abs/1706.03762')"))
        self.assertIn("AG204", codes("_a = _b = _c = _d = _e = 1"))
        self.assertIn("AG208", codes("import polars as pl\ndf = pl.read_csv('/home/moi/donnees.csv')"))
        self.assertIn("AG209", codes("get, set_ = mo.state(0)"))
        self.assertIn("AG210", codes("s = mo.ui.slider(0, 1)\ns"))
        self.assertNotIn("AG210", codes("s = mo.ui.array([mo.ui.slider(0, 1)], label='réglages')\ns"))

    def test_entete_absente(self):
        source = fichier(["import marimo as mo"], entete="")
        self.assertIn("AG205", [d.code for d in appliquer(lire_source(source))])


class Moteur(unittest.TestCase):
    def test_chaque_regle_a_raison_et_correction(self):
        for code, regle in REGLES.items():
            with self.subTest(code=code):
                self.assertRegex(code, r"^AG\d{3}$")
                self.assertTrue(regle.resume and regle.pourquoi and regle.correction)
                self.assertIn(regle.gravite, ("erreur", "avertissement", "conseil"))

    def test_lignes_du_fichier(self):
        source = fichier(["import marimo as mo", "s = mo.ui.slider(0, 1, label='a')\nprint(s.value)\ns"])
        diag = next(d for d in appliquer(lire_source(source)) if d.code == "AG001")
        self.assertEqual(source.splitlines()[diag.ligne - 1].strip(), "print(s.value)")

    def test_cellules_proposees_jointes_au_notebook(self):
        carnet = lire_source(fichier(["import marimo as mo\nimport polars as pl", "df = pl.DataFrame({'a': [1]})"]))
        joint = joindre(carnet, ["df['b'] = 1", "y = inconnu"])
        trouves = {(d.code, d.cellule) for d in appliquer(joint)}
        self.assertIn(("AG101", 3), trouves)
        self.assertIn(("AG007", 4), trouves)

    def test_cellule_setup_numerotee_zero(self):
        for ouverture in ("with app.setup:", "with app.setup(hide_code=True):"):
            with self.subTest(ouverture=ouverture):
                source = (f"{ENTETE}import marimo\n\napp = marimo.App()\n\n{ouverture}\n"
                          "    import marimo as mo\n    import polars as pl\n\n\n"
                          "@app.cell\ndef _():\n    df = pl.DataFrame({'a': [1]})\n    return (df,)\n\n\n"
                          "@app.cell\ndef _(df):\n    df['b'] = 2\n    return\n")
                carnet = lire_source(source)
                self.assertEqual([(c.genre, c.numero) for c in carnet.cellules], [("setup", 0), ("cell", 1), ("cell", 2)])
                self.assertEqual(carnet.cellules[0].hide_code, "hide_code" in ouverture)
                diagnostics = appliquer(carnet)
                self.assertNotIn("AG007", [d.code for d in diagnostics])
                mutation = next(d for d in diagnostics if d.code == "AG101")
                self.assertEqual((mutation.cellule, mutation.etiquette), (2, "cellule 2"))

    def test_exemple_mauvais_et_exemple_propre(self):
        mauvais = {d.code for d in appliquer(lire_fichier(ICI / "exemples" / "mauvais.py"))}
        self.assertTrue({"AG001", "AG002", "AG003", "AG004", "AG101", "AG102", "AG103", "AG104", "AG105"} <= mauvais, mauvais)
        propre = [d for d in appliquer(lire_fichier(ICI / "exemples" / "propre.py")) if d.gravite != "conseil"]
        self.assertEqual(propre, [])


if __name__ == "__main__":
    unittest.main()
