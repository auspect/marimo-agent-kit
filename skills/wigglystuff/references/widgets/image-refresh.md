<!-- wigglystuff 0.6.0, recopié de docs/reference/image-refresh.md (MIT) -->
# ImageRefreshWidget API


`ImageRefreshWidget` renders one `<img>` element and repoints it at a new `src` whenever
that traitlet changes, so a running loop can redraw a single image slot rather than emit a
fresh picture per iteration. `src` is normally a base64 data URI; the
`wigglystuff.utils.refresh_matplotlib` decorator turns a plotting function into exactly
that, which is the usual way this widget gets fed.

See also: [HTMLRefreshWidget](html-refresh.md) for the same in-place trick with arbitrary
markup, [ProgressBar](progress-bar.md) for reporting how far the loop has got, and
[FramePlayer](frame-player.md) for replaying frames once the loop has finished.

### `ImageRefreshWidget`

`from wigglystuff.html import ImageRefreshWidget`

```python
ImageRefreshWidget(*args: 'object', **kwargs: 'object') -> 'None'
```

A widget that displays an image and refreshes when the source changes.

This widget creates an image element that automatically updates whenever
the `src` attribute is modified, making it ideal for displaying dynamically
generated images in Jupyter notebooks.

Attributes:
    src (str): The image source, typically a base64-encoded data URI.

Example:

```python
import marimo as mo
from wigglystuff import ImageRefreshWidget
from wigglystuff.utils import refresh_matplotlib
import matplotlib.pylab as plt
import numpy as np

@refresh_matplotlib
def plot_data(data):
    plt.plot(np.arange(len(data)), np.cumsum(data))

widget = mo.ui.anywidget(ImageRefreshWidget(src=plot_data([1, 2, 3, 4])))

# Update the widget with new data
widget.src = plot_data([1, 2, 3, 4, 5, 6])
```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `src` | Unicode | `''` |


### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `src` | `str` | The image source, typically a base64-encoded data URI. |

---
Démo : [`../demos/htmlwidget.py`](../demos/htmlwidget.py)
