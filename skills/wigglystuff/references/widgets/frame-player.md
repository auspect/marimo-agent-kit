<!-- wigglystuff 0.6.0, recopié de docs/reference/frame-player.md (MIT) -->
# FramePlayer API


`FramePlayer` takes any iterable of frames — PIL images, file paths, URLs, bytes, base64
strings or matplotlib figures, mixed is fine — and plays them inline with play/pause, loop
and a scrubber, which saves writing a second cell that reads a slider and re-renders. Use
`set_frames()` to swap the sequence later and `n_frames` to check how many are loaded.
Every frame is base64-inlined into the widget model, so downsize long or high-resolution
sequences before passing them in.

See also: [PlaySlider](play-slider.md) if you would rather drive your own render step,
[ImageRefreshWidget](image-refresh.md) for one image slot updated live as it is computed,
and [WebcamCapture](webcam-capture.md) for collecting the frames in the first place.

### `FramePlayer`

`from wigglystuff.frame_player import FramePlayer`

```python
FramePlayer(frames: 'Iterable[Any]', value: 'int' = 0, interval_ms: 'int' = 100, loop: 'bool' = True, width: 'int' = 0, show_index: 'bool' = True, **kwargs: 'Any') -> 'None'
```

Play a sequence of images as an inline, optionally-looping "video".

Hook up any iterable of frames — PIL images, file paths, URLs, bytes,
base64 strings, or matplotlib figures (mixed is fine) — and the widget
renders the current frame with play/pause/loop controls and a scrubber,
so you don't need a second cell that reads a slider value and re-renders.

For long or high-resolution sequences, downsize the frames before passing
them in — every frame is base64-inlined into the widget model.

Examples:
    ```python
    import marimo as mo
    from PIL import Image
    from wigglystuff import FramePlayer

    frames = [Image.new("RGB", (128, 128), (i * 8 % 255, 0, 0)) for i in range(30)]
    player = mo.ui.anywidget(FramePlayer(frames, interval_ms=80, loop=True))
    player
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `frames` | List | |
| `interval_ms` | Int | `100` |
| `loop` | Bool | `True` |
| `playing` | Bool | `False` |
| `show_index` | Bool | `True` |
| `value` | Int | `0` |
| `width` | Int | `0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `frames` | `list[str]` | Base64 data URIs, one per frame. |
| `value` | `int` | Index of the currently displayed frame. |
| `interval_ms` | `int` | Milliseconds between frames while playing. |
| `playing` | `bool` | Whether playback is currently running. |
| `loop` | `bool` | Wrap back to the first frame at the end instead of stopping. |
| `width` | `int` | Display width in pixels (`0` = the image's natural width). |
| `show_index` | `bool` | Whether to show the "current / total" frame readout. |

---
Démo : [`../demos/frame_player.py`](../demos/frame_player.py)
