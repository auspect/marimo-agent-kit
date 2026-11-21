<!-- wigglystuff 0.6.0, recopié de docs/reference/manim-web.md (MIT) -->
# ManimWeb API


`ManimWeb` loads [manim-web](https://github.com/maloyan/manim-web) — a TypeScript/WebGL
reimplementation of Manim that renders in the browser — from a CDN, then runs a scene you
supply as an inline JS string, a path to a local file, or a URL. Your code runs with the
`manim` namespace, the `container` element, the `width`/`height` ints and the widget
`model` in scope; manim-web's own `Player` draws a full playback UI with a scrub timeline,
speed control and export. Python's only job is handing over the source and the sizing.
The code is executed verbatim in the browser, so only pass JavaScript you trust.

See also: [EsmWidget](esm-widget.md) for running any other CDN library the same way,
[ObservablePlot](observable-plot.md) for JS charts fed by Python values, and
[FramePlayer](frame-player.md) for playing back frames you rendered in Python.

### `ManimWeb`

`from wigglystuff.manim_web import ManimWeb`

```python
ManimWeb(code: Optional[str] = None, *, src: Optional[str] = None, width: int = 500, height: int = 300, version: str = '0.3.24', **kwargs: Any) -> None
```

Run a `manim-web <https://github.com/maloyan/manim-web>`_ scene in a notebook.

``manim-web`` is a TypeScript/WebGL reimplementation of Manim that renders
animations entirely in the browser. This widget is a thin runner: it loads
the manim-web engine from a CDN, then executes a blob of JavaScript you
supply (the ``code`` traitlet). The animation plays inline; Python's only
job is to hand over the source and the sizing.

Your JavaScript is run as the body of an async function with the manim-web
module namespace (``manim``), the target DOM element (``container``), the
``width`` / ``height`` ints, and the widget ``model`` in scope. The
recommended entry point is manim-web's own ``Player``, which renders a full
playback UI into ``container`` — play/pause, a scrub timeline with segment
markers, speed control, fullscreen and export::

    const player = new manim.Player(container, {
        width, height, autoPlay: true, backgroundColor: manim.WHITE,
    });
    player.sequence(async (scene) => {
        const circle = new manim.Circle({
            radius: 1.5, color: manim.BLUE, fillOpacity: 1,
        });
        await scene.play(new manim.Create(circle));
    });

``PlayerOptions`` extends ``SceneOptions``, so ``width``/``height``/
``backgroundColor`` work alongside ``autoPlay`` and ``loop``. Colours are
plain hex strings (``manim.BLUE``, or ``"#e94560"`` directly); set
``fillOpacity: 1`` for solid shapes on a light background.

The code is executed verbatim in the browser, so only pass JavaScript you
trust (typically your own).

Examples:
    ```python
    import marimo as mo
    from wigglystuff import ManimWeb

    scene = '''
        const player = new manim.Player(container, {
            width, height, autoPlay: true, backgroundColor: manim.WHITE,
        });
        player.sequence(async (scene) => {
            const c = new manim.Circle({
                radius: 1.5, color: manim.BLUE, fillOpacity: 1,
            });
            await scene.play(new manim.Create(c));
        });
    '''
    mo.ui.anywidget(ManimWeb(code=scene, width=800, height=450))
    ```

    Point at a local file or a URL instead of an inline string — the first
    argument accepts any of the three forms:

    ```python
    ManimWeb("scenes/intro.js")
    ManimWeb("https://example.com/scene.js")
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `code` | Unicode | `''` |
| `error` | Unicode | `''` |
| `height` | Int | `300` |
| `version` | Unicode | `'0.3.24'` |
| `width` | Int | `500` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `code` | `str` | Resolved scene JavaScript (inline JS, or the contents of a file / URL, fetched in Python), run against the manim-web `manim` namespace and a `container` element. |
| `width` | `int` | Container width in pixels. |
| `height` | `int` | Container height in pixels. |
| `version` | `str` | manim-web version loaded from the CDN. |
| `error` | `str` | Read-back of the latest JS runtime error, or `""`. |

---
Démo : [`../demos/manim_web.py`](../demos/manim_web.py)
