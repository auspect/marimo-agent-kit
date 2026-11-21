<!-- wigglystuff 0.6.0, recopié de docs/reference/curve-editor.md (MIT) -->
# CurveEditor API


`CurveEditor` is a chart-space curve editor: drag the knots and switch among D3's line
interpolators — `natural`, `catmull_rom`, `step`, `monotone_x` and friends — to see how
each one reads through the same points. Open curves keep their points sorted by x so they
behave like ordinary chart lines, while closed curves preserve drawing order so a loop
stays editable as drawn. `samples` streams points along the rendered path back to Python,
and `playing` sweeps `t` along it.

See also: [BezierCurve](bezier-curve.md) for control-point Bezier curves instead of
interpolated knots, [SplineDraw](spline-draw.md) for fitting a curve to points you paint,
and [Slider2D](slider2d.md) for dragging a single x/y point.

### `CurveEditor`

`from wigglystuff.curve_editor import CurveEditor`

```python
CurveEditor(points: 'Iterable[dict[str, Any]] | None' = None, *, curve: 'str' = 'natural', x_bounds: 'tuple[float, float]' = (0.0, 1.0), y_bounds: 'tuple[float, float]' = (0.0, 1.0), width: 'int' = 600, height: 'int' = 360, tension: 'float' = 0.0, alpha: 'float' = 0.5, closed: 'bool' = False, playing: 'bool' = False, loop: 'bool' = False, t: 'float' = 0.0, interval_ms: 'int' = 30, duration_ms: 'int' = 12000, sync_throttle_ms: 'int' = 250, selected_index: 'int' = -1, show_axes: 'bool' = False, n_samples: 'int' = 100, **kwargs: 'Any') -> 'None'
```

Chart-space curve editor powered by D3 line interpolators.

Drag knots on an x/y chart and switch among D3's chart-oriented curve
factories. Open curves store points in x order so step, monotone, and bump
curves behave like normal chart lines instead of freeform paths. Closed
curves preserve point order so they can be edited as drawn loops.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import CurveEditor

    editor = mo.ui.anywidget(CurveEditor(curve="catmull_rom", alpha=0.5))
    editor
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `alpha` | Float | `0.5` |
| `closed` | Bool | `False` |
| `curve` | Unicode | `'natural'` |
| `duration_ms` | Int | `12000` |
| `height` | Int | `360` |
| `interval_ms` | Int | `30` |
| `loop` | Bool | `False` |
| `n_samples` | Int | `100` |
| `playing` | Bool | `False` |
| `points` | List | |
| `samples` | List | |
| `selected_index` | Int | `-1` |
| `show_axes` | Bool | `False` |
| `sync_throttle_ms` | Int | `250` |
| `t` | Float | `0.0` |
| `tension` | Float | `0.0` |
| `width` | Int | `600` |
| `x` | Float | `0.0` |
| `x_bounds` | Tuple | |
| `y` | Float | `0.0` |
| `y_bounds` | Tuple | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `points` | `list[dict]` | Chart knots as `{"x": float, "y": float}` in data coordinates. Open curves store points sorted by x-coordinate; closed curves preserve drawing order. |
| `samples` | `list[dict]` | `n_samples` points along the rendered curve in data coordinates, emitted by the browser after each render. |
| `x` | `float` | Current rendered path x-coordinate at `t`. |
| `y` | `float` | Current rendered path y-coordinate at `t`. |
| `t` | `float` | Path progress, clamped to `[0, 1]`. |
| `curve` | `str` | One of `linear`, `step`, `step_before`, `step_after`, `basis`, `natural`, `cardinal`, `catmull_rom`, `monotone_x`, or `bump_x`. |
| `tension` | `float` | Cardinal curve tension, clamped to `[0, 1]`. |
| `alpha` | `float` | Catmull-Rom alpha, clamped to `[0, 1]`. |
| `closed` | `bool` | Whether to virtually append the first point so the path returns to the start. |
| `playing` | `bool` | Whether playback is currently advancing `t`. |
| `loop` | `bool` | Whether playback wraps from `t=1` to `t=0`. |
| `interval_ms` | `int` | Milliseconds between browser playback ticks. |
| `duration_ms` | `int` | Milliseconds for one full `t=0` to `t=1` traversal. |
| `sync_throttle_ms` | `int` | Minimum milliseconds between playback updates synced to Python. |
| `selected_index` | `int` | Selected point index, or `-1` when no point is selected. |
| `show_axes` | `bool` | Whether to render numeric tick marks and labels on the x and y axes. |
| `n_samples` | `int` | Number of points emitted on the `samples` traitlet. Must be at least 2. |
| `x_bounds` | `tuple[float, float]` | Data-coordinate x bounds. |
| `y_bounds` | `tuple[float, float]` | Data-coordinate y bounds. |
| `width` | `int` | SVG width in pixels. |
| `height` | `int` | SVG height in pixels. |

## Helper methods

| Method | Returns | Description |
| --- | --- | --- |
| `current_point()` | `tuple[float, float]` | Current path progress point. In Python this is a linear knot approximation; the browser syncs from the actual rendered D3 path. |

---
Démo : [`../demos/curveeditor.py`](../demos/curveeditor.py)
