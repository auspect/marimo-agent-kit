"""Ce que les agents envoient au hook, et ce que leur code de sortie veut dire.

Claude Code envoie `tool_name` et `tool_input` à un hook `PostToolUse`. Copilot envoie `toolName`
et `toolArgs`. Pour Claude Code, le code 2 rend la sortie d'erreur à l'agent, le code 0 laisse
passer, et `hookSpecificOutput.additionalContext` ajoute du contexte. Copilot lit
`additionalContext` à la racine de la réponse.

Au démarrage, Claude Code envoie `hook_event_name: "SessionStart"` et Copilot appelle
`mak hook sessionStart`. Le hook rend alors le contexte du projet : son gestionnaire de paquets,
le proxy et les consignes.

Avant un outil (`PreToolUse`, ou `mak hook preToolUse` pour Copilot), la garde juge la commande.
Elle refuse par le code 2 et la raison sur la sortie d'erreur, que les deux agents comprennent.
Chez Copilot, tout code non nul refuse l'outil : la garde ne doit donc jamais planter.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .carnet import est_notebook
from .verifier import verifier

ECRITURES = {"write", "edit", "multiedit", "create", "str_replace_editor", "apply_patch", "notebookedit", "replace"}


def chemin_ecrit(donnees: dict) -> tuple[str, Path | None]:
    if "tool_name" in donnees:
        outil, args, origine = donnees.get("tool_name", ""), donnees.get("tool_input") or {}, "claude"
    else:
        outil, args, origine = donnees.get("toolName", ""), donnees.get("toolArgs") or {}, "copilot"
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                args = {}
    if str(outil).lower() not in ECRITURES or not isinstance(args, dict):
        return origine, None
    texte = args.get("file_path") or args.get("path") or args.get("filePath") or args.get("notebook_path")
    if not texte:
        return origine, None
    chemin = Path(texte)
    if not chemin.is_absolute():
        chemin = Path(donnees.get("cwd") or ".") / chemin
    return origine, chemin


def debut_de_session(donnees: dict, origine: str) -> int:
    from .environnement import charger, contexte_agent, trouver_projet

    depuis = Path(donnees["cwd"]) if isinstance(donnees.get("cwd"), str) else None
    texte = contexte_agent(charger(depuis), trouver_projet(depuis))
    if origine == "claude":
        sortie = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": texte}}
    else:
        sortie = {"additionalContext": texte}
    print(json.dumps(sortie, ensure_ascii=False))
    return 0


def avant_outil(donnees: dict) -> int:
    from .environnement import charger
    from .garde import juger, mode_garde, noter

    try:
        if "tool_name" in donnees:
            outil, args = str(donnees.get("tool_name", "")), donnees.get("tool_input") or {}
        else:
            outil, args = str(donnees.get("toolName", "")), donnees.get("toolArgs") or {}
            if isinstance(args, str):
                args = json.loads(args)
        config = charger(Path(donnees["cwd"]) if isinstance(donnees.get("cwd"), str) else None)
        mode = mode_garde(config)
        refus = juger(outil, args) if isinstance(args, dict) and mode != "off" else []
        if not refus:
            return 0
        noter(config, outil, refus, "refusé" if mode == "agir" else "aurait refusé")
        if mode != "agir":
            return 0
    except Exception:  # noqa: BLE001 : une garde qui plante bloquerait l'agent chez Copilot
        return 0
    sys.stderr.write("marimo-agent-kit, garde : " + " ".join(r.raison for r in refus) + "\n")
    return 2


def principal(entree=None, executer: bool = False, evenement: str | None = None) -> int:
    try:
        donnees = json.loads((entree or sys.stdin).read() or "{}")
    except ValueError:
        donnees = {}
    if not isinstance(donnees, dict):
        donnees = {}
    if donnees.get("hook_event_name") == "SessionStart":
        return debut_de_session(donnees, "claude")
    if (evenement or "").lower() == "sessionstart":
        return debut_de_session(donnees, "copilot")
    if donnees.get("hook_event_name") == "PreToolUse" or (evenement or "").lower() == "pretooluse":
        return avant_outil(donnees)
    origine, chemin = chemin_ecrit(donnees)
    if chemin is None or chemin.suffix != ".py" or not chemin.exists():
        return 0
    try:
        source = chemin.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    if not est_notebook(source):
        return 0
    rapport = verifier(chemin, executer=executer, delai=120)
    compte = rapport.compte()
    if any(e.etat == "échec" for e in rapport.etapes) and not compte["erreur"]:
        return 0
    if compte["erreur"]:
        sys.stderr.write("marimo-agent-kit : ce notebook a des erreurs. Corrige-les avant de continuer.\n\n"
                         + rapport.en_texte(conseils=False) + "\n")
        return 2
    if compte["avertissement"]:
        texte = "marimo-agent-kit a relu le notebook :\n" + rapport.en_texte(conseils=False)
        if origine == "claude":
            sortie = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": texte}}
        else:
            sortie = {"additionalContext": texte}
        print(json.dumps(sortie, ensure_ascii=False))
    return 0
