<!-- wigglystuff 0.6.0, recopié de docs/reference/spline-draw.md (MIT) -->
# SplineDraw API


`SplineDraw` puts a paintable scatter canvas in front of a fit you write yourself: pass a
`spline_fn(x, y) -> (x_curve, y_curve)` callable and the curve is recomputed in Python
every time you draw. Reach for it when you want to show what a smoother, a regression
spline, or any other one-dimensional fit does to data you invent on the spot. With up to
four point classes each class gets its own fitted curve, and `curve_error` surfaces
whatever the callback raised.

See also: [ScatterWidget](scatter-widget.md) for the same drawing canvas without the fit,
[CurveEditor](curve-editor.md) for placing knots by hand instead of fitting them, and
[ChartSelect](chart-select.md) for selecting regions of data you already have.

### `SplineDraw`

`from wigglystuff.spline_draw import SplineDraw`

```python
SplineDraw(spline_fn: 'Callable', *, n_classes: 'int' = 1, brushsize: 'int' = 40, width: 'int' = 600, height: 'int' = 400, **kwargs: 'Any') -> 'None'
```

Draw scatter points and see a spline curve fitted through them.

This widget is built on the same D3/SVG canvas as ScatterWidget. The spline
is computed by a Python callback function. Pass any callable with signature
``(x, y) -> (x_curve, y_curve)`` where inputs and outputs are 1-D numpy
arrays.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import SplineDraw
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import SplineTransformer
    from sklearn.linear_model import LinearRegression

    pipe = make_pipeline(SplineTransformer(), LinearRegression())

    def spline_fn(x, y):
        pipe.fit(x.reshape(-1, 1), y)
        x_curve = np.linspace(x.min(), x.max(), 200)
        return x_curve, pipe.predict(x_curve.reshape(-1, 1))

    widget = mo.ui.anywidget(SplineDraw(spline_fn=spline_fn))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `brushsize` | Int | `40` |
| `curve` | List | |
| `curve_error` | Unicode | `''` |
| `data` | List | |
| `height` | Int | `400` |
| `n_classes` | Int | `1` |
| `width` | Int | `600` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `data` | `list` | Drawn scatter points (list of dicts with `x`, `y`, `color`). |
| `curve` | `list` | Fitted curve data computed by the spline function. |
| `curve_error` | `str` | Error message from the last spline computation, or empty string on success. |
| `brushsize` | `int` | Brush radius in pixels. |
| `n_classes` | `int` | Number of point classes (1–4). |
| `width` | `int` | SVG viewBox width in pixels. |
| `height` | `int` | SVG viewBox height in pixels. |

---
Démo : [`../demos/splinedraw.py`](../demos/splinedraw.py)
