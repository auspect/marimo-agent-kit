<!-- wigglystuff 0.6.0, recopié de docs/reference/tangle.md (MIT) -->
# Tangle Widgets API


The Tangle widgets put a control inside your prose rather than next to it, after
Bret Victor's Tangle. `TangleSlider` renders a number you drag left and right,
`TangleChoice` cycles through labels in place when you click it, and `TangleSelect`
is the same choice as a dropdown. Interpolate one into a markdown string and the
sentence itself becomes the interface.

See also: [TangleDistribution](tangle-distribution.md) for an inline number that
carries a whole distribution (mean ± spread),
[TangleLatex](tangle-latex.md) for draggable numbers inside a KaTeX formula, [HoverSlider](hover-slider.md) for a conventional track that also reports
what the pointer is over, and [SortableList](sortable-list.md) for reordering a set
of options instead of picking one.

## TangleSlider

### `TangleSlider`

`from wigglystuff.tangle import TangleSlider`

```python
TangleSlider(amount: Optional[float] = None, min_value: float = -100, max_value: float = 100, step: float = 1.0, steps: Optional[List[float]] = None, pixels_per_step: int = 2, prefix: str = '', suffix: str = '', digits: int = 1, **kwargs: Any) -> None
```

Inline slider inspired by Bret Victor's Tangle UI.

``amount`` follows the drag live. ``committed_amount`` keeps the value from
before the drag until it is released, so the notebook can compare old and
new while you scrub; ``dragging`` is True in between. Outside a drag the two
are equal.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import TangleSlider

    slider = mo.ui.anywidget(TangleSlider(amount=50, min_value=0, max_value=100))
    slider
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `amount` | Float | `0.0` |
| `committed_amount` | Float | `0.0` |
| `digits` | Int | `1` |
| `dragging` | Bool | `False` |
| `max_value` | Float | `100.0` |
| `min_value` | Float | `-100.0` |
| `pixels_per_step` | Int | `2` |
| `prefix` | Unicode | `''` |
| `step` | Float | `1.0` |
| `steps` | List | |
| `suffix` | Unicode | `''` |


### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `amount` | `float` | Current value; updates while dragging. |
| `committed_amount` | `float` | Value from before the current drag; catches up on release. |
| `dragging` | `bool` | `True` while a drag is in progress. |
| `min_value` | `float` | Lower bound. |
| `max_value` | `float` | Upper bound. |
| `step` | `float` | Step size. |
| `pixels_per_step` | `int` | Drag distance per step. |
| `prefix` | `str` | Text before the value. |
| `suffix` | `str` | Text after the value. |
| `digits` | `int` | Decimal precision for display. |


## TangleChoice

### `TangleChoice`

`from wigglystuff.tangle import TangleChoice`

```python
TangleChoice(choices: List[str], **kwargs: Any) -> None
```

Inline choice widget that cycles through labeled options.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import TangleChoice

    choice = mo.ui.anywidget(TangleChoice(choices=["small", "medium", "large"]))
    choice
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `choice` | Unicode | `''` |
| `choices` | List | |


### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `choice` | `str` | Current selection. |
| `choices` | `list[str]` | Available options. |


## TangleSelect

### `TangleSelect`

`from wigglystuff.tangle import TangleSelect`

```python
TangleSelect(choices: List[str], **kwargs: Any) -> None
```

Dropdown-based take on the Tangle choice pattern.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import TangleSelect

    select = mo.ui.anywidget(TangleSelect(choices=["red", "green", "blue"]))
    select
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `choice` | Unicode | `''` |
| `choices` | List | |


### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `choice` | `str` | Current selection. |
| `choices` | `list[str]` | Available options. |


---
Démo : [`../demos/tangle.py`](../demos/tangle.py)
