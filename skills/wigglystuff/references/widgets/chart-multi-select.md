<!-- wigglystuff 0.6.0, recopié de docs/reference/chart-multi-select.md (MIT) -->
# ChartMultiSelect API


`ChartMultiSelect` is `ChartSelect` with memory: every box or lasso you draw over the
matplotlib PNG stays on the canvas tagged with a class label, up to four classes. Draw one
region per class and `get_labels(x, y)` returns a class per point, with `-1` for anything
unclassified and last-drawn winning where regions overlap. It is a quick way to hand-label
a scatter plot before training on it.

See also: [ChartSelect](chart-select.md) for a single throwaway selection,
[ScatterWidget](scatter-widget.md) for painting labeled points instead of labeling
existing ones, and [ChartPuck](chart-puck.md) for dragging a point on the same kind of
chart overlay.

### `ChartMultiSelect`

`from wigglystuff.chart_multi_select import ChartMultiSelect`

```python
ChartMultiSelect(fig: 'Any', n_classes: 'int' = 2, mode: 'str' = 'box', modes: 'list[str] | None' = None, selection_opacity: 'float' = 0.3, **kwargs: 'Any') -> 'None'
```

Multi-region selection overlay for matplotlib charts.

Like ``ChartSelect`` but supports multiple persistent box/lasso selections,
each tagged with a class label.  Draw regions for different classes, then
use ``get_labels`` to classify points.

Examples:
    Basic usage:

    ```python
    import marimo as mo
    import matplotlib.pyplot as plt
    from wigglystuff import ChartMultiSelect

    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data)

    ms = mo.ui.anywidget(ChartMultiSelect(fig, n_classes=3))
    # ms.selections is a list of selection dicts
    # ms.get_labels(x_data, y_data) returns class labels
    ```

    Filtering by class:

    ```python
    labels = ms.get_labels(x_data, y_data)
    class_0 = x_data[labels == 0]
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `active_class` | Int | `0` |
| `axes_pixel_bounds` | Tuple | |
| `chart_base64` | Unicode | `''` |
| `height` | Int | `400` |
| `mode` | Unicode | `'box'` |
| `modes` | List | |
| `n_classes` | Int | `2` |
| `selected_index` | Int | `-1` |
| `selection_opacity` | Float | `0.3` |
| `selections` | List | |
| `stroke_width` | Int | `2` |
| `width` | Int | `400` |
| `x_bounds` | Tuple | |
| `y_bounds` | Tuple | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `mode` | `str` | Selection mode: "box" or "lasso". |
| `modes` | `list[str]` | Available modes (controls which buttons are shown). |
| `n_classes` | `int` | Number of class labels (1–4). |
| `active_class` | `int` | Currently active class for the next drawn selection. |
| `selections` | `list[dict]` | All selections. Each dict has `type`, `class_id`, and geometry keys. |
| `selected_index` | `int` | Index of the highlighted selection (-1 = none). |
| `x_bounds` | `tuple[float, float]` | Min/max x-axis bounds from matplotlib. |
| `y_bounds` | `tuple[float, float]` | Min/max y-axis bounds from matplotlib. |
| `axes_pixel_bounds` | `tuple[float, float, float, float]` | Axes position in pixels (left, top, right, bottom). |
| `width` | `int` | Canvas width in pixels. |
| `height` | `int` | Canvas height in pixels. |
| `chart_base64` | `str` | Base64-encoded PNG of the matplotlib figure. |
| `selection_opacity` | `float` | Opacity of selection fill (0-1). |
| `stroke_width` | `int` | Width of selection border in pixels. |

## Helper methods

| Method | Returns | Description |
| --- | --- | --- |
| `clear()` | `None` | Remove all selections. |
| `get_labels(x_arr, y_arr)` | `ndarray[int]` | Class labels per point (-1 = unclassified, last-drawn wins for overlap). |
| `get_mask(x_arr, y_arr, class_id=None)` | `ndarray[bool]` | Boolean mask for classified points (optionally filtered by class). |
| `get_indices(x_arr, y_arr, class_id=None)` | `ndarray[int]` | Indices of classified points. |
| `redraw()` | `None` | Re-render chart (only for `from_callback` widgets). |

---
Démo : [`../demos/chartmultiselect.py`](../demos/chartmultiselect.py)
