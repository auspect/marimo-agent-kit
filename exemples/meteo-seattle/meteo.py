import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Seattle sous la pluie")

with app.setup:
    import altair as alt
    import marimo as mo
    import polars as pl


@app.cell(hide_code=True)
def introduction():
    mo.md("""
    # Seattle sous la pluie

    Seattle passe pour la ville où il pleut tout le temps. Des années de
    relevés quotidiens, de 2012 à 2015, disent ce qu'il en est : combien de
    jours sont pluvieux, à quelle saison, et avec quelle intensité.
    """)
    return


@app.cell(hide_code=True)
def source_contexte():
    mo.md("""
    ## Les relevés

    Une ligne par jour : la hauteur de pluie en millimètres, les températures
    maximale et minimale, le vent et un type de temps. Les données viennent de
    la NOAA, par le jeu `seattle-weather` de vega-datasets.
    """)
    return


@app.cell
def chargement():
    fichier_meteo = mo.notebook_location() / "public" / "seattle-weather.csv"
    meteo = pl.read_csv(str(fichier_meteo), try_parse_dates=True)
    meteo
    return (meteo,)


@app.cell
def reperes():
    noms_mois = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre",
    ]
    seuils_pluie = {"0,1 mm": 0.1, "1 mm": 1.0, "5 mm": 5.0}
    classes_intensite = [
        ("moins de 1 mm", 0.0, 1.0),
        ("1 à 5 mm", 1.0, 5.0),
        ("5 à 10 mm", 5.0, 10.0),
        ("10 à 20 mm", 10.0, 20.0),
        ("20 mm et plus", 20.0, float("inf")),
    ]
    pluie_legere_mm, pluie_forte_mm = 5.0, 10.0
    return (
        classes_intensite,
        noms_mois,
        pluie_forte_mm,
        pluie_legere_mm,
        seuils_pluie,
    )


@app.cell
def formats(noms_mois):
    def nombre(valeur, decimales=0):
        return f"{valeur:.{decimales}f}".replace(".", ",")

    def pourcent(part):
        return f"{nombre(100 * part)} %"

    def date_fr(iso):
        _annee, _mois, _jour = (int(p) for p in iso.split("-"))
        _quantieme = "1er" if _jour == 1 else str(_jour)
        return f"{_quantieme} {noms_mois[_mois - 1]} {_annee}"

    return date_fr, nombre, pourcent


@app.cell(hide_code=True)
def controles_contexte():
    mo.md("""
    ## Les réglages

    Un jour compte comme pluvieux à partir d'un seuil de pluie. L'Organisation
    météorologique mondiale retient 1 mm. On peut aussi restreindre l'analyse à
    une année.
    """)
    return


@app.cell
def controles(meteo, seuils_pluie):
    annees_disponibles = [
        str(a) for a in meteo["date"].dt.year().unique().sort().to_list()
    ]
    annee = mo.ui.dropdown(
        options=["Toutes", *annees_disponibles], value="Toutes", label="Année"
    )
    seuil = mo.ui.dropdown(
        options=seuils_pluie, value="1 mm", label="Seuil d'un jour de pluie"
    )
    mo.hstack([annee, seuil], justify="start", gap=2, wrap=True)
    return annee, seuil


@app.cell
def jours_qualifies(meteo, seuil):
    jours = meteo.with_columns(
        pl.col("date").dt.year().alias("annee"),
        pl.col("date").dt.month().alias("mois"),
        (pl.col("precipitation") >= seuil.value).alias("pluie"),
    )
    return (jours,)


@app.cell
def selection(annee, jours):
    jours_choisis = (
        jours if annee.value == "Toutes" else jours.filter(pl.col("annee") == int(annee.value))
    )
    jours_choisis.head(10)
    return (jours_choisis,)


@app.cell(hide_code=True)
def saison_contexte():
    mo.md("""
    ## La saison fait tout

    La part de jours pluvieux et la hauteur moyenne de chaque mois montrent si
    la pluie est constante ou concentrée sur une saison.
    """)
    return


@app.cell
def par_mois(jours_choisis, noms_mois):
    _annees = jours_choisis["annee"].n_unique()
    climat_mensuel = (
        jours_choisis.group_by("mois")
        .agg(
            pl.col("pluie").mean().alias("part_pluie"),
            (pl.col("precipitation").sum() / _annees).alias("hauteur_mm"),
            pl.col("temp_max").mean().alias("temp_max"),
            pl.col("temp_min").mean().alias("temp_min"),
        )
        .sort("mois")
        .with_columns(
            pl.col("mois")
            .map_elements(lambda m: noms_mois[m - 1], return_dtype=pl.String)
            .alias("nom")
        )
    )
    climat_mensuel
    return (climat_mensuel,)


