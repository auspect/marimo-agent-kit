<!-- wigglystuff 0.6.0, recopié de docs/reference/heatmap-select.md (MIT) -->
# HeatmapSelect API


`HeatmapSelect` renders a 2D array as a dense grid — one image pixel per cell, in the
spirit of the parameter spaces in Bret Victor's
[*Up and Down the Ladder of Abstraction*](https://worrydream.com/LadderOfAbstraction/).
Hover or click a cell in the body to pick one point of the sweep, or grab the left or
bottom gutter to pin a whole row or column. The three pins are independent and coexist, so
you can hold a cell, a row and a column at once. The values behind the picture never cross
the wire: the widget reports indices and you do the slicing, which is what lets a 14 641-cell
field stay a single PNG. Reach for it when a sweep has two knobs and you want to see the runs
behind any slice of it.

See also: [ChartSelect](chart-select.md) for box and lasso selection over a matplotlib
figure, [ChartPuck](chart-puck.md) for dragging a single point across a chart, and
[Slider2D](slider2d.md) for picking a continuous `(x, y)` pair rather than a grid cell.

### `HeatmapSelect`

`from wigglystuff.heatmap_select import HeatmapSelect`

```python
HeatmapSelect(image: Any, *, x_range: Tuple[float, float] = (0.0, 1.0), y_range: Tuple[float, float] = (0.0, 1.0), x_label: str = '', y_label: str = '', x_suffix: str = '', y_suffix: str = '', origin: str = 'lower', cell_width: int = 4, cell_height: int = 4, row_color: str = '', col_color: str = '', cmap: Any = 'gray', norm: Any = None, vmin: Optional[float] = None, vmax: Optional[float] = None, throttle: Union[int, str] = 50, **kwargs: Any)
```

A dense parameter-space grid where you pick one cell or a whole row/column.

Modelled on the grid in Bret Victor's *Up and Down the Ladder of
Abstraction*. The body picks a single cell; the left gutter picks a whole row
(a horizontal band); the bottom gutter picks a whole column (a vertical band).

Hovering previews, clicking *pins*. The three pins are independent and
coexist — you can hold a cell, a row and a column at once, and clicking one
region only replaces that region's pin. Double-clicking a region drops just
that pin. What to make of a combination is the caller's business.

One pixel of ``image`` is one grid cell, and the values behind the picture
never cross the wire — the widget hands back indices, and you do the slicing
yourself with ``values[widget.pinned_row]``. Use ``x_at``/``y_at`` to turn an
index back into a data coordinate.

Examples:
    ```python
    import numpy as np
    import marimo as mo
    from wigglystuff import HeatmapSelect

    steps = np.random.rand(100, 91)
    widget = mo.ui.anywidget(
        HeatmapSelect(
            steps,
            x_range=(0, 90),
            y_range=(0.1, 10.0),
            x_label="bend angle",
            y_label="turning rate",
            x_suffix="°",
            y_suffix="°",
        )
    )
    widget
    ```

    Then react to the pins in another cell. They are independent, so this is
    three ``if``s rather than a branch:

    ```python
    if widget.pinned_row is not None:
        row_sweep = steps[widget.pinned_row, :]
    if widget.pinned_col is not None:
        col_sweep = steps[:, widget.pinned_col]
    if widget.pinned_cell is not None:
        row, col = widget.pinned_cell
        value = steps[row, col]
        x, y = widget.x_at(col), widget.y_at(row)
    ```

    Coloring follows matplotlib, so a Bret-Victor-style crash region is just
    a masked array plus a "bad" color — the widget has no concept of one:

    ```python
    import matplotlib

    HeatmapSelect(
        np.ma.masked_where(crashed, distance),
        cmap=matplotlib.colormaps["gray"].with_extremes(bad="red"),
    )
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `cell_height` | Int | `4` |
| `cell_width` | Int | `4` |
| `col_color` | Unicode | `''` |
| `hover_cell` | Tuple | `None` |
| `hover_col` | Int | `None` |
| `hover_row` | Int | `None` |
| `image_base64` | Unicode | `''` |
| `n_cols` | Int | `1` |
| `n_rows` | Int | `1` |
| `origin` | Unicode | `'lower'` |
| `pinned_cell` | Tuple | `None` |
| `pinned_col` | Int | `None` |
| `pinned_row` | Int | `None` |
| `row_color` | Unicode | `''` |
| `throttle` | Union | `50` |
| `x_label` | Unicode | `''` |
| `x_range` | Tuple | |
| `x_suffix` | Unicode | `''` |
| `y_label` | Unicode | `''` |
| `y_range` | Tuple | |
| `y_suffix` | Unicode | `''` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `image_base64` | `str` | The grid bitmap as a PNG data URI. One image pixel is one cell. |
| `n_rows` | `int` | Grid rows, derived from the image height. |
| `n_cols` | `int` | Grid columns, derived from the image width. |
| `x_range` | `tuple[float, float]` | Data coordinates of the first and last *column* centers. |
| `y_range` | `tuple[float, float]` | Data coordinates of the first and last *row* centers. |
| `x_label` | `str` | Label under the bottom gutter. May contain `\n` to stack lines. |
| `y_label` | `str` | Label beside the left gutter. May contain `\n` to stack lines. |
| `x_suffix` | `str` | Appended to x tick labels, e.g. `"°"`. |
| `y_suffix` | `str` | Appended to y tick labels. |
| `origin` | `str` | `"lower"` puts image row 0 at the bottom (like `imshow`), `"upper"` at the top. |
| `cell_width` | `int` | Screen pixels per cell horizontally. |
| `cell_height` | `int` | Screen pixels per cell vertically. |
| `row_color` | `str` | Tint for the row band from the left (y) axis. Empty uses `--hs-row-color`. |
| `col_color` | `str` | Tint for the column band from the bottom (x) axis. Empty uses `--hs-col-color`. |
| `pinned_cell` | `tuple[int, int] \| None` | `(row, col)` of the pinned cell. |
| `pinned_row` | `int \| None` | Row index pinned from the left axis. |
| `pinned_col` | `int \| None` | Column index pinned from the bottom axis. |
| `hover_cell` | `tuple[int, int] \| None` | `(row, col)` under the cursor, when it is over the grid body. |
| `hover_row` | `int \| None` | Row under the cursor, when it is over the left gutter. |
| `hover_col` | `int \| None` | Column under the cursor, when it is over the bottom gutter. |
| `throttle` | `int \| str` | Hover sync rate. `0` = every move, int = ms, `"dragend"` = on release. Pin changes always sync immediately. |

## Interaction

| Gesture | Result |
| --- | --- |
| Hover the body | Sets `hover_cell`. |
| Hover the left gutter | Sets `hover_row` — a horizontal band. |
| Hover the bottom gutter | Sets `hover_col` — a vertical band. |
| Click (anywhere, including a gutter) | Pins that region. Only that region's pin is replaced. |
| Drag | Keeps moving that region's pin. |
| Double-click a region | Drops only that region's pin. |
| Mouse out | Clears the hover traits; pins are untouched. |

The three pins are independent, so a cell, a row and a column can all be held at
once. Hovering never disturbs a pin — it draws a faint ghost instead.

## Coloring

Pass a 2D numeric array and the widget colormaps it with matplotlib's own
conventions: `cmap` (a name or a `Colormap`), `norm`, `vmin`, `vmax`. The default
is grayscale. Cells that are **masked or non-finite** take the colormap's "bad"
color, which is all you need for a crash region:

```python
import matplotlib
import numpy as np
from wigglystuff import HeatmapSelect

HeatmapSelect(
    np.ma.masked_where(crashed, distance),
    cmap=matplotlib.colormaps["gray"].with_extremes(bad="red"),
)
```

Autoscaling is relative, exactly as with `imshow`: uniformly rescaling the data
produces an identical picture. Pin `vmin`/`vmax` if you need an absolute scale
across successive `set_image` calls.

You can also skip colormapping entirely and hand over a finished picture — a PIL
image, an `(rows, cols, 3|4)` uint8 array, a path, or a base64 PNG.

## Sizing

The plot size is *derived*: `n_cols * cell_width` by `n_rows * cell_height`. Cells
are therefore always whole pixel blocks and never shimmer, which is why there is
no `width`/`height` argument — both are read-only properties.

---
Démo : [`../demos/heatmap_select.py`](../demos/heatmap_select.py)
