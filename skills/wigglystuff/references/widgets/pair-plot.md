<!-- wigglystuff 0.6.0, recopié de docs/reference/pair-plot.md (MIT) -->
# PairPlot API


`PairPlot` shows every pair of numeric columns as a scatter plot, with a
histogram of each column on the diagonal. Select rows in one cell and they
light up in all the others.

```python
import numpy as np
from wigglystuff import PairPlot

X = np.random.default_rng(0).normal(size=(1_000_000, 8))
labels = np.random.default_rng(1).integers(0, 5, size=len(X))

plot = PairPlot(X, color=labels)
plot
```

DataFrames work too. `color` can then be a column name, and the other numeric
columns become the dimensions (pick them with `columns=`):

```python
PairPlot(df, color="species")
PairPlot(df, columns=["bill_length", "bill_depth", "body_mass"], color="species")
```

## Selecting rows

- **Drag** inside any scatter cell to draw a **box**, or switch to **Lasso** in
  the toolbar (or pass `mode="lasso"`) for a freehand outline.
- **Drag a selection** to move it. Every cell and histogram updates while you
  drag; Python receives the new `selection` when you let go.
- Selected rows keep their category color; everything else turns gray. The
  diagonal shows the selection stacked on top of the full histogram.
- **Click** outside the selection, double-click, or press **Clear** to clear it.

The selection is synced as a small description in data coordinates, not as a
list of row indices, so it stays cheap at a million rows:

```python
{"type": "box", "x_index": 0, "y_index": 1,
 "x_min": -1.2, "x_max": 0.8, "y_min": -0.5, "y_max": 2.1}
{"type": "lasso", "x_index": 0, "y_index": 1, "vertices": [[x, y], ...]}
```

Python evaluates it against the full data, so these are exact:

```python
plot.selected_count    # number of selected rows
plot.get_mask()        # boolean NumPy mask
plot.get_indices()     # integer row indices
plot.selected_data     # selected rows, same type as the input
```

## Keep, Exclude, Reset

Like the [parallel coordinates](parallel-coords.md) widget, a selection can
become a filter:

- **Keep** drops every row outside the selection.
- **Exclude** drops every row inside it.
- **Reset** brings every row back.

After a filter the axes and histograms animate to the rows that remain, which
works as a zoom. Filters stack and are synced as the `filters` list, which
Python replays to get exact results. The same actions exist in Python:

```python
plot.keep()               # or plot.exclude()
plot.get_active_mask()    # rows left after the filters
plot.active_data          # those rows, same type as the input
plot.reset()
```

New selections only count rows that are still in the plot.

## How it scales

The numbers go to the browser once, as binary float32, and stay in a Web
Worker. WebGL draws a sample of at most `max_marks` points spread across the
cells (with 8 dimensions, about 36,000 per cell), while counts, histograms and
selections use every row. At a million rows a selection takes a few tens of
milliseconds, so a box keeps up while you drag it. Point size and opacity
adapt to how crowded a cell is unless you set `point_size`.

Non-finite values are skipped in the axes, histograms and selections. Up to
eight categories get distinct colors by default; pass `color_map` to choose
your own.

### `PairPlot`

`from wigglystuff.pair_plot import PairPlot`

```python
PairPlot(data: 'Any', *, columns: 'Sequence[str] | None' = None, color: 'Any' = None, color_map: 'Mapping[Any, str] | None' = None, layout: 'str' = 'full', mode: 'str' = 'box', cell_size: 'int | None' = None, max_marks: 'int' = 2000000, point_size: 'float | None' = None, show_filters: 'bool' = True, show_mode_toggle: 'bool' = True, show_layout_toggle: 'bool' = True, **kwargs: 'Any') -> 'None'
```

Interactive scatterplot matrix with linked box and lasso selection.

``PairPlot`` sends numeric data to the browser as binary float32 data and
keeps the full matrix in a Web Worker.  The visible plot is bounded by a
global mark budget, while a selection is evaluated against every row.

