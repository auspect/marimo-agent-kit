<!-- wigglystuff 0.6.0, recopié de docs/reference/three-widget.md (MIT) -->
# ThreeWidget API


`ThreeWidget` renders a list of `{"x", "y", "z"}` dicts as a Three.js point cloud you
can orbit with the mouse, with optional per-point `color` and `size`. Reach for it when
a 2D scatter hides the structure you care about — embeddings, sensor traces, parameter
sweeps. `update_points()` swaps the data in place and, with `animate_updates=True`,
tweens between frames instead of redrawing from scratch.

See also: [CubeWidget](cube-widget.md) for picking a slice out of a 3D parameter space,
[ParallelCoordinates](parallel-coords.md) for data with more than three dimensions, and
[HoverZoom](hover-zoom.md) for magnifying a crowded 2D plot instead.

### `ThreeWidget`

`from wigglystuff.three_widget import ThreeWidget`

```python
ThreeWidget(*, data: Optional[collections.abc.Iterable[dict[str, Any]]] = None, width: int = 600, height: int = 400, show_grid: bool = False, show_axes: bool = False, dark_mode: bool = False, axis_labels: Optional[collections.abc.Iterable[str]] = None, animate_updates: bool = False, animation_duration_ms: int = 400, auto_rotate: bool = False, auto_rotate_speed: float = 2.0, xlim: Optional[tuple[float, float]] = None, ylim: Optional[tuple[float, float]] = None, zlim: Optional[tuple[float, float]] = None, camera_azimuth: float = 45.0, camera_elevation: float = 30.0, **kwargs: Any) -> None
```

Interactive 3D scatter plot powered by Three.js.

The widget renders a collection of 3D points with per-point color and size
attributes, suitable for quick exploratory visualizations in notebook
environments.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import ThreeWidget

    data = [
        {"x": 1.0, "y": 2.0, "z": 3.0, "color": "tomato", "size": 0.2},
        {"x": -1.0, "y": 0.5, "z": -2.0, "color": "#22c55e", "size": 0.15},
    ]
    widget = mo.ui.anywidget(ThreeWidget(data=data, show_grid=True, show_axes=True))
    widget
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `animate_updates` | Bool | `False` |
| `animation_duration_ms` | Int | `400` |
| `auto_rotate` | Bool | `False` |
| `auto_rotate_speed` | Float | `2.0` |
| `axis_labels` | List | |
| `camera_azimuth` | Float | `45.0` |
| `camera_elevation` | Float | `30.0` |
| `dark_mode` | Bool | `False` |
| `data` | List | |
| `height` | Int | `400` |
| `show_axes` | Bool | `False` |
| `show_grid` | Bool | `False` |
| `width` | Int | `600` |
| `xlim` | List | |
| `ylim` | List | |
| `zlim` | List | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `data` | `list[dict[str, Any]]` | Point list with `x`, `y`, `z`, and optional `color`/`size`. |
| `width` | `int` | Canvas width in pixels. |
| `height` | `int` | Canvas height in pixels. |
| `show_grid` | `bool` | Show the grid helper. |
| `show_axes` | `bool` | Show the axes helper. |
| `dark_mode` | `bool` | Toggle dark background and lighting. |
| `axis_labels` | `list[str]` | Optional labels for x/y/z axes. |
| `animate_updates` | `bool` | Animate transitions when updating points. |
| `animation_duration_ms` | `int` | Duration for animated updates in milliseconds. |

---
Démo : [`../demos/threewidget.py`](../demos/threewidget.py)
