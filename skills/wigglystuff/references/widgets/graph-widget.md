<!-- wigglystuff 0.6.0, recopié de docs/reference/graph-widget.md (MIT) -->
# GraphWidget API


`GraphWidget` takes nodes and edges from Python — plain strings, numbers or dicts —
and lays them out as a force-directed graph. Browser-side positions survive changes to
`nodes` and `edges`, so growing a graph from Python does not reshuffle the whole
picture, and clicks come back on `selected_nodes` and `selected_edges` for the rest of
the notebook to read.

See also: [EdgeDraw](edge-draw.md) for drawing the edges by hand instead of passing
them in, [Neo4jWidget](neo4j-widget.md) for querying a live Neo4j database, and
[WidgetDAG](widget-dag.md) for arranging live widgets as a DAG.

### `GraphWidget`

`from wigglystuff.graph_widget import GraphWidget`

```python
GraphWidget(nodes: 'Iterable[Any] | None' = None, edges: 'Iterable[Any] | None' = None, *, directed: 'bool' = True, bounded: 'bool' = True, width: 'int | None' = None, height: 'int' = 400, **kwargs: 'Any') -> 'None'
```

Programmatic force-directed graph widget.

``GraphWidget`` renders nodes and edges supplied from Python. Nodes may be
strings, numbers, or dicts. Edges may be ``(source, target)`` pairs or dicts
with ``source`` and ``target`` keys.

``width=None`` (the default) makes the widget fill its container's width
and reflow when the container resizes. Passing an integer ``width`` pins
the SVG to that exact pixel size. ``height`` is always an exact pixel
height (default 400).

Example:
    ```python
    import marimo as mo
    from wigglystuff import GraphWidget

    widget = mo.ui.anywidget(GraphWidget(nodes=["Alpha", "Beta"], edges=[("Alpha", "Beta")]))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `bounded` | Bool | `True` |
| `directed` | Bool | `True` |
| `edges` | List | |
| `height` | Int | `400` |
| `hovered_node` | Unicode | `None` |
| `nodes` | List | |
| `selected_edges` | List | |
| `selected_nodes` | List | |
| `width` | Int | `None` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `nodes` | `list[dict]` | Node dicts with normalized `id` and optional `name`, `size`, `color`, and `data`. |
| `edges` | `list[dict]` | Edge dicts with normalized `id`, `source`, `target`, and optional `name`, `width`, `color`, and `data`. |
| `directed` | `bool` | Draw directed edges when true. |
| `bounded` | `bool` | Keep nodes inside the visible SVG bounds when true. Disable it for graphs that should spread beyond the viewport and be explored with pan/zoom. |
| `width` | `int \| None` | Canvas width in pixels. `None` (default) makes the widget fill its container's width and reflow when the container resizes. |
| `height` | `int` | Canvas height in pixels (default `400`). |
| `selected_nodes` | `list[str]` | IDs of currently selected nodes. |
| `selected_edges` | `list[str]` | IDs of currently selected edges. |

## Layout Notes

`GraphWidget` preserves browser-side node positions when `nodes` or `edges`
change. Newly connected nodes are initialized near the existing endpoint they
attach to. Use `attach_node(source, name, ...)` when adding one new node plus
its connecting edge from Python; if `name` or `id` already resolves to a node,
only the edge is added. Use `detach_node(node)` to remove all edges attached to
a node while keeping the node visible, or `detach_node(node, delete=True)` to
remove the node too.

---
Démo : [`../demos/graphwidget.py`](../demos/graphwidget.py)
