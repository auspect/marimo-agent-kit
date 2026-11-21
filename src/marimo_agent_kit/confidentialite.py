from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from .api import python_avec_marimo
from .environnement import ENV_SOBRE, VARIABLES

SCRIPT = r'''
import importlib.util, json, os
r = {"ddgs": importlib.util.find_spec("ddgs") is not None,
     "markdownify": importlib.util.find_spec("markdownify") is not None}
try:
    import marimo
    r["version"] = marimo.__version__
    from marimo._config.cli_state import get_cli_state
    r["consentement_new"] = get_cli_state().accepted_text_to_notebook_terms_at
    from marimo._config.manager import get_default_config_manager
    c = get_default_config_manager(current_path=os.getcwd()).get_config()
    r["presets_mcp"] = list(c.get("mcp", {}).get("presets", []))
    r["serveurs_mcp"] = sorted(c.get("mcp", {}).get("mcpServers", {}))
    r["copilot"] = c.get("completion", {}).get("copilot")
except Exception as e:
    r["erreur"] = f"{type(e).__name__}: {e}"
print(json.dumps(r))
'''


@dataclass
class Constat:
    etat: Literal["ok", "à régler", "attention", "info", "non vérifié"]
    sujet: str
    detail: str


def _vrai(valeur: str | None) -> bool:
    return (valeur or "").strip().lower() in ("1", "true", "yes", "on")


def infos_marimo() -> dict | None:
    python = python_avec_marimo()
    if python is None:
        return None
    try:
        sortie = subprocess.run([*python, "-c", SCRIPT], capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=120, env={**os.environ, **ENV_SOBRE})
        return json.loads(sortie.stdout.strip().splitlines()[-1])
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def diagnostiquer(env: Mapping[str, str], infos: dict | None) -> list[Constat]:
    constats = []
    if env.get("MARIMO_SKIP_UPDATE_CHECK") == "1":
        constats.append(Constat("ok", "vérification de version", "MARIMO_SKIP_UPDATE_CHECK=1"))
    else:
        constats.append(Constat("à régler", "vérification de version",
                                "`marimo edit` contacte marimo.io une fois par jour : MARIMO_SKIP_UPDATE_CHECK=1"))
    if _vrai(env.get("MARIMO_TRACING")):
        cible = env.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or env.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        ou = f"envoyés à {cible}" if cible else "écrits dans un fichier local"
        constats.append(Constat("attention", "traces de l'assistant",
                                f"MARIMO_TRACING est allumé : prompts et réponses {ou}. Retire la variable si ce n'est pas voulu."))
    else:
        constats.append(Constat("ok", "traces de l'assistant", "MARIMO_TRACING éteint"))
    if infos is None:
        constats.append(Constat("non vérifié", "environnement de marimo",
                                "aucun Python avec marimo trouvé : recherche web, MCP, Copilot non regardés"))
    else:
        if infos.get("ddgs"):
            constats.append(Constat("attention", "recherche web du chat",
                                    "`ddgs` est installé : l'option web du chat envoie des requêtes à DuckDuckGo"))
        if infos.get("markdownify"):
            constats.append(Constat("attention", "lecture de pages web",
                                    "`markdownify` est installé : le chat peut lire une adresse que le modèle choisit"))
        if not infos.get("ddgs") and not infos.get("markdownify"):
            constats.append(Constat("ok", "recherche et lecture web", "ni `ddgs` ni `markdownify`"))
        if "erreur" in infos:
            constats.append(Constat("non vérifié", "configuration de marimo", infos["erreur"][:160]))
        else:
            if "context7" in infos.get("presets_mcp", []):
                constats.append(Constat("attention", "MCP context7", "le préréglage envoie les questions à context7.com"))
            serveurs = infos.get("serveurs_mcp", [])
            if serveurs:
                constats.append(Constat("info", "serveurs MCP", "lancés par marimo : " + ", ".join(serveurs)))
            copilot = infos.get("copilot")
            if copilot in ("github", "codeium", "windsurf"):
                constats.append(Constat("attention", "complétion de code",
                                        f"`{copilot}` : le code des cellules part chez ce service"))
            if infos.get("consentement_new"):
                constats.append(Constat("attention", 'marimo new "invite"',
                                        f"conditions acceptées le {infos['consentement_new']} : l'invite part à ai.marimo.app"))
            else:
                constats.append(Constat("info", 'marimo new "invite"',
                                        "envoie l'invite à ai.marimo.app après accord : à éviter au travail"))
    if env.get("PYDANTIC_AI_NO_BANNER") is None:
        constats.append(Constat("info", "bannière pydantic-ai", "PYDANTIC_AI_NO_BANNER=1 la masque (affichage seulement)"))
    constats.append(Constat("info", "navigateur", "unpkg et jsdelivr servent seulement l'autocomplétion d'emoji et "
                                                  "d'icônes, MathJax et l'export WASM"))
    return constats


def lignes_a_poser(env: Mapping[str, str]) -> list[str]:
    manquantes = [(nom, valeur, raison) for nom, (valeur, raison) in VARIABLES.items() if env.get(nom) != valeur]
    if not manquantes:
        return ["Rien à poser : les variables sont déjà là."]
    lignes = ["PowerShell (pour ton compte, sans droits d'administration ; rouvre le terminal ensuite) :"]
    lignes += [f'  [Environment]::SetEnvironmentVariable("{n}", "{v}", "User")   # {r}' for n, v, r in manquantes]
    lignes += ["bash ou zsh (dans ~/.bashrc ou ~/.zshrc) :"]
    lignes += [f"  export {n}={v}" for n, v, _ in manquantes]
    if _vrai(env.get("MARIMO_TRACING")):
        lignes += ["Pour éteindre les traces : retire MARIMO_TRACING de ton profil."]
    return lignes


def en_texte(constats: list[Constat], env: Mapping[str, str], version: str | None) -> str:
    tete = f"Ce qui sort du poste avec marimo {version}" if version else "Ce qui sort du poste avec marimo"
    largeur = max(len(c.etat) for c in constats)
    lignes = [tete + " :", ""]
    lignes += [f"  [{c.etat}]{' ' * (largeur - len(c.etat))} {c.sujet}. {c.detail}" for c in constats]
    return "\n".join([*lignes, "", *lignes_a_poser(env)])

