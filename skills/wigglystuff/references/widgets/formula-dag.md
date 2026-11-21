<!-- wigglystuff 0.6.0, recopié de docs/reference/formula-dag.md (MIT) -->
# FormulaDAG API


`FormulaDAG` lays out a set of LaTeX formulas as a DAG. Name each formula and
write `\use{name}` inside another one: the widget renders that formula's output
symbol in place, infers the edge, and draws an arrow from the producer straight
onto the spot where it's used. Formulas flow top to bottom by dependency depth,
and each producer gets one color for its symbol, its arrows, and every use.
Hover a formula to highlight what it depends on and what depends on it; click
it to set `selected`.

Draggable `\tangle{name}` numbers and `\note{name}{...}` notes work like in
[TangleLatex](tangle-latex.md), shared across the whole DAG. Give a formula an
`fn` (its argument names pick parameters or other formulas) and its value is
computed live into `outputs`. While you drag a number, every formula that
depends on it shows its live value in place of its symbol, both where it's
defined and wherever it's used.

Call `to_html()` for a self-contained, static HTML page of the current state
(for docs, blog posts, or attachments), or `save("dag.html")` to write it to
a file. KaTeX still loads from a CDN, so the page needs internet access.

See also: [TangleLatex](tangle-latex.md) for a single formula, and
[WidgetDAG](widget-dag.md) for arranging live widgets as a DAG.

### `FormulaDAG`

`from wigglystuff.formula_dag import FormulaDAG`

```python
FormulaDAG(formulas: 'Mapping[str, Any]', parameters: 'Mapping[str, Mapping[str, Any]] | None' = None, notes: 'Mapping[str, Any] | None' = None, *, legend: 'bool' = True, theme: 'str' = 'auto', **kwargs: 'Any') -> 'None'
```

Lay out LaTeX formulas as a DAG, wired by where each output is used.

Each formula has a name. Writing ``\use{name}`` inside another formula
renders that formula's output symbol (by default the left-hand side of its
first ``=``) and draws an arrow from the producing formula straight onto
the spot where it is used. The edges are inferred from those markers, so
there is no edge list to maintain; cycles are rejected.

Formulas flow top to bottom: a formula sits one row below the deepest
formula it uses. Each producer gets a color shared by its output symbol,
its arrows, and every place it is used. Hover a formula to highlight what
it depends on and what depends on it; click it to set ``selected``.

Numbers and notes work like ``TangleLatex``, shared across the whole DAG:
``\tangle{name}`` in any formula is a draggable number configured in
``parameters`` (the same name in two formulas is one value), and
``\note{name}{tex}`` attaches the plain-language note ``notes[name]`` to
that part of its formula. ``values`` follows a drag live;
``committed_values`` keeps the pre-drag values until release.

Examples:
    ```python
    from wigglystuff import FormulaDAG

    FormulaDAG(
        {
            "mu": r"\mu = \frac{1}{n}\sum_i x_i",
            "var": r"\sigma^2 = \frac{1}{n}\sum_i (x_i - \use{mu})^2",
            "sigma": r"\sigma = \sqrt{\use{var}}",
            "z": r"z_i = \frac{x_i - \use{mu}}{\note{scale}{\use{sigma}}}",
            "band": r"b = \use{mu} \pm \tangle{k}\,\use{sigma}",
        },
        parameters={"k": {"value": 2, "min_value": 0, "max_value": 4, "step": 0.5}},
        notes={"scale": "measured in standard deviations"},
    )
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `committed_outputs` | Dict | |
| `committed_values` | Dict | |
| `dragging` | Bool | `False` |
| `error` | Unicode | `''` |
| `formulas` | List | |
| `hovered` | Unicode | `''` |
| `layers` | List | |
| `legend` | Bool | `True` |
| `notes` | Dict | |
| `output_errors` | Dict | |
| `outputs` | Dict | |
| `parameters` | Dict | |
| `routes` | List | |
| `selected` | Unicode | `''` |
| `theme` | Enum | `'auto'` |
| `values` | Dict | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `formulas` | `list[dict]` | Normalized formulas: `name`, `lhs`, `tex`, `symbol`, `label`, `inputs`, `color`, ... |
| `layers` / `routes` | `list` | Row layout and edge routes (computed in Python). |
| `parameters` | `dict` | Normalized `\tangle` number configuration. |
| `notes` | `dict` | Normalized `\note` configuration, each with its home `formula`. |
| `values` | `dict` | Live number values; follows a drag. |
| `committed_values` | `dict` | Values from before the current drag. |
| `dragging` | `bool` | True while a number is being dragged. |
| `outputs` | `dict` | Live `fn` results per formula (`None` on failure). |
| `committed_outputs` | `dict` | `fn` results for `committed_values`. |
| `output_errors` | `dict` | Exception messages for formulas whose `fn` failed. |
| `hovered` | `str` | Note under the pointer. |
| `selected` | `str` | Clicked formula name. |
| `legend` | `bool` | Show the legend strip of number and output chips. |
| `theme` | `str` | `"auto"`, `"light"`, or `"dark"`. |
| `error` | `str` | KaTeX load or render errors. |

---
Démo : [`../demos/formula_dag.py`](../demos/formula_dag.py)
