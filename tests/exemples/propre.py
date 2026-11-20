# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "polars"]
# ///
# La même analyse que `mauvais.py`, écrite comme marimo l'attend.

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import polars as pl


@app.cell
def _():
    mo.md("""
    # Ventes mensuelles

    Choisis un seuil, puis lance le calcul : la table montre les mois qui le dépassent.
    """)
    return


@app.cell
def _():
    ventes = pl.DataFrame({"mois": [1, 2, 3, 4], "montant": [120.0, 95.5, 143.2, 110.0]})
    ventes_triees = ventes.sort("mois", descending=True)
    ventes_triees
    return (ventes,)


@app.cell
def _(ventes):
    moyenne = ventes["montant"].mean()
    mo.md(f"La moyenne des ventes vaut **{moyenne:.1f}**.")
    return


@app.cell
def _():
    seuil = mo.ui.slider(0, 200, value=100, label="Seuil de montant", show_value=True)
    mois = mo.ui.array([mo.ui.checkbox(value=True, label=f"Mois {m}") for m in range(1, 5)], label="Mois retenus")
    lancer = mo.ui.run_button(label="Calculer")
    mo.vstack([seuil, mois, lancer])
    return lancer, mois, seuil


@app.cell
async def _():
    async def charger():
        return 42

    reponse = await charger()
    return


@app.cell
def _(lancer, mois, seuil, ventes):
    mo.stop(not lancer.value, mo.md("Clique sur **Calculer** pour filtrer."))
    retenus = [m for m, coche in zip(range(1, 5), mois.value) if coche]
    au_dessus = ventes.filter((pl.col("montant") > seuil.value) & pl.col("mois").is_in(retenus))
    au_dessus
    return


if __name__ == "__main__":
    app.run()
