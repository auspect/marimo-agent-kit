<!-- wigglystuff 0.6.0, recopié de docs/reference/neo4j-widget.md (MIT) -->
# Neo4jWidget API


`Neo4jWidget` takes a `neo4j` driver (or a `uri` plus `auth`), reads the database's
labels, relationship types and property keys up front, and puts a Cypher input above a
graph view of whatever the query returns. Clicking a node runs a follow-up query to
pull in its neighbors, so you can walk outward from a small result instead of writing
ever-longer Cypher. What is on screen stays readable from Python via `nodes`,
`relationships`, `selected_nodes` and `selected_relationships`.

It talks to a real database, so this page has no in-browser demo — [run it on
molab](https://molab.marimo.io/notebooks/nb_ghifaw8nRCuDAgc1UTajXU?utm_source=wigglystuff)
against your own server instead. See also: [GraphWidget](graph-widget.md) for graphs you
build in Python, [EdgeDraw](edge-draw.md) for sketching one by hand, and
[Treemap](treemap.md) for hierarchies rather than graphs.

## Who can run queries

Anyone who can see the widget can type Cypher into the query box, and it runs with the
credentials of the driver you passed in. By default (`read_only=True`) queries from the
query box run in a read-access session, so the database refuses writes such as `CREATE`
or `DETACH DELETE`; pass `read_only=False` to allow writes. `initial_query` and
`run_query()`, which you call from Python, are not restricted. When you publish a
notebook, also connect with a database account that only has read rights.

### `Neo4jWidget`

`from wigglystuff.neo4j_widget import Neo4jWidget`

```python
Neo4jWidget(driver=None, *, uri: Optional[str] = None, auth: Optional[tuple] = None, database: Optional[str] = None, width: int = 800, height: int = 500, max_nodes: int = 300, initial_query: Optional[str] = None, read_only: bool = True, **kwargs: Any) -> None
```

Interactive Neo4j graph explorer with Cypher query input.

Anyone who can see the widget can run Cypher through its query box with
the driver's credentials. By default (`read_only=True`) those queries run
in a read-access session, so writes such as `CREATE` or `DELETE` are
refused by the server. For published notebooks, also connect with a
database account that only has read rights.

Examples:
    ```python
    import marimo as mo
    from neo4j import GraphDatabase
    from wigglystuff import Neo4jWidget

    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    widget = mo.ui.anywidget(Neo4jWidget(driver))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `error` | Unicode | `''` |
| `height` | Int | `500` |
| `nodes` | List | |
| `query_running` | Bool | `False` |
| `relationships` | List | |
| `schema` | Dict | |
| `selected_nodes` | List | |
| `selected_relationships` | List | |
| `width` | Int | `800` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `width` | `int` | Widget width in pixels (default: 800). |
| `height` | `int` | Widget height in pixels (default: 500). |
| `schema` | `dict` | Auto-extracted node labels, relationship types, and property keys. |
| `nodes` | `list` | List of node dicts currently displayed. |
| `relationships` | `list` | List of relationship dicts currently displayed. |
| `error` | `str` | Last error message (empty when no error). |
| `query_running` | `bool` | Whether a query is currently executing. |
| `selected_nodes` | `list` | Element IDs of currently selected nodes. |
| `selected_relationships` | `list` | Element IDs of currently selected relationships. |
