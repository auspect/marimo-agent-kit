<!-- wigglystuff 0.6.0, recopié de docs/reference/bezier-curve.md (MIT) -->
# BezierCurve API


`BezierCurve` is an arbitrary-degree Bezier editor: drag the control points and the
curve follows, while `samples` streams evenly spaced points along it back to Python.
Set `playing` to sweep the parameter `t` from 0 to 1 and animate anything downstream
of `x`/`y`.

See also: [CurveEditor](curve-editor.md) for D3 line interpolators in chart space,
[SplineDraw](spline-draw.md) for fitting a spline to drawn points, and
[Slider2D](slider2d.md) for a single draggable x/y point.

### `BezierCurve`

`from wigglystuff.bezier_curve import BezierCurve`

```python
BezierCurve(points: 'Iterable[dict[str, Any]] | None' = None, *, closed: 'bool' = False, playing: 'bool' = False, loop: 'bool' = False, t: 'float' = 0.0, x_bounds: 'tuple[float, float]' = (0.0, 1.0), y_bounds: 'tuple[float, float]' = (0.0, 1.0), width: 'int' = 600, height: 'int' = 360, interval_ms: 'int' = 30, duration_ms: 'int' = 12000, sync_throttle_ms: 'int' = 250, show_axes: 'bool' = False, n_samples: 'int' = 100, **kwargs: 'Any') -> 'None'
```

Interactive arbitrary-degree Bezier curve editor.

Double-click to add control points, drag points to reshape the curve, and
use the play controls to advance ``t`` from 0 to 1. Coordinates synced to
Python use the configurable data bounds rather than SVG pixels.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import BezierCurve

    curve = mo.ui.anywidget(BezierCurve(closed=True, loop=True))
    curve
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `closed` | Bool | `False` |
| `duration_ms` | Int | `12000` |
| `height` | Int | `360` |
| `interval_ms` | Int | `30` |
| `loop` | Bool | `False` |
| `n_samples` | Int | `100` |
| `playing` | Bool | `False` |
| `points` | List | |
| `samples` | List | |
| `show_axes` | Bool | `False` |
| `sync_throttle_ms` | Int | `250` |
| `t` | Float | `0.0` |
| `width` | Int | `600` |
| `x` | Float | `0.0` |
| `x_bounds` | Tuple | |
| `y` | Float | `0.0` |
| `y_bounds` | Tuple | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `points` | `list[dict]` | Control points as `{"x": float, "y": float}` in data coordinates. |
| `samples` | `list[dict]` | `n_samples` points along the rendered curve in data coordinates. |
| `x` | `float` | Current Bezier point x-coordinate at `t`. |
| `y` | `float` | Current Bezier point y-coordinate at `t`. |
| `t` | `float` | Curve parameter, clamped to `[0, 1]`. |
| `closed` | `bool` | Whether to virtually append the first point so the curve returns to the start. |
| `playing` | `bool` | Whether playback is currently advancing `t`. |
| `loop` | `bool` | Whether playback wraps from `t=1` to `t=0`. |
| `interval_ms` | `int` | Milliseconds between browser playback ticks. |
| `duration_ms` | `int` | Milliseconds for one full `t=0` to `t=1` traversal. |
| `sync_throttle_ms` | `int` | Minimum milliseconds between playback updates synced to Python. |
| `show_axes` | `bool` | Whether to render numeric tick marks and labels on the x and y axes. |
| `n_samples` | `int` | Number of points emitted on the `samples` traitlet. Must be at least 2. |
| `x_bounds` | `tuple[float, float]` | Data-coordinate x bounds. |
| `y_bounds` | `tuple[float, float]` | Data-coordinate y bounds. |
| `width` | `int` | SVG width in pixels. |
| `height` | `int` | SVG height in pixels. |

## Helper methods

| Method | Returns | Description |
| --- | --- | --- |
| `current_point()` | `tuple[float, float]` | Current Bezier point at `t`. |
| `sample(n=100)` | `list[dict]` | `n` sampled points along the curve. |

---
Démo : [`../demos/beziercurve.py`](../demos/beziercurve.py)
