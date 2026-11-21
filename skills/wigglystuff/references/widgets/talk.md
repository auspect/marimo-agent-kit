<!-- wigglystuff 0.6.0, recopié de docs/reference/talk.md (MIT) -->
# WebkitSpeechToTextWidget API


`WebkitSpeechToTextWidget` is a thin bridge to the browser's WebKit speech recognition
API: press the button, talk, and the recognized text lands in `transcript` as a Python
string. Setting `trigger_listen` starts a session from code instead of the button, and
`listening` reflects whether recognition is running. Because it delegates to the
browser, availability depends on the browser — WebKit speech recognition is a
Chrome/Safari feature and is absent or unreliable elsewhere, so treat it as
best-effort rather than a dependable transcription pipeline.

See also: [AnnotationWidget](annotation.md) for labelling with speech, keys and buttons
in one surface, [KeystrokeWidget](keystroke.md) for keyboard input, and
[WebcamCapture](webcam-capture.md) for pulling video frames from the same browser APIs.

### `WebkitSpeechToTextWidget`

`from wigglystuff.talk import WebkitSpeechToTextWidget`

```python
WebkitSpeechToTextWidget(*args: 'object', **kwargs: 'object') -> 'None'
```

Speech-to-text widget backed by the browser's Webkit Speech API.

The widget exposes the ``transcript`` text along with the ``listening`` and
``trigger_listen`` booleans; it does not require initialization arguments.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import WebkitSpeechToTextWidget

    speech = mo.ui.anywidget(WebkitSpeechToTextWidget())
    speech
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `listening` | Bool | `False` |
| `transcript` | Unicode | `''` |
| `trigger_listen` | Bool | `False` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `transcript` | `str` | Latest transcript from the browser. |
| `listening` | `bool` | Whether speech recognition is active. |
| `trigger_listen` | `bool` | Toggle listening when set to true (auto-resets). |


---
Démo : [`../demos/talk.py`](../demos/talk.py)
