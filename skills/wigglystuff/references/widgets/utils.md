<!-- wigglystuff 0.6.0, recopié de docs/reference/utils.md (MIT) -->
# Utils API


Besides the widgets, `wigglystuff` ships a handful of plain helper functions: one that
builds a forecast chart from a time series, one that converts an Altair chart to SVG,
and two decorators that let a function's plot be swapped in place instead of
re-rendered.

See also: [AltairWidget](altair-widget.md) for flicker-free Altair updates,
[ImageRefreshWidget](image-refresh.md) and [HTMLRefreshWidget](html-refresh.md) for the
widgets the refresh decorators return.

## `forecast_chart`

### `forecast_chart`

`from wigglystuff.utils import forecast_chart`

```python
forecast_chart(df, date_col: 'str', value_col: 'str', fit_window: 'int' = 180, projection_days: 'int' = 365, title: 'str | None' = None, width: 'int | str | None' = None, height: 'int' = 400)
```

Create a time series chart with an exponential forecast.

Fits y = a * b^x via log-linear regression (Huber loss for robustness)
on the last ``fit_window`` data points and projects forward.

Args:
    df: A Polars DataFrame with at least a date column and a value column.
    date_col: Name of the date column.
    value_col: Name of the numeric value column.
    fit_window: Number of most-recent data points to use for the fit.
    projection_days: How many days to project into the future.
    title: Optional chart title.
    width: Chart width in pixels, or "container" for responsive. Defaults to "container".
    height: Chart height in pixels (default 400).

Returns:
    An interactive Altair chart with actual data (solid) and
    forecast (dashed).

Examples:
    ```python
    import polars as pl
    from wigglystuff import forecast_chart

    df = pl.DataFrame({"date": [...], "value": [...]})
    forecast_chart(df, "date", "value", fit_window=90)
    ```


---

## `altair2svg` 

### `altair2svg`

`from wigglystuff.utils import altair2svg`

```python
altair2svg(chart: 'Any') -> 'str'
```

Convert an Altair chart to SVG format.

Args:
    chart: An Altair chart object.

Returns:
    str: The SVG representation of the chart as a string.

Note:
    This function writes to disk temporarily as Altair doesn't provide
    an in-memory API for SVG conversion.


---

## `refresh_matplotlib`

### `refresh_matplotlib`

`from wigglystuff.utils import refresh_matplotlib`

```python
refresh_matplotlib(func: 'Callable[..., Any]') -> 'Callable[..., str]'
```

Decorator to convert matplotlib plotting functions to base64-encoded images.

This decorator wraps a matplotlib plotting function and returns a base64-encoded
data URI that can be used with ImageRefreshWidget for live updates.

Args:
    func: A function that creates matplotlib plots using plt commands.

Returns:
    callable: A wrapper function that returns a base64-encoded JPEG data URI.

Example:
    >>> @refresh_matplotlib
    ... def plot_sine(x):
    ...     plt.plot(x, np.sin(x))
    ...
    >>> widget = ImageRefreshWidget()
    >>> widget.src = plot_sine(np.linspace(0, 2*np.pi, 100))


---

## `refresh_altair`

### `refresh_altair`

`from wigglystuff.utils import refresh_altair`

```python
refresh_altair(func: 'Callable[..., Any]') -> 'Callable[..., str]'
```

Decorator to convert Altair chart functions to SVG strings.

This decorator wraps a function that returns an Altair chart and converts
the chart to an SVG string that can be used with HTMLRefreshWidget for live updates.

Args:
    func: A function that returns an Altair chart object.

Returns:
    callable: A wrapper function that returns an SVG string representation of the chart.

Example:
    >>> @refresh_altair
    ... def create_chart(data):
    ...     return alt.Chart(data).mark_bar().encode(x='x', y='y')
    ...
    >>> widget = HTMLRefreshWidget()
    >>> widget.html = create_chart(df)


---
Démo : [`../demos/forecast_chart.py`](../demos/forecast_chart.py)
