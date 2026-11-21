<!-- wigglystuff 0.6.0, recopié de docs/reference/env-config.md (MIT) -->
# EnvConfig API


`EnvConfig` renders one masked input per environment variable so a notebook can ask for
API keys instead of having them pasted into a cell. Pass a list of names for a plain
existence check, or a dict mapping names to validator callables — a validator that raises
marks that row invalid and shows the message. Anything already set in `os.environ` is
picked up as a starting value, but the widget never writes back to it and never syncs the
values to the browser; you read them with `config["KEY"]`, and `require_valid()` raises
when something is still missing so the rest of the notebook stops early.

See also: [CellTour](cell-tour.md) for walking a first-time reader through setup,
[CopyToClipboard](copy-to-clipboard.md) for handing a generated value back to them, and
[ApiDoc](api-doc.md) for documenting the client you just configured.

### `EnvConfig`

`from wigglystuff.env_config import EnvConfig`

```python
EnvConfig(variables: Union[Sequence[str], dict[str, Optional[Callable[[str], NoneType]]]], **kwargs: Any) -> None
```

Environment variable configuration widget for secure API key management.

Displays a UI for configuring environment variables, with password-style
masking and optional validation callbacks. Useful for notebooks that need
API keys configured before proceeding.

Values are stored internally and never written back to os.environ.

Examples:
    ```python
    import marimo as mo
    from wigglystuff import EnvConfig

    # Simple usage - just check vars exist
    config = mo.ui.anywidget(EnvConfig(["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]))
    config

    # With validators
    config = mo.ui.anywidget(EnvConfig({
        "OPENAI_API_KEY": lambda k: openai.Client(api_key=k).models.list(),
        "ANTHROPIC_API_KEY": None,  # Just check existence
    }))

    # Block until valid
    config.require_valid()

    # Access values
    config["OPENAI_API_KEY"]
    ```

Traitlets synchronisés dans le paquet installé :

| Traitlet | Type | Défaut |
|---|---|---|
| `all_valid` | Bool | `False` |
| `variables` | List | |


## Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `variables` | `list` | List of variable info dicts with name, status, error, and has_validator. Secret values are not synced. |
| `all_valid` | `bool` | True when all variables are valid. |

## Helper methods

| Method | Description |
| --- | --- |
| `require_valid()` | Raises `EnvironmentError` if any variable is missing/invalid. |
| `config["KEY"]` | Dictionary-style access to stored values. |
| `"KEY" in config` | Check if a variable is configured and has a value. |

---
Démo : [`../demos/envconfig.py`](../demos/envconfig.py)
