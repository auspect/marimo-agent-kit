<!-- wigglystuff 0.6.0, recopié de docs/reference/hint.md (MIT) -->
# Hint API


`Hint` wraps a widget and curves an arrow from a note to its edge, so a reader skimming
a notebook can tell which parts are interactive and why. It is a marimo display helper
rather than an `AnyWidget`, and the wrapped widget stays live — keep your own reference
and read `.value` as usual.

See also: [WidgetDAG](widget-dag.md) for arranging live widgets as a DAG and drawing the
arrows between them, [CellTour](cell-tour.md) for a stepped guided tour of a notebook,
and [AnnotationWidget](annotation.md) for collecting labels rather than explaining them.

### `Hint`

`from wigglystuff.hint import Hint`

```python
Hint(target: Any, note: Any, *, side: str = 'right', color: str = 'currentColor', gap: float = 3) -> None
```

Point an arrow at a widget and explain it, right in the notebook.

Wraps ``target`` and draws a curved arrow from ``note`` to the edge of the
target's box, so a reader knows what to interact with and why. This is a
marimo-only display helper, not an ``AnyWidget``: display it as the last
expression of a cell and keep reading ``.value`` off the widget you passed in.

A ``Hint`` renders as ordinary marimo content, so it composes: put several in
an ``mo.hstack``, drop one into an ``mo.md`` f-string, or nest one inside
another to hang two arrows off the same widget.

Args:
    target: The widget being annotated -- anything marimo can render.
    note: The explanation. A ``str`` is rendered with ``mo.md`` (so markdown
        and LaTeX work); any other object is rendered as-is.
    side: Where the note sits: ``"left"``, ``"right"``, ``"top"`` or
        ``"bottom"``.
    color: Any CSS color, applied to the arc and its arrowhead. Defaults to
        ``"currentColor"``, so the arc picks up the notebook's own text
        color and follows a light/dark theme switch for free.
    gap: Space between the two boxes, in marimo stack-gap units. The arc
        needs somewhere to live, so a little room helps.

Example:
    ```python
    import marimo as mo
    from wigglystuff import Hint

    slider = mo.ui.slider(1, 10, label="N")
    Hint(slider, "drag to change **N**")
    ```


## Parameters

`Hint` is a display helper, not an `AnyWidget`, so it has no synced traitlets.
Everything is set once at construction.

| Parameter | Type | Notes |
| --- | --- | --- |
| `target` | any | The thing being annotated. Anything marimo can render: an `mo.ui` element, another wigglystuff widget, a figure, an image, or plain markdown. |
| `note` | `str` or any | The explanation. A `str` goes through `mo.md`, so markdown and LaTeX work. Any other object is rendered as-is, e.g. `mo.md(...).callout()`. |
| `side` | `str` | Where the note sits: `"left"`, `"right"`, `"top"` or `"bottom"`. Anything else raises `ValueError`. |
| `color` | `str` | CSS color for the arc and its arrowhead. Defaults to `currentColor`, so the arc follows the notebook's text color and light/dark theme. |
| `gap` | `int` | Space between the widget and the note, in marimo stack-gap units. The arc needs a little room to live in. |

## Notes

`Hint` is a marimo-only display helper. Its arc overlay reaches into marimo's
rendered DOM to draw in the same coordinate space as the widget and note boxes,
so it is not wired for plain Jupyter and raises a clear `RuntimeError` there.
Both `marimo edit` and `marimo run` work; marimo *script* mode
(`python demo.py`) does not, because there is no rendered DOM to draw into.

The wrapped widget stays live and reactive. Keep your own reference to it and
read `.value` as usual — `Hint` never sits between you and your data:

```python
n = mo.ui.slider(1, 10, label="N")
Hint(n, "drag to change **N**")   # in one cell
n.value                            # still works in another
```

A `Hint` renders as ordinary marimo content, so it composes: drop several into an
`mo.hstack`, interpolate one into an `mo.md` f-string, use one as a `WidgetDAG`
node, or nest one inside another to hang a second arrow off the same widget.

### Sizing caveat

Anything that *measures* a `Hint` sees the bounding box of the widget **plus its
note**, because the note is laid out beside the widget inside the hint. Two
consequences:

- Nesting aims the outer arrow at the whole inner group, not at the widget.
- `WidgetDAG` routes edges to the left edge of a node, so prefer `side="right"`
  for hinted DAG nodes. A `side="left"` note would sit between the widget and
  the incoming arrow.

---
Démo : [`../demos/hint.py`](../demos/hint.py)
