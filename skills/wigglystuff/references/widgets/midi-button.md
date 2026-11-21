<!-- wigglystuff 0.6.0, recopié de docs/reference/midi-button.md (MIT) -->
# MidiButton API


`MidiButton` is a pad you can press on-screen or bind to a hardware MIDI pad.
Where [Knob](knob.md) and [Fader](fader.md) learn a continuous control-change,
`MidiButton` learns a MIDI **note** — the message a drum pad or launch button
sends — and turns presses into an event or a latched state.

Pick `mode="momentary"` (the default; `value` is `True` only while held) or
`mode="toggle"` (each press flips `value`). Every press also bumps
`press_timestamp`, so an `observe` handler fires even on repeated presses, and
`velocity` carries the note-on velocity (0-127; on-screen clicks send 127).

Put a glyph on the face with `icon`: a built-in name (`play`, `pause`, `stop`,
`record`, `skip-back`, `skip-forward`, `circle`, `square`, `triangle`, `heart`,
`star`, `bell`, `zap`, `check`, `x`, `plus`, `minus`, `power`, `mic`, `music`),
or any emoji/text rendered literally. With an `icon` set, `label` becomes a
caption above the pad; with no icon, `label` renders on the face.

MIDI is on by default: the pad shows a "MIDI learn" chip — click it, hit a pad
on your hardware, and the next note-on binds to this button (Web MIDI, Chromium
browsers). The binding is remembered in browser localStorage so it survives a
restart. Pass `midi=False` for a plain on-screen pad; read the binding back via
`midi_note` / `midi_channel` / `midi_device`.

See also: [Knob](knob.md) and [Fader](fader.md) for the continuous-CC members of
the same MIDI-learn family.

### `MidiButton`

`from wigglystuff.midi_button import MidiButton`

```python
MidiButton(label: str = '', icon: str = '', mode: str = 'momentary', value: bool = False, size: int = 64, color: str = '', midi: bool = True, midi_note: int = -1, midi_channel: int = -1, midi_key: str = '', midi_scope: Optional[str] = None, **kwargs: Any) -> None
```

A button that you can press on-screen or bind to a hardware MIDI pad.

Unlike :class:`Knob` / :class:`Fader` (which learn a continuous
control-change), a ``MidiButton`` learns a MIDI **note** — the message a
drum pad or launch button sends — and turns presses into an event or a
latched on/off state.

Two modes:

- ``"momentary"`` (default): ``value`` is ``True`` only while the button is
  held (mouse down, or note-on until note-off). Every press also bumps
  ``press_timestamp`` so an ``observe`` handler fires even on repeated
  presses.
- ``"toggle"``: each press flips ``value`` between ``True`` and ``False``;
  releases are ignored.

The MIDI "learn" flow mirrors the Knob: click the small **MIDI** chip, then
hit a pad on your hardware — the next note-on binds to this button. Bindings
persist in browser localStorage (keyed by ``midi_key`` / ``label``) and use
the Web MIDI API (Chromium browsers, secure context).

Examples:
    ```python
    import marimo as mo
    from wigglystuff import MidiButton

    trigger = mo.ui.anywidget(MidiButton(label="Fire", midi=True))
    trigger
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `''` |
| `icon` | Unicode | `''` |
| `label` | Unicode | `''` |
| `midi` | Bool | `True` |
| `midi_channel` | Int | `-1` |
| `midi_device` | Unicode | `''` |
| `midi_key` | Unicode | `''` |
| `midi_learning` | Bool | `False` |
| `midi_note` | Int | `-1` |
| `midi_scope` | Unicode | `''` |
| `midi_supported` | Bool | `False` |
| `mode` | Unicode | `'momentary'` |
| `press_timestamp` | Float | `0.0` |
| `size` | Int | `64` |
| `value` | Bool | `False` |
| `velocity` | Int | `0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `bool` | Pressed (momentary) or on/off (toggle) state. |
| `press_timestamp` | `float` | Bumped on every press so `observe` fires on repeats. |
| `velocity` | `int` | Note-on velocity (0-127) of the last press; 127 for a click. |
| `label` | `str` | Caption above the pad, or the face text when no icon. |
| `icon` | `str` | Built-in icon name, or any emoji/text for the face. |
| `mode` | `str` | `"momentary"` or `"toggle"`. |
| `size` | `int` | Pad size in pixels (square). |
| `color` | `str` | CSS color for the active pad. Empty follows the theme. |
| `midi` | `bool` | Show the MIDI-learn chip and listen for notes. |
| `midi_note` | `int` | Bound note number (0-127), or `-1` when unbound. |
| `midi_channel` | `int` | Bound MIDI channel (0-15), or `-1` for any. |
| `midi_device` | `str` | Name of the bound MIDI input device. |
| `midi_supported` | `bool` | Whether the browser exposes Web MIDI (set from JS). |
| `midi_learning` | `bool` | Whether the pad is currently in learn mode. |
| `midi_key` | `str` | localStorage key for the persisted binding (defaults to `label`). |
| `midi_scope` | `str` | Namespace for the binding; empty uses the browser URL path. |

---
Démo : [`../demos/midi_button.py`](../demos/midi_button.py)
