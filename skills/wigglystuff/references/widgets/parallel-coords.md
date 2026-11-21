<!-- wigglystuff 0.6.0, recopié de docs/reference/parallel-coords.md (MIT) -->
# ParallelCoordinates API


`ParallelCoordinates` wraps [HiPlot](https://github.com/facebookresearch/hiplot) so every row
of your data becomes one polyline across a set of draggable axes, colored by whichever column
you pass to `color_by`. Brush an axis to select rows, then keep or exclude them — from the
buttons or from `keep()` / `exclude()` in Python — and pull the survivors back out through
`filtered_data`, `filtered_as_pandas` or `filtered_as_polars`. Reach for it when you are
sifting a hyperparameter sweep or any table with more numeric columns than a scatter plot
can hold.

See also: [RidgelineChart](ridgeline-chart.md) for many same-shaped series stacked as
waveforms, [ChartSelect](chart-select.md) for box and lasso selection on a matplotlib
figure, and [NestedTable](nested-table.md) for reading the numbers instead of the lines.

### `ParallelCoordinates`

`from wigglystuff.parallel_coords import ParallelCoordinates`

```python
ParallelCoordinates(data: 'Any' = None, *, color_by: 'str' = '', color_map: 'dict[str, str] | None' = None, height: 'int' = 500, width: 'int' = 0, ignore: 'list[str] | None' = None) -> 'None'
```

Interactive parallel coordinates plot powered by HiPlot.

Wraps Facebook Research's HiPlot library to provide brush filtering on
axes, axis reordering via drag, and coloring lines by a selected
dimension -- all inside a notebook widget.

Args:
    data: Dataset as a list of dictionaries, pandas DataFrame, or polars
        DataFrame. Each row becomes one polyline in the chart.
    color_by: Column name used to color lines. Leave empty for a single
        default color.
    color_map: Mapping of categorical values to CSS colors (e.g.
        ``{"a": "red", "b": "#0000ff"}``). Values not in the map use the
        default palette. Colors are auto-converted to ``rgb(...)`` format.
    height: Widget height in pixels.
    width: Widget width in pixels. Set to 0 for container width.
    ignore: Column names to exclude from the plot.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import ParallelCoordinates
    import polars as pl

    df = pl.DataFrame({
        "x": [1, 2, 3, 4, 5],
        "y": [5, 4, 3, 2, 1],
        "label": ["a", "a", "b", "b", "b"],
    })
    widget = mo.ui.anywidget(ParallelCoordinates(df, color_by="label", color_map={"a": "red"}))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `brush_extents` | Dict | |
| `color_by` | Unicode | `''` |
| `color_map` | Dict | |
| `data` | List | |
| `filtered_uids` | List | |
| `height` | Int | `500` |
| `selected_uids` | List | |
| `width` | Int | `0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `data` | `list[dict]` | Input rows rendered as polylines. |
| `color_by` | `str` | Column used for line coloring. |
| `color_map` | `dict` | Map of categorical values to CSS colors (e.g. `{"a": "red", "b": "#00f"}`). Unmapped values use the default palette. |
| `height` | `int` | Plot height in pixels. |
| `width` | `int` | Plot width in pixels. Set to 0 for container width. |
| `brush_extents` | `dict` | Current brush ranges on axes. Resets to `{}` after Keep/Exclude. |
| `filtered_indices` | `list[int]` | Indices currently passing filters/selection. |
| `selected_indices` | `list[int]` | Indices currently selected in the active brush. |

## Methods

| Method | Description |
| --- | --- |
| `selections` | Property returning `filter_history` + a trailing `{"action": "current", "extents": ...}` entry for the active brush (if any). |
| `keep()` | Trigger a Keep action on the current brush selection (same as the Keep button). |
| `exclude()` | Trigger an Exclude action on the current brush selection (same as the Exclude button). |
| `restore()` | Restore all rows and clear `filter_history` (same as the Restore button). |
| `filtered_data` | Property returning the list of dicts for rows passing all filters. |
| `filtered_as_pandas` | Property returning filtered data as a pandas DataFrame. |
| `filtered_as_polars` | Property returning filtered data as a polars DataFrame. |
| `selected_data` | Property returning the list of dicts for selected rows. |

---
Démo : [`../demos/parallelcoords.py`](../demos/parallelcoords.py)
