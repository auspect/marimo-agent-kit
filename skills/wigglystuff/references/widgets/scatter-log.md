<!-- wigglystuff 0.6.0, recopié de docs/reference/scatter-log.md (MIT) -->
# ScatterLog API


`ScatterLog` accumulates `(x, y[, color])` points and draws them as a live scatter. Where a
plain marimo state variable gets reset by reactivity, a `ScatterLog` instance is stable
across cell re-runs, so it can grow a history: create it once in a dependency-free cell,
then call `.append(...)` from a reactive cell to record a metric, a swept parameter, or
several named series against the same x. It subclasses `AltairWidget`, so each append
patches the Vega view in place — no flicker, and zoom and pan are preserved.

See also: [AltairWidget](altair-widget.md) for the flicker-free chart it builds on,
[ScatterWidget](scatter-widget.md) for drawn points instead of logged ones, and
[ParallelCoordinates](parallel-coords.md) for watching many dimensions at once.

### `ScatterLog`

`from wigglystuff.scatter_log import ScatterLog`

```python
ScatterLog(*, x_label: str = 'x', y_label: str = 'y', color_label: str = 'color', max_points: int = 500, width: int = 600, height: int = 400, **kwargs: Any) -> None
```

Accumulate ``(x, y[, color])`` points and draw them as a live scatter.

Unlike a plain marimo state variable -- which reactivity keeps resetting --
a ``ScatterLog`` instance is stable across cell re-runs, so it can *grow* a
history. Create it once in its own (dependency-free) cell, then call
``.append(...)`` from a separate reactive cell; each re-run of that cell adds
a point. Because ``x`` and ``y`` are passed explicitly they can come from
different upstream widgets.

It subclasses :class:`AltairWidget`, so appends update the chart in place via
the Vega changeset API (no flicker, zoom/pan preserved). Read the accumulated
points back with ``.data``.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import ScatterLog

    log = ScatterLog(x_label="energy", y_label="p(win)")
    mo.ui.anywidget(log)  # display once

    # ...in a reactive cell that depends on `slider`:
    log.append(x=slider.value, y=prob, color="run-1")
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `height` | Int | `400` |
| `spec` | Dict | |
| `width` | Int | `600` |


## Usage

Create the widget once, display it, then append points from a separate reactive
cell. Pass `y=` for one series or use named keyword arguments to append several
series at the same x-coordinate.

```python
log = ScatterLog(x_label="step", y_label="score")
log.append(x=step, loss=loss, accuracy=accuracy)
```

`data` returns a copy of the accumulated points, `clear()` resets the plot, and
`max_points` bounds the retained history.

## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `spec` | `dict` | Current Vega-Lite scatter specification. |
| `width` | `int` | Container width in pixels. |
| `height` | `int` | Container height in pixels. |

---
Démo : [`../demos/scatter_log.py`](../demos/scatter_log.py)
