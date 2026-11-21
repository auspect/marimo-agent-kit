<!-- wigglystuff 0.6.0, recopié de docs/reference/nested-table.md (MIT) -->
# NestedTable API


`NestedTable` shows a hierarchy as a table of collapsible rows: the node name, one column per
value key (or a single `Value` column for scalar trees), and an optional share-of-root
percentage beside any subset of those columns. Use it when the numbers themselves matter and
a chart would only approximate them — cost breakdowns, test timings, rolled-up group totals.
It reads the same tree format as `Treemap` and shares its `from_paths`, `from_records` and
`from_dataframe` constructors, while `expanded_paths` and `selected_path` sync both ways.

See also: [Treemap](treemap.md) for the same hierarchy drawn as nested rectangles,
[ModuleTreeWidget](module-tree.md) for a tree of PyTorch layers, and
[Matrix](matrix.md) for editing a flat grid of numbers instead.

### `NestedTable`

`from wigglystuff.nested_table import NestedTable`

```python
NestedTable(data: 'Mapping[str, Any] | None' = None, *, initial_expand_depth: 'int' = 1, show_percent: 'bool | Sequence[str]' = True, format: 'Formatter | Mapping[str, Formatter] | None' = None, width: 'str' = '100%')
```

Recursive expandable table for hierarchical data.

Each row shows the node name followed by one column per value key (or a
single ``Value`` column when values are scalars), and optionally a
share-of-root column next to any subset of value columns.

Args:
    data: Hierarchy dict with leaf values that are either scalars or
        ``{column: number}`` dicts.
    initial_expand_depth: Levels expanded on first render.
    show_percent: Which value columns get a share-of-root column next
        to them. ``True`` (default) enables it for every column,
        ``False`` disables it everywhere, or pass a sequence of column
        names to enable it for just those.
    format: Per-value formatter. Either a callable ``(value) -> str``
        applied to every cell, or a mapping ``{column: callable}`` for
        per-column formatters. Default: integer when whole, else two
        decimals.
    width: CSS width string for the table.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import NestedTable

    widget = mo.ui.anywidget(NestedTable.from_paths(
        {
            "analytics/cluster/Agg": {"hours": 12.5, "count": 5},
            "analytics/graph/Shortest": {"hours": 6.0, "count": 2},
            "animate/Easing": {"hours": 4.25, "count": 8},
        },
        format={"hours": lambda v: f"{v:.1f}h"},
        show_percent=["hours"],
    ))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `columns` | List | |
| `data` | Dict | |
| `expanded_paths` | List | |
| `initial_expand_depth` | Int | `1` |
| `selected_path` | List | |
| `show_percent` | List | |
| `width` | Unicode | `'100%'` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `data` | `dict` | Hierarchy `{name, value?, children?}`. Leaf `value` is a number or `{column: number}`. |
| `columns` | `list[str]` | Auto-detected dict-value column keys. Empty for scalar trees. |
| `show_percent` | `list[str]` | Column names that show a share-of-root column. Constructor accepts `bool` or `Sequence[str]` and normalizes. |
| `initial_expand_depth` | `int` | How many levels are expanded on first render. |
| `expanded_paths` | `list[list[str]]` | Paths of currently-expanded rows. Bidirectional. |
| `selected_path` | `list[str]` | Path of the last row whose name was clicked. Selection is highlighted in the UI. |
| `width` | `str` | CSS width of the table. |

## Alternate constructors

- `NestedTable.from_paths(mapping, sep="/", root_name="root")` — build from `{path_string: value}`.
- `NestedTable.from_records(records, path_cols, value_cols=None, root_name="root")` — build from a list of record dicts. `value_cols` accepts `str`, a list of names (controlling column order), or `None` to auto-detect every numeric field.
- `NestedTable.from_dataframe(df, path_cols, value_cols=None, root_name="root")` — build from a pandas or polars dataframe. Same `value_cols` semantics.

---
Démo : [`../demos/nested_table.py`](../demos/nested_table.py)
