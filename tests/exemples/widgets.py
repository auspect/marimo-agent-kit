# /// script
# requires-python = ">=3.11"
# dependencies = ["marimo", "numpy", "wigglystuff==0.6.0"]
# ///
# Le motif du skill wigglystuff : un widget par cellule, lié à un nom public, lu ailleurs.

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    from wigglystuff import FloatingPanel, Slider2D, TangleDistribution, TangleSlider


@app.cell
def _():
    mo.md("""
    # Un a priori et un point de départ

    Règle la loi a priori dans la phrase, puis déplace le point de départ de l'optimisation.
    """)
    return


@app.cell
def _():
    a_priori = mo.ui.anywidget(TangleDistribution("norm", params={"loc": 0.0, "scale": 1.0}, template="N({loc:.1f}, {scale:.1f})"))
    nb_tirages = mo.ui.anywidget(TangleSlider(amount=500, min_value=100, max_value=5000, step=100, suffix=" tirages"))
    mo.md(f"La moyenne suit {a_priori} ; on en tire {nb_tirages}.")
    return a_priori, nb_tirages


@app.cell
def _(a_priori, nb_tirages):
    # `committed_amount` ne change qu'au relâcher : le tirage ne se refait pas à chaque pixel
    tirages = a_priori.widget.sample(int(nb_tirages.committed_amount), seed=0)
    mo.md(f"Moyenne empirique : **{np.mean(tirages):.3f}** sur {len(tirages)} tirages.")
    return


@app.cell
def _():
    depart = mo.ui.anywidget(Slider2D(x=0.5, y=-0.5, x_bounds=(-2.0, 2.0), y_bounds=(-2.0, 2.0), width=260, height=260))
    FloatingPanel(depart, title="Point de départ")
    return (depart,)


@app.cell
def _(depart):
    distance = float(np.hypot(depart.x, depart.y))
    mo.md(f"Départ en ({depart.x:.2f}, {depart.y:.2f}), à {distance:.2f} de l'origine.")
    return


if __name__ == "__main__":
    app.run()
