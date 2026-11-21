<!-- wigglystuff 0.6.0, recopié de docs/reference/color-picker.md (MIT) -->
# ColorPicker API


`ColorPicker` wraps the browser's native color input and syncs the chosen `#RRGGBB`
value back to Python as `color`, with an `rgb` property that hands you the three channels
as integers. Reach for it when a plot color, a brush color or a mask tint is easier to
choose by eye than to type as a literal; `show_label` controls whether the hex string is
printed next to the swatch.

See also: [Paint](paint.md) for a canvas with the same picker built into its toolbar,
[CopyToClipboard](copy-to-clipboard.md) for handing the resulting hex string to someone
else, and [TangleSlider](tangle.md) for the same by-eye approach to numbers.

### `ColorPicker`

`from wigglystuff.color_picker import ColorPicker`

```python
ColorPicker(*, color: Optional[str] = None, show_label: bool = True, **kwargs: Any)
```

Simple color picker syncing a ``#RRGGBB`` hex value back to Python.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import ColorPicker

    picker = mo.ui.anywidget(ColorPicker(color="#ff5733"))
    picker
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `color` | Unicode | `'#000000'` |
| `show_label` | Bool | `True` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `color` | `str` | Hex color string (e.g., `#ff00aa`). |


---
Démo : [`../demos/colorpicker.py`](../demos/colorpicker.py)
