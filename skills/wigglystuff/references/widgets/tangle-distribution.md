<!-- wigglystuff 0.6.0, recopié de docs/reference/tangle-distribution.md (MIT) -->
# TangleDistribution API


Sometimes a single number is too confident. `TangleDistribution` puts a whole
distribution inside your prose, rendered as `50.0 ± 10.0` by default. Drag
left/right to change one parameter and up/down to change the other; while you
drag, a small chart floats above the page with the starting shape dashed and the
current one filled, so you can see exactly what you are changing.

Fourteen families are supported (`TangleDistribution.distributions`), named after
their `scipy.stats` counterparts and using the same parameters. The maths is built
in, so `cdf`, `ppf`, `pdf`/`pmf` and `sample` work without scipy, and only for the
families listed here.

| family | kind | ↔ drag | ↕ drag |
| --- | --- | --- | --- |
| `norm` | continuous | `loc` | `scale` |
| `lognorm` | continuous | `scale` (the median) | `s` |
| `gamma` | continuous | `scale` | `a` (the shape) |
| `expon` | continuous | `scale` (the mean) | (none) |
| `weibull_min` | continuous | `scale` | `c` (the shape) |
| `uniform` | continuous | `loc` (left edge) | `scale` (width) |
| `laplace` | continuous | `loc` | `scale` |
| `logistic` | continuous | `loc` | `scale` |
| `beta` | continuous | `a` | `b` |
| `poisson` | discrete | `mu` | (none) |
| `binom` | discrete | `p` | `n` (whole number) |
| `nbinom` | discrete | `p` | `n` |
| `geom` | discrete | `p` | (none) |
| `randint` | discrete | `low` | `high` (excluded, as in scipy) |

`params` only changes when you let go of a drag. While dragging, `live_params`
follows the pointer and `dragging` is `True`, so the rest of a notebook can show
the old and the new distribution side by side. Every method takes `live=True` to
use the in-progress values:

```python
from wigglystuff import TangleDistribution

delivery = TangleDistribution("lognorm", params={"scale": 25, "s": 0.3}, template="{mean:.0f} ± {sd:.0f} minutes")

delivery.ppf(0.9)            # 90% of deliveries arrive within this many minutes
delivery.cdf(30)             # chance it arrives within half an hour
delivery.sample(1000)        # numpy array of draws
delivery.ppf(0.9, live=True) # the same, for the distribution being dragged right now
```

The inline text comes from `template`. Its placeholders are the keys of `params`
plus the computed `mean` and `sd` (`widget.template_fields` lists them), each with
an optional `:.Nf` precision, e.g. `"median {scale:.0f} days (s={s:.2f})"`.

See also: [Tangle widgets](tangle.md) for a single draggable number, and
[TangleFunction](tangle-function.md) for turning a whole function call into
draggable arguments.

### `TangleDistribution`

`from wigglystuff.tangle import TangleDistribution`

```python
TangleDistribution(distribution: str = 'norm', params: Optional[Dict[str, float]] = None, bounds: Optional[Dict[str, Tuple[Optional[float], Optional[float]]]] = None, steps: Optional[Dict[str, float]] = None, pixels_per_step: int = 2, template: str = '{mean} ± {sd}', digits: Optional[int] = None, sync_throttle_ms: int = 100, **kwargs: Any) -> None
```

Inline tangle number that carries a whole distribution.

Drag left/right to change the first parameter and up/down to change the
second. While dragging, a small chart of the distribution floats above the
page so you can see the shape change. Family and parameter names follow
``scipy.stats``, but only the families below are supported (see
``TangleDistribution.distributions``), and the maths is built in, so scipy
is not needed.

| family | kind | ↔ drag | ↕ drag |
| --- | --- | --- | --- |
| ``"norm"`` | continuous | ``loc`` | ``scale`` |
| ``"lognorm"`` | continuous | ``scale`` (the median) | ``s`` |
| ``"gamma"`` | continuous | ``scale`` | ``a`` (the shape) |
| ``"expon"`` | continuous | ``scale`` (the mean) | (none) |
| ``"weibull_min"`` | continuous | ``scale`` | ``c`` (the shape) |
| ``"uniform"`` | continuous | ``loc`` (left edge) | ``scale`` (width) |
| ``"laplace"`` | continuous | ``loc`` | ``scale`` |
| ``"logistic"`` | continuous | ``loc`` | ``scale`` |
| ``"beta"`` | continuous | ``a`` | ``b`` |
| ``"poisson"`` | discrete | ``mu`` | (none) |
| ``"binom"`` | discrete | ``p`` | ``n`` (whole number) |
| ``"nbinom"`` | discrete | ``p`` | ``n`` |
| ``"geom"`` | discrete | ``p`` | (none) |
| ``"randint"`` | discrete | ``low`` | ``high`` (excluded, as in scipy) |

Template fields are the parameters in the table plus ``mean`` and ``sd``.

Reading the distribution back in Python:

- ``params`` holds the committed values and only changes when a drag is
  released. While dragging, ``live_params`` follows the pointer (throttled
  by ``sync_throttle_ms``) and ``dragging`` is True, so the rest of the
  notebook can compare the old distribution against the new one live.
- ``mean`` and ``sd`` are computed from ``params``.
- ``pdf(x)`` (continuous) or ``pmf(k)`` (discrete), ``cdf(x)``,
  ``ppf(q)`` and ``sample(n)`` all accept ``live=True`` to use
  ``live_params`` instead. ``sample`` needs numpy, as do the others when
  given an array.

The inline text comes from ``template``, by default ``"{mean} ± {sd}"``.
Placeholders are the keys of ``params`` plus the computed ``mean`` and
``sd`` (``widget.template_fields`` lists them), each with an optional
``:.Nf`` precision, e.g. ``"median {scale:.0f} days (s={s:.2f})"``.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import TangleDistribution

    duration = mo.ui.anywidget(
        TangleDistribution("lognorm", params={"scale": 10, "s": 0.4}, template="{mean} ± {sd} days")
    )
    duration
    ```

    ```python
    duration.ppf(0.9)  # 90% of runs finish within this many days
    duration.cdf(14)   # chance of finishing within two weeks
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `bounds` | Dict | |
| `digits` | Int | `1` |
| `distribution` | Unicode | `'norm'` |
| `dragging` | Bool | `False` |
| `live_params` | Dict | |
| `params` | Dict | |
| `pixels_per_step` | Int | `2` |
| `steps` | Dict | |
| `sync_throttle_ms` | Int | `100` |
| `template` | Unicode | `'{mean} ± {sd}'` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `distribution` | `str` | Family name, one of `TangleDistribution.distributions`. |
| `params` | `dict` | Committed parameters by scipy name; changes when a drag is released. |
| `live_params` | `dict` | In-progress parameters while dragging; equals `params` otherwise. |
| `dragging` | `bool` | `True` while the pointer is held down on the widget. |
| `bounds` | `dict` | `[low, high]` per parameter; either end may be `None`. |
| `steps` | `dict` | Change per drag step, per parameter. |
| `pixels_per_step` | `int` | Drag distance per step. |
| `template` | `str` | Inline text with `{param}`, `{mean}` and `{sd}` placeholders. |
| `digits` | `int` | Default number of decimals in the inline text. |
| `sync_throttle_ms` | `int` | Cap on how often `live_params` reaches Python while dragging. |

---
Démo : [`../demos/tangle_distribution.py`](../demos/tangle_distribution.py)
