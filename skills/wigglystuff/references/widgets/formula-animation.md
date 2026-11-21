<!-- wigglystuff 0.6.0, recopié de docs/reference/formula-animation.md (MIT) -->
# FormulaAnimation API


`FormulaAnimation` steps through a LaTeX derivation one line at a time. Give it a
list of `{"tex": ..., "note": ...}` dicts and the current line sits centered while
the previous line floats above it dimmed, with a short caption under the active
line. Playback is manual: move with the built-in prev/next buttons, with the arrow
keys (click the widget to opt into keyboard control), or by driving the reactive
`step` trait from Python — for example, an `mo.ui.slider` in another cell. With
`spotlight=True` a final step frames the finished formula alone in an elevated
card. The `steps` list is plain JSON, so an LLM can emit a derivation directly.

See also: [TangleLatex](tangle-latex.md) for a single formula with draggable
numbers, and [FramePlayer](frame-player.md) for stepping through a sequence of
rendered images.

### `FormulaAnimation`

`from wigglystuff.formula_animation import FormulaAnimation`

```python
FormulaAnimation(steps: 'Sequence[Mapping[str, Any]]', *, title: 'str | None' = None, spotlight: 'bool' = True, height: 'int' = 360, theme: 'str' = 'auto', **kwargs: 'Any') -> 'None'
```

Animate a LaTeX derivation one step at a time.

Give it a list of ``{"tex": ..., "note": ...}`` steps and it renders a
stack of KaTeX equations where the current line sits centered, the previous
line floats above it dimmed, and a short caption shows under the active
line. Playback is manual: move through the derivation with the built-in
prev/next buttons, with the arrow keys (after clicking the widget to enable
them), or by driving the ``step`` trait from Python (e.g. a marimo slider).

With ``spotlight=True`` a final step frames the last formula alone in a
boxed, slightly zoomed state so the finished result stands out.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import FormulaAnimation

    anim = mo.ui.anywidget(
        FormulaAnimation(
            title="The abc-formula",
            steps=[
                {"tex": r"ax^2 + bx + c = 0", "note": "A quadratic equation, with a ≠ 0."},
                {"tex": r"x^2 + \tfrac{b}{a}x + \tfrac{c}{a} = 0", "note": "Make the leading coefficient 1."},
                {"tex": r"x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}", "note": "The abc-formula."},
            ],
        )
    )
    anim
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `error` | Unicode | `''` |
| `height` | Int | `360` |
| `spotlight` | Bool | `True` |
| `step` | Int | `0` |
| `steps` | List | |
| `theme` | Enum | `'auto'` |
| `title` | Unicode | `None` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `steps` | `list[dict]` | Normalized `{"tex": str, "note": str}` derivation lines. |
| `title` | `str \| None` | Optional heading rendered above the animation. |
| `spotlight` | `bool` | Append a final step framing the last formula alone. |
| `step` | `int` | Current index; reactive, slider-drivable, moved by buttons/keys. |
| `height` | `int` | Height of the animation stage in pixels. |
| `theme` | `str` | `"auto"`, `"light"`, or `"dark"`. |
| `error` | `str` | Set if KaTeX fails to load in the browser. |

---
Démo : [`../demos/formula_animation.py`](../demos/formula_animation.py)
