"""Le projet, son gestionnaire de paquets, et l'environnement que le kit donne à ce qu'il lance.

Le kit ne règle pas le réseau. pixi, le gestionnaire par défaut, et uv suivent leur propre
configuration : un miroir ou un dépôt interne se déclare chez eux, et tout ce que le kit lance en
profite. Les fichiers `mak.env` portent le proxy, l'autorité de certification et les consignes
pour l'agent. Ils se lisent dans cet ordre, le dernier l'emportant : celui livré dans le paquet,
celui de l'utilisateur, le plus proche du notebook, puis celui que nomme `MAK_CONFIG`. Une
variable déjà présente dans l'environnement du shell garde sa valeur.
"""

from __future__ import annotations

import os
import re
import shutil
import ssl
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

ICI = Path(__file__).resolve().parent
NOM_FICHIER = "mak.env"

VARIABLES = {
    "MARIMO_SKIP_UPDATE_CHECK": ("1", "pas de visite quotidienne à marimo.io au lancement de `marimo edit`"),
    "PYDANTIC_AI_NO_BANNER": ("1", "pas de bannière pydantic-ai dans le terminal (rien n'est envoyé, c'est de l'affichage)"),
}
ENV_SOBRE = {nom: valeur for nom, (valeur, _) in VARIABLES.items()}

