from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .contrat import contrat_court, reference_regles
from .environnement import trouver_projet
from .ressources import SKILLS, dossier_skill

ICI = Path(__file__).resolve().parent
DOSSIERS_SKILL = {"agents": ".agents/skills", "claude": ".claude/skills", "github": ".github/skills"}
# `.claude/settings.json` est lu par Claude Code et par Copilot ; `.github/hooks/` par Copilot seul.
FICHIERS_HOOKS = {"claude": ".claude/settings.json", "github": ".github/hooks/marimo-agent-kit.json"}


@dataclass
class Action:
    cible: str
    etat: Literal["à créer", "créé", "déjà là", "à compléter à la main", "laissé (diffère)"]
    detail: str = ""


def commande_mak(source: str | None = None) -> list[str]:
    if source:
        return ["uvx", "--from", source, "mak"]
    if shutil.which("mak"):
        return ["mak"]
    racine = ICI.parent.parent
    if (racine / "pyproject.toml").exists():
        return ["uvx", "--from", str(racine), "mak"]
    return ["uvx", "--from", "marimo-agent-kit", "mak"]


def fichiers_du_skill(nom: str = "marimo-agent-kit") -> dict[str, bytes]:
    racine = dossier_skill(nom)
    fichiers = {str(c.relative_to(racine)).replace("\\", "/"): c.read_bytes()
                for c in sorted(racine.rglob("*")) if c.is_file() and "__pycache__" not in c.parts}
    if nom == "marimo-agent-kit":
        fichiers["reference/regles.md"] = reference_regles().encode("utf-8")
    return fichiers


def poser_skill(dossier: Path, cible: str, appliquer: bool, remplacer: bool = False,
                noms: tuple[str, ...] = SKILLS) -> list[Action]:
    actions = []
    for nom_skill in noms:
        destination = dossier / DOSSIERS_SKILL[cible] / nom_skill
        for relatif, contenu in fichiers_du_skill(nom_skill).items():
            chemin = destination / relatif
            nom = str(chemin.relative_to(dossier))
            if chemin.exists() and chemin.read_bytes() == contenu:
                actions.append(Action(nom, "déjà là"))
                continue
            if chemin.exists() and not remplacer:
                actions.append(Action(nom, "laissé (diffère)", "`--remplacer` pour mettre la version du paquet"))
                continue
            if appliquer:
                chemin.parent.mkdir(parents=True, exist_ok=True)
                chemin.write_bytes(contenu)
            actions.append(Action(nom, "créé" if appliquer else "à créer"))
    return actions


def bloc_paquets(gestionnaire: str) -> str:
    return ("\n[tool.marimo.package_management]\n"
            "# Le bouton d'installation de l'éditeur ajoute le paquet manquant au projet par ce gestionnaire.\n"
            f'manager = "{gestionnaire}"\n')


def bloc_marimo(commande: list[str], gestionnaire: str = "pixi") -> str:
    # Chaîne littérale TOML (''' … ''') : aucun antislash n'y est interprété.
    regles = contrat_court().replace("'''", "' ' '")
    return (
        "\n[tool.marimo.ai]\n"
        "# Ajouté par marimo-agent-kit : envoyé avec chaque requête de l'assistant de marimo.\n"
        f"rules = '''\n{regles}'''\n"
        "\n[tool.marimo.mcp.mcpServers.marimo_agent_kit]\n"
        "# Outils pour les modes Ask et Agent de l'assistant (demande marimo[mcp]).\n"
        f"command = {json.dumps(commande[0])}\n"
        f"args = {json.dumps([*commande[1:], 'mcp'], ensure_ascii=False)}\n"
        + bloc_paquets(gestionnaire)
    )


def poser_marimo(dossier: Path, appliquer: bool, source: str | None = None) -> list[Action]:
    pyproject = dossier / "pyproject.toml"
    projet = trouver_projet(dossier)
    gestionnaire = "uv" if projet is not None and projet.gestionnaire == "uv" else "pixi"
    bloc = bloc_marimo(commande_mak(source), gestionnaire)
    if not pyproject.exists():
        return [Action("pyproject.toml", "à compléter à la main",
                       "marimo ne lit sa configuration de projet que dans pyproject.toml. `pixi init --format pyproject` "
                       "en crée un que pixi lit aussi. Sinon, mets ce bloc dans ~/.config/marimo/marimo.toml sans le "
                       "préfixe `tool.marimo.` :\n" + bloc)]
    texte = pyproject.read_text(encoding="utf-8")
    ajout, detail = bloc, f'[tool.marimo.ai] rules, le serveur MCP et manager = "{gestionnaire}"'
    if "[tool.marimo.ai]" in texte or "[tool.marimo.mcp" in texte or "[tool.marimo.package_management]" in texte:
        if "marimo_agent_kit" not in texte:
            return [Action("pyproject.toml", "à compléter à la main",
                           "[tool.marimo.ai], [tool.marimo.mcp] ou [tool.marimo.package_management] existe déjà : "
                           "fusionne ce bloc à la main :\n" + bloc)]
        if "[tool.marimo.package_management]" in texte:
            return [Action("pyproject.toml", "déjà là")]
        ajout, detail = bloc_paquets(gestionnaire), f'manager = "{gestionnaire}" pour le bouton d\'installation'
    if projet is not None and projet.gestionnaire is None:
        detail += ". pixi ne gère pas encore ce projet : `pixi init --format pyproject` l'y ajoute"
    if appliquer:
        pyproject.write_text(texte.rstrip("\n") + "\n" + ajout, encoding="utf-8")
    return [Action("pyproject.toml", "créé" if appliquer else "à créer", detail)]


