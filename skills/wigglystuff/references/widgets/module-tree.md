<!-- wigglystuff 0.6.0, recopié de docs/reference/module-tree.md (MIT) -->
# ModuleTreeWidget API


`ModuleTreeWidget` turns a PyTorch `nn.Module` into an expandable tree: every submodule with
its parameter count and per-tensor shapes, plus trainable, frozen and buffer badges and a
density indicator, so you can see where the weights in a model actually sit. If you work in
marimo you do not need it — returning an `nn.Module` from a cell renders the same view, since
this widget has graduated to marimo core — but it still works in plain Jupyter and other
anywidget hosts.

PyTorch is too heavy to run in the browser, so this page has no in-browser demo —
[run it on molab](https://molab.marimo.io/notebooks/nb_K7QvvoASZErgKxwD8XSMWi?utm_source=wigglystuff)
instead. See also: [NestedTable](nested-table.md) for the same collapsing-tree layout over
any hierarchy, [Treemap](treemap.md) for sizing a hierarchy by value, and
[LiveEdit](live-edit.md) for tracing what a Python function does line by line.

### `ModuleTreeWidget`

`from wigglystuff.module_tree import ModuleTreeWidget`

```python
ModuleTreeWidget(module: Any = None, *, initial_expand_depth: int = 1)
```

Interactive tree viewer for PyTorch ``nn.Module`` architecture.

Displays the full module hierarchy with parameter counts, shapes,
trainable/frozen/buffer badges, and a density indicator.

Note:
    This widget has graduated to marimo core. If you are using marimo,
    you can simply return an ``nn.Module`` from a cell — marimo's
    built-in PyTorch formatter will render it. ``ModuleTreeWidget``
    will continue to work in plain Jupyter and other anywidget hosts.

Examples:
    ```python
    import marimo as mo
    import torch.nn as nn
    from wigglystuff import ModuleTreeWidget

    model = nn.Sequential(
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 10),
    )
    mo.ui.anywidget(ModuleTreeWidget(model, initial_expand_depth=2))
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `initial_expand_depth` | Int | `1` |
| `tree` | Dict | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `tree` | `dict` | JSON-serializable tree extracted from a PyTorch `nn.Module`. |
| `initial_expand_depth` | `int` | Number of tree levels to expand on first render (default: 1). |
