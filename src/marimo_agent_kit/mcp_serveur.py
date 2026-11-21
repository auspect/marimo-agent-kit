from __future__ import annotations

import json
import sys
from pathlib import Path

from . import __version__
from .api import en_texte as api_en_texte
from .api import interroger
from .contrat import contrat_court
from .verifier import verifier
from .verifier_cellules import verifier_cellules

PROTOCOLE_PAR_DEFAUT = "2025-06-18"

OUTILS = [
    {
        "name": "verifier_notebook",
        "description": (
            "Vérifie un notebook marimo (.py) par marimo check, les règles des erreurs fréquentes d'agent "
            "(valeur d'un élément d'interface lue dans sa cellule, mo.md sans f, mutation entre cellules, élément "
            "non lié, asyncio.run…), puis l'exécution de chaque cellule dans le noyau. À lancer après chaque "
            "modification, avant de dire que le notebook est prêt. Corrige toutes les erreurs."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "chemin": {"type": "string", "description": "Chemin du notebook, absolu ou relatif au dossier de travail."},
                "executer": {"type": "boolean", "description": "Exécuter les cellules (défaut : vrai).", "default": True},
                "conseils": {"type": "boolean", "description": "Lister aussi les conseils de lisibilité.", "default": False},
            },
            "required": ["chemin"],
        },
    },
    {
        "name": "verifier_cellules",
        "description": (
            "Vérifie des corps de cellules AVANT de les insérer (sans @app.cell ni return). Donne le notebook pour "
            "que les noms existants, les imports et les mutations soient jugés dans leur contexte. Rapide : rien "
            "n'est exécuté."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "cellules": {"type": "array", "items": {"type": "string"}, "description": "Corps des cellules proposées."},
                "notebook": {"type": "string", "description": "Chemin du notebook où elles iront (facultatif)."},
                "conseils": {"type": "boolean", "default": False},
            },
            "required": ["cellules"],
        },
    },
    {
        "name": "api_marimo",
        "description": (
            "Signature, documentation et membres d'un symbole de marimo dans la version installée (ex. mo.ui.slider, "
            "mo.ui, mo.stop, mo.cache). À utiliser avant d'écrire un appel dont tu n'es pas sûr : n'invente pas de "
            "paramètre."
        ),
        "inputSchema": {"type": "object", "properties": {"symbole": {"type": "string"}}, "required": ["symbole"]},
    },
    {
        "name": "chercher_api_marimo",
        "description": "Cherche un mot dans les noms et les résumés de l'API de marimo installée, par exemple cache, table ou stop.",
        "inputSchema": {"type": "object", "properties": {"motif": {"type": "string"}}, "required": ["motif"]},
    },
    {
        "name": "widgets_wigglystuff",
        "description": (
            "Documentation hors ligne des widgets wigglystuff (Slider2D, TangleDistribution, ChartPuck, PairPlot, "
            "StateViewer…) : sans argument le catalogue, avec `nom` la page (usage, signature, traitlets, démo), avec "
            "`motif` une recherche. Signale si le projet a une autre version que celle de la doc."
        ),
        "inputSchema": {"type": "object", "properties": {"nom": {"type": "string"}, "motif": {"type": "string"}}},
    },
    {
        "name": "regles_marimo",
        "description": "Le contrat court pour écrire des cellules marimo justes et lisibles. À lire une fois par session.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _chemin(texte: str) -> Path:
    return Path(texte).expanduser()


def appeler(nom: str, arguments: dict) -> tuple[str, bool]:
    if nom == "verifier_notebook":
        chemin = _chemin(arguments["chemin"])
        if not chemin.exists():
            return f"{chemin} n'existe pas (dossier de travail : {Path.cwd()}).", True
        rapport = verifier(chemin, executer=arguments.get("executer", True))
        return rapport.en_texte(conseils=arguments.get("conseils", False)), False
    if nom == "verifier_cellules":
        notebook = arguments.get("notebook")
        rapport = verifier_cellules(arguments["cellules"], _chemin(notebook) if notebook else None)
        return rapport.en_texte(conseils=arguments.get("conseils", False)), False
    if nom == "api_marimo":
        return api_en_texte(interroger(arguments["symbole"])), False
    if nom == "chercher_api_marimo":
        return api_en_texte(interroger(arguments["motif"], mode="chercher")), False
    if nom == "widgets_wigglystuff":
        from .widgets import en_texte as widgets_en_texte

        return widgets_en_texte(arguments.get("nom") or None, arguments.get("motif") or None), False
    if nom == "regles_marimo":
        return contrat_court(), False
    return f"Outil inconnu : {nom}", True


def traiter(message: dict) -> dict | None:
    methode, ident = message.get("method"), message.get("id")
    if ident is None:  # notification
        return None
    if methode == "initialize":
        version = (message.get("params") or {}).get("protocolVersion") or PROTOCOLE_PAR_DEFAUT
        resultat = {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "marimo-agent-kit", "version": __version__},
            "instructions": "Outils pour écrire et vérifier des notebooks marimo. Lis regles_marimo une fois ; "
                            "lance verifier_notebook après chaque modification.",
        }
    elif methode == "ping":
        resultat = {}
    elif methode == "tools/list":
        resultat = {"tools": OUTILS}
    elif methode == "tools/call":
        params = message.get("params") or {}
        try:
            texte, erreur = appeler(params.get("name", ""), params.get("arguments") or {})
        except Exception as exc:
            texte, erreur = f"{type(exc).__name__} : {exc}", True
        resultat = {"content": [{"type": "text", "text": texte}], "isError": erreur}
    else:
        return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": f"Méthode inconnue : {methode}"}}
    return {"jsonrpc": "2.0", "id": ident, "result": resultat}


def servir(entree=None, sortie=None) -> None:
    entree = entree or sys.stdin
    sortie = sortie or sys.stdout
    for ligne in entree:
        ligne = ligne.strip()
        if not ligne:
            continue
        try:
            message = json.loads(ligne)
        except ValueError:
            reponse = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON illisible"}}
        else:
            reponse = traiter(message) if isinstance(message, dict) else None
        if reponse is not None:
            sortie.write(json.dumps(reponse, ensure_ascii=False) + "\n")
            sortie.flush()
