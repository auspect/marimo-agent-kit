<!-- wigglystuff 0.6.0, recopié de docs/reference/cube-widget.md (MIT) -->
# CubeWidget API


`CubeWidget` draws three named axes as an isometric cube and locks them one at a time:
the first click picks a plane, the second narrows it to a line, the third to a single
point. Each lock reveals a slider for that axis value, and `plane`, `line` and `point`
sync back to Python so downstream cells can slice a grid of results the same way. Use
`lock_axis()`, `unlock_axis()` and `reset()` to drive the same selection from code.

See also: [ThreeWidget](three-widget.md) for plotting the points themselves in 3D,
[Slider2D](slider2d.md) for steering two continuous parameters at once, and
[Matrix](matrix.md) for editing the grid of numbers a slice comes from.

### `CubeWidget`

`from wigglystuff.cube_widget import CubeWidget`

```python
CubeWidget(x_axis: dict[str, typing.Any] | None = None, y_axis: dict[str, typing.Any] | None = None, z_axis: dict[str, typing.Any] | None = None, **kwargs: Any) -> None
```

Select a plane, line, and point by progressively locking cube axes.

Clicking an axis locks it and reveals a slider for its value. The first
locked axis selects a plane, the second selects a line, and the third
selects a point. Lock order is exposed so downstream code can preserve the
same progressive slicing semantics.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import CubeWidget

    cube = mo.ui.anywidget(
        CubeWidget(
            x_axis={"name": "Angle", "values": [0, 45, 90]},
            y_axis={"name": "Force", "values": [0, 50, 100]},
            z_axis={"name": "Time", "values": [0, 1, 2]},
        )
    )
    cube
    ```

Args:
    x_axis: X-axis configuration with a display ``name`` and numeric
        ``values`` defining its range.
    y_axis: Y-axis configuration with a display ``name`` and numeric
        ``values`` defining its range.
    z_axis: Z-axis configuration with a display ``name`` and numeric
        ``values`` defining its range.
    **kwargs: Forwarded to ``anywidget.AnyWidget``.

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `axis_values` | Dict | |
| `line` | Dict | |
| `locked_order` | List | |
| `plane` | Dict | |
| `point` | Dict | |
| `x_axis` | Dict | |
| `y_axis` | Dict | |
| `z_axis` | Dict | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `x_axis` | `dict` | X-axis display name and numeric values. |
| `y_axis` | `dict` | Y-axis display name and numeric values. |
| `z_axis` | `dict` | Z-axis display name and numeric values. |
| `locked_order` | `list[str]` | Axis keys in plane → line → point lock order. |
| `axis_values` | `dict[str, float]` | Current value for each axis key. |
| `plane` | `dict | None` | First locked axis display name and value. |
| `line` | `dict | None` | Second locked axis display name and value. |
| `point` | `dict | None` | Third locked axis display name and value. |

## Helpers

- `lock_axis(axis_key, value=None)` locks an axis and optionally sets its value.
- `unlock_axis(axis_key)` removes an axis from the lock order.
- `reset()` clears every lock while preserving the current axis values.

---
Démo : [`../demos/cube_widget.py`](../demos/cube_widget.py)
