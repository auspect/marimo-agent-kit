<!-- wigglystuff 0.6.0, recopié de docs/reference/knob.md (MIT) -->
# Knob API


`Knob` is a rotary control that looks like a knob on a synth or mixing console.
Unlike [CircularSlider](circular-slider.md) (a full 360° ring), it sweeps a
partial arc with a gap at the bottom by default, with a pointer showing the
current position. Angles are measured in degrees clockwise from 12 o'clock, so
the default `start_angle=-135` / `end_angle=135` gives the classic 270° sweep;
pass a full `start_angle=0, end_angle=360` for a gapless dial that wraps.

Ticks are configurable — `ticks=N` for evenly spaced marks, a list of values, or
`(value, label)` pairs. Pass `steps` instead for a **rotary selector** that snaps
to discrete detents (numbers or named positions). With `midi=True` the knob shows
a "MIDI learn" button: click it, move a control on your hardware, and the next
control-change message binds to the knob (Web MIDI, Chromium browsers). The
binding is remembered in browser localStorage so it survives a restart.

See also: [Fader](fader.md) for the linear console version, and
[CircularSlider](circular-slider.md) for a full-ring dial.

### `Knob`

`from wigglystuff.knob import Knob`

```python
Knob(value: Optional[float] = None, min_value: float = 0.0, max_value: float = 100.0, step: float = 1.0, start_angle: float = -135.0, end_angle: float = 135.0, ticks: Union[NoneType, int, Sequence[Union[float, Sequence[Any]]]] = None, steps: Optional[Sequence[Any]] = None, size: int = 80, label: str = '', show_value: bool = True, color: str = '', midi: bool = False, midi_cc: int = -1, midi_channel: int = -1, midi_key: str = '', midi_scope: Optional[str] = None, **kwargs: Any) -> None
```

Audio-panel style rotary knob for selecting a single value.

Unlike :class:`CircularSlider` (a full 360° ring), the knob sweeps a partial
arc with a gap at the bottom, like a synth or mixer knob. A pointer line
shows the current position and you can drag it round. Angles are measured in
degrees clockwise from 12 o'clock, so the default ``start_angle=-135`` /
``end_angle=135`` gives the classic 270° sweep.

The value range increases clockwise from ``start_angle`` (mapped to
``min_value``) to ``end_angle`` (mapped to ``max_value``). Pass a full 360°
sweep (e.g. ``start_angle=0, end_angle=360``) for a gapless full-circle
knob that wraps at the seam.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import Knob

    gain = mo.ui.anywidget(
        Knob(min_value=0, max_value=11, value=5, ticks=12, label="Gain")
    )
    gain
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `''` |
| `end_angle` | Float | `135.0` |
| `label` | Unicode | `''` |
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
| `show_value` | Bool | `True` |
| `size` | Int | `80` |
| `start_angle` | Float | `-135.0` |
| `step` | Float | `1.0` |
| `steps` | List | |
| `ticks` | List | |
| `value` | Float | `0.0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `float` | Current value, mapped across the arc. |
| `min_value` | `float` | Lower bound (at `start_angle`). |
| `max_value` | `float` | Upper bound (at `end_angle`). |
| `step` | `float` | Snap increment in value units (continuous mode). |
| `start_angle` | `float` | Angle of `min_value`, degrees clockwise from 12 o'clock. |
| `end_angle` | `float` | Angle of `max_value`; a 360° span makes a full circle. |
| `ticks` | `list[dict]` | Normalized `{"value", "label"}` tick marks. |
| `steps` | `list[float]` | Discrete detents to snap to; empty means continuous. |
| `size` | `int` | Diameter in pixels. |
| `label` | `str` | Optional text label shown above the knob. |
| `show_value` | `bool` | Render the current value as text below the knob. |
| `color` | `str` | CSS color for the value arc and pointer. Empty follows the theme. |
| `midi` | `bool` | Show the MIDI-learn button and listen for control-change. |
| `midi_cc` | `int` | Bound control-change number (0-127), or `-1` when unbound. |
| `midi_channel` | `int` | Bound MIDI channel (0-15), or `-1` for any. |
| `midi_device` | `str` | Name of the bound MIDI input device. |
| `midi_supported` | `bool` | Whether the browser exposes Web MIDI (set from JS). |
| `midi_learning` | `bool` | Whether the knob is currently in learn mode. |
| `midi_key` | `str` | localStorage key for the persisted binding (defaults to `label`). |
| `midi_scope` | `str` | Namespace for the binding; empty uses the browser URL path. |

---
Démo : [`../demos/knob.py`](../demos/knob.py)
