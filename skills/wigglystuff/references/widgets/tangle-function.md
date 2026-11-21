<!-- wigglystuff 0.6.0, recopié de docs/reference/tangle-function.md (MIT) -->
# TangleFunction API


`TangleFunction` introspects a function's type hints and defaults and renders it
as a clean call expression such as `train(lr=0.01, epochs=10, optimizer='adam')`.
Numbers drag horizontally to scrub (and click to type an exact value),
`Literal`/`Enum`/`bool` arguments click to cycle through their known options, and
strings are click-to-edit. The live arguments land in `values`, ready to splat
into the function with `fn(**tf.value["values"])`.

Numbers are unbounded scrubbers by default. Give one a range or a step by
annotating it with [`annotated_types`](https://pypi.org/project/annotated-types/)
constraints (`Ge`, `Le`, `Gt`, `Lt`, `MultipleOf`) — the same constraints
pydantic uses, so `pydantic.Field(ge=..., le=...)` works too — or with a
`params=` override.

See also: [TangleLatex](tangle-latex.md) for the same drag gesture inside a LaTeX
formula, and [Tangle widgets](tangle.md) for individual inline sliders and
choices in plain prose.

### `TangleFunction`

`from wigglystuff.tangle_function import TangleFunction`

```python
TangleFunction(fn: 'Callable[..., Any]', params: 'Optional[Mapping[str, Mapping[str, Any]]]' = None, *, theme: 'str' = 'auto', width: 'int' = 560, **kwargs: 'Any') -> 'None'
```

Render a typed Python function as an interactive call expression.

Each argument becomes editable in place: numbers drag horizontally to scrub,
``Literal``/``Enum``/``bool`` arguments click to cycle through their known
options, and strings are click-to-edit. The live arguments are synced to the
``values`` dict, ready to splat into the function.

``values`` follows a drag live. ``committed_values`` keeps the values from
before the drag until it is released, so the notebook can compare the old
call with the new one while you scrub; ``dragging`` is True in between.
Outside a drag the two are equal.

Examples:
    ```python
    import marimo as mo
    from typing import Literal
    from wigglystuff import TangleFunction

    def train(lr: float = 0.01, epochs: int = 10,
              optimizer: Literal["adam", "sgd"] = "adam", shuffle: bool = True):
        ...

    tf = mo.ui.anywidget(TangleFunction(train))
    tf
    # in another cell:
    train(**tf.value["values"])
    ```

Numbers are unbounded scrubbers by default. Give one a range or a step by
annotating it with `annotated_types` constraints (the same ones pydantic
uses, so ``pydantic.Field(ge=..., le=...)`` works too):

    ```python
    from typing import Annotated
    from annotated_types import Ge, Le, MultipleOf

    def generate(temperature: Annotated[float, Ge(0), Le(2), MultipleOf(0.05)] = 0.7):
        ...

    mo.ui.anywidget(TangleFunction(generate))
    ```

Note:
    For ``Enum`` parameters the emitted value is the member's ``.value`` (so
    it stays JSON-serializable and matches the displayed label). ``Literal``
    is the recommended way to expose a known set of options.

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `committed_values` | Dict | |
| `dragging` | Bool | `False` |
| `error` | Unicode | `''` |
| `fn_name` | Unicode | `'f'` |
| `param_order` | List | |
| `parameters` | Dict | |
| `theme` | Enum | `'auto'` |
| `values` | Dict | |
| `width` | Int | `560` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `fn_name` | `str` | The function's name, shown before the opening parenthesis. |
| `parameters` | `dict` | Per-parameter render spec (kind, options/bounds/step/digits). |
| `param_order` | `list` | Parameter names in signature order. |
| `values` | `dict` | Live current value for each parameter; splat into the function. |
| `committed_values` | `dict` | Values from before the current drag; catch up on release. |
| `dragging` | `bool` | `True` while a drag is in progress. |
| `theme` | `str` | `"auto"`, `"light"`, or `"dark"`. |
| `width` | `int` | Max width in pixels before the expression wraps one arg per line. |
| `error` | `str` | Validation/render error surfaced from the widget. |

---
Démo : [`../demos/tangle_function.py`](../demos/tangle_function.py)
