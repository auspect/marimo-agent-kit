<!-- wigglystuff 0.6.0, recopié de docs/reference/widget-flow.md (MIT) -->
# WidgetFlow API


`WidgetFlow` is a marimo display helper rather than an AnyWidget. It lays live
widgets (or any renderable: charts, images, `mo.stat`, ...) out as a layered
DAG in the style of [FormulaDAG](formula-dag.md). You pass the widgets and the
arrows between them as pairs of the same objects. You can also skip the edge
list: `WidgetFlow.from_widgets([...])` reads the edges off marimo's dataflow
graph and captions each widget with its variable name. The widgets stay live
and reactive, because the flow only arranges references to them.

The layout is in your hands where it matters. Edges take labels, colours,
dashes and explicit `exit`/`enter` ports, and ported arrows route around the
other widgets. `beside` puts a widget next to the one it feeds, `layers` pins
a widget to a later layer, and `align` packs every layer onto one shared grid,
so a chain of widgets down a column gets straight arrows. `notes` hang an
explanatory note beside a widget.

Parts of the flow can be hidden and brought back. Widgets in `collapsible`
get a hover button that folds them to a pill showing their caption. `groups`
draw a dashed frame whose tab folds a whole stretch of the flow into one pill,
and the arrows in and out of the group re-aim at the pill. Folding happens in
the browser, so nothing is laid out again and every widget keeps its state.
Nest one `WidgetFlow` inside another to treat a sub-flow as a single node.

See also: [WidgetDAG](widget-dag.md) for a simpler column layout,
[FormulaDAG](formula-dag.md) for formulas wired by `\use{name}`, and
[Hint](hint.md) for a single arrow from a note to a widget.

### `WidgetFlow`

`from wigglystuff.widget_flow import WidgetFlow`

```python
WidgetFlow(nodes, edges, *, direction='down', notes=None, ports=None, labels=False, layers=None, beside=None, align='center', collapsible=None, collapsed=None, groups=None, theme='auto')
```

Lay live widgets out as a DAG, in the style of ``FormulaDAG``.

Pass the widgets (or any renderable: charts, images, ``mo.stat``, ...) as a
list, and the arrows between them as pairs of those same objects. The
widgets stay live and reactive; this only arranges references to them. To
skip the edge list, ``WidgetFlow.from_widgets`` reads the arrows off
marimo's own dataflow graph.

This is a marimo-only display helper: the arrow overlay reaches into
marimo's rendered DOM, so it does not work in plain Jupyter.

