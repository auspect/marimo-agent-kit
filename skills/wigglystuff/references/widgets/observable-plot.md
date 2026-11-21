<!-- wigglystuff 0.6.0, recopié de docs/reference/observable-plot.md (MIT) -->
# ObservablePlot API


`ObservablePlot` is a thin runner for [Observable Plot](https://observablehq.com/plot/): it
loads Plot and d3 from a CDN, evaluates the JavaScript you hand it — inline, from a local
file, or from a URL — and mounts the DOM node that expression returns. Python values passed
in `variables` become in-scope JavaScript variables, with DataFrames and numpy arrays
converted to JSON records first. Reassigning `code` or `variables` rebuilds the chart, and
the new node is swapped in only once it is ready, so slider-driven updates never flash a
blank frame.

See also: [AltairWidget](altair-widget.md) for driving a Vega-Lite spec from Python,
[EsmWidget](esm-widget.md) for running any CDN library with a two-way `data` bridge, and
[RidgelineChart](ridgeline-chart.md) for a chart that needs no JavaScript at all.

### `ObservablePlot`

`from wigglystuff.observable_plot import ObservablePlot`

```python
ObservablePlot(code: Optional[str] = None, *, src: Optional[str] = None, variables: Optional[Dict[str, Any]] = None, width: int = 500, height: int = 300, version: str = 'latest', **kwargs: Any) -> None
```

Run `Observable Plot <https://observablehq.com/plot/>`_ code in a notebook.

Observable Plot is a JavaScript charting library. This widget is a thin
runner: it loads Plot (and d3) from a CDN, then evaluates a blob of
JavaScript you supply (the ``code`` traitlet) exactly as you would write it
in an Observable notebook — a bare ``Plot.plot({...})`` expression that
returns a DOM node. The returned node is mounted inline; Python's job is to
hand over the source, the data, and the sizing.

Python values are injected into the code's scope by name via ``variables``:
each key becomes an in-scope JavaScript variable holding the (JSON-ified)
value. So ``variables={"vacancies": df}`` lets your code reference
``vacancies`` directly::

    Plot.plot({
        marks: [
            Plot.barY(vacancies, { x: "month", y: "vacancies" }),
            Plot.ruleY([0]),
        ],
    })

``Plot`` and ``d3`` are always in scope, along with ``container`` (the
target DOM element), the ``width`` / ``height`` ints, and the widget
``model``. Pandas / polars DataFrames and numpy arrays in ``variables`` are
converted to plain JSON structures (records / lists) before syncing.

The code is evaluated verbatim in the browser, so only pass JavaScript you
trust (typically your own).

Reassigning ``code``, ``variables``, ``width``, ``height``, or ``version``
re-runs the code and rebuilds the chart. Observable Plot has no incremental
redraw — each run produces a fresh SVG — but the new node is swapped in
atomically (the previous chart stays put until it is ready), so updates
driven by e.g. a slider do not flash a blank frame.

Examples:
    ```python
    import marimo as mo
    import pandas as pd
    from wigglystuff import ObservablePlot

    df = pd.DataFrame({"month": ["Jan", "Feb", "Mar"], "vacancies": [3, 5, 2]})
    code = '''
        Plot.plot({
            marks: [
                Plot.barY(vacancies, { x: "month", y: "vacancies" }),
                Plot.ruleY([0]),
            ],
        })
    '''
    mo.ui.anywidget(ObservablePlot(code, variables={"vacancies": df}))
    ```

    Point at a local file or a URL instead of an inline string — the first
    argument accepts any of the three forms:

    ```python
    ObservablePlot("charts/bars.js", variables={"vacancies": df})
    ObservablePlot("https://example.com/chart.js")
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `code` | Unicode | `''` |
| `error` | Unicode | `''` |
| `height` | Int | `300` |
| `variables` | Dict | |
| `version` | Unicode | `'latest'` |
| `width` | Int | `500` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `code` | `str` | Resolved Observable Plot JavaScript (inline JS, or the contents of a file / URL, fetched in Python), evaluated as an expression that returns the DOM node to mount. |
| `variables` | `dict` | Name → value mapping injected into the code's scope as JavaScript variables. DataFrames and numpy arrays are converted to JSON records/lists on assignment. |
| `width` | `int` | Container width in pixels. |
| `height` | `int` | Container height in pixels. |
| `version` | `str` | `@observablehq/plot` version loaded from the CDN (defaults to `"latest"`). |
| `error` | `str` | Read-back of the latest JS runtime / CDN-load error, or `""`. |

---
Démo : [`../demos/observableplot.py`](../demos/observableplot.py)
