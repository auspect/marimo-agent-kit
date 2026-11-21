<!-- wigglystuff 0.6.0, recopié de docs/reference/async-flow.md (MIT) -->
# AsyncFlow API


`AsyncFlow` runs a coroutine on the notebook's own event loop and streams its task
activity into a swimlane timeline that fills in as the run proceeds: one lane per task,
solid bars where a task is running, hatched bars where it sits suspended at an `await`,
indented under the parent that spawned it. You use it as
`flow = await AsyncFlow.trace(main())`, which displays the live widget and returns it
once the run finishes. Capture relies on `sys.monitoring`, so Python 3.12 or newer is
required.

See also: [LiveEdit](live-edit.md) for the same pass-by-pass reading of a synchronous
function, [ObservablePlot](observable-plot.md) for charting the timings you collect, and
[EsmWidget](esm-widget.md) for building your own timeline view in JavaScript.

### `AsyncFlow`

`from wigglystuff.async_flow import AsyncFlow`

```python
AsyncFlow(*, width: 'int' = 0, **kwargs: 'Any') -> 'None'
```

Live, source-linked timeline of a single async run.

Runs a coroutine on the notebook's own event loop and streams its task
activity — spawn, suspend-at-``await``, resume, done — into a swimlane
timeline that fills in as the run proceeds. One lane per task; solid bars are
running, hatched bars are suspended at an ``await``.

Example (marimo, top-level ``await``)::

    import asyncio
    from wigglystuff import AsyncFlow

    async def worker(name, delay):
        await asyncio.sleep(delay)
        return name

    async def main():
        return await asyncio.gather(worker("A", 0.3), worker("B", 0.1))

    flow = await AsyncFlow.trace(main())   # displays live, returns the widget
    flow.result                            # ['A', 'B']

Requires ``sys.monitoring`` (Python 3.12+).

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `events` | List | |
| `now_ms` | Float | `0.0` |
| `running` | Bool | `False` |
| `width` | Int | `0` |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `events` | `list[dict]` | Captured event stream; re-synced on every poll tick so the timeline grows live. Each entry has `t_ms`, `coro`, `event`, `task`, `line`, `detail`. |
| `now_ms` | `float` | Elapsed wall-clock milliseconds; advances every tick so suspended bars keep growing during long sleeps. |
| `running` | `bool` | Whether a run is currently in flight. |
| `width` | `int` | Widget width in pixels; `0` grows to fit. |

---
Démo : [`../demos/asyncflow.py`](../demos/asyncflow.py)
