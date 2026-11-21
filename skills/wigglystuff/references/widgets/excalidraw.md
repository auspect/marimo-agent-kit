<!-- wigglystuff 0.6.0, recopié de docs/reference/excalidraw.md (MIT) -->
# Excalidraw API


`Excalidraw` puts the Excalidraw whiteboard in a notebook cell: an infinite canvas with
shapes, arrows, text and freehand strokes. Excalidraw and React are fetched from a CDN
the first time the widget renders, so it needs network access. The drawing lives on the
`scene` traitlet and nothing is written to disk until you call `save()`; `get_pil()`
hands the board to Python as an image — handy for a multimodal model — and
`Excalidraw.from_file()` loads a saved `.excalidraw` file back.

See also: [Paint](paint.md) for a smaller MS-Paint-style canvas, [GridDraw](grid-draw.md)
for dots and lines snapped to a grid, and [EdgeDraw](edge-draw.md) for node and link
diagrams you can compute on.

### `Excalidraw`

`from wigglystuff.excalidraw import Excalidraw`

```python
Excalidraw(scene: Optional[dict] = None, height: int = 600, sync_throttle_ms: int = 1000, theme: str = 'light', **kwargs)
```

An embedded [Excalidraw](https://excalidraw.com) whiteboard.

Draw shapes, arrows, text, and freehand sketches on an infinite canvas.
The current drawing is kept in memory on the ``scene`` traitlet as an
Excalidraw scene dict (``elements`` / ``appState`` / ``files``). Like the
other drawing widgets, nothing is written to disk automatically — call
:meth:`save` when you want to persist, and load with :meth:`from_file`.

Args:
    scene: Optional Excalidraw scene dict to preload the canvas with.
    height: Canvas height in pixels.
    sync_throttle_ms: Minimum delay between syncing edits back to Python.
    theme: ``"light"`` (default) or ``"dark"``. Set it to ``""`` to instead
        follow the notebook's theme.

Example:
    ```python
    import marimo as mo
    from wigglystuff import Excalidraw

    draw = mo.ui.anywidget(Excalidraw())
    draw
    ```

    After sketching something:

    ```python
    draw.save("diagram.excalidraw")          # write to disk
    again = Excalidraw.from_file("diagram.excalidraw")  # load it back
    again.save()                              # write back to diagram.excalidraw
    again.save("other.excalidraw")            # save elsewhere (and remember it)
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `height` | Int | `600` |
| `image_base64` | Unicode | `''` |
| `scene` | Dict | |
| `sync_throttle_ms` | Int | `1000` |
| `theme` | Unicode | `''` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `scene` | `dict` | Excalidraw scene (`elements` / `appState` / `files`). |
| `image_base64` | `str` | PNG data URL of the drawing; read via `get_pil()`. |
| `theme` | `str` | `"light"` (default) or `"dark"`; `""` follows the notebook theme. |
| `height` | `int` | Canvas height in pixels. |
| `sync_throttle_ms` | `int` | Minimum delay between syncing edits back to Python. |

Excalidraw itself is loaded from a CDN the first time the widget renders, so the
widget needs network access and does not work fully offline.

---
Démo : [`../demos/excalidraw.py`](../demos/excalidraw.py)
