<!-- wigglystuff 0.6.0, recopié de docs/reference/circular-slider.md (MIT) -->
# CircularSlider API


`CircularSlider` lays a value range around a dial: `start` sits at 12 o'clock and
values increase clockwise. `CircularRangeSlider` is the two-handle version, and
because the track is a circle a drag across the seam gives you a wrap-around
`(low, high)` tuple where `low > high` — which is what you want for hours, angles
and compass headings. Both mirror `mo.ui.slider` and `mo.ui.range_slider`
semantics, so `start`, `stop`, `step` and `value` behave as you already expect.

See also: [HoverSlider](hover-slider.md) for a linear track that also reports the
value under the pointer, [PlaySlider](play-slider.md) for a slider that advances on
a timer, and [Slider2D](slider2d.md) for steering two parameters with one gesture.

### `CircularSlider`

`from wigglystuff.circular_slider import CircularSlider`

```python
CircularSlider(start: float = 0.0, stop: float = 100.0, step: float = 1.0, value: Optional[float] = None, size: int = 220, thickness: int = 18, show_value: bool = True, color: str = '', label: str = '', **kwargs: Any) -> None
```

Circular dial slider for selecting a single value.

Mirrors ``mo.ui.slider`` semantics (``start``/``stop``/``step``/``value``)
but lays the range out around a full circle. The ``start`` value sits at
12 o'clock and values increase clockwise.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import CircularSlider

    dial = mo.ui.anywidget(CircularSlider(start=0, stop=100, step=1, value=42))
    dial
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `''` |
| `label` | Unicode | `''` |
| `show_value` | Bool | `True` |
| `size` | Int | `220` |
| `start` | Float | `0.0` |
| `step` | Float | `1.0` |
| `stop` | Float | `100.0` |
| `thickness` | Int | `18` |
| `value` | Float | `0.0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `float` | Current value, mapped onto the circular track. |
| `start` | `float` | Lower bound of the value range (sits at 12 o'clock). |
| `stop` | `float` | Upper bound of the value range. |
| `step` | `float` | Snap increment in value units. |
| `size` | `int` | Diameter in pixels. |
| `thickness` | `int` | Ring track thickness in pixels. |
| `show_value` | `bool` | Render the current value as text below the dial. |
| `color` | `str` | CSS color for the fill arc and handle border (e.g. `"#ef4444"`). Empty string follows the light/dark theme. |
| `label` | `str` | Optional text label shown above the dial. Empty string hides it. |

---

### `CircularRangeSlider`

`from wigglystuff.circular_slider import CircularRangeSlider`

```python
CircularRangeSlider(start: float = 0.0, stop: float = 100.0, step: float = 1.0, value: Optional[Tuple[float, float]] = None, size: int = 220, thickness: int = 18, show_value: bool = True, color: str = '', label: str = '', **kwargs: Any) -> None
```

Circular dial slider for selecting a span of values.

Mirrors ``mo.ui.range_slider`` semantics but lays the range out around a
full circle. ``value`` is a ``(low, high)`` tuple; both ends are draggable.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import CircularRangeSlider

    span = mo.ui.anywidget(CircularRangeSlider(start=0, stop=100, step=1, value=(20, 80)))
    span
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `''` |
| `label` | Unicode | `''` |
| `show_value` | Bool | `True` |
| `size` | Int | `220` |
| `start` | Float | `0.0` |
| `step` | Float | `1.0` |
| `stop` | Float | `100.0` |
| `thickness` | Int | `18` |
| `value` | Tuple | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `tuple[float, float]` | Current `(low, high)` range. A drag that crosses the 12 o'clock seam produces a wrap-around tuple where `low > high`. |
| `start` | `float` | Lower bound of the value range. |
| `stop` | `float` | Upper bound of the value range. |
| `step` | `float` | Snap increment in value units. |
| `size` | `int` | Diameter in pixels. |
| `thickness` | `int` | Ring track thickness in pixels. |
| `show_value` | `bool` | Render the current `low – high` range as text below the dial. |

---
Démo : [`../demos/circular_slider.py`](../demos/circular_slider.py)
