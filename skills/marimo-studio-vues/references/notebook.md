# Un notebook qui sert plusieurs vues

Le modèle est `exemples/meteo-seattle/meteo.py` dans le dépôt marimo-agent-kit, et
`exemples/earthquakes.py` dans ce dossier pour l'exemple officiel.

## Ce que le notebook doit fournir

| Besoin des vues | Dans le notebook | Projection |
|---|---|---|
| Contrôles que le lecteur change | Une cellule nommée, par exemple `controles`, qui affiche `mo.hstack([annee, seuil])` | `<marimo-cell name="controles">`, `{{< marimo cell="controles" >}}` |
| Chiffres clés et tableaux agrégés | Un dictionnaire JSON, par exemple `donnees_vues` | `mo-value="donnees_vues"`, `marimo_value("donnees_vues.synthese")` |
| Phrases qui affirment | `donnees_vues["messages"]`, rédigées avec les valeurs interpolées | `{{< marimo value="donnees_vues.messages.saison" >}}` |
| Série longue, par exemple un an de relevés quotidiens | Un DataFrame à part, par exemple `jours_vue` | `mo-value="jours_vue"`, lu comme un tableau Arrow |
| Graphique pour l'écran | Un graphique Altair avec `width="container"` | `{{< marimo output="graphique_saison" >}}` |
| Graphique pour le papier | La même chose avec une largeur fixe : `graphique.properties(width=560, height=240)` | `marimo_output("figure_saison", width: 100%)` |

Une vue ne recopie jamais un chiffre ni un constat. Si une vue a besoin d'une phrase de plus,
ajoute-la aux `messages` du notebook. Les libellés d'interface, comme « Jours de pluie », restent
dans la vue.

## Règles apprises sur l'exemple

- **Rédige les constats dans le notebook.** Les quatre vues affichent le même titre, « Il pleut
  un jour sur 2,9 à Seattle », parce qu'il vient de `messages["titre"]`. Changer un contrôle
  change la phrase partout.
- **Arrondis dans le notebook ce qui s'affiche en deux endroits.** Python arrondit 1 106,5 à
  1 106, `Intl.NumberFormat` à 1 107. L'exemple range `round(...)` dans la synthèse, et formate
  les nombres sans séparateur de milliers des deux côtés.
- **Écris les seuils une fois.** Les bornes des classes et les seuils « pluie légère » et « pluie
  forte » sont des constantes nommées de la cellule `reperes`. Les messages et la légende des
  vues les lisent ; aucune vue n'écrit « 10 mm ».
- **Les contrôles des exports Prepared sont indépendants.** Un contrôle que Python recrée à
  partir d'un autre ne correspond à aucun état préparé. Dérive les valeurs en aval.
- **Les options d'un menu déroulant sont des libellés.** `mo.ui.dropdown(options={"1 mm": 1.0})`
  : `states.yaml` prend la liste `["1 mm"]`, le notebook lit `seuil.value == 1.0` et
  `seuil.selected_key == "1 mm"`.
- **Pas de date du jour, pas de réseau inutile.** Les données de l'exemple sont dans `public/`,
  lues par `mo.notebook_location() / "public" / "seattle-weather.csv"` : un export les embarque.

## Travailler dans le noyau

Le notebook tourne dans l'éditeur ; on le modifie et on relance ses cellules par `marimo pair`.
Un fichier Python passé à `--code-file` est exécuté dans le noyau, avec `await` permis au premier
niveau.

```python
import marimo_studio

workspace = marimo_studio.agent.current_workspace()
status = await workspace.status()
print(status.state_root, [vue.name for vue in status.views])
print(await workspace.view("grand-public").preview_url(runtime="server"))
```

Si tu modifies `notebook.py` sur le disque alors que l'éditeur tourne avec `--watch`, marimo
recharge le fichier et marque les cellules touchées « stale » sans les exécuter. Relance-les :

```python
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    perimees = [cid for cid, cell in ctx.cells.items() if cell.status == "stale"]
    for cid in perimees:
        ctx.run_cell(cid)
```

Le skill `marimo-pair` décrit le reste de l'API. Une vue ne voit les nouvelles valeurs qu'après
l'exécution des cellules : construire la vue ne relance pas le notebook.

## Vérifier le notebook

```bash
mak verifier notebook.py
```

Le kit trouve l'environnement pixi du projet et y exécute les cellules. Le notebook n'a pas
d'en-tête PEP 723, puisque `pyproject.toml` porte la configuration de Studio
(`references/environnement.md`) : rien ne pousse le kit vers un bac à sable uv. Si un notebook
garde un en-tête, ajoute `--bac-a-sable non` pour rester dans l'environnement pixi. Sur
l'exemple, le rapport dit `propre. 0 erreur, 0 avertissement`.
