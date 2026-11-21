<!-- wigglystuff 0.6.0, recopié de docs/reference/widget-dag.md (MIT) -->
# WidgetDAG API


`WidgetDAG` is a marimo display helper rather than an AnyWidget: it takes a mapping of
ids to renderables plus a list of `(src, dst)` edges, puts each node in a column
derived from its edge depth, and draws the connecting arrows. Think `mo.hstack`, except
the columns and the arrows come from the graph. The nodes stay live — a `Matrix` or
`Paint` embedded as a node is still editable — and `WidgetDAG.from_widgets([...])` lets
you skip the edge list entirely by reading marimo's own dataflow graph, one node per
cell.

See also: [GraphWidget](graph-widget.md) for a force-directed graph of data instead of
widgets, [EdgeDraw](edge-draw.md) for drawing a graph by hand, and
[ModuleTreeWidget](module-tree.md) for walking a PyTorch module hierarchy.

### `WidgetDAG`

`from wigglystuff.widget_dag import WidgetDAG`

```python
WidgetDAG(nodes, edges, layout=<function layered_layout at 0x7f4aada6e200>)
```

Lay widgets out as a DAG and draw the arrows -- like ``mo.hstack``, but
columns come from edge depth and the connections are drawn for you.

.. deprecated::
    ``WidgetDAG`` is deprecated in favour of ``WidgetFlow``, which draws
    FormulaDAG-style arrows and adds notes, edge labels, ports, captions and
    a ``direction`` switch. ``WidgetDAG.from_widgets([...])`` becomes
    ``WidgetFlow.from_widgets([...], direction="right")``; for
    ``WidgetDAG(nodes, edges)`` pass the widget objects as a list and the
    edges as pairs of objects. Constructing a ``WidgetDAG`` emits a
    ``FutureWarning``.

``nodes`` maps an id to any renderable (an input widget, an image, a chart
-- anything marimo can show). ``edges`` is a list of ``(src_id, dst_id)``.
``layout`` is ``(nodes, edges) -> {id: column}`` (default ``layered_layout``).
The widgets stay live and reactive; this only arranges references to them.

This is a marimo-only display helper: the arrow overlay reaches into
marimo's rendered DOM, so it is not wired for plain Jupyter.

Instead of spelling out ``edges`` by hand, ``WidgetDAG.from_widgets`` derives
them from marimo's own dataflow graph -- pass the widgets and the arrows
follow the notebook's dependency order (see that method).

Example:
    ```python
    import marimo as mo
    from wigglystuff import Matrix, WidgetDAG

    kernel = mo.ui.anywidget(Matrix(rows=3, cols=3))
    WidgetDAG(
        nodes={"kernel": kernel, "image": mo.image("cat.png"), "conv": out},
        edges=[("image", "conv"), ("kernel", "conv")],
    )
    ```


## Layout

A layout is any callable `(nodes, edges) -> {id: column}`. The default is
`layered_layout`; pass your own to `WidgetDAG(..., layout=...)` to swap in a
different algorithm.

### `layered_layout`

`from wigglystuff.widget_dag import layered_layout`

```python
layered_layout(nodes, edges)
```

Assign each node a layer (0 = first).

Longest-path layering, then pull every node forward to sit just before
its earliest child. That keeps edges between adjacent layers for
pipeline/tree shapes, so arrows stay inside the empty gaps between layers
and never cross a widget. Longer edges get routed through waypoint lanes.

A layout is just ``(nodes, edges) -> {id: layer}``; pass your own to
``WidgetDAG(..., layout=...)`` to swap in a different algorithm.


## Notes

`WidgetDAG` is a marimo-only display helper. Its arrow overlay reaches into
marimo's rendered DOM to draw connections in the same coordinate space as the
node boxes, so it is not wired for plain Jupyter. The nodes stay live and
reactive — embedding a widget (e.g. a `Matrix` or `Paint`) as a node keeps it
interactive, and editing it re-runs the cell that built the DAG.

---
Démo : [`../demos/widget_dag.py`](../demos/widget_dag.py)
