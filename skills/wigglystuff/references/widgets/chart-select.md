<!-- wigglystuff 0.6.0, recopié de docs/reference/chart-select.md (MIT) -->
# ChartSelect API


`ChartSelect` draws a box or freehand lasso on top of a matplotlib figure that has been
rendered to a base64 PNG, then hands the region back in data coordinates. `get_mask` and
`get_indices` turn that region into a filter for the arrays or DataFrame behind the plot,
so brushing a chart becomes a query. This widget has graduated to marimo core: in marimo
prefer `mo.ui.matplotlib`, and keep `ChartSelect` for plain Jupyter and other anywidget
hosts.

See also: [ChartMultiSelect](chart-multi-select.md) for several persistent class-labeled
regions, [ChartPuck](chart-puck.md) for picking one point instead of a region, and
[ParallelCoordinates](parallel-coords.md) for brushing many dimensions at once.

### `ChartSelect`

`from wigglystuff.chart_select import ChartSelect`

```python
ChartSelect(fig: 'Any', mode: 'str' = 'box', modes: 'list[str] | None' = None, selection_color: 'str' = '#3b82f6', selection_opacity: 'float' = 0.3, **kwargs: 'Any') -> 'None'
```

Region selection overlay for matplotlib charts.

Allows interactive box or lasso (freehand) selection on a static matplotlib
chart. Returns selection coordinates in data space for user-side filtering.

Note:
    This widget has graduated to marimo core. If you are using marimo,
    prefer [`marimo.ui.matplotlib`](https://docs.marimo.io/guides/working_with_data/plotting/#matplotlib).
    `ChartSelect` will continue to work in plain Jupyter and other
    anywidget hosts.

Examples:
    Basic usage:

    ```python
    import marimo as mo
    import matplotlib.pyplot as plt
    from wigglystuff import ChartSelect

    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data)

    select = mo.ui.anywidget(ChartSelect(fig))
    # select.selection contains the selection bounds/vertices
    # select.has_selection is True when a selection exists
    ```

    Filtering with a mask:

    ```python
    mask = select.get_mask(x_data, y_data)
    selected_x = x_data[mask]
    ```

    Filtering a DataFrame:

    ```python
    indices = select.get_indices(df["x"], df["y"])
    selected_df = df.iloc[indices]
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `axes_pixel_bounds` | Tuple | |
| `chart_base64` | Unicode | `''` |
| `has_selection` | Bool | `False` |
| `height` | Int | `400` |
| `mode` | Unicode | `'box'` |
| `modes` | List | |
| `selection` | Dict | |
| `selection_color` | Unicode | `'#3b82f6'` |
| `selection_opacity` | Float | `0.3` |
| `stroke_width` | Int | `2` |
| `width` | Int | `400` |
| `x_bounds` | Tuple | |
| `y_bounds` | Tuple | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `mode` | `str` | Selection mode: "box" or "lasso". |
| `modes` | `list[str]` | Available modes (controls which buttons are shown). |
| `selection` | `dict` | Selection data in data coordinates. Box: `{x_min, y_min, x_max, y_max}`. Lasso: `{vertices: [[x, y], ...]}`. |
| `has_selection` | `bool` | Whether a selection is currently active. |
| `x_bounds` | `tuple[float, float]` | Min/max x-axis bounds from matplotlib. |
| `y_bounds` | `tuple[float, float]` | Min/max y-axis bounds from matplotlib. |
| `axes_pixel_bounds` | `tuple[float, float, float, float]` | Axes position in pixels (left, top, right, bottom). |
| `width` | `int` | Canvas width in pixels. |
| `height` | `int` | Canvas height in pixels. |
| `chart_base64` | `str` | Base64-encoded PNG of the matplotlib figure. |
| `selection_color` | `str` | CSS color for selection fill and stroke. |
| `selection_opacity` | `float` | Opacity of selection fill (0-1). |
| `stroke_width` | `int` | Width of selection border in pixels. |

## Helper methods

| Method | Returns | Description |
| --- | --- | --- |
| `clear()` | `None` | Clear the current selection. |
| `get_bounds()` | `tuple` or `None` | Bounding box `(x_min, y_min, x_max, y_max)` in data coordinates. |
| `get_vertices()` | `list[tuple]` | Selection vertices as `(x, y)` tuples. |
| `contains_point(x, y)` | `bool` | Check if a point is inside the selection. |
| `get_mask(x_arr, y_arr)` | `ndarray[bool]` | Boolean mask for points inside selection. |
| `get_indices(x_arr, y_arr)` | `ndarray[int]` | Indices of points inside selection. |
| `redraw()` | `None` | Re-render chart (only for `from_callback` widgets). |

---
Démo : [`../demos/chartselect.py`](../demos/chartselect.py)
