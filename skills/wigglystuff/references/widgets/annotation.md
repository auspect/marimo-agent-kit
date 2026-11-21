<!-- wigglystuff 0.6.0, recopié de docs/reference/annotation.md (MIT) -->
# AnnotationWidget API


`AnnotationWidget` is the input half of an annotation workflow: a row of action buttons
(`previous`, `accept`, `fail`, `defer` by default), a note field with speech-to-text, and
the same actions bound to number keys and gamepad buttons so you can label a queue
without reaching for the mouse. It deliberately does not render the thing being
annotated — your notebook shows the content and reacts to the `action` traitlet, and
because `action_timestamp` changes on every trigger, `observe` fires even when the same
action is picked twice in a row.

See also: [KeystrokeWidget](keystroke.md) for raw keypresses without the button UI,
[GamepadWidget](gamepad.md) for reading a controller's axes and buttons directly, and
[ProgressBar](progress-bar.md) for showing how far through the queue you are.

### `AnnotationWidget`

`from wigglystuff.annotation import AnnotationWidget`

```python
AnnotationWidget(*, actions: Optional[Sequence[str]] = None, keyboard_mapping: Optional[dict[str, str]] = None, gamepad_mapping: Optional[dict[str, str]] = None, debounce_ms: Optional[int] = None, width: Optional[int] = None, **kwargs: Any) -> None
```

Annotation input widget with buttons, keyboard shortcuts, gamepad, and speech-to-text.

This widget provides a UI input surface for annotation workflows. It does
NOT render the object being annotated — the notebook handles content
display and reacts to the ``action`` traitlet.

The ``action_timestamp`` traitlet changes on every action, even repeated
ones, so ``observe`` always fires.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import AnnotationWidget

    widget = mo.ui.anywidget(AnnotationWidget())
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `action` | Unicode | `''` |
| `action_timestamp` | Float | `0.0` |
| `actions` | List | |
| `debounce_ms` | Int | `200` |
| `disabled` | Bool | `False` |
| `gamepad_mapping` | Dict | |
| `keyboard_mapping` | Dict | |
| `listening` | Bool | `False` |
| `note` | Unicode | `''` |
| `show_save` | Bool | `True` |
| `width` | Int | `400` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `action` | `str` | Name of the most recently triggered action (e.g., `accept`, `fail`). |
| `action_timestamp` | `float` | Timestamp (ms since epoch) of the latest action; changes on every trigger so `observe` always fires, even for repeats. |
| `note` | `str` | Free-form note text, populated by typing or speech-to-text. |
| `listening` | `bool` | `True` while speech-to-text is actively transcribing. |
| `disabled` | `bool` | When `True`, all input controls are inert. |
| `show_save` | `bool` | Toggles visibility and availability of the footer Save button. |
| `actions` | `list[str]` | Ordered list of main action button labels. Defaults to `["previous", "accept", "fail", "defer"]`. |
| `keyboard_mapping` | `dict[str, str]` | Maps keys to action names. By default, action buttons are mapped to number keys in order (`1`, `2`, ...), with `s` for save and `m` for mic. The special target `mic` toggles the speech-to-text microphone. |
| `gamepad_mapping` | `dict[str, str]` | Maps gamepad button indices (as strings) to action names. By default, action buttons are mapped to gamepad buttons in order (`0`, `1`, ...), followed by save and mic. The `mic` target works here too. |
| `debounce_ms` | `int` | Minimum interval between accepted action triggers, in milliseconds. |
| `width` | `int` | Widget width in pixels. |

---
Démo : [`../demos/annotation.py`](../demos/annotation.py)
