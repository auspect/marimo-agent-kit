<!-- wigglystuff 0.6.0, recopié de docs/reference/tangle-latex.md (MIT) -->
# TangleLatex API


`TangleLatex` renders a KaTeX formula in which named numbers are draggable. Mark
them with `\tangle{name}` inside `latex` and configure each name in `parameters`; a
parameter can show its formatted number or stay symbolic until it is dragged or
edited, and repeated markers share one value. The live numbers land in `values`
while you drag, so downstream cells recompute as the equation changes.

To explain what the symbols mean, wrap any part of the formula in
`\note{name}{...}` and describe it in `notes`. The note is drawn above or below
the formula with an arrow to exactly that part, and hovering a note (or
dragging the parameter it explains) fades the others:

```python
TangleLatex(
    latex=r"p(x) = \frac{1}{\tangle{sigma}\sqrt{2\pi}}"
    r"\exp\left(-\frac{(x-\note{center}{\tangle{mu}})^2}{2\note{width}{\tangle{sigma}}^2}\right)",
    parameters={"mu": {"value": 0}, "sigma": {"value": 1, "min_value": 0.1}},
    notes={
        "center": "**mean**: where the bell is centered",
        "width": "**standard deviation**: how wide the bell is",
    },
)
```

See also: [Tangle widgets](tangle.md) for the same drag gesture in plain prose,
[Matrix](matrix.md) for editing numbers as a grid, and
[Slider2D](slider2d.md) for two coupled parameters on one canvas.

### `TangleLatex`

`from wigglystuff.tangle_latex import TangleLatex`

```python
TangleLatex(latex: 'str', parameters: 'Mapping[str, Mapping[str, Any]]', notes: 'Mapping[str, Any] | None' = None, *, display_mode: 'bool' = True, editor: 'str' = 'popover', reveal_all_on_drag: 'bool' = False, theme: 'str' = 'auto', **kwargs: 'Any') -> 'None'
```

Render a KaTeX formula with draggable named numeric parameters.

Put ``\tangle{name}`` markers in ``latex`` and configure each name in
``parameters``. A parameter can display its formatted number directly or
remain symbolic until it is dragged or edited. Repeated markers share one
value and update together.

``values`` follows a drag live. ``committed_values`` keeps the values from
before the drag until it is released, so the notebook can compare the old
formula with the new one while you scrub; ``dragging`` is True in between.
Outside a drag the two are equal.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import TangleLatex

    formula = mo.ui.anywidget(
        TangleLatex(
            latex=r"f(x) =  angle{a}x^2 +   angle{b}x +     angle{a}",
            parameters={
                "a": {
                    "value": 2.5,
                    "min_value": -5,
                    "max_value": 5,
                    "step": 0.1,
                    "display": "symbol",
                },
                "b": {
                    "value": 1,
                    "min_value": -10,
                    "max_value": 10,
                    "step": 0.5,
                    "display": "symbol",
                },
            },
            reveal_all_on_drag=True,
        )
    )
    formula
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `committed_values` | Dict | |
| `display_mode` | Bool | `True` |
| `dragging` | Bool | `False` |
| `editor` | Enum | `'popover'` |
| `error` | Unicode | `''` |
| `hovered` | Unicode | `''` |
| `latex` | Unicode | `''` |
| `notes` | Dict | |
| `parameters` | Dict | |
| `reveal_all_on_drag` | Bool | `False` |
| `theme` | Enum | `'auto'` |
| `values` | Dict | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `latex` | `str` | LaTeX source containing `\tangle{name}` markers. |
| `parameters` | `dict` | Per-parameter config (value, bounds, step, digits, color, symbol, ...). |
| `values` | `dict` | Live current value for each parameter; updates while dragging. |
| `committed_values` | `dict` | Values from before the current drag; catch up on release. |
| `dragging` | `bool` | `True` while a drag is in progress. |
| `display_mode` | `bool` | Render the formula in display mode. |
| `editor` | `str` | Exact-value editor style: `"popover"` or `"inline"`. |
| `reveal_all_on_drag` | `bool` | Reveal every tangle value while dragging any one of them. |
| `notes` | `dict` | Normalized notes for `\note{name}{...}` parts (text, side, color). |
| `hovered` | `str` | Name of the note under the pointer, or `""`. |
| `theme` | `str` | `"auto"`, `"light"`, or `"dark"`. |
| `error` | `str` | Validation/render error surfaced from the widget. |

---
Démo : [`../demos/tangle_latex.py`](../demos/tangle_latex.py)
