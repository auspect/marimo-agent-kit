<!-- wigglystuff 0.6.0, recopié de docs/reference/pip.md (MIT) -->
# Pip API

`Pip` wraps a widget and adds a button to its top-right corner. Pressing that
button moves the widget into a window that floats above other windows,
including other applications, and leaves a placeholder in the notebook that
brings it back. This is the browser's [Document Picture-in-Picture][pip-api]
window, not a second browser tab.

The wrapped widget is the same object in both places, so a `Pip` can be put
around an existing widget without changing the code that reads it:

```python
import marimo as mo
from wigglystuff import GridDraw, Pip

sketch = mo.ui.anywidget(GridDraw(rows=6, cols=6, width=300, height=300))
panel = mo.ui.anywidget(Pip(sketch, width=340, height=360))
panel
```

```python
sketch.widget.dots  # the same trait, wherever the grid is drawn
```

Pop the grid out, put the floating window beside something worth copying from,
and draw in it: the clicks and drags belong to that window, and the dots land
back in the notebook.

Wrapping the child in `mo.ui.anywidget` is what makes cells that read it re-run
as it changes; a bare widget still updates in Python, but nothing re-runs.

Only a click can open the window. Closing it can be done by the reader, from
the placeholder or the window's own controls, or from Python by setting
`floating` to `False`.

[pip-api]: https://developer.mozilla.org/en-US/docs/Web/API/Document_Picture-in-Picture_API

## A separate window is a separate document

The floating window is created with the browser's
[Document Picture-in-Picture][pip-api] API. It is not a browser tab and not an
iframe: it is a document of its own, with its own `window` and `document`,
displayed in a window the operating system keeps above others. Both of this
widget's constraints follow from that.

**It exists only where the API does.** Chromium 116 and Firefox 151 implement
it; Safari does not, and there the button is not drawn and the child stays
inline. A tab is allowed a single such window, so opening a second `Pip` closes
the first, which restores its inline view. The request must also come from a
top-level page, so a notebook displayed inside an iframe cannot open one — which
is why the demo below is a link rather than an embed.

**Events and styles belong to the window they happen in.** A widget that follows
the pointer by listening on `window` — the usual way to keep tracking a drag
after the pointer leaves the element — is listening to the *notebook's* window,
and so hears nothing while it floats. Dragging such a widget does nothing until
it comes back. Widgets that capture the pointer on their own element are
unaffected, because the events never leave the element:

| Dragging works while floating | Dragging stops while floating |
| --- | --- |
| [GridDraw](grid-draw.md), [CurveEditor](curve-editor.md), [BezierCurve](bezier-curve.md), [HoverSlider](hover-slider.md), [ThreeWidget](three-widget.md) | [Knob](knob.md), [Fader](fader.md), [Matrix](matrix.md), [TangleSlider](tangle.md), [Slider2D](slider2d.md), [CircularSlider](circular-slider.md) |

Widgets driven by clicks, buttons or text entry work in both places either way.

Styles arrive by the same rule, with one thing carried across deliberately. A
widget's own stylesheet is mounted into the floating window, in that window's
realm, so it is styled there. Its light and dark rules are usually selected by
a class the notebook sets on an ancestor, which the floating document does not
have, so `Pip` copies that class over and keeps it in step with the notebook.
What is not copied is the notebook's own CSS, so a widget drawn with the
notebook's classes or variables, rather than its own, looks unstyled while
floating. No widget in this collection is.

Try it as a full page:
[demos/pip.py on molab](https://molab.marimo.io/github/koaning/wigglystuff/blob/main/demos/pip.py/wasm?utm_source=wigglystuff).

### `Pip`

`from wigglystuff.pip import Pip`

```python
Pip(child: Any, *, width: int = 400, height: int = 300, **kwargs: Any) -> None
```

A wrapper that floats another widget in a picture-in-picture window.

A `Pip` draws the widget it wraps inline, with a button in the top-right
corner. Pressing that button moves the widget into a window that floats
above other windows, including other applications, and leaves a placeholder
in the notebook that brings it back.

The wrapped widget is the same object in both places. Its traits, observers
and value are unaffected by where it is drawn, so a `Pip` can be dropped
around an existing widget without changing any code that reads it.

Only a click can open the window; the browser refuses to open one on a
program's request. Closing it can be done from either side: by the reader,
or by setting `floating` to `False`.

Warning:
    This is the browser's [Document Picture-in-Picture](https://developer.mozilla.org/en-US/docs/Web/API/Document_Picture-in-Picture_API)
    window, and it inherits two limits from that API.

    The first is availability. Chromium and Firefox implement it; Safari does
    not, and there the button is not drawn and the child stays inline. A tab
    is allowed one such window, so opening a second `Pip` closes the first,
    which restores its inline view. And the request must come from a
    top-level page, so a notebook inside an iframe cannot open one.

    The second is that the window is a document of its own, with its own
    `window` and `document`, separate from the notebook's. A widget that
    listens on the notebook's `window` — as most drag handling does, to
    follow the pointer outside the element — never receives the events that
    happen while it floats, and stops responding to dragging until it comes
    back. Widgets that use pointer capture on their own element work in both
    places. Styles reach the window along the same lines: the child's own
    stylesheet is mounted into it, and the notebook's light or dark setting
    is mirrored so the two match, but the notebook's own classes and
    variables are not, so a widget drawn with those looks unstyled there.

Args:
    child: The widget to wrap. Any widget with a `model_id` works.
    width: Width of the floating window in pixels, when first opened.
    height: Height of the floating window in pixels, when first opened.

Attributes:
    floating: Whether the child is in the floating window. Setting this to
        `False` closes the window. Setting it to `True` has no effect and
        reports a warning to the browser console.

Raises:
    traitlets.TraitError: If `child` is not a widget.
    ValueError: If `width` or `height` is not positive.

Examples:
    A grid that can be drawn on while it floats beside another window:

    ```python
    import marimo as mo
    from wigglystuff import GridDraw, Pip

    sketch = GridDraw(rows=6, cols=6, width=300, height=300)
    Pip(sketch, width=340, height=360)
    ```

    The wrapped widget is read the same way in either place:

    ```python
    sketch.dots
    ```

    In marimo, wrap the child in `mo.ui.anywidget` when cells that read it
    should re-run as it changes, and reach the widget through `.widget`:

    ```python
    sketch = mo.ui.anywidget(GridDraw(rows=6, cols=6))
    panel = mo.ui.anywidget(Pip(sketch, width=340, height=360))
    panel
    ```

    ```python
    sketch.widget.dots  # this cell re-runs as the grid is drawn on
    ```

    Closing the window from Python:

    ```python
    panel.widget.floating = False
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `child` | WidgetTrait | `None` |
| `floating` | Bool | `False` |
| `height` | Int | `300` |
| `width` | Int | `400` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `child` | widget | The wrapped widget; serialized to the wire as an `anywidget:<model_id>` reference. |
| `width` | `int` | Initial width of the floating window, in pixels. |
| `height` | `int` | Initial height of the floating window, in pixels. |
| `floating` | `bool` | Whether the child is currently floating. Set `False` to close the window; setting `True` is refused (needs a user gesture). |
