<!-- wigglystuff 0.6.0, recopié de docs/reference/hover-slider.md (MIT) -->
# HoverSlider API


`HoverSlider` treats hovering as an input channel of its own: `hover_value` follows
the pointer while `value` stays parked where you last clicked, so a cell can show
you what a setting would do before you commit to it. Pass `start`/`stop`/`step` for
a linear range or `steps` for a list of discrete values, and use
`sync_throttle_ms` to cap how often the hover stream reruns downstream cells.

See also: [PlaySlider](play-slider.md) for stepping through a range on a timer,
[CircularSlider](circular-slider.md) for the same range laid out on a dial, and
[TangleSlider](tangle.md) for a draggable number that lives inside a sentence.

### `HoverSlider`

`from wigglystuff.hover_slider import HoverSlider`

```python
HoverSlider(start: Optional[float] = None, stop: Optional[float] = None, step: Optional[float] = None, steps: Optional[Sequence[float]] = None, value: Optional[float] = None, sync_throttle_ms: int = 100, show_value: bool = True, label: str = '', color: str = '', width: int = 400, **kwargs: Any) -> None
```

Horizontal slider that reports both a committed value and a live hover value.

Hovering the track is an input channel of its own: ``hover_value`` follows the
pointer while ``value`` stays parked where you last clicked. That lets a
notebook preview a result before you commit to it. Click (or drag the puck) to
move ``value``; when the pointer leaves the track ``hover_value`` falls back to
``value``, so it is never ``None``.

Mirrors ``mo.ui.slider`` semantics: pass ``start``/``stop``/``step`` for a linear
range, or ``steps`` for a list of discrete values (the two are mutually
exclusive). Numeric types are preserved -- ``steps=[1, 2, 3]`` hands back an
``int``, ``steps=[1, 2.5, 4]`` hands back floats.

Note:
    Hover fires a *lot*. Because ``mo.ui.anywidget`` reruns dependent cells on
    every synced trait change, ``sync_throttle_ms`` is the knob that decides how
    hard this widget hits your notebook: the default of 100ms caps it at roughly
    10 reruns per second while the pointer sweeps. Raise it if downstream cells
    are expensive; set it to ``0`` to sync every single pointer move.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import HoverSlider

    slider = mo.ui.anywidget(HoverSlider(start=0, stop=100, step=1, value=42))
    slider
    ```

    ```python
    # `hover_value` previews, `value` is what the user actually committed.
    mo.md(f"previewing {slider.value['hover_value']}, committed {slider.value['value']}")
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `''` |
| `hover_value` | _Number | `0` |
| `hovering` | Bool | `False` |
| `label` | Unicode | `''` |
| `show_value` | Bool | `True` |
| `start` | _Number | `0` |
| `step` | _Number | `1` |
| `steps` | List | |
| `stop` | _Number | `100` |
| `sync_throttle_ms` | Int | `100` |
| `value` | _Number | `0` |
| `width` | Int | `400` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `value` | `int \| float` | Committed value. Moves on click, drag, and arrow keys — never on plain hover. |
| `hover_value` | `int \| float` | Value under the pointer. Falls back to `value` when the pointer leaves, so it is never `None`. |
| `hovering` | `bool` | Whether the pointer is on the track, i.e. whether `hover_value` is live. |
| `start` | `int \| float` | Lower bound. In `steps` mode this is `steps[0]`. |
| `stop` | `int \| float` | Upper bound. In `steps` mode this is `steps[-1]`. |
| `step` | `int \| float \| None` | Snap increment. `None` in `steps` mode. |
| `steps` | `list[int \| float]` | Discrete values, laid out evenly across the track. Empty means linear mode. |
| `sync_throttle_ms` | `int` | Cap on how often hover updates reach Python. `0` syncs every pointer move. |
| `show_value` | `bool` | Render the committed and hovered values below the track. |
| `label` | `str` | Text above the track. Empty string hides it. |
| `color` | `str` | CSS color for the fill, puck border, and hover marker. Empty uses the theme default. |
| `width` | `int` | Widget width in pixels. |

---
Démo : [`../demos/hover_slider.py`](../demos/hover_slider.py)
