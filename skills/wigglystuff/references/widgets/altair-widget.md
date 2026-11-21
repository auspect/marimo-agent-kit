<!-- wigglystuff 0.6.0, recopié de docs/reference/altair-widget.md (MIT) -->
# AltairWidget API


`AltairWidget` swaps a chart's data through the Vega View API instead of re-rendering
the whole spec, so driving an Altair chart from a slider updates smoothly rather than
flickering on every change.

Altair is a heavier dependency than the rest of wigglystuff, so this widget has no
in-browser demo — [run it on molab](https://molab.marimo.io/github/koaning/wigglystuff/blob/main/demos/altairwidget.py?utm_source=wigglystuff)
instead. See also: [ObservablePlot](observable-plot.md) for Observable Plot JS,
[ScatterLog](scatter-log.md) for accumulating reactive values into a live scatter, and
[RidgelineChart](ridgeline-chart.md) for stacked waveforms.

### `AltairWidget`

`from wigglystuff.altair_widget import AltairWidget`

```python
AltairWidget(chart: Any = None, *, width: int = 600, height: int = 400, **kwargs: Any) -> None
```

Flicker-free Altair chart widget.

Wraps an Altair chart and uses the Vega View API to update data in-place
when only the data portion of the spec changes, avoiding full DOM rebuilds.

The widget should be created once and then updated via the ``chart`` setter
from a reactive cell. This keeps the DOM element stable and allows the
JavaScript side to detect data-only changes and apply them smoothly.

Examples:
    ```python
    import marimo as mo
    import altair as alt
    import pandas as pd
    from wigglystuff import AltairWidget

    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    chart = alt.Chart(df).mark_point().encode(x="x", y="y")
    widget = mo.ui.anywidget(AltairWidget(chart))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `height` | Int | `400` |
| `spec` | Dict | |
| `width` | Int | `600` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `spec` | `dict` | Full Vega-Lite spec (from `chart.to_dict()`). |
| `width` | `int` | Container width in pixels. |
| `height` | `int` | Container height in pixels. |
