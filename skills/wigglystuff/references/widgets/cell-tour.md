<!-- wigglystuff 0.6.0, recopié de docs/reference/cell-tour.md (MIT) -->
# CellTour API


`CellTour` walks a reader through a marimo notebook one popover at a time. Each step
points at a cell by index (`{"cell": 0}`) or by name (`{"cell_name": "imports"}`) instead
of a hand-written CSS selector, which is what makes it easier to keep in sync than a raw
Driver.js tour. Set `auto_start` to open the tour on render, and read `active` and
`current_step` back in Python to react to where the reader has got to.

See also: [ApiDoc](api-doc.md) for putting a reference card next to the example it
documents, [EnvConfig](env-config.md) for gating a notebook on credentials before the
reader starts, and [LiveEdit](live-edit.md) for explaining what a function does pass by
pass.

### `CellTour`

`from wigglystuff.cell_tour import CellTour`

```python
CellTour(steps: Sequence[dict] = (), *, auto_start: bool = False, show_progress: bool = True, **kwargs: Any) -> None
```

Simplified tour widget for marimo notebooks.

Wraps ``DriverTour`` with cell-aware step helpers so you can reference
marimo cells by index or `data-cell-name` attributes. Works in both
marimo edit mode and app mode (``marimo run`` / molab); the cell
selectors require marimo ``>= 0.23``, when app mode started rendering
``.marimo-cell`` and ``[data-cell-name]`` on cell containers.

Examples:
    Using cell indices:

    ```python
    import marimo as mo
    from wigglystuff import CellTour

    tour = mo.ui.anywidget(CellTour(steps=[
        {"cell": 0, "title": "Imports", "description": "Load libraries"},
        {"cell": 2, "title": "Processing", "description": "Data transformation"},
    ]))
    tour
    ```

    Using cell names (requires naming cells in marimo):

    ```python
    import marimo as mo
    from wigglystuff import CellTour

    tour = mo.ui.anywidget(CellTour(steps=[
        {"cell_name": "imports", "title": "Imports", "description": "Load libraries"},
        {"cell_name": "process", "title": "Processing", "description": "Transform data"},
    ]))
    tour
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `active` | Bool | `False` |
| `auto_start` | Bool | `False` |
| `current_step` | Int | `0` |
| `show_progress` | Bool | `True` |
| `steps` | List | |


`CellTour` works in both marimo edit mode and app mode (`marimo run` /
molab). The cell selectors it emits (`.marimo-cell` and
`[data-cell-name="…"]`) require marimo `>= 0.23`, when app mode started
rendering those markers on cell containers.

## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `steps` | `list[dict]` | DriverTour-style steps (CellTour inputs are normalized). |
| `auto_start` | `bool` | Start tour automatically on render. |
| `show_progress` | `bool` | Show progress indicator when true. |
| `active` | `bool` | Whether the tour is currently running. |
| `current_step` | `int` | Index of the active step. |


---
Démo : [`../demos/celltour.py`](../demos/celltour.py)
