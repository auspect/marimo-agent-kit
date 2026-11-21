<!-- wigglystuff 0.6.0, recopié de docs/reference/webcam-capture.md (MIT) -->
# WebcamCapture API


`WebcamCapture` puts a live camera preview in the notebook with a capture button and an
auto-capture toggle. Each snapshot lands in `image_base64`, and `get_pil()` or
`get_bytes()` turn it into something a model can eat. Set `interval_ms` and flip
`capturing` to pull frames on a cadence — enough to run inference on a rough video
stream. `facing_mode` picks the front or rear camera; `error` reports refused access.

See also: [Paint](paint.md) for drawing on a canvas instead of photographing one,
[HoverZoom](hover-zoom.md) for inspecting a captured frame up close, and
[FramePlayer](frame-player.md) for replaying a run of captures as a loop.

### `WebcamCapture`

`from wigglystuff.webcam_capture import WebcamCapture`

```python
WebcamCapture(interval_ms: 'int' = 1000, facing_mode: 'str' = 'user') -> 'None'
```

Webcam capture widget with manual and interval snapshots.

The widget shows a live webcam preview plus a capture button and an
auto-capture toggle. When ``capturing`` is enabled, the browser updates
``image_base64`` on the cadence specified by ``interval_ms``.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import WebcamCapture

    cam = mo.ui.anywidget(WebcamCapture(interval_ms=1000))
    cam
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `capturing` | Bool | `False` |
| `error` | Unicode | `''` |
| `facing_mode` | Unicode | `'user'` |
| `image_base64` | Unicode | `''` |
| `interval_ms` | Int | `1000` |
| `ready` | Bool | `False` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `image_base64` | `str` | PNG data URL for the latest frame. |
| `capturing` | `bool` | Enable auto-capture mode. |
| `interval_ms` | `int` | Auto-capture interval in milliseconds. |
| `facing_mode` | `str` | Camera facing mode ("user" or "environment"). |
| `ready` | `bool` | True when the preview stream is ready. |
| `error` | `str` | Error message when webcam access fails. |


---
Démo : [`../demos/webcam_capture.py`](../demos/webcam_capture.py)
