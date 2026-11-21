<!-- wigglystuff 0.6.0, recopié de docs/reference/scatter-widget.md (MIT) -->
# ScatterWidget API


`ScatterWidget` is a paintable scatter canvas: pick a class color, drag the brush, and the
points you paint come back as `data` (or as a DataFrame via `data_as_pandas`). It is the
fastest way to invent a small labeled 2D dataset for testing a classifier, sanity-checking
a clustering algorithm, or drawing the pathological case you want to explain. Up to four
classes, each with its own color and label, plus a `batch` key per stroke.

See also: [SplineDraw](spline-draw.md) for the same canvas with a Python-fitted curve on
top, [ChartMultiSelect](chart-multi-select.md) for labeling data you already have, and
[ScatterLog](scatter-log.md) for accumulating computed points rather than drawn ones.

> **Note:** `ScatterWidget` is provided by the [`drawdata`](https://github.com/koaning/drawdata) package and re-exported here for convenience. You can use it via `from wigglystuff import ScatterWidget` or `from drawdata import ScatterWidget`.

### `ScatterWidget`

`from wigglystuff.scatter_widget import ScatterWidget`

```python
ScatterWidget(*, n_classes: int = 4, brushsize: int = 40, width: int = 800, height: int = 400, **kwargs: Any) -> None
```

Interactive scatter drawing widget for painting multi-class 2D data points.

The widget renders a D3-powered SVG canvas where you can paint data points
using a configurable brush. Points are grouped by class (color) and batch,
making it easy to generate labeled 2D datasets interactively.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import ScatterWidget

    widget = mo.ui.anywidget(ScatterWidget(n_classes=3))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `brushsize` | Int | `40` |
| `data` | List | |
| `height` | Int | `400` |
| `n_classes` | Int | `4` |
| `width` | Int | `800` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `data` | `list[dict]` | List of drawn points with `x`, `y`, `color`, `label`, `batch` keys. |
| `brushsize` | `int` | Brush radius in pixels (default: 40). |
| `width` | `int` | SVG viewBox width in pixels (default: 800). |
| `height` | `int` | SVG viewBox height in pixels (default: 400). |
| `n_classes` | `int` | Number of point classes, 1-4 (default: 4). |

---
Démo : [`../demos/scatterwidget.py`](../demos/scatterwidget.py)