@app.cell
def graphique_mois(climat_mensuel):
    graphique_saison = (
        alt.Chart(climat_mensuel)
        .mark_bar(color="#3b6ea8")
        .encode(
            x=alt.X("nom:N", sort=None, title="Mois"),
            y=alt.Y("part_pluie:Q", axis=alt.Axis(format="%"), title="Jours de pluie"),
            tooltip=[
                alt.Tooltip("nom:N", title="Mois"),
                alt.Tooltip("part_pluie:Q", format=".0%", title="Jours de pluie"),
                alt.Tooltip("hauteur_mm:Q", format=".0f", title="Hauteur (mm)"),
            ],
        )
        .properties(title="Part des jours de pluie par mois", width="container", height=260)
    )
    graphique_saison
    return (graphique_saison,)


@app.cell(hide_code=True)
def intensite_contexte():
    mo.md("""
    ## Souvent, mais peu à la fois

    On classe les jours où il est tombé au moins 0,1 mm selon la hauteur du
    jour, puis on compare le nombre de jours de chaque classe à la part du
    volume total qu'elle apporte.
    """)
    return


@app.cell
def intensite(classes_intensite, jours_choisis):
    _mouilles = jours_choisis.filter(pl.col("precipitation") > 0)
    _volume = _mouilles["precipitation"].sum()
    _lignes = []
    for _nom, _bas, _haut in classes_intensite:
        _classe = _mouilles.filter(
            (pl.col("precipitation") >= _bas) & (pl.col("precipitation") < _haut)
        )
        _lignes.append(
            {
                "classe": _nom,
                "bas_mm": _bas,
                "haut_mm": None if _haut == float("inf") else _haut,
                "jours": _classe.height,
                "part_jours": _classe.height / max(_mouilles.height, 1),
                "part_volume": _classe["precipitation"].sum() / _volume if _volume else 0.0,
            }
        )
    intensite_pluie = pl.DataFrame(_lignes)
    intensite_pluie
    return (intensite_pluie,)


@app.cell
def graphique_intensite(intensite_pluie):
    _long = intensite_pluie.unpivot(
        index="classe", on=["part_jours", "part_volume"], variable_name="mesure", value_name="part"
    ).with_columns(
        pl.col("mesure").replace({"part_jours": "Jours", "part_volume": "Volume"})
    )
    graphique_pluie = (
        alt.Chart(_long)
        .mark_bar()
        .encode(
            y=alt.Y("classe:N", sort=None, title="Hauteur du jour"),
            x=alt.X("part:Q", axis=alt.Axis(format="%"), title="Part"),
            yOffset="mesure:N",
            color=alt.Color(
                "mesure:N",
                scale=alt.Scale(range=["#3b6ea8", "#c8553d"]),
                title=None,
            ),
            tooltip=[
                alt.Tooltip("classe:N", title="Classe"),
                alt.Tooltip("mesure:N", title="Mesure"),
                alt.Tooltip("part:Q", format=".0%", title="Part"),
            ],
        )
        .properties(title="Jours de pluie et volume, par classe", width="container", height=240)
    )
    graphique_pluie
    return (graphique_pluie,)


@app.cell
def figures_papier(graphique_pluie, graphique_saison):
    # Une vue PDF redessine chaque figure à la largeur où elle la place. Une
    # largeur « container » ne vaut que dans un navigateur : le papier reçoit
    # donc sa propre version, de largeur fixe.
    figure_saison = graphique_saison.properties(width=560, height=240)
    figure_pluie = graphique_pluie.properties(width=360, height=220)
    mo.vstack([figure_saison, figure_pluie])
    return


@app.cell(hide_code=True)
def annees_contexte():
    mo.md("""
    ## D'une année à l'autre

    Les totaux annuels se calculent sur toutes les années, avec le seuil
    choisi, pour situer l'année retenue parmi les autres.
    """)
    return


@app.cell
def par_annee(jours):
    bilan_annuel = (
        jours.group_by("annee")
        .agg(
            pl.col("precipitation").sum().alias("hauteur_mm"),
            pl.col("pluie").sum().alias("jours_pluie"),
            pl.col("pluie").mean().alias("part_pluie"),
            pl.col("temp_max").mean().alias("temp_max"),
        )
        .sort("annee")
    )
    bilan_annuel
    return (bilan_annuel,)


@app.cell
def series(jours_choisis):
    _suites = (
        jours_choisis.select("date", "pluie")
        .with_columns(pl.col("pluie").rle_id().alias("suite"))
        .group_by("suite", "pluie")
        .agg(pl.len().alias("jours"), pl.col("date").min().alias("debut"), pl.col("date").max().alias("fin"))
    )

    def _plus_longue(pluvieuse):
        _ligne = _suites.filter(pl.col("pluie") == pluvieuse).sort("jours", "debut", descending=[True, False]).row(0, named=True)
        return {"jours": _ligne["jours"], "debut": _ligne["debut"].isoformat(), "fin": _ligne["fin"].isoformat()}

    plus_longues_series = {"pluie": _plus_longue(True), "sec": _plus_longue(False)}
    plus_longues_series
    return (plus_longues_series,)


