<!-- wigglystuff 0.6.0, recopié de docs/reference/sortable-list.md (MIT) -->
# SortableList API


`SortableList` renders a list you reorder by dragging and hands the current order
back to Python as `value`. Turn on `addable`, `removable` and `editable` when the
list should be a small CRUD surface rather than a fixed set — ranking candidates,
sequencing pipeline steps, tidying up a label taxonomy.

See also: [Matrix](matrix.md) for editing a grid of numbers,
[TangleChoice](tangle.md) for picking one option inline in a sentence, and
[EdgeDraw](edge-draw.md) for sketching relationships between named items.

### `SortableList`

`from wigglystuff.sortable_list import SortableList`

```python
SortableList(value: Sequence[str], *, addable: bool = False, removable: bool = False, editable: bool = False, label: str = '', **kwargs: Any) -> None
```

Drag-and-drop list widget with optional add/remove/edit affordances.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import SortableList

    sortable = mo.ui.anywidget(SortableList(value=["apple", "banana", "cherry"], removable=True))
    sortable
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `addable` | Bool | `False` |
| `editable` | Bool | `False` |
| `label` | Unicode | `''` |
| `removable` | Bool | `False` |
| `value` | List | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `list[str]` | Ordered list items. |
| `addable` | `bool` | Allow inserting new items. |
| `removable` | `bool` | Allow deleting items. |
| `editable` | `bool` | Allow inline edits. |
| `label` | `str` | Optional heading above the list. |


---
Démo : [`../demos/sortlist.py`](../demos/sortlist.py)
