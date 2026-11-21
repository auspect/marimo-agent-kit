<!-- wigglystuff 0.6.0, recopié de docs/reference/slider2d.md (MIT) -->
# Slider2D API


`Slider2D` renders a square canvas with a draggable dot and syncs its `x` and `y`
position back to Python, so a single gesture steers two parameters at once — in
Jupyter, marimo, Colab, or anything else that speaks AnyWidget.

See also: [ChartPuck](chart-puck.md) for dragging a puck over a matplotlib chart,
[CircularSlider](circular-slider.md) for a single-value dial, and
[Matrix](matrix.md) for editing a whole grid of numbers.

### `Slider2D`

`from wigglystuff.slider2d import Slider2D`

```python
Slider2D(x: float = 0.0, y: float = 0.0, width: int = 400, height: int = 400, x_bounds: tuple[float, float] = (-1.0, 1.0), y_bounds: tuple[float, float] = (-1.0, 1.0), **kwargs: Any) -> None
```

Two dimensional slider for simultaneous adjustments.

Emits synchronized ``x``/``y`` floats that stay within configurable bounds
while rendering to a pixel canvas sized via ``width``/``height``.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import Slider2D

    slider = mo.ui.anywidget(Slider2D(x=0.5, y=0.5, x_bounds=(0.0, 1.0), y_bounds=(0.0, 1.0)))
    slider
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `height` | Int | `400` |
| `width` | Int | `400` |
| `x` | Float | `0.0` |
| `x_bounds` | Tuple | |
| `y` | Float | `0.0` |
| `y_bounds` | Tuple | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `x` | `float` | Current x position. |
| `y` | `float` | Current y position. |
| `x_bounds` | `tuple[float, float]` | Min/max x bounds. |
| `y_bounds` | `tuple[float, float]` | Min/max y bounds. |
| `width` | `int` | Canvas width in pixels. |
| `height` | `int` | Canvas height in pixels. |

---
Démo : [`../demos/slider2d.py`](../demos/slider2d.py)
