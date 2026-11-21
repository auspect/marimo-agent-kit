<!-- wigglystuff 0.6.0, recopié de docs/reference/treemap.md (MIT) -->
# Treemap API


`Treemap` draws a `{name, value, children}` hierarchy as nested rectangles: click one to zoom
into its subtree, click the breadcrumb bar above the chart to zoom back out. Leaf values can
be a single number or a `{column: number}` dict, in which case `value_col` picks the column
that sizes the rectangles. You rarely build the tree by hand — `from_paths`, `from_records`
and `from_dataframe` cover slash-separated paths, record dicts and pandas or polars frames —
and `selected_path` plus `clicked_path` report where the reader is looking.

See also: [NestedTable](nested-table.md) for the same tree shown as an expandable table,
[ModuleTreeWidget](module-tree.md) for the PyTorch-specific version of that idea, and
[GraphWidget](graph-widget.md) for hierarchies that are really graphs.

### `Treemap`

`from wigglystuff.treemap import Treemap`

```python
Treemap(data: 'Mapping[str, Any] | None' = None, *, width: 'int | str' = 600, height: 'int' = 400, max_depth: 'int' = 3, value_col: 'str | None' = None, format: 'Callable[[float], str] | None' = None)
```

Zoomable hierarchical treemap.

Click a rectangle to zoom into its subtree; click the breadcrumb bar
above the chart to zoom back out. Parent rectangles reserve a header
strip for their name and aggregated value; children render nested
inside, up to ``max_depth`` levels below the current view.

Values on each leaf can be a single number, or a dict of ``{column: number}``
for multi-column data. In the multi-column case, pass ``value_col`` to pick
which column drives rectangle sizing.

Args:
    data: Hierarchy dict.
    width: Chart width. Either an integer in pixels, or a CSS length
        string like ``"100%"`` for responsive sizing.
    height: Chart height in pixels.
    max_depth: How many nesting levels to render below the current
        zoom (default ``3``).
    value_col: When the tree has dict values, the column that drives
        rectangle sizing. Ignored for scalar values.
    format: Optional callable ``(value) -> str`` applied to rectangle
        value labels. Default: raw integer when whole, else two decimals.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import Treemap

    mo.ui.anywidget(
        Treemap.from_paths(
            {
                "analytics/cluster/Agg": {"hours": 10, "count": 5},
                "analytics/graph/Shortest": {"hours": 6, "count": 2},
                "animate/Easing": {"hours": 4, "count": 8},
            },
            value_col="hours",
        )
    )
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `clicked_path` | List | |
| `data` | Dict | |
| `height` | Int | `400` |
| `hovered_path` | List | |
| `max_depth` | Int | `3` |
| `selected_path` | List | |
| `value_col` | Unicode | `''` |
| `width` | Union | `600` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `data` | `dict` | Hierarchy `{name, value?, children?}`. Leaf `value` is a number or `{column: number}`. |
| `width` | `int \| str` | Chart width in pixels, or a CSS length like `"100%"`. |
| `height` | `int` | Chart height in pixels. |
| `max_depth` | `int` | How many levels below the current zoom to draw. |
| `value_col` | `str` | When leaves carry dicts, the column that drives rectangle sizing. |
| `selected_path` | `list[str]` | Breadcrumb path of the currently-zoomed node. |
| `clicked_path` | `list[str]` | Path of the most recently clicked node (fires for leaves too). |

## Alternate constructors

- `Treemap.from_paths(mapping, sep="/", root_name="root")` — build from `{path_string: value}`.
- `Treemap.from_records(records, path_cols, value_cols=None, root_name="root")` — build from a list of record dicts. `value_cols` accepts `str`, a list of names (controlling column order), or `None` to auto-detect every numeric field.
- `Treemap.from_dataframe(df, path_cols, value_cols=None, root_name="root")` — build from a pandas or polars dataframe. Same `value_cols` semantics.

---
Démo : [`../demos/treemap.py`](../demos/treemap.py)
