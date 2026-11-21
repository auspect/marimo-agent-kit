<!-- wigglystuff 0.6.0, recopié de docs/reference/ridgeline-chart.md (MIT) -->
# RidgelineChart API


`RidgelineChart` draws each row of a pandas or polars DataFrame as its own line and lets the
rows overlap, the layout made famous by the PSR B1919+21 pulsar plot on Joy Division's
"Unknown Pleasures". It is a good fit for many same-shaped series — spectra, per-day
distributions, sensor channels — where you care about how the peaks shift from row to row.
Tune `overlap`, `peak_scale` and `fill_opacity` to trade legibility against density, and
read `selected_index` and `selected_row` to find out which waveform was clicked.

See also: [ParallelCoordinates](parallel-coords.md) for comparing many numeric columns of
the same row, [ObservablePlot](observable-plot.md) for writing a chart directly in
JavaScript, and [AltairWidget](altair-widget.md) for a full Vega-Lite spec.

### `RidgelineChart`

`from wigglystuff.ridgeline_chart import RidgelineChart`

```python
RidgelineChart(df: Any, width: int = 600, height: int = 400, overlap: float = 0.5, stroke_width: float = 1.5, fill_opacity: float = 1.0, peak_scale: float = 1.0, x_label: str = '', y_label: str = '', **kwargs: Any) -> None
```

Stacked overlapping line charts creating a ridge/horizon effect.

Inspired by the iconic PSR B1919+21 pulsar visualization from
Joy Division's "Unknown Pleasures" album cover. Each row represents
a waveform that can overlap with adjacent rows.

Examples:
    ```python
    import marimo as mo
    import pandas as pd
    import numpy as np
    from wigglystuff import RidgelineChart

    # Generate sample waveform data
    n_rows = 40
    n_points = 100
    data = {}
    for i in range(n_points):
        col = []
        for j in range(n_rows):
            x = i / n_points * 4 * np.pi
            y = np.sin(x + j * 0.1) * np.random.uniform(0.5, 1.5)
            col.append(y)
        data[i] = col

    df = pd.DataFrame(data)
    df.index = range(10, 10 + n_rows)  # Custom index

    chart = mo.ui.anywidget(RidgelineChart(df, x_label="Time", y_label="Channel"))
    chart
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `data` | List | |
| `fill_opacity` | Float | `1.0` |
| `height` | Int | `400` |
| `overlap` | Float | `0.5` |
| `peak_scale` | Float | `1.0` |
| `selected_index` | Any | `None` |
| `selected_row` | List | |
| `stroke_width` | Float | `1.5` |
| `width` | Int | `600` |
| `x_label` | Unicode | `''` |
| `x_values` | List | |
| `y_label` | Unicode | `''` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `data` | `list` | Internal data representation: list of {index, values} dicts. |
| `x_values` | `list` | X-coordinates (column names from DataFrame). |
| `width` | `int` | Chart width in pixels. |
| `height` | `int` | Chart height in pixels. |
| `overlap` | `float` | Amount of vertical overlap between rows (0.0 to 1.0). |
| `stroke_width` | `float` | Line stroke width in pixels. |
| `fill_opacity` | `float` | Opacity of the fill beneath each line (0.0 to 1.0). |
| `peak_scale` | `float` | Multiplier for peak height. |
| `x_label` | `str` | Label for the x-axis. |
| `y_label` | `str` | Label for the y-axis. |
| `selected_index` | `Any` | The index of the currently selected row (synced back to Python). |
| `selected_row` | `list` | The values of the currently selected row (synced back to Python). |

---
Démo : [`../demos/ridgelinechart.py`](../demos/ridgelinechart.py)
