<!-- wigglystuff 0.6.0, recopié de docs/reference/floating-panel.md (MIT) -->
# FloatingPanel API


`FloatingPanel` wraps any marimo content in a `position: fixed` panel that stays in view
while the notebook scrolls, is draggable by its header, and minimizes to just that header
with the `−` toggle. It is a marimo display helper rather than an `AnyWidget`, and the
wrapped content stays live — keep your own reference and read `.value` as usual.

Unlike [Pip](pip.md), which moves a widget into a separate Picture-in-Picture window, the
panel is an ordinary element in the page, so it also works inside an iframe such as molab.

See also: [Pip](pip.md) for floating a widget in a real OS window, and [Hint](hint.md) and
[WidgetDAG](widget-dag.md) for other marimo-only display helpers.

### `FloatingPanel`

`from wigglystuff.floating_panel import FloatingPanel`

```python
FloatingPanel(child: Any, *, corner: str = 'bottom-right', width: Optional[int] = None, collapsed: bool = False, title: str = '') -> None
```

Pin any marimo content in a draggable panel that floats above the page.

Wraps ``child`` in a ``position: fixed`` panel that stays in view while the
notebook scrolls, is draggable by its header, and can be minimized. Unlike
``Pip`` (which opens a separate Picture-in-Picture window), the panel is an
ordinary element in the page, so it also works inside an iframe such as
molab. This is a marimo-only display helper, not an ``AnyWidget``: display it
as the last expression of a cell and keep reading ``.value`` off the widgets
you passed in -- they stay fully live.

A ``FloatingPanel`` renders as ordinary marimo content, so it composes: the
``child`` can be a single ``mo.ui`` element, an ``mo.vstack``/``mo.hstack``
layout, a chart, an image, or a wigglystuff widget.

Args:
    child: The content to float -- anything marimo can render.
    corner: Where the panel starts before it is dragged: ``"top-left"``,
        ``"top-right"``, ``"bottom-left"`` or ``"bottom-right"``.
    width: Panel width in pixels. Defaults to ``None``, which shrink-wraps
        the panel to its content -- the right choice for most content, since
        marimo widgets keep their own width. Set an integer for a fixed
        width, e.g. to reflow long text.
    collapsed: Start minimized, showing only the draggable header. The
        header's ``−``/``+`` toggle collapses and expands it; nothing is ever
        fully dismissed, so the content is always one click away. Collapsing
        keeps the panel's expanded width so the header stays a readable bar.
    title: Optional caption shown on the header bar, next to the drag grip.
        It stays visible when the panel is minimized, so a collapsed panel is
        still identifiable. Long titles truncate with an ellipsis.

Example:
    ```python
    import marimo as mo
    from wigglystuff import FloatingPanel

    slider = mo.ui.slider(1, 10, label="N")
    FloatingPanel(slider, corner="top-right")
    ```


## Parameters

`FloatingPanel` is a display helper, not an `AnyWidget`, so it has no synced traitlets.
Everything is set once at construction.

| Parameter | Type | Notes |
| --- | --- | --- |
| `child` | any | The content to float. Anything marimo can render: an `mo.ui` element, an `mo.vstack`/`mo.hstack` layout, a figure, an image, another wigglystuff widget, or plain markdown. |
| `corner` | `str` | Where the panel starts before it is dragged: `"top-left"`, `"top-right"`, `"bottom-left"` or `"bottom-right"`. Anything else raises `ValueError`. |
| `width` | `int` or `None` | Panel width in pixels. Defaults to `None`, which shrink-wraps the panel to its content — the right choice for most content, since marimo widgets keep their own width. Set an integer for a fixed width, e.g. to reflow long text. A non-positive width raises `ValueError`. |
| `collapsed` | `bool` | Start minimized, showing only the draggable header. The header's `−`/`+` toggle collapses and expands it; nothing is ever fully dismissed. |

## Notes

`FloatingPanel` is a marimo-only display helper. A companion overlay reaches into
marimo's rendered DOM to build the drag header, pin the panel, and — crucially —
portal the panel to `document.body` so its `z-index` wins over every cell (a
panel left inside a cell is painted under any cell marimo raises on hover). It is
not wired for plain Jupyter and raises a clear `RuntimeError` there. Both
`marimo edit` and `marimo run` work; marimo *script* mode (`python demo.py`) does
not, because there is no rendered DOM to draw into.

The floated content stays live and reactive. Keep your own reference to it and
read `.value` as usual — `FloatingPanel` never sits between you and your data:

```python
slider = mo.ui.slider(1, 10, label="N")
FloatingPanel(slider, corner="top-right")   # in one cell
slider.value                                 # still works in another
```

A panel can still be covered by marimo's *own* fixed chrome (the top search bar,
the corner action buttons); just drag it to a clear spot.

---
Démo : [`../demos/floating_panel.py`](../demos/floating_panel.py)
