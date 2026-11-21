from __future__ import annotations

import os

VARIABLES = {
    "MARIMO_SKIP_UPDATE_CHECK": ("1", "pas de visite quotidienne à marimo.io au lancement de `marimo edit`"),
    "PYDANTIC_AI_NO_BANNER": ("1", "pas de bannière pydantic-ai dans le terminal (rien n'est envoyé, c'est de l'affichage)"),
}

ENV_SOBRE = {nom: valeur for nom, (valeur, _) in VARIABLES.items()}


def env_sobre() -> dict[str, str]:
    return {**os.environ, **ENV_SOBRE}
