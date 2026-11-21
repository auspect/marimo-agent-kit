<!-- wigglystuff 0.6.0, recopié de docs/reference/hover-zoom.md (MIT) -->
# HoverZoom API


`HoverZoom` shows an image with a rectangle indicator under the cursor and a magnified
panel beside it — the e-commerce product zoom pattern, aimed at plots. It is handy when a
matplotlib figure has more points than pixels and the overlapping labels only separate
under magnification. It takes a figure, file path, URL, PIL image, bytes or base64
string, and `get_pil_zoom()` returns the region currently under the cursor as an image.

See also: [ChartPuck](chart-puck.md) for dragging a control point over a chart,
[WebcamCapture](webcam-capture.md) for getting images into the notebook in the first
place, and [FramePlayer](frame-player.md) for stepping through a sequence of images.

### `HoverZoom`

`from wigglystuff.hover_zoom import HoverZoom`

```python
HoverZoom(image: 'Optional[Union[str, Path, Any]]' = None, *, zoom_factor: 'float' = 3.0, width: 'int' = 500, height: 'int' = 0)
```

Image widget with a magnified side panel that appears on hover.

Hovering over the image shows a rectangle indicator and a zoom panel
to the right displaying the magnified region — the classic e-commerce
product zoom pattern.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import HoverZoom

    # From a file path
    widget = mo.ui.anywidget(HoverZoom("photo.jpg", zoom_factor=3.0))

    # From a matplotlib figure
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.scatter(x, y, s=5, alpha=0.5)
    widget = mo.ui.anywidget(HoverZoom(fig, zoom_factor=4.0))
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `height` | Int | `0` |
| `image` | Unicode | `''` |
| `width` | Int | `500` |
| `zoom_factor` | Float | `3.0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `image` | `str` | Base64-encoded image data. |
| `zoom_factor` | `float` | Magnification level for the zoom panel. |
| `width` | `int` | Display width of the source image in pixels. |
| `height` | `int` | Display height in pixels (0 = auto). |

---
Démo : [`../demos/hoverzoom.py`](../demos/hoverzoom.py)