Args:
    nodes: The widgets, in reading order. Each object may appear once.
    edges: ``(src, dst)``, ``(src, dst, "label")`` or ``(src, dst, opts)``
        tuples of the widget objects. ``opts`` is a dict with any of
        ``label`` (plain text beside the arrow), ``exit``/``enter`` (where
        the arrow leaves its source and lands on its target: ``"top"``,
        ``"bottom"``, ``"left"`` or ``"right"``, or a ``(side, position)``
        pair with a position between 0 and 1), ``color`` (any CSS color)
        and ``dashed`` (``True`` for a dashed line).
    direction: ``"down"`` (layers top to bottom) or ``"right"`` (layers
        left to right).
    notes: ``(widget, note)`` pairs. The note (a ``str`` renders as
        markdown, so LaTeX works; any other object renders as-is) sits
        beside the widget with a short arrow onto it.
    ports: ``(src, dst, opts)`` triples that apply ``opts`` (the same dict
        as above) to an arrow that is drawn anyway -- the way to label,
        colour or re-port an edge you didn't spell out, e.g. one
        ``from_widgets`` inferred.
    labels: Captions under the widgets. ``True`` captions each widget with
        the variable it is bound to (needs a marimo kernel),
        ``(widget, "text")`` pairs pick the captions yourself, ``False``
        (default) shows none.
    layers: ``(widget, n)`` pairs push a widget down to at least layer
        ``n`` (0 is the first); whatever depends on it moves with it.
    beside: ``(widget, anchor)`` pairs put ``widget`` in ``anchor``'s
        layer, right after it across the flow (to its right going down,
        below it going right). A third item ``"before"`` puts it right
        before the anchor instead (to its left going down, above it going
        right); ``"after"`` is the default. An arrow between the two
        connects their facing sides unless its ``exit``/``enter`` say
        otherwise. Several widgets on one side of an anchor follow in the
        order given.
    align: where each layer's widgets sit. ``"center"`` (default) centres
        every layer on its own. ``"left"`` or ``"right"`` going down
        (``"top"`` or ``"bottom"`` going right) put all layers on one grid
        packed to that side: the first widget of every layer shares a
        column (the last one, packing right), centred in it, so a chain of
        widgets down that column gets straight arrows.
    collapsible: Widgets that get a small button (top-right, on hover)
        that folds them to a pill showing just their caption, and back.
        Arrows keep landing on the pill and nothing else moves. Fold a
        nested ``WidgetFlow`` to hide a whole group at once.
    collapsed: Widgets that start folded (they're collapsible too).
        Folding happens in the browser; this only sets where it starts.
    groups: ``(label, widgets)`` pairs, or ``(label, widgets,
        "collapsed")`` to start folded. A group gets a faint dashed frame
        with a tab carrying its label; the tab folds the whole group into
        one pill, and the arrows in and out of it land on the pill. A
        widget is in at most one group, and a group must hold every
        widget on a path between two of its own.
    theme: ``"auto"`` (follow the notebook), ``"light"`` or ``"dark"``.

Widgets are referred to by the objects themselves, so options that name a
widget take ``(widget, value)`` pairs rather than dicts: charts and marimo
UI elements can't be dict keys.

The look is tweakable from CSS: ``--wf-edge``, ``--wf-note``, ``--wf-ink``,
``--wf-layer-gap`` and ``--wf-node-gap`` on the ``.wf`` root.

Example:
    ```python
    WidgetFlow(
        [n_points, noise, data_chart, degree, fit_chart],
        edges=[
            (n_points, data_chart),
            (noise, data_chart, "σ"),
            (data_chart, fit_chart, {"label": "x, y", "color": "#c2410c"}),
            (degree, fit_chart, {"enter": "right"}),
        ],
        notes=[(noise, "std of the gaussian noise")],
    )
    ```

    Left-align the layers and put ``degree`` right of the chart it feeds:

    ```python
    WidgetFlow.from_widgets(
        [n_points, noise, data_chart, degree, fit_chart],
        align="left",
        beside=[(degree, fit_chart)],
    )
    ```

    Let the data chart fold away, and fold the fitting step as a whole,
    starting folded:

    ```python
    WidgetFlow.from_widgets(
        [n_points, noise, data_chart, degree, fit_chart],
        collapsible=[data_chart],
        groups=[("fit", [degree, fit_chart], "collapsed")],
    )
    ```


## Folding parts of the flow

```python
WidgetFlow(
    [drawing, X, noise, X_noisy, Z, weights, Y, angle, plots],
    edges=[...],
    collapsible=[drawing, plots],              # hover button on these
    groups=[("Z → Y", [Z, weights, Y, angle])],  # dashed frame + tab
    collapsed=[plots],                         # start folded
)
```

A group must include every widget on a path between two of its own widgets,
because the pill replaces them all. Arrows that end up joining the same pair
of nodes once the group folds stay separate when they land in different
spots.

## Notes

`WidgetFlow` is a marimo-only display helper. Its arrow overlay reaches into
marimo's rendered DOM to draw in the same coordinate space as the widgets, so
it does not work in plain Jupyter. In Jupyter it raises a clear error instead
of printing a silent repr.

---
Démo : [`../demos/widget_flow.py`](../demos/widget_flow.py)
