<!-- wigglystuff 0.6.0, recopié de docs/reference/chart-puck.md (MIT) -->
# ChartPuck API


`ChartPuck` renders your matplotlib figure once to a base64 PNG and floats a draggable
puck on top of it, so the chart stays a static image and only the puck moves. `x` and `y`
report the puck position in the axes' own data coordinates, which makes an existing plot
usable as an input control. Pass lists to get several pucks at once, `throttle` to choose
between syncing every drag move and syncing on release, and `from_callback` when the
figure itself should be redrawn as the puck moves.

See also: [Slider2D](slider2d.md) for a bare x/y pad with no chart behind it,
[ChartSelect](chart-select.md) for selecting a region of the same chart instead of a
point, and [ChartMultiSelect](chart-multi-select.md) for labeling several regions.

### `ChartPuck`

`from wigglystuff.chart_puck import ChartPuck`

```python
ChartPuck(fig: 'Any', x: 'float | list[float] | None' = None, y: 'float | list[float] | None' = None, puck_radius: 'int' = 10, puck_color: 'str | list[str]' = '#e63946', throttle: 'int | str' = 0, drag_x_bounds: 'tuple[float, float] | None' = None, drag_y_bounds: 'tuple[float, float] | None' = None) -> 'None'
```

Draggable puck overlay for matplotlib charts.

Allows interactive selection of coordinates on a static matplotlib chart.
Supports single or multiple pucks. The puck positions are tracked in data
coordinates.

Examples:
    Single puck:
    ```python
    import marimo as mo
    import matplotlib.pyplot as plt
    from wigglystuff import ChartPuck

    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [1, 2, 3])

    puck = mo.ui.anywidget(ChartPuck(fig))
    # puck.x, puck.y track the puck position in data coordinates
    ```

    Multiple pucks:
    ```python
    import marimo as mo

    puck = mo.ui.anywidget(ChartPuck(fig, x=[0.5, 1.5, 2.5], y=[0.5, 1.5, 2.5]))
    # puck.x, puck.y are lists of coordinates
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `axes_pixel_bounds` | Tuple | |
| `chart_base64` | Unicode | `''` |
| `drag_x_bounds` | Union | `None` |
| `drag_y_bounds` | Union | `None` |
| `height` | Int | `400` |
| `puck_color` | List | |
| `puck_radius` | Int | `10` |
| `throttle` | Union | `0` |
| `width` | Int | `400` |
| `x` | List | |
| `x_bounds` | Tuple | |
| `x_scale` | Unicode | `'linear'` |
| `y` | List | |
| `y_bounds` | Tuple | |
| `y_scale` | Unicode | `'linear'` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `x` | `list[float]` | Puck x-coordinates in data space. |
| `y` | `list[float]` | Puck y-coordinates in data space. |
| `x_bounds` | `tuple[float, float]` | Min/max x-axis bounds from matplotlib. |
| `y_bounds` | `tuple[float, float]` | Min/max y-axis bounds from matplotlib. |
| `axes_pixel_bounds` | `tuple[float, float, float, float]` | Axes position in pixels (left, top, right, bottom). |
| `width` | `int` | Canvas width in pixels. |
| `height` | `int` | Canvas height in pixels. |
| `chart_base64` | `str` | Base64-encoded PNG of the matplotlib figure. |
| `puck_radius` | `int` | Radius of puck(s) in pixels. |
| `puck_color` | `str \| list[str]` | CSS color(s) of puck(s). A single color applies to all; a list assigns one per puck. |
| `throttle` | `int \| str` | Drag sync rate. `0` = every move, int = ms throttle, `"dragend"` = on release. |

---
Démo : [`../demos/chartpuck.py`](../demos/chartpuck.py)
