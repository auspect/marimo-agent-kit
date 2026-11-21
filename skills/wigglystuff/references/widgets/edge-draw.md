<!-- wigglystuff 0.6.0, recopié de docs/reference/edge-draw.md (MIT) -->
# EdgeDraw API


`EdgeDraw` starts from a list of node labels and lets you drag from one node to another
to add a link, which arrives in Python on `links` as `{"source": ..., "target": ...}`
dicts. Reach for it when the graph is what you are trying to express rather than
something you already have in data: `get_adjacency_matrix()`, `get_neighbors()` and
`has_cycle()` turn the sketch into something you can compute on.

See also: [GraphWidget](graph-widget.md) for graphs supplied from Python rather than
drawn, [GridDraw](grid-draw.md) for dots and lines snapped to a grid, and
[Excalidraw](excalidraw.md) for freehand diagrams that are not meant to be parsed.

### `EdgeDraw`

`from wigglystuff.edge_draw import EdgeDraw`

```python
EdgeDraw(names: 'List[str]', height: 'int' = 400, width: 'int' = 600, directed: 'bool' = True, links: 'Optional[Iterable[Union[Sequence[str], dict]]]' = None) -> 'None'
```

Sketch node/link diagrams and sync edges as adjacency-friendly data.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import EdgeDraw

    graph = mo.ui.anywidget(EdgeDraw(names=["A", "B", "C", "D"]))
    graph
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `directed` | Bool | `True` |
| `height` | Int | `400` |
| `links` | List | |
| `names` | List | |
| `width` | Int | `600` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `names` | `list[str]` | Ordered node labels. |
| `links` | `list[dict]` | Link dicts with `source` and `target` keys. |
| `directed` | `bool` | Draw directed edges when true. |
| `width` | `int` | Canvas width in pixels. |
| `height` | `int` | Canvas height in pixels. |


---
Démo : [`../demos/edgedraw.py`](../demos/edgedraw.py)
