<!-- wigglystuff 0.6.0, recopié de docs/reference/play-slider.md (MIT) -->
# PlaySlider API


`PlaySlider` is a slider with a play/pause button that walks `value` from
`min_value` to `max_value` by itself, one `step` every `interval_ms`, optionally
looping back to the start. Reach for it when a computation is already parameterized
by an index — frames, epochs, timesteps — and you want to watch it move instead of
dragging the handle yourself.

See also: [FramePlayer](frame-player.md) for playing back a sequence of images,
[HoverSlider](hover-slider.md) for previewing a value before committing to it, and
[CircularSlider](circular-slider.md) for a dial-shaped range.

### `PlaySlider`

`from wigglystuff.play_slider import PlaySlider`

```python
PlaySlider(value: Optional[float] = None, min_value: float = 0.0, max_value: float = 100.0, step: float = 1.0, interval_ms: int = 200, loop: bool = False, width: int = 400, **kwargs: Any) -> None
```

Slider with a play/pause button that auto-advances at a configurable pace.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import PlaySlider

    slider = mo.ui.anywidget(PlaySlider(min_value=0, max_value=50, step=1, interval_ms=300))
    slider
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `interval_ms` | Int | `200` |
| `loop` | Bool | `False` |
| `max_value` | Float | `100.0` |
| `min_value` | Float | `0.0` |
| `playing` | Bool | `False` |
| `step` | Float | `1.0` |
| `value` | Float | `0.0` |
| `width` | Int | `400` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `int` | Current slider value. |
| `min_value` | `int` | Minimum value. |
| `max_value` | `int` | Maximum value. |
| `step` | `int` | Step size per tick. |
| `interval_ms` | `int` | Milliseconds between auto-advance ticks. |
| `playing` | `bool` | Whether the slider is currently auto-advancing. |
| `loop` | `bool` | Whether to loop back to `min_value` after reaching `max_value`. |
| `width` | `int` | Widget width in pixels. |

---
Démo : [`../demos/play_slider.py`](../demos/play_slider.py)
