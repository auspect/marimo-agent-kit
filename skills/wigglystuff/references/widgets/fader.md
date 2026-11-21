<!-- wigglystuff 0.6.0, recopié de docs/reference/fader.md (MIT) -->
# Fader API


`Fader` is a linear slider drawn to look like a channel fader on a mixing
console: a cap slides along a slot, with a configurable tick scale (e.g. dB
marks) alongside the track. It is vertical by default with `max_value` at the
top; pass `orientation="horizontal"` for a left-to-right fader.

Ticks are configurable — `ticks=N` for evenly spaced marks, a list of values, or
`(value, label)` pairs. Pass `steps` instead for a **stepped fader** that snaps
to discrete detents. With `midi=True` the fader shows a "MIDI learn" button:
click it, move a control on your hardware, and the next control-change message
binds to the fader (Web MIDI, Chromium browsers). The binding is remembered in
browser localStorage so it survives a restart.

See also: [Knob](knob.md) for the rotary console version, and
[HoverSlider](hover-slider.md) for a linear slider that also reports the value
under the pointer.

### `Fader`

`from wigglystuff.fader import Fader`

```python
Fader(value: Optional[float] = None, min_value: float = 0.0, max_value: float = 100.0, step: float = 1.0, ticks: Union[NoneType, int, Sequence[Union[float, Sequence[Any]]]] = None, steps: Optional[Sequence[Any]] = None, orientation: str = 'vertical', length: int = 200, label: str = '', show_value: bool = True, color: str = '', midi: bool = False, midi_cc: int = -1, midi_channel: int = -1, midi_key: str = '', midi_scope: Optional[str] = None, **kwargs: Any) -> None
```

Mixing-console style fader: a cap that slides along a track.

A linear slider drawn to look like a channel fader, with a configurable
tick scale (e.g. dB marks) alongside the track. Vertical by default, with
``max_value`` at the top; pass ``orientation="horizontal"`` for a
left-to-right fader.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import Fader

    level = mo.ui.anywidget(
        Fader(min_value=-60, max_value=6, value=0, ticks=[-60, -20, -6, 0, 6],
              label="Level")
    )
    level
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `''` |
| `label` | Unicode | `''` |
| `length` | Int | `200` |
| `max_value` | Float | `100.0` |
| `midi` | Bool | `False` |
| `midi_cc` | Int | `-1` |
| `midi_channel` | Int | `-1` |
| `midi_device` | Unicode | `''` |
| `midi_key` | Unicode | `''` |
| `midi_learning` | Bool | `False` |
| `midi_scope` | Unicode | `''` |
| `midi_supported` | Bool | `False` |
| `min_value` | Float | `0.0` |
| `orientation` | Unicode | `'vertical'` |
| `show_value` | Bool | `True` |
| `step` | Float | `1.0` |
| `steps` | List | |
| `ticks` | List | |
| `value` | Float | `0.0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `float` | Current value, mapped along the track. |
| `min_value` | `float` | Lower bound (bottom / left). |
| `max_value` | `float` | Upper bound (top / right). |
| `step` | `float` | Snap increment in value units (continuous mode). |
| `ticks` | `list[dict]` | Normalized `{"value", "label"}` tick marks. |
| `steps` | `list[float]` | Discrete detents to snap to; empty means continuous. |
| `orientation` | `str` | `"vertical"` (default) or `"horizontal"`. |
| `length` | `int` | Track length in pixels (the long dimension). |
| `label` | `str` | Optional text label shown above the fader. |
| `show_value` | `bool` | Render the current value as text next to the fader. |
| `color` | `str` | CSS color for the filled track and cap. Empty follows the theme. |
| `midi` | `bool` | Show the MIDI-learn button and listen for control-change. |
| `midi_cc` | `int` | Bound control-change number (0-127), or `-1` when unbound. |
| `midi_channel` | `int` | Bound MIDI channel (0-15), or `-1` for any. |
| `midi_device` | `str` | Name of the bound MIDI input device. |
| `midi_supported` | `bool` | Whether the browser exposes Web MIDI (set from JS). |
| `midi_learning` | `bool` | Whether the fader is currently in learn mode. |
| `midi_key` | `str` | localStorage key for the persisted binding (defaults to `label`). |
| `midi_scope` | `str` | Namespace for the binding; empty uses the browser URL path. |

---
Démo : [`../demos/fader.py`](../demos/fader.py)