def _fusionner_json(chemin: Path, modifier, appliquer: bool, dossier: Path) -> Action:
    nom = str(chemin.relative_to(dossier))
    donnees = {}
    if chemin.exists():
        try:
            donnees = json.loads(chemin.read_text(encoding="utf-8") or "{}")
        except ValueError:
            return Action(nom, "à compléter à la main", "JSON illisible : rien n'a été touché")
    if not modifier(donnees):
        return Action(nom, "déjà là")
    if appliquer:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(json.dumps(donnees, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return Action(nom, "créé" if appliquer else "à créer")


def _hooks_poses(chemin: Path, commande: str) -> bool:
    try:
        return commande in chemin.read_text(encoding="utf-8")
    except OSError:
        return False


def poser_hooks(dossier: Path, appliquer: bool, source: str | None = None, cible: str = "claude") -> list[Action]:
    commande = " ".join([*commande_mak(source), "hook"])
    autre = next(c for c in FICHIERS_HOOKS if c != cible)
    if _hooks_poses(dossier / FICHIERS_HOOKS[autre], commande):
        return [Action(FICHIERS_HOOKS[cible], "à compléter à la main",
                       f"les hooks sont déjà dans {FICHIERS_HOOKS[autre]}. Copilot lit les deux fichiers et lancerait "
                       "chaque hook deux fois : garde un seul des deux.")]
    if cible == "github":
        return [_fusionner_json(dossier / FICHIERS_HOOKS["github"], lambda d: _hooks_copilot(d, commande), appliquer, dossier)]

    def modifier(donnees: dict) -> bool:
        hooks = donnees.setdefault("hooks", {})
        change = False
        for evenement, matcher, delai in (("PostToolUse", "Write|Edit|MultiEdit", 120), ("SessionStart", "", 30),
                                          ("PreToolUse", "Bash|PowerShell", 15)):
            entrees = hooks.setdefault(evenement, [])
            if any(commande == h.get("command") for e in entrees for h in e.get("hooks", [])):
                continue
            entree = {"hooks": [{"type": "command", "command": commande, "timeout": delai}]}
            entrees.append({"matcher": matcher, **entree} if matcher else entree)
            change = True
        return change

    return [_fusionner_json(dossier / FICHIERS_HOOKS["claude"], modifier, appliquer, dossier)]


def _hooks_copilot(donnees: dict, commande: str) -> bool:
    donnees.setdefault("version", 1)
    hooks = donnees.setdefault("hooks", {})
    change = False
    for evenement, argument, matcher, delai in (
        ("sessionStart", "sessionStart", "", 30),
        ("preToolUse", "preToolUse", "bash|powershell", 15),
        ("postToolUse", "", "create|edit|str_replace_editor", 120),
    ):
        ligne = f"{commande} {argument}".strip()
        entrees = hooks.setdefault(evenement, [])
        if any(ligne in (e.get("bash"), e.get("powershell")) for e in entrees):
            continue
        entree = {"type": "command", "bash": ligne, "powershell": ligne, "timeoutSec": delai}
        entrees.append({**entree, "matcher": matcher} if matcher else entree)
        change = True
    return change


def poser_mcp(dossier: Path, appliquer: bool, source: str | None = None) -> list[Action]:
    commande = commande_mak(source)

    def modifier(donnees: dict) -> bool:
        serveurs = donnees.setdefault("mcpServers", {})
        if "marimo_agent_kit" in serveurs:
            return False
        serveurs["marimo_agent_kit"] = {"command": commande[0], "args": [*commande[1:], "mcp"]}
        return True

    return [_fusionner_json(dossier / ".mcp.json", modifier, appliquer, dossier)]


def installer(dossier: Path, skill: str | None, marimo: bool, hooks: str | None, mcp: bool,
              appliquer: bool, remplacer: bool = False, source: str | None = None,
              noms: tuple[str, ...] = SKILLS) -> list[Action]:
    actions: list[Action] = []
    if skill:
        actions += poser_skill(dossier, skill, appliquer, remplacer, noms)
    if marimo:
        actions += poser_marimo(dossier, appliquer, source)
    if hooks:
        actions += poser_hooks(dossier, appliquer, source, hooks)
    if mcp:
        actions += poser_mcp(dossier, appliquer, source)
    return actions
