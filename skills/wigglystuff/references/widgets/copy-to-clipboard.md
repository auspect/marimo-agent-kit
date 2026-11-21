<!-- wigglystuff 0.6.0, recopié de docs/reference/copy-to-clipboard.md (MIT) -->
# CopyToClipboard API


`CopyToClipboard` is a single button that writes `text_to_copy` to the OS clipboard when
clicked. Because `text_to_copy` is a synced traitlet, you can keep setting it from Python
and the button always carries the current value — useful for a generated prompt, a
connection string, or a block of SQL that the reader needs to paste somewhere else.

See also: [ColorPicker](color-picker.md) for producing a hex string worth copying,
[AnnotationWidget](annotation.md) for capturing text the other direction, and
[HTMLRefreshWidget](html-refresh.md) for showing that text in the cell instead.

### `CopyToClipboard`

`from wigglystuff.copy_to_clipboard import CopyToClipboard`

```python
CopyToClipboard(text_to_copy: str = '', **kwargs: Any)
```

Button widget that copies the provided ``text_to_copy`` payload.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import CopyToClipboard

    button = mo.ui.anywidget(CopyToClipboard(text_to_copy="Hello, world!"))
    button
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `text_to_copy` | Unicode | `''` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `text_to_copy` | `str` | Payload copied when the button is pressed. |


---
Démo : [`../demos/copytoclipboard.py`](../demos/copytoclipboard.py)