Args:
    data: A two-dimensional NumPy array, pandas DataFrame, or polars
        DataFrame containing numeric dimensions.
    columns: Labels for NumPy columns, or the DataFrame columns to display.
        NumPy columns default to ``x0``, ``x1``, ...; DataFrames default to
        every numeric column except a named ``color`` column.
    color: Optional categorical values with one entry per row.  For a
        DataFrame this may instead be the name of a color column.
    color_map: Optional mapping from category values to CSS colors.
    layout: ``"full"`` or ``"lower"``.
    mode: Selection tool, ``"box"`` or ``"lasso"``. A box can be dragged
        to a new spot after it is drawn; both are switchable in the widget.
    cell_size: Size of each matrix cell in CSS pixels. ``None`` (the
        default) fits the matrix to the available width.
    max_marks: Approximate maximum number of point marks rendered across
        all visible off-diagonal cells.
    point_size: Point diameter in CSS pixels. ``None`` (the default)
        picks a size and opacity from how many points share a cell.
    show_filters: Show the **Keep**, **Exclude**, **Clear** and **Reset**
        buttons. Turn it off when the plot is only for looking: clicking
        empty space still clears the selection, and :meth:`keep`,
        :meth:`exclude` and :meth:`reset` still work from Python.
    show_mode_toggle: Show the **Box** / **Lasso** toggle. Without it the
        tool stays whatever ``mode`` says.
    show_layout_toggle: Show the **Full** / **Lower** toggle. Without it
        the matrix stays whatever ``layout`` says.

The selection is synced as a compact data-coordinate description (box
corners or lasso vertices). Use :meth:`get_mask`, :meth:`get_indices`, or
:attr:`selected_data` to obtain exact Python-side results without syncing
a potentially huge index list.

Like HiPlot, a selection can be turned into a filter: **Keep** drops every
row outside it and **Exclude** drops every row inside it, after which the
axes rescale to the rows that remain. Filters stack, are synced as the
replayable ``filters`` list, and **Reset** removes them all. The same
actions are available from Python as :meth:`keep`, :meth:`exclude`, and
:meth:`reset`; :attr:`active_data` holds the rows that survive the filters.

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `categories` | List | |
| `cell_size` | Int | `None` |
| `columns` | List | |
| `data_version` | Int | `0` |
| `error` | Unicode | `''` |
| `filters` | List | |
| `max_marks` | Int | `2000000` |
| `mode` | Enum | `'box'` |
| `palette` | List | |
| `point_size` | Float | `None` |
| `selected_count` | Int | `0` |
| `selection` | Dict | |
| `show_filters` | Bool | `True` |
| `show_layout_toggle` | Bool | `True` |
| `show_mode_toggle` | Bool | `True` |
| `status` | Unicode | `'loading'` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `selection` | `dict` | Current box or lasso in data coordinates, or `{}`. |
| `selected_count` | `int` | Exact number of selected rows (after filters). |
| `filters` | `list[dict]` | Keep/Exclude steps: `{"action": "keep" \| "exclude", "selection": {...}}`. |
| `mode` | `str` | Selection tool: `"box"` or `"lasso"`. |
| `layout` | `str` | `"full"` matrix or `"lower"` triangle. |
| `columns` | `list[str]` | Dimension names. |
| `categories` | `list[str]` | Color categories, in sorted order. |
| `palette` | `list[str]` | One CSS color per category. |
| `cell_size` | `int \| None` | Cell size in pixels; `None` fits the available width. |
| `point_size` | `float \| None` | Point diameter in pixels; `None` adapts to density. |
| `max_marks` | `int` | Budget of points drawn across all cells. |
| `status` | `str` | `"loading"`, `"ready"` or `"error"`. |
| `error` | `str` | Error message from the browser, if any. |

---
Démo : [`../demos/pair_plot.py`](../demos/pair_plot.py)
