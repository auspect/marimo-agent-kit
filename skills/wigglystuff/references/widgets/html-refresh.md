<!-- wigglystuff 0.6.0, recopié de docs/reference/html-refresh.md (MIT) -->
# HTMLRefreshWidget API


`HTMLRefreshWidget` keeps one `div` around and rewrites its contents every time the `html`
traitlet changes. It is the escape hatch for anything you can already express as markup —
an SVG chart, a small table, a line of status text — updated in place from a running cell
instead of printed again underneath. Note that the value is inserted as HTML, so only pass
markup you trust.

See also: [ImageRefreshWidget](image-refresh.md) for the same pattern with a rasterised
image, [ProgressBar](progress-bar.md) for the common case of showing a percentage, and
[EsmWidget](esm-widget.md) for when the thing you want to refresh needs JavaScript.

### `HTMLRefreshWidget`

`from wigglystuff.html import HTMLRefreshWidget`

```python
HTMLRefreshWidget(*args: 'object', **kwargs: 'object') -> 'None'
```

A widget that displays HTML content and refreshes when it changes.

This widget creates a div element that automatically updates whenever
the `html` attribute is modified, making it ideal for displaying dynamically
generated HTML content like SVG charts in Jupyter notebooks.

Attributes:
    html (str): The HTML content to display.

Example:

```python
import time
import marimo as mo
from wigglystuff import HTMLRefreshWidget

widget = mo.ui.anywidget(HTMLRefreshWidget(html="<p>Hello!</p>"))

# Update the widget with dynamic content
for i in range(10):
    widget.html = f"<p>Count: {i}</p>"
    time.sleep(0.5)
```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `html` | Unicode | `''` |


### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `html` | `str` | The HTML content to display. |

---
Démo : [`../demos/htmlwidget.py`](../demos/htmlwidget.py)
