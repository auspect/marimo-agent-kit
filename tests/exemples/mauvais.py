# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "polars"]
# ///
# Les erreurs qu'un agent peu habitué à marimo écrit souvent, une par cellule.
# Ce fichier sert aux essais et à la démonstration : il ne doit pas être corrigé.

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import asyncio
    return asyncio, mo, pl


@app.cell
def _(pl):
    ventes = pl.DataFrame({"mois": [1, 2, 3, 4], "montant": [120.0, 95.5, 143.2, 110.0]})
    return (ventes,)


@app.cell
def _(ventes):
    ventes.sort("mois", descending=True)
    ventes["montant"].append(ventes["montant"].head(1))
    return


@app.cell
def _(mo):
    seuil = mo.ui.slider(0, 200, value=100, label="Seuil")
    print("seuil choisi :", seuil.value)
    seuil
    return (seuil,)


@app.cell
def _(mo, ventes):
    moyenne = ventes["montant"].mean()
    mo.md("La moyenne des ventes vaut {moyenne}.")
    return (moyenne,)


@app.cell
def _(mo):
    mo.md("## Ventes au-dessus du seuil")
    filtres = [mo.ui.checkbox(label=f"Mois {m}") for m in range(1, 5)]
    mo.hstack(filtres)
    return (filtres,)


@app.cell
def _(ventes):
    display(ventes)
    return


@app.cell
def _(asyncio):
    async def charger():
        return 42

    reponse = asyncio.run(charger())
    return (reponse,)


@app.cell
def _(mo):
    lancer = mo.ui.button(label="Calculer")
    lancer
    return (lancer,)


@app.cell
def _(lancer, seuil, ventes):
    if lancer.value:
        au_dessus = ventes.filter(ventes["montant"] > seuil.value)
    return (au_dessus,)


@app.cell
def _(au_dessus):
    au_dessus
    return


if __name__ == "__main__":
    app.run()
