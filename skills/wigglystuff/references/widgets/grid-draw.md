<!-- wigglystuff 0.6.0, recopié de docs/reference/grid-draw.md (MIT) -->
# GridDraw API


`GridDraw` constrains drawing to a square grid: dots land on intersections and lines are
unit segments between neighboring intersections, always horizontal or vertical. Because
everything is addressed as integer `[row, col]` coordinates from `[0, 0]` to
`[rows, cols]`, `dots` and `lines` come back to Python as lists you can index a maze,
board or layout with instead of pixels you have to interpret. Pass a list to
`line_width` to get a width picker in the toolbar.

See also: [Paint](paint.md) for freehand painting on a canvas, [EdgeDraw](edge-draw.md)
for node and link diagrams, and [Matrix](matrix.md) for typing numbers into a grid
rather than drawing on one.

### `GridDraw`

`from wigglystuff.grid_draw import GridDraw`

```python
GridDraw(rows: 'int' = 8, cols: 'int' = 8, line_width: 'int | Sequence[int]' = 2, dot_radius: 'int' = 6, theme: 'str | None' = None, width: 'int' = 440, height: 'int' = 440, dots: 'Iterable[Sequence[int]] | None' = None, lines: 'Iterable[dict[str, Any]] | None' = None, **kwargs: 'Any') -> 'None'
```

Drawable square grid widget for dots and orthogonal line segments.

`rows` and `cols` count cells. Intersections are addressed as
`[row, col]` coordinates from `[0, 0]` through `[rows, cols]`.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import GridDraw

    grid = mo.ui.anywidget(GridDraw(rows=8, cols=8, line_width=[1, 2, 4]))
    grid
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `cols` | Int | `8` |
| `dot_radius` | Int | `6` |
| `dots` | List | |
| `height` | Int | `440` |
| `line_width` | Any | `2` |
| `lines` | List | |
| `rows` | Int | `8` |
| `theme` | Any | `None` |
| `width` | Int | `440` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `dots` | `list` | Drawn intersections as `[[row, col], ...]`. |
| `lines` | `list` | Drawn unit segments as `{"from": [r, c], "to": [r, c], "width": int}` dictionaries. |
| `rows` | `int` | Number of grid cells vertically; row intersections are `0..rows`. |
| `cols` | `int` | Number of grid cells horizontally; column intersections are `0..cols`. |
| `line_width` | `int \| list[int]` | Fixed line width, or picker options when a list is supplied. |
| `dot_radius` | `int` | Drawn dot radius in pixels. |
| `theme` | `str \| None` | `None` follows the notebook; `"light"` or `"dark"` forces the widget theme. |
| `width` | `int` | Widget width in pixels. |
| `height` | `int` | Widget height in pixels. |

---
Démo : [`../demos/griddraw.py`](../demos/griddraw.py)
