<!-- wigglystuff 0.6.0, recopié de docs/reference/text-compare.md (MIT) -->
# TextCompare API


`TextCompare` shows two texts in side-by-side panels and highlights every run of matching
words, with `min_match_words` setting how long a run has to be before it counts. Hover a
highlight and the other panel scrolls to the same passage, which is what makes shared or
lifted text quick to spot between two documents. The `matches` traitlet hands the same
list back to Python with start and end offsets and a word count per match.

See also: [HoverZoom](hover-zoom.md) for inspecting image detail with the same hover
gesture, [LiveEdit](live-edit.md) for reading a Python run instead of prose, and
[ApiDoc](api-doc.md) for putting reference text next to the code it describes.

### `TextCompare`

`from wigglystuff.text_compare import TextCompare`

```python
TextCompare(text_a: str = '', text_b: str = '', min_match_words: int = 3, **kwargs: Any) -> None
```

Side-by-side text comparison widget with hover-based match highlighting.

Compares two texts and highlights matching word sequences, useful for
plagiarism detection or finding shared passages between documents.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import TextCompare

    compare = mo.ui.anywidget(TextCompare(
        text_a="The quick brown fox jumps over the lazy dog.",
        text_b="A quick brown fox leaps over a lazy dog."
    ))
    compare
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `matches` | List | |
| `min_match_words` | Int | `3` |
| `selected_match` | Int | `-1` |
| `text_a` | Unicode | `''` |
| `text_b` | Unicode | `''` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `text_a` | `str` | First text to compare. |
| `text_b` | `str` | Second text to compare. |
| `matches` | `list` | List of detected matches, each with start_a, end_a, start_b, end_b, text, and word_count. |
| `selected_match` | `int` | Index of the currently hovered match (-1 if none). |
| `min_match_words` | `int` | Minimum consecutive words to consider a match (default: 3). |

---
Démo : [`../demos/textcompare.py`](../demos/textcompare.py)
