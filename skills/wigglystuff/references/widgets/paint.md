<!-- wigglystuff 0.6.0, recopié de docs/reference/paint.md (MIT) -->
# Paint API


`Paint` drops an MS-Paint-style canvas into a notebook — brush, marker, eraser,
rainbow spray and a color picker, each toggleable — and hands the result back to
Python as a PIL image via `get_pil()`, ready to feed a model or a preprocessing
pipeline.

See also: [Excalidraw](excalidraw.md) for a full whiteboard, [GridDraw](grid-draw.md)
for snapping dots and lines to a grid, and [ScatterWidget](scatter-widget.md) for
painting labeled 2D datasets.

### `Paint`

`from wigglystuff.paint import Paint`

```python
Paint(height: 'int' = 500, width: 'int' = 889, store_background: 'bool' = True, init_image: 'Optional[Any]' = None, rainbow_brush: 'bool' = False, brush: 'bool' = True, marker: 'bool' = True, eraser: 'bool' = True, color_picker: 'bool' = True, color: 'str' = '#000000')
```

Notebook-friendly drawing canvas with brush, marker, eraser, undo, and PIL helpers.

Pass ``rainbow_brush=True`` to add an extra spray-paint tool that scatters
randomly-colored particles around the cursor — handy for generating noisy,
multi-color masks for image models.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import Paint

    paint = mo.ui.anywidget(Paint(width=400, height=300))
    paint
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `base64` | Unicode | `''` |
| `brush` | Bool | `True` |
| `color` | Unicode | `'#000000'` |
| `color_picker` | Bool | `True` |
| `eraser` | Bool | `True` |
| `height` | Int | `500` |
| `marker` | Bool | `True` |
| `rainbow_brush` | Bool | `False` |
| `store_background` | Bool | `True` |
| `width` | Int | `889` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `base64` | `str` | PNG data URL or raw base64 payload. |
| `width` | `int` | Canvas width in pixels. |
| `height` | `int` | Canvas height in pixels. |
| `store_background` | `bool` | Persist strokes when background changes. |
| `rainbow_brush` | `bool` | Show the rainbow spray tool (default off). |
| `brush` | `bool` | Show the thin brush tool. |
| `marker` | `bool` | Show the thick marker tool. |
| `eraser` | `bool` | Show the eraser tool. |
| `color_picker` | `bool` | Show the color picker. |
| `color` | `str` | Drawing color (hex); two-way synced with the picker. |


---
Démo : [`../demos/paint.py`](../demos/paint.py)
