<!-- wigglystuff 0.6.0, recopié de docs/reference/gamepad.md (MIT) -->
# GamepadWidget API


`GamepadWidget` polls the browser's Gamepad API and mirrors the controller state into
traitlets: `axes` for the two analog sticks, four booleans for the D-pad, and
`current_button_press` plus timestamps for the latest button. It takes no arguments —
plug in a controller, press a button so the browser reports it, and observe the traits.
Useful for labelling loops and robot teleop where a keyboard is the wrong shape.

See also: [KeystrokeWidget](keystroke.md) for keyboard shortcuts instead of a controller,
[AnnotationWidget](annotation.md) for a labelling surface that already maps buttons,
keys and a gamepad to actions, and [WebkitSpeechToTextWidget](talk.md) for voice input.

### `GamepadWidget`

`from wigglystuff.gamepad import GamepadWidget`

```python
GamepadWidget(*args: 'object', **kwargs: 'object') -> 'None'
```

Listen to browser gamepad events and sync state back to Python.

This widget does not require any initialization arguments; all state is
mirrored through traitlets such as ``axes`` and ``current_button_press``.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import GamepadWidget

    gamepad = mo.ui.anywidget(GamepadWidget())
    gamepad
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `axes` | List | |
| `button_id` | Int | `0` |
| `current_button_press` | Int | `-1` |
| `current_timestamp` | Float | `0.0` |
| `dpad_down` | Bool | `False` |
| `dpad_left` | Bool | `False` |
| `dpad_right` | Bool | `False` |
| `dpad_up` | Bool | `False` |
| `previous_timestamp` | Float | `0.0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `current_button_press` | `int` | Index of the most recently pressed button. |
| `current_timestamp` | `float` | Timestamp (ms since epoch) of the latest press. |
| `previous_timestamp` | `float` | Timestamp of the previous press. |
| `axes` | `list[float]` | Analog stick positions (4 values). |
| `dpad_up` | `bool` | D-pad up state. |
| `dpad_down` | `bool` | D-pad down state. |
| `dpad_left` | `bool` | D-pad left state. |
| `dpad_right` | `bool` | D-pad right state. |
| `button_id` | `int` | Reserved for custom mappings (not set by the default UI). |


---
Démo : [`../demos/gamepad.py`](../demos/gamepad.py)
