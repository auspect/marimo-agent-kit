<!-- wigglystuff 0.6.0, recopié de docs/reference/progress-bar.md (MIT) -->
# ProgressBar API


`ProgressBar` draws a bar that fills as `value` climbs towards `max_value`, with a
`color`, `width`, `height` and an optional `value / max` readout underneath. The reason it
exists is that it does not depend on ipywidgets, so a loop that assigns `bar.value` reports
progress the same way in whatever notebook you happen to be running, and it follows the
surrounding light or dark theme.

See also: [HTMLRefreshWidget](html-refresh.md) for status text updated in place next to it,
[AnnotationWidget](annotation.md) for the labeling queue that bar is often counting, and
[PlaySlider](play-slider.md) when the value should be driven by the reader instead.

## Script mode: a rich terminal bar

The same `ProgressBar` works outside a notebook too. When the code runs as a
script — either a plain Python file or a marimo notebook run with
`uv run notebook.py` — and the optional [`rich`](https://github.com/Textualize/rich)
library is installed, each `bar.value` assignment is mirrored into a fancy
animated bar in the terminal: a spinner, a bar colored from `color`, a
percentage, an `M/N` count (shown when `show_text` is `True`) and a
time-remaining estimate. Because the value is applied as an absolute position,
the terminal bar moves backward too if `value` decreases.

marimo distinguishes these modes with `mo.app_meta().mode` (`"edit"`/`"run"` in
the browser, `"script"` on the command line), and `ProgressBar` keys off the
same signal — so one notebook shows the browser widget when edited and the rich
bar when executed. No changes to your loop are needed either way:

```python
import time
from wigglystuff import ProgressBar

bar = ProgressBar(max_value=50)
for i in range(51):
    bar.value = i
    time.sleep(0.05)
```

Install rich with `pip install rich`. If `rich` is not installed, or the code
runs inside a notebook editor, this behaves exactly as before — nothing extra is
rendered.

### `ProgressBar`

`from wigglystuff.html import ProgressBar`

```python
ProgressBar(value: int = 0, max_value: int = 100, color: str = '#22c55e', show_text: bool = True, width: str = '100%', height: int = 24)
```

A customizable progress bar widget for notebooks.

This widget displays a visual progress bar that updates in real-time as
the `value` attribute changes.

One of the main benefits of this utility is that you have a progress bar
that doesn't depend on ipywidgets while you still have something that
works across notebook projects.

When used in **script mode** (outside a marimo/jupyter notebook) and the
optional ``rich`` library is installed, the same progress is mirrored into a
fancy animated bar in the terminal. This needs no changes to your loop code:
just keep setting ``.value``. Install rich with ``pip install rich``. If
``rich`` is not installed, or you are in a notebook, this does nothing extra.

Attributes:
    value (int): The current progress value. Defaults to 0.
    max_value (int): The maximum value representing 100% completion. Defaults to 100.
    color (str): The fill color of the progress bar. Defaults to '#22c55e'.
    show_text (bool): Whether to show the progress text below the bar. Defaults to True.
    width (str): The CSS width of the progress bar. Defaults to '100%'.
    height (int): The height of the bar in pixels. Defaults to 24.

Example:

```python
import time
import marimo as mo
from wigglystuff import ProgressBar

progress = mo.ui.anywidget(ProgressBar(value=0, max_value=100))

for i in range(101):
    progress.value = i
    time.sleep(0.1)
```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `'#22c55e'` |
| `height` | Int | `24` |
| `max_value` | Int | `100` |
| `show_text` | Bool | `True` |
| `value` | Int | `0` |
| `width` | Unicode | `'100%'` |


### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `int` | The current progress value. Defaults to 0. |
| `max_value` | `int` | The maximum value representing 100% completion. Defaults to 100. |

---
Démo : [`../demos/progressbar.py`](../demos/progressbar.py)