@app.cell
def synthese_chiffres(
    annee,
    bilan_annuel,
    climat_mensuel,
    intensite_pluie,
    jours_choisis,
    pluie_forte_mm,
    pluie_legere_mm,
    plus_longues_series,
    seuil,
):
    _humide = climat_mensuel.sort("part_pluie", descending=True).row(0, named=True)
    _sec = climat_mensuel.sort("part_pluie").row(0, named=True)
    _legers = intensite_pluie.filter(pl.col("haut_mm") <= pluie_legere_mm)
    _forts = intensite_pluie.filter(pl.col("bas_mm") >= pluie_forte_mm)
    synthese = {
        "annee": annee.value,
        "seuil": seuil.selected_key,
        "seuil_mm": seuil.value,
        "debut": jours_choisis["date"].min().isoformat(),
        "fin": jours_choisis["date"].max().isoformat(),
        "jours": jours_choisis.height,
        "jours_pluie": int(jours_choisis["pluie"].sum()),
        "part_pluie": float(jours_choisis["pluie"].mean()),
        "hauteur_annuelle_mm": round(
            jours_choisis["precipitation"].sum() / jours_choisis["annee"].n_unique()
        ),
        "mois_humide": _humide["nom"],
        "part_mois_humide": float(_humide["part_pluie"]),
        "mois_sec": _sec["nom"],
        "part_mois_sec": float(_sec["part_pluie"]),
        "legers_mm": pluie_legere_mm,
        "forts_mm": pluie_forte_mm,
        "part_jours_legers": float(_legers["part_jours"].sum()),
        "part_volume_forts": float(_forts["part_volume"].sum()),
        "serie_pluie": plus_longues_series["pluie"],
        "serie_seche": plus_longues_series["sec"],
        "annee_plus_humide": int(bilan_annuel.sort("hauteur_mm", descending=True)["annee"][0]),
        "annee_plus_seche": int(bilan_annuel.sort("hauteur_mm")["annee"][0]),
    }
    synthese
    return (synthese,)


@app.cell
def messages_redaction(date_fr, nombre, pourcent, synthese):
    _periode = (
        f"de {synthese['debut'][:4]} à {synthese['fin'][:4]}"
        if synthese["annee"] == "Toutes"
        else f"en {synthese['annee']}"
    )
    messages = {
        "periode": f"du {date_fr(synthese['debut'])} au {date_fr(synthese['fin'])}",
        "titre": f"Il pleut un jour sur {nombre(1 / synthese['part_pluie'], 1)} à Seattle",
        "chapeau": (
            f"{_periode.capitalize()}, {pourcent(synthese['part_pluie'])} des jours "
            f"reçoivent au moins {synthese['seuil']} de pluie, soit "
            f"{synthese['jours_pluie']} jours sur {synthese['jours']}."
        ),
        "saison": (
            f"La pluie suit la saison : {pourcent(synthese['part_mois_humide'])} des jours "
            f"en {synthese['mois_humide']}, {pourcent(synthese['part_mois_sec'])} en "
            f"{synthese['mois_sec']}."
        ),
        "intensite": (
            f"{pourcent(synthese['part_jours_legers'])} des jours mouillés reçoivent moins "
            f"de {nombre(synthese['legers_mm'])} mm, mais les jours de "
            f"{nombre(synthese['forts_mm'])} mm et plus apportent "
            f"{pourcent(synthese['part_volume_forts'])} du volume."
        ),
        "series": (
            f"La plus longue suite de jours de pluie dure {synthese['serie_pluie']['jours']} jours, "
            f"la plus longue suite sèche {synthese['serie_seche']['jours']} jours."
        ),
        "hauteur": (
            f"Il tombe en moyenne {nombre(synthese['hauteur_annuelle_mm'])} mm par an "
            f"{_periode}."
        ),
    }
    mo.md("\n\n".join(f"- {texte}" for texte in messages.values()))
    return (messages,)


@app.cell
def restitution(
    bilan_annuel,
    climat_mensuel,
    intensite_pluie,
    jours_choisis,
    messages,
    synthese,
):
    donnees_vues = {
        "synthese": synthese,
        "messages": messages,
        "mois": climat_mensuel.to_dicts(),
        "annees": bilan_annuel.to_dicts(),
        "intensite": intensite_pluie.to_dicts(),
        "source": {
            "nom": "NOAA, jeu seattle-weather de vega-datasets 3.3.1",
            "lien": "https://github.com/vega/vega-datasets",
        },
    }
    # Une série longue voyage en tableau Arrow, pas en JSON : l'export Prepared
    # limite le nombre de valeurs JSON d'un état.
    jours_vue = jours_choisis.select(
        pl.col("date").dt.strftime("%Y-%m-%d"),
        "precipitation",
        "pluie",
    )
    mo.md(
        f"Valeurs prêtes pour les vues : {jours_vue.height} jours, "
        f"{len(donnees_vues['mois'])} mois, {len(donnees_vues['intensite'])} classes."
    )
    return


@app.cell(hide_code=True)
def conclusion(messages):
    mo.md(f"""
    ## En bref

    {messages["chapeau"]} {messages["saison"]} {messages["intensite"]}
    """)
    return


if __name__ == "__main__":
    app.run()
