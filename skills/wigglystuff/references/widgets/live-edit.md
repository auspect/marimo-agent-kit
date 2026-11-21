<!-- wigglystuff 0.6.0, recopié de docs/reference/live-edit.md (MIT) -->
# LiveEdit API


`LiveEdit` takes one call — `LiveEdit.inspect_run(fn, *args, **kwargs)` — and lays the
run out next to its source: the setup values, a row per loop pass including nested child
loops, and the value that came back. Click a numeric column header to chart that column
across passes. `LiveEdit.from_pytest("tests/test_foo.py::test_bar")` does the same for a
test body, with a failing `assert` rendered on the offending line instead of raised, so
a broken test becomes something you read rather than something you re-run with print
statements.

See also: [AsyncFlow](async-flow.md) for the same idea applied to an async run,
[ApiDoc](api-doc.md) for rendering a function's signature and docstring, and
[Matrix](matrix.md) for editing the numbers you feed in by hand.

### `LiveEdit`

`from wigglystuff.live_edit import LiveEdit`

```python
LiveEdit(code: 'str', *, args: 'tuple[Any, ...]' = (), kwargs: 'dict[str, Any] | None' = None, editable: 'bool' = False, function_name: 'str | None' = None, globalns: 'dict[str, Any] | None' = None, height: 'int | None' = None, float_precision: 'int | None' = None, visible_columns: 'list[str] | None' = None, **widget_kwargs: 'Any') -> 'None'
```

Read-only function trace widget for inspecting one Python run.

``LiveEdit.inspect_run(fn, *args, **kwargs)`` is the primary constructor for
v1. The widget stores the original Python args privately and only syncs
repr-based trace data to the browser, which keeps future editable code
updates possible without serializing arbitrary Python objects.

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `annotations` | Dict | |
| `code` | Unicode | `''` |
| `editable` | Bool | `False` |
| `error` | Dict | |
| `height` | Int | `520` |
| `theme` | Unicode | `'auto'` |
| `trace` | Dict | |
| `visible_columns` | List | |
| `width` | Int | `0` |


### `inspect_run`

`from wigglystuff.live_edit import inspect_run`

```python
inspect_run(fn: 'Any', *args: 'Any', **kwargs: 'Any') -> 'LiveEdit'
```

Inspect one run of a Python function with ``LiveEdit``.


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `code` | `str` | Source code for the traced function. This is the future live-edit source of truth. |
| `trace` | `dict` | Structured setup values, loop passes, nested child loops, and returned value. |
| `annotations` | `dict` | Static line/token metadata used by the browser for hover linking. |
| `error` | `dict or None` | Parse, runtime, or argument mismatch error payload; `None` when the run succeeds. |
| `editable` | `bool` | Reserved for the future browser editor mode. Defaults to `False`. |
| `theme` | `str` | `"auto"`, `"light"`, or `"dark"`. |
| `width` | `int` | Widget width in pixels. |
| `height` | `int` | Maximum widget height in pixels. |

---
Démo : [`../demos/liveedit.py`](../demos/liveedit.py)
