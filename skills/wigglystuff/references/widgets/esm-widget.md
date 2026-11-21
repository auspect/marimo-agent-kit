<!-- wigglystuff 0.6.0, recopié de docs/reference/esm-widget.md (MIT) -->
# EsmWidget API


`EsmWidget` is the escape hatch. You hand it a JavaScript ES module that
`export default { render }`, and it loads that module in the browser and calls `render`.
Because it is loaded as a real module, top-level `import` works, so any CDN library —
motion.dev, Observable Plot, d3, three.js — is one line away. The reason to use it is the
`data` traitlet: a JSON-able value synced both directions where a change fires
`change:data` in the browser without re-running `render`, so your module can tween toward
the new state instead of hard-cutting. Reach for it when nothing packaged fits and the
alternative is writing a whole anywidget from scratch.

See also: [ObservablePlot](observable-plot.md) for Observable Plot with the plumbing
already written, [ManimWeb](manim-web.md) for browser-side Manim scenes, and
[AltairWidget](altair-widget.md) for charts driven from Python instead of JS.

### `EsmWidget`

`from wigglystuff.esm_widget import EsmWidget`

```python
EsmWidget(code: Optional[str] = None, *, src: Optional[str] = None, data: Any = None, css: str = '', width: int = 500, height: int = 300, **kwargs: Any) -> None
```

Render an inline `ES module <https://developer.mozilla.org/docs/Web/JavaScript/Guide/Modules>`_ in a notebook.

This is a thin, library-agnostic runner. You hand it a JavaScript ES module
(the ``code``), and it loads that module in the browser and calls its
``render`` function. Because the module is loaded as a *real* ES module,
top-level ``import`` statements work — so you can pull any library straight
from a CDN (motion.dev, Observable Plot, d3, chart.js, three.js, …)::

    import { animate } from "https://cdn.jsdelivr.net/npm/motion@12/+esm";

The module must follow the standard `anywidget
<https://anywidget.dev/en/afm/>`_ contract — ``export default { render }`` —
where ``render`` receives ``{ model, el }``, may append to ``el``, and may
return a cleanup function.

The point of the widget is the ``data`` traitlet: a JSON-able value synced
both ways. Update it from Python and the browser sees a ``change:data``
event; set it from JS and Python sees the new value. Crucially, changing
``data`` does **not** re-run ``render`` — your module observes the change and
decides what to do, so animation libraries can *tween* toward the new state
instead of hard-cutting.

Examples:
    Tween on data change with motion.dev:

    ```python
    import marimo as mo
    from wigglystuff import EsmWidget

    w = EsmWidget(
        '''
        import { animate } from "https://cdn.jsdelivr.net/npm/motion@12/+esm";
        export default {
          render({ model, el }) {
            const box = document.createElement("div");
            box.style.cssText = "width:60px;height:60px;background:#e94560";
            el.appendChild(box);
            const draw = () => animate(box, { x: model.get("data").x }, { type: "spring" });
            draw();
            model.on("change:data", draw);
          }
        }
        ''',
        data={"x": 0},
        width=600,
        height=200,
    )
    mo.ui.anywidget(w)
    # ...then, from another cell:
    w.data = {"x": 240}   # the box springs to the new position
    ```

    Redraw on data change with Observable Plot:

    ```python
    EsmWidget(
        '''
        import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/+esm";
        export default {
          render({ model, el }) {
            const draw = () => el.replaceChildren(
              Plot.plot({ marks: [Plot.dot(model.get("data").points, { x: "x", y: "y" })] })
            );
            draw();
            model.on("change:data", draw);
          }
        }
        ''',
        data={"points": [{"x": 1, "y": 2}, {"x": 2, "y": 1}]},
    )
    ```

    Point at a local file or a URL instead of an inline string:

    ```python
    EsmWidget("widgets/chart.js")
    EsmWidget("https://example.com/widget.js")
    ```

The module is executed verbatim in the browser, so only pass JavaScript you
trust (typically your own).

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `code` | Unicode | `''` |
| `css` | Unicode | `''` |
| `data` | Any | `None` |
| `error` | Unicode | `''` |
| `height` | Int | `300` |
| `width` | Int | `500` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `code` | `str` | Resolved ES module JavaScript (inline JS, or the contents of a file / URL, fetched in Python). Must `export default { render }`; loaded in the browser as a real module, so top-level `import` statements work. |
| `css` | `str` | Optional inline CSS injected into the widget root. |
| `data` | `Any` | Any JSON-able value, synced two-way. Changing it fires `change:data` in the browser but does **not** re-run `render`. |
| `width` | `int` | Container width in pixels. `0` sets no fixed width: the widget takes the width its parent layout gives it, and `css` can still set one. |
| `height` | `int` | Container height in pixels. |
| `error` | `str` | Read-back of the latest JS runtime error, or `""`. |

---
Démo : [`../demos/esm_widget.py`](../demos/esm_widget.py)
