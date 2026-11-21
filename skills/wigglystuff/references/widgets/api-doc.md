<!-- wigglystuff 0.6.0, recopié de docs/reference/api-doc.md (MIT) -->
# ApiDoc API


`ApiDoc` takes a Python class or function and renders what `inspect` can see about it —
the signature, a parameter table with types and defaults, the docstring, and any methods
and properties — as a formatted card in the notebook, without a docs build in the loop.
Useful when you are teaching a library in a notebook and want the reference sitting next
to the example instead of in another tab; `show_private` decides whether
underscore-prefixed methods show up.

See also: [ModuleTreeWidget](module-tree.md) for inspecting a PyTorch module's structure,
[LiveEdit](live-edit.md) for showing what a function actually does when it runs, and
[CellTour](cell-tour.md) for walking a reader through the notebook around it.

### `ApiDoc`

`from wigglystuff.api_doc import ApiDoc`

```python
ApiDoc(obj: Any = None, *, width: int = 700, show_private: bool = False)
```

Renders API documentation for a Python class or function in a notebook.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import ApiDoc

    mo.ui.anywidget(ApiDoc(MyClass))
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `doc` | Dict | |
| `show_private` | Bool | `False` |
| `width` | Int | `700` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `doc` | `dict` | Introspected documentation payload (auto-generated from the target object). |
| `width` | `int` | Container width in pixels. |
| `show_private` | `bool` | Whether to include private (underscore-prefixed) methods. |

---
Démo : [`../demos/apidoc.py`](../demos/apidoc.py)