VARIABLES_PROXY = ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "NO_PROXY")
VARIABLES_CA = ("SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "UV_SYSTEM_CERTS", "UV_NATIVE_TLS")
LIGNE_ENV = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")
SECRET = re.compile(r"KEY|TOKEN|SECRET|PASSW|CREDENTIAL|AUTH", re.I)


@dataclass
class Configuration:
    env: dict[str, str]
    origines: dict[str, str] = field(default_factory=dict)
    fichiers: list[tuple[str, Path]] = field(default_factory=list)
    contexte: list[str] = field(default_factory=list)
    problemes: list[str] = field(default_factory=list)

    def proxy(self) -> dict[str, str]:
        return {nom.lower(): valeur for nom in VARIABLES_PROXY if (valeur := _lire(self.env, nom))}

    def ouvreur(self, url: str, contexte: ssl.SSLContext | None = None) -> urllib.request.OpenerDirector:
        proxys = {cle.removesuffix("_proxy"): valeur for cle, valeur in self.proxy().items() if cle != "no_proxy"}
        if not proxys.get("https") and proxys.get("all"):
            proxys["https"] = proxys["all"]
        hote = urllib.parse.urlsplit(url).hostname or ""
        if urllib.request.proxy_bypass_environment(hote, {"no": self.proxy().get("no_proxy", "")}):
            proxys = {}
        gestionnaires: list[urllib.request.BaseHandler] = [
            urllib.request.ProxyHandler({k: v for k, v in proxys.items() if k != "all"})]
        if contexte is not None:
            gestionnaires.append(urllib.request.HTTPSHandler(context=contexte))
        return urllib.request.build_opener(*gestionnaires)

    def resume_proxy(self) -> str:
        proxy = self.proxy()
        cible = proxy.get("https_proxy") or proxy.get("all_proxy") or proxy.get("http_proxy", "")
        if not cible:
            return ""
        exclus = [h.strip() for h in proxy.get("no_proxy", "").split(",") if h.strip()]
        sauf = f", sauf pour {', '.join(exclus[:6])}" if exclus else ""
        if len(exclus) > 6:
            sauf += f" et {len(exclus) - 6} autres (`NO_PROXY`)"
        return masquer(cible) + sauf

    def fichier_ca(self) -> str | None:
        return _lire(self.env, "SSL_CERT_FILE") or _lire(self.env, "REQUESTS_CA_BUNDLE")


@dataclass
class Projet:
    manifeste: Path
    gestionnaire: str | None  # "pixi", "uv", ou None pour un pyproject.toml qui ne nomme ni l'un ni l'autre


def _lire(env: Mapping[str, str], nom: str) -> str:
    return env.get(nom) or env.get(nom.lower()) or ""


def masquer(texte: str) -> str:
    return re.sub(r"(https?://)[^/@\s]+@", r"\1***@", texte)


def valeur_affichable(nom: str, valeur: str) -> str:
    return "***" if SECRET.search(nom) else masquer(valeur)


def _accueil(env: Mapping[str, str]) -> Path:
    return Path(env.get("USERPROFILE") or env.get("HOME") or Path.home())


def dossier_etat(env: Mapping[str, str]) -> Path:
    if os.name == "nt" and env.get("LOCALAPPDATA"):
        return Path(env["LOCALAPPDATA"]) / "marimo-agent-kit"
    return Path(env.get("XDG_STATE_HOME") or _accueil(env) / ".local" / "state") / "marimo-agent-kit"


def _dossier_config(env: Mapping[str, str]) -> Path:
    if os.name == "nt" and env.get("APPDATA"):
        return Path(env["APPDATA"])
    return Path(env.get("XDG_CONFIG_HOME") or _accueil(env) / ".config")


def _dossiers(depuis: Path | None) -> list[Path]:
    depart = (depuis or Path.cwd()).resolve()
    return [depart if depart.is_dir() else depart.parent, *depart.parents]


def _le_plus_proche(depuis: Path, nom: str) -> Path | None:
    return next((dossier / nom for dossier in _dossiers(depuis) if (dossier / nom).is_file()), None)


def _manifeste_pixi(dossier: Path) -> Path | None:
    if (dossier / "pixi.toml").is_file():
        return dossier / "pixi.toml"
    pyproject = dossier / "pyproject.toml"
    if pyproject.is_file() and "[tool.pixi" in pyproject.read_text(encoding="utf-8", errors="replace"):
        return pyproject
    return None


def trouver_projet(depuis: Path | None = None) -> Projet | None:
    """Le manifeste le plus proche, et le gestionnaire qu'il déclare."""
    for dossier in _dossiers(depuis):
        if manifeste := _manifeste_pixi(dossier):
            return Projet(manifeste, "pixi")
        pyproject = dossier / "pyproject.toml"
        if pyproject.is_file():
            uv = "[tool.uv" in pyproject.read_text(encoding="utf-8", errors="replace") or (dossier / "uv.lock").is_file()
            return Projet(pyproject, "uv" if uv else None)
    return None


def _executable(environnement: Path, nom: str) -> Path | None:
    candidats = (environnement / "bin" / nom, environnement / "Scripts" / f"{nom}.exe", environnement / f"{nom}.exe")
    return next((c for c in candidats if c.is_file()), None)


def lanceur(nom: str, depuis: Path | None = None) -> list[str] | None:
    """La commande `marimo` ou `python` de l'environnement du projet qui contient marimo.

    L'environnement pixi par défaut passe avant `.venv`, et il se lance par `pixi run`, qui
    l'active : marimo y trouve pixi pour installer un paquet manquant, et `PIXI_PROJECT_MANIFEST`
    désigne le projet même quand marimo tourne depuis un autre dossier.
    """
    for dossier in _dossiers(depuis):
        manifeste = _manifeste_pixi(dossier)
        if manifeste and _executable(dossier / ".pixi" / "envs" / "default", "marimo") and shutil.which("pixi"):
            return ["pixi", "run", "--manifest-path", str(manifeste), nom]
        venv = dossier / ".venv"
        if _executable(venv, "marimo") and (outil := _executable(venv, nom)):
            return [str(outil)]
    return None


def lire_fichier_env(chemin: Path) -> tuple[list[tuple[str, str]], list[str]]:
    paires, problemes = [], []
    for numero, brute in enumerate(chemin.read_text(encoding="utf-8-sig").splitlines(), 1):
        ligne = brute.strip()
        if not ligne or ligne.startswith("#"):
            continue
        trouve = LIGNE_ENV.match(ligne)
        if not trouve:
            problemes.append(f"{chemin}:{numero} : ligne illisible, le format attendu est NOM=valeur")
            continue
        nom, valeur = trouve.group(1), trouve.group(2).strip()
        if len(valeur) >= 2 and valeur[0] == valeur[-1] and valeur[0] in "\"'":
            valeur = valeur[1:-1]
        paires.append((nom, valeur))
    return paires, problemes


def fichiers_de_config(depuis: Path, env: Mapping[str, str]) -> tuple[list[tuple[str, Path]], list[str]]:
    candidats: list[tuple[str, Path | None]] = [
        ("paquet", ICI / NOM_FICHIER),
        ("utilisateur", _dossier_config(env) / "marimo-agent-kit" / NOM_FICHIER),
        ("projet", _le_plus_proche(depuis, NOM_FICHIER)),
    ]
    problemes = []
    if env.get("MAK_CONFIG"):
        explicite = Path(env["MAK_CONFIG"]).expanduser()
        candidats.append(("MAK_CONFIG", explicite))
        if not explicite.is_file():
            problemes.append(f"MAK_CONFIG nomme {explicite}, qui n'existe pas")
    vus, retenus = set(), []
    for origine, chemin in candidats:
        if chemin is not None and chemin.is_file() and chemin.resolve() not in vus:
            vus.add(chemin.resolve())
            retenus.append((origine, chemin))
    return retenus, problemes


def charger(depuis: Path | None = None, env: Mapping[str, str] | None = None) -> Configuration:
    shell = dict(os.environ if env is None else env)
    depuis = depuis or Path.cwd()
    fichiers, problemes = fichiers_de_config(depuis, shell)
    fusion: dict[str, tuple[str, str]] = {}
    contexte: list[str] = []
    for origine, chemin in fichiers:
        paires, defauts = lire_fichier_env(chemin)
        problemes += defauts
        for nom, valeur in paires:
            if nom == "MAK_CONTEXTE":
                contexte.append(valeur)
            else:
                fusion[nom] = (valeur, f"{origine} ({chemin})")
    if shell.get("MAK_CONTEXTE"):
        contexte.append(shell["MAK_CONTEXTE"])
    resultat, origines = dict(shell), {}
    for nom, (valeur, origine) in fusion.items():
        if nom in shell:
            origines[nom] = "shell (le fichier est ignoré pour cette variable)"
        else:
            resultat[nom] = valeur
            origines[nom] = origine
    resultat.update(ENV_SOBRE)
    return Configuration(env=resultat, origines=origines, fichiers=fichiers, contexte=contexte, problemes=problemes)


def env_sobre(depuis: Path | None = None) -> dict[str, str]:
    return charger(depuis).env


def ligne_paquets(projet: Projet | None) -> str:
    if projet is None:
        return ("Aucun projet trouvé. pixi est le gestionnaire conseillé : `pixi init --format pyproject`, puis "
                "`pixi add marimo`. Demande à l'utilisateur avant de créer le projet.")
    if projet.gestionnaire == "pixi":
        return (f"pixi gère le projet ({projet.manifeste.name}). Ajoute un paquet par `pixi add <paquet>`, ou "
                "`pixi add --pypi <paquet>` s'il manque aux canaux conda.")
    if projet.gestionnaire == "uv":
        return f"uv gère le projet ({projet.manifeste.name}). Ajoute un paquet par `uv add <paquet>`."
    return (f"{projet.manifeste.name} ne déclare ni pixi ni uv. `pixi init --format pyproject` y ajoute pixi, le "
            "gestionnaire conseillé. Demande à l'utilisateur avant.")


def contexte_agent(config: Configuration, projet: Projet | None = None) -> str:
    lignes = ["## Paquets du projet (marimo-agent-kit)", "", f"- Paquets : {ligne_paquets(projet)}"]
    if config.resume_proxy():
        lignes.append(f"- Proxy : {config.resume_proxy()}.")
    certificats = [f"{nom}={valeur_affichable(nom, v)}" for nom in VARIABLES_CA if (v := config.env.get(nom))]
    if certificats:
        lignes.append("- Certificats : " + ", ".join(certificats) + ".")
    lignes += [
        "",
        "À respecter :",
        "1. Installe un paquet seulement par le gestionnaire du projet. Sa configuration choisit les dépôts : ne passe "
        "ni `--index-url`, ni `--extra-index-url`, ni `--default-index`. N'utilise ni `pip install`, ni une source "
        "`git+`, ni `npx`.",
        "2. Lis la documentation de la version installée : `mak api <symbole>` pour marimo et ses règles de lint "
        "(`mak api MB002`), `mak widgets` pour wigglystuff, les dossiers `references/` des skills.",
        "3. Si un paquet ne s'installe pas, ne contourne pas : dis à l'utilisateur ce qui manque.",
    ]
    if config.contexte:
        lignes += ["", "Consignes du projet :", *[f"- {phrase}" for phrase in config.contexte]]
    if config.problemes:
        lignes += ["", "Configuration à corriger (à signaler à l'utilisateur) :", *[f"- {p}" for p in config.problemes]]
    return "\n".join(lignes)


def detail_configuration(config: Configuration, projet: Projet | None = None, marimo: list[str] | None = None) -> str:
    lignes = []
    if config.fichiers:
        lignes.append("Fichiers lus, le dernier l'emportant :")
        lignes += [f"  {origine} : {chemin}" for origine, chemin in config.fichiers]
    else:
        lignes.append(f"Aucun fichier {NOM_FICHIER} : ni dans le paquet, ni chez l'utilisateur, ni près du notebook.")
    if config.origines:
        lignes += ["", "Variables des fichiers :"]
        lignes += [f"  {nom}={valeur_affichable(nom, config.env.get(nom, ''))}  ← {origine}"
                   for nom, origine in sorted(config.origines.items())]
    lignes += ["", "Posées par le kit sur ce qu'il lance :", *[f"  {nom}={valeur}" for nom, valeur in ENV_SOBRE.items()]]
    lignes += ["", f"Projet : {projet.manifeste if projet else 'aucun'}", f"Paquets : {ligne_paquets(projet)}",
               f"marimo : {' '.join(marimo) if marimo else 'pas dans un environnement du projet'}"]
    if config.problemes:
        lignes += ["", "À corriger :", *[f"  {p}" for p in config.problemes]]
    return "\n".join(lignes)
