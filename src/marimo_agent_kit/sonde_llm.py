"""marimo 0.25.2 parle à un fournisseur personnalisé au nom inconnu par `POST {base_url}/chat/completions`
(pydantic-ai, `OpenAIChatModel`), avec `Authorization: Bearer <clé>` et `api-key: <clé>`. Selon la
fonction utilisée, il ajoute :

| Fonction de marimo | Ce que la requête contient en plus |
|---|---|
| Chat en mode Manual | `stream: true`, `stream_options: {include_usage: true}` |
| Autocomplétion en ligne | `max_completion_tokens: 1024`, sans flux |
| Génération ou modification de cellule | un outil `final_result` et `tool_choice: "required"` |
| Chat en modes Ask et Agent (outils MCP compris) | les outils, `tool_choice: "auto"` |
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass

OUTIL_REGLES = {"type": "function", "function": {
    "name": "regles_marimo", "description": "Rend les règles d'écriture des notebooks marimo.",
    "parameters": {"type": "object", "properties": {}}}}
OUTIL_SORTIE = {"type": "function", "function": {
    "name": "final_result", "description": "La cellule marimo à insérer.",
    "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}}


@dataclass
class Essai:
    fonction: str
    ok: bool
    detail: str


def _envoyer(url: str, corps: dict, entetes: dict[str, str], contexte: ssl.SSLContext | None, delai: int
             ) -> tuple[int, str]:
    requete = urllib.request.Request(url, data=json.dumps(corps).encode(), method="POST",
                                     headers={"Content-Type": "application/json", **entetes})
    try:
        with urllib.request.urlopen(requete, timeout=delai, context=contexte) as reponse:
            return reponse.status, reponse.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as erreur:
        return erreur.code, erreur.read().decode("utf-8", errors="replace")


def _lire_flux(texte: str) -> tuple[str, list[dict], bool]:
    contenu, appels, flux = "", {}, False
    for ligne in texte.splitlines():
        if not ligne.startswith("data:"):
            continue
        donnee = ligne[5:].strip()
        if donnee == "[DONE]":
            flux = True
            continue
        try:
            morceau = json.loads(donnee)
        except ValueError:
            continue
        flux = True
        for choix in morceau.get("choices", []):
            delta = choix.get("delta") or {}
            contenu += delta.get("content") or ""
            for appel in delta.get("tool_calls") or []:
                courant = appels.setdefault(appel.get("index", 0), {"name": "", "arguments": ""})
                fonction = appel.get("function") or {}
                courant["name"] += fonction.get("name") or ""
                courant["arguments"] += fonction.get("arguments") or ""
    return contenu, list(appels.values()), flux


def _resume_erreur(code: int, texte: str) -> str:
    try:
        message = json.loads(texte).get("error", texte)
        message = message.get("message", message) if isinstance(message, dict) else message
    except (ValueError, AttributeError):
        message = texte
    return f"HTTP {code} : {str(message).strip()[:220]}"


def sonder(base_url: str, modele: str, cle: str = "inutilise", entetes: dict[str, str] | None = None,
           ca: str | None = None, verifier_tls: bool = True, delai: int = 60) -> list[Essai]:
    url = base_url.rstrip("/") + "/chat/completions"
    tous_entetes = {"Authorization": f"Bearer {cle}", "api-key": cle, **(entetes or {})}
    contexte = None
    if not verifier_tls:
        contexte = ssl._create_unverified_context()
    elif ca:
        contexte = ssl.create_default_context(cafile=ca)
    systeme = {"role": "system", "content": "Tu aides à écrire des notebooks marimo. Réponds en une phrase."}
    essais: list[Essai] = []

    def envoyer(corps: dict) -> tuple[int, str]:
        try:
            return _envoyer(url, {"model": modele, **corps}, tous_entetes, contexte, delai)
        except (urllib.error.URLError, OSError, TimeoutError) as erreur:
            return 0, f"connexion impossible : {getattr(erreur, 'reason', erreur)}"

    code, texte = envoyer({"messages": [systeme, {"role": "user", "content": "Dis bonjour."}],
                           "stream": True, "stream_options": {"include_usage": True}})
    if code == 200:
        contenu, _, flux = _lire_flux(texte)
        essais.append(Essai("chat, mode Manual (flux)", flux and bool(contenu.strip()),
                            f'réponse "{contenu.strip()[:60]}"' if flux else "réponse reçue, mais pas en flux SSE"))
    else:
        essais.append(Essai("chat, mode Manual (flux)", False, _resume_erreur(code, texte) if code else texte))
        if code == 0:
            return essais

    code, texte = envoyer({"messages": [systeme, {"role": "user", "content": "Complète : print('bon"}],
                           "stream": False, "max_completion_tokens": 16})
    essais.append(Essai("autocomplétion (max_completion_tokens)", code == 200,
                        "accepté" if code == 200 else _resume_erreur(code, texte)))

    code, texte = envoyer({"messages": [systeme, {"role": "user", "content": "Écris une cellule qui affiche 1."}],
                           "stream": True, "stream_options": {"include_usage": True},
                           "tools": [OUTIL_SORTIE], "tool_choice": "required"})
    if code == 200:
        _, appels, _ = _lire_flux(texte)
        valide = False
        if appels and appels[0]["name"] == "final_result":
            try:
                valide = "code" in json.loads(appels[0]["arguments"] or "{}")
            except ValueError:
                valide = False
        essais.append(Essai("génération de cellule (tool_choice required)", valide,
                            "appel de final_result valide" if valide else f"accepté, mais pas d'appel valide : {appels[:1]}"))
    else:
        essais.append(Essai("génération de cellule (tool_choice required)", False, _resume_erreur(code, texte)))

    code, texte = envoyer({"messages": [systeme, {"role": "user", "content": "Appelle l'outil regles_marimo."}],
                           "stream": True, "stream_options": {"include_usage": True},
                           "tools": [OUTIL_REGLES], "tool_choice": "auto"})
    if code == 200:
        _, appels, _ = _lire_flux(texte)
        appele = any(a["name"] == "regles_marimo" for a in appels)
        essais.append(Essai("modes Ask et Agent, outils MCP (tool_choice auto)", appele,
                            "outil appelé" if appele else "accepté, mais le modèle n'a pas appelé l'outil demandé"))
    else:
        essais.append(Essai("modes Ask et Agent, outils MCP (tool_choice auto)", False, _resume_erreur(code, texte)))
    return essais


def bloc_configuration(nom: str, base_url: str, modele: str, variable_cle: str | None,
                       entetes: dict[str, str] | None, ca: str | None) -> str:
    reference = f'"env:{variable_cle}"' if variable_cle else '"inutilise"  # marimo exige une clé, même factice'
    lignes = [f"[tool.marimo.ai.custom_providers.{nom}]", f"base_url = {json.dumps(base_url)}", "api_key = " + reference]
    if ca:
        lignes.append(f"ca_bundle_path = {json.dumps(ca)}")
    if entetes:
        lignes.append("extra_headers = { " + ", ".join(f"{json.dumps(k)} = {json.dumps(v)}" for k, v in entetes.items()) + " }")
    lignes += ["", "[tool.marimo.ai.models]", f'chat_model = "{nom}/{modele}"', f'edit_model = "{nom}/{modele}"',
               f'autocomplete_model = "{nom}/{modele}"', f'custom_models = ["{nom}/{modele}"]']
    return "\n".join(lignes)


def en_texte(essais: list[Essai], configuration: str) -> str:
    lignes = [f"[{'ok' if e.ok else 'non'}] {e.fonction}. {e.detail}" for e in essais]
    ok = {e.fonction.split(" (")[0] for e in essais if e.ok}
    if len(ok) == 4:
        verdict = "Tout passe : chat, autocomplétion, génération de cellule et outils (dont ceux de marimo-agent-kit)."
    elif "chat, mode Manual" in ok:
        verdict = ("Utilisable en mode Manual. Le contrat `[ai] rules` s'applique, mais ce qui est marqué \"non\" "
                   "échouera dans marimo.")
    else:
        verdict = "marimo ne pourra pas discuter avec ce point d'accès tel quel."
    return "\n".join([*lignes, "", verdict, "", "À mettre dans pyproject.toml (ou marimo.toml sans `tool.marimo.`) :", "",
                      configuration])


def cle_depuis(variable: str | None) -> str:
    if variable:
        valeur = os.environ.get(variable)
        if not valeur:
            raise SystemExit(f"La variable d'environnement {variable} est vide ou absente.")
        return valeur
    return "inutilise"
