<!-- wigglystuff 0.6.0, recopié de docs/reference/matrix.md (MIT) -->
# Matrix API


`Matrix` is a spreadsheet-like editor for a grid of numbers, with `min_value` and
`max_value` bounds, `row_names`/`col_names` labels, and `mirror` to keep edits
symmetric across the diagonal. It is the quick way to hand-build a covariance
matrix, a transition table or a small weight grid and watch the result downstream.
If you are on marimo, prefer `marimo.ui.matrix`; this widget stays for plain Jupyter
and other anywidget hosts.

See also: [Slider2D](slider2d.md) for two coupled numbers instead of a grid,
[SortableList](sortable-list.md) for ordering items rather than editing values, and
[TangleSlider](tangle.md) for a single number inline in text.

### `Matrix`

`from wigglystuff.matrix import Matrix`

```python
Matrix(matrix: Optional[List[List[float]]] = None, rows: int = 3, cols: int = 3, min_value: float = -100, max_value: float = 100, step: float = 1.0, digits: int = 1, mirror: bool = False, triangular: bool = False, row_names: Optional[List[str]] = None, col_names: Optional[List[str]] = None, static: bool = False, flexible_cols: bool = False, **kwargs: Any) -> None
```

Spreadsheet-like numeric editor with bounds, naming, and symmetry helpers.

Note:
    This widget has graduated to marimo core. If you are using marimo,
    prefer [`marimo.ui.matrix`](https://docs.marimo.io/api/inputs/matrix/).
    `Matrix` will continue to work in plain Jupyter and other anywidget
    hosts.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import Matrix

    matrix = mo.ui.anywidget(Matrix(rows=3, cols=3, min_value=0, max_value=10))
    matrix
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `col_names` | List | |
| `cols` | Int | `3` |
| `digits` | Int | `1` |
| `flexible_cols` | Bool | `False` |
| `matrix` | List | |
| `max_value` | Float | `100.0` |
| `min_value` | Float | `-100.0` |
| `mirror` | Bool | `False` |
| `row_names` | List | |
| `rows` | Int | `3` |
| `static` | Bool | `False` |
| `step` | Float | `1.0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `matrix` | `list[list[float]]` | Cell values. |
| `rows` | `int` | Row count. |
| `cols` | `int` | Column count. |
| `min_value` | `float` | Minimum allowed value. |
| `max_value` | `float` | Maximum allowed value. |
| `mirror` | `bool` | Mirror edits across the diagonal when enabled. |
| `step` | `float` | Step size for edits. |
| `digits` | `int` | Decimal precision for display. |
| `row_names` | `list[str]` | Optional row labels. |
| `col_names` | `list[str]` | Optional column labels. |
| `static` | `bool` | Disable editing when true. |
| `flexible_cols` | `bool` | Allow column count changes interactively. |


---
Démo : [`../demos/matrix.py`](../demos/matrix.py)
