<!-- wigglystuff 0.6.0, recopié de docs/reference/keystroke.md (MIT) -->
# KeystrokeWidget API


`KeystrokeWidget` records the most recent keypress made while the widget has focus and
puts it in `last_key` as a dict mirroring the browser `KeyboardEvent`: `key`, `code`, the
four modifier booleans, and a millisecond `timestamp`. It takes no arguments. Click the
panel first, then press a combination — the timestamp changes on every press, so
observing `last_key` also catches the same shortcut being hit twice in a row.

See also: [GamepadWidget](gamepad.md) for controller buttons and sticks,
[AnnotationWidget](annotation.md) for mapping keys straight onto labelling actions, and
[WebkitSpeechToTextWidget](talk.md) for dictating instead of typing.

### `KeystrokeWidget`

`from wigglystuff.keystroke import KeystrokeWidget`

```python
KeystrokeWidget(*args: 'object', **kwargs: 'object') -> 'None'
```

Capture the latest keyboard shortcut pressed inside the widget.

No initialization arguments are required; the widget simply records
keystrokes into the ``last_key`` trait.

The ``last_key`` payload mirrors browser ``KeyboardEvent`` data with:
``key``, ``code``, modifier booleans (``ctrlKey``, ``shiftKey``,
``altKey``, ``metaKey``), and a ``timestamp`` in milliseconds since epoch.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import KeystrokeWidget

    keystroke = mo.ui.anywidget(KeystrokeWidget())
    keystroke
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `last_key` | Dict | |


## Synced traitlets

`last_key` is a dictionary synced from the browser after each keypress. When no
keypress has been captured yet, it is an empty dict.

| Key | Type | Notes |
| --- | --- | --- |
| `key` | `str` | Display value for the key (e.g., `a`, `Enter`). |
| `code` | `str` | Physical key code (e.g., `KeyA`, `Enter`). |
| `ctrlKey` | `bool` | `True` when Control is held. |
| `shiftKey` | `bool` | `True` when Shift is held. |
| `altKey` | `bool` | `True` when Alt/Option is held. |
| `metaKey` | `bool` | `True` when Command/Meta is held. |
| `timestamp` | `int` | Milliseconds since epoch at capture time. |


---
Démo : [`../demos/keystroke.py`](../demos/keystroke.py)
