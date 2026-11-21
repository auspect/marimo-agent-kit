"""Ce que le kit laisse sortir du poste, et l'environnement qu'il donne à ce qu'il lance.

Le réseau est coupé par défaut, sauf vers les dépôts internes que uv ou pixi déclarent déjà.
`MAK_RESEAU` choisit le mode : `interne` (défaut), `aucun` ou `public`. Les fichiers `mak.env`
portent le proxy, l'autorité de certification et toute variable propre au pack. Ils se lisent
dans cet ordre, le dernier l'emportant : celui livré dans le paquet, celui de l'utilisateur,
le plus proche du notebook, puis celui que nomme `MAK_CONFIG`. Une variable déjà présente
dans l'environnement du shell garde sa valeur.
"""

from __future__ import annotations

import os
import re
import ssl
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ICI = Path(__file__).resolve().parent
NOM_FICHIER = "mak.env"
MODES = ("interne", "aucun", "public")

VARIABLES = {
    "MARIMO_SKIP_UPDATE_CHECK": ("1", "pas de visite quotidienne à marimo.io au lancement de `marimo edit`"),
    "PYDANTIC_AI_NO_BANNER": ("1", "pas de bannière pydantic-ai dans le terminal (rien n'est envoyé, c'est de l'affichage)"),
}
ENV_SOBRE = {nom: valeur for nom, (valeur, _) in VARIABLES.items()}

HOTES_PUBLICS = ("pypi.org", "pythonhosted.org", "anaconda.org", "anaconda.com", "prefix.dev", "github.com",
                 "githubusercontent.com", "astral.sh", "npmjs.org", "marimo.io")
VARIABLES_PROXY = ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "NO_PROXY")
VARIABLES_CA = ("SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "UV_SYSTEM_CERTS", "UV_NATIVE_TLS")
VARIABLES_INDEX_UV = ("UV_DEFAULT_INDEX", "UV_INDEX_URL", "UV_INDEX", "UV_EXTRA_INDEX_URL", "UV_FIND_LINKS")
CLES_INDEX_UV = {"index-url", "default-index", "extra-index-url", "url", "find-links"}
LIGNE_ENV = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")
LIGNE_TOML = re.compile(r'^\s*"?([\w./:-]+)"?\s*=\s*(.*)$')
URL = re.compile(r"https?://[^\s\"'\],]+")
SECRET = re.compile(r"KEY|TOKEN|SECRET|PASSW|CREDENTIAL|AUTH", re.I)


@dataclass
class Source:
    url: str
    ou: str

    @property
    def interne(self) -> bool:
        hote = (urllib.parse.urlsplit(self.url).hostname or "").lower()
        return bool(hote) and not any(hote == p or hote.endswith("." + p) for p in HOTES_PUBLICS)


@dataclass
class Configuration:
    mode: Literal["interne", "aucun", "public"]
    env: dict[str, str]
    origines: dict[str, str] = field(default_factory=dict)
    fichiers: list[tuple[str, Path]] = field(default_factory=list)
    contexte: list[str] = field(default_factory=list)
    problemes: list[str] = field(default_factory=list)
    depots_uv: list[Source] = field(default_factory=list)
    miroirs_python: list[Source] = field(default_factory=list)
    depots_pixi: list[Source] = field(default_factory=list)

    @property
    def uv_interne(self) -> bool:
        return bool(self.depots_uv) and all(s.interne for s in self.depots_uv)

    @property
    def python_interne(self) -> bool:
        return bool(self.miroirs_python) and all(s.interne for s in self.miroirs_python)

    @property
    def pixi_interne(self) -> bool:
        return bool(self.depots_pixi) and all(s.interne for s in self.depots_pixi)

    @property
    def uv_en_ligne(self) -> bool:
        return self.env.get("UV_OFFLINE") != "1"

    def pixi_permis(self) -> tuple[bool, str]:
        if self.mode == "public":
            return True, ""
        if self.mode == "aucun":
            return False, "mode aucun : pixi n'a pas de mode hors ligne vérifié par le kit"
        if not self.pixi_interne:
            return False, "pixi n'a pas de miroir interne déclaré : il irait sur conda.anaconda.org ou prefix.dev"
        return True, ""

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


def _lire(env: Mapping[str, str], nom: str) -> str:
    return env.get(nom) or env.get(nom.lower()) or ""


def masquer(texte: str) -> str:
    return re.sub(r"(https?://)[^/@\s]+@", r"\1***@", texte)


def valeur_affichable(nom: str, valeur: str) -> str:
    return "***" if SECRET.search(nom) else masquer(valeur)


def _accueil(env: Mapping[str, str]) -> Path:
    return Path(env.get("USERPROFILE") or env.get("HOME") or Path.home())


def _dossier_config(env: Mapping[str, str]) -> Path:
    if os.name == "nt" and env.get("APPDATA"):
        return Path(env["APPDATA"])
    return Path(env.get("XDG_CONFIG_HOME") or _accueil(env) / ".config")


def _le_plus_proche(depart: Path, nom: str) -> Path | None:
    depart = depart.resolve()
    for dossier in [depart if depart.is_dir() else depart.parent, *depart.parents]:
        if (dossier / nom).is_file():
            return dossier / nom
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


def _sources_toml(chemin: Path, cles: set[str], section: str = "", miroirs: bool = False) -> tuple[list[Source], list[Source]]:
    # Lu ligne à ligne, sans tomllib, qui manque à Python 3.10.
    index, pythons, courante, cle = [], [], "", ""
    try:
        texte = chemin.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], []
    for ligne in texte.splitlines():
        brute = ligne.strip()
        if not brute or brute.startswith("#"):
            continue
        if brute.startswith("["):
            courante = brute.strip("[] ")
            continue
        if section and not courante.startswith(section):
            continue
        trouve = LIGNE_TOML.match(brute)
        if trouve:
            cle, valeur = trouve.group(1), trouve.group(2)
        else:
            valeur = brute
        if courante.endswith("mirrors") and miroirs:
            index += [Source(u, str(chemin)) for u in URL.findall(valeur)]
        elif cle == "python-install-mirror":
            pythons += [Source(u, str(chemin)) for u in URL.findall(valeur)]
        elif cle in cles:
            index += [Source(u, str(chemin)) for u in URL.findall(valeur)]
    return index, pythons


def _sources_uv(depuis: Path, env: Mapping[str, str]) -> tuple[list[Source], list[Source]]:
    index = [Source(u, nom) for nom in VARIABLES_INDEX_UV for u in URL.findall(env.get(nom, ""))]
    pythons = [Source(u, "UV_PYTHON_INSTALL_MIRROR") for u in URL.findall(env.get("UV_PYTHON_INSTALL_MIRROR", ""))]
    if env.get("UV_NO_CONFIG"):
        return index, pythons
    fichiers: list[tuple[Path, str]] = []
    if env.get("UV_CONFIG_FILE"):
        fichiers.append((Path(env["UV_CONFIG_FILE"]).expanduser(), ""))
    depart = depuis.resolve()
    for dossier in [depart if depart.is_dir() else depart.parent, *depart.parents]:
        if (dossier / "uv.toml").is_file():
            fichiers.append((dossier / "uv.toml", ""))
            break
        pyproject = dossier / "pyproject.toml"
        if pyproject.is_file() and "[tool.uv" in pyproject.read_text(encoding="utf-8", errors="replace"):
            fichiers.append((pyproject, "tool.uv"))
            break
    fichiers.append((_dossier_config(env) / "uv" / "uv.toml", ""))
    systeme = Path(env.get("PROGRAMDATA", "C:/ProgramData")) / "uv" / "uv.toml" if os.name == "nt" else Path("/etc/uv/uv.toml")
    fichiers.append((systeme, ""))
    for chemin, section in fichiers:
        if chemin.is_file():
            i, p = _sources_toml(chemin, CLES_INDEX_UV, section)
            index += i
            pythons += p
    return index, pythons


def _sources_pixi(depuis: Path, env: Mapping[str, str]) -> list[Source]:
    candidats = [_accueil(env) / ".pixi" / "config.toml", _dossier_config(env) / "pixi" / "config.toml"]
    if env.get("PIXI_HOME"):
        candidats.insert(0, Path(env["PIXI_HOME"]) / "config.toml")
    if os.name != "nt":
        candidats.append(Path("/etc/pixi/config.toml"))
    projet = _le_plus_proche(depuis, ".pixi/config.toml")
    if projet is not None:
        candidats.append(projet)
    sources, vus = [], set()
    for chemin in candidats:
        if chemin.is_file() and chemin.resolve() not in vus:
            vus.add(chemin.resolve())
            sources += _sources_toml(chemin, {"default-channels", "index-url", "extra-index-urls", "channel-alias"},
                                     miroirs=True)[0]
    return sources


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
    demande = resultat.get("MAK_RESEAU", "interne").strip().lower()
    if demande not in MODES:
        problemes.append(f"MAK_RESEAU={demande!r} est inconnu ; le kit prend le mode le plus strict, aucun")
        demande = "aucun"
    depots_uv, miroirs_python = _sources_uv(depuis, resultat)
    config = Configuration(mode=demande, env=resultat, origines=origines, fichiers=fichiers, contexte=contexte,
                           problemes=problemes, depots_uv=depots_uv, miroirs_python=miroirs_python,
                           depots_pixi=_sources_pixi(depuis, resultat))
    resultat.update(ENV_SOBRE)
    if config.mode != "public":
        if config.mode == "aucun" or not config.uv_interne:
            resultat["UV_OFFLINE"] = "1"
        if config.mode == "aucun" or not config.python_interne:
            resultat["UV_PYTHON_DOWNLOADS"] = "never"
    return config


def env_sobre(depuis: Path | None = None) -> dict[str, str]:
    return charger(depuis).env


def _hotes(sources: list[Source]) -> str:
    hotes = sorted({urllib.parse.urlsplit(s.url).hostname or s.url for s in sources})
    return ", ".join(hotes)


def _ou(sources: list[Source]) -> str:
    return ", ".join(sorted({s.ou for s in sources}))


def contexte_agent(config: Configuration) -> str:
    lignes = ["## Réseau du poste (marimo-agent-kit)", ""]
    publics_uv = [s for s in config.depots_uv if not s.interne]
    if config.mode == "public":
        lignes.append("Mode public : le kit ne restreint pas le réseau. Les outils peuvent contacter le web.")
    elif config.mode == "aucun":
        lignes.append("Mode aucun : aucun accès réseau. uv ne lit que son cache (`UV_OFFLINE=1`) et ne télécharge pas "
                      "de Python. Un paquet absent du cache ne s'installe pas.")
    else:
        lignes.append("Mode interne : seuls les dépôts internes ci-dessous sont contactés. Rien ne part sur le web public.")
    lignes.append("")
    if config.uv_en_ligne and config.depots_uv:
        lignes.append(f"- Paquets Python : uv passe par {_hotes(config.depots_uv)}, déclaré dans {_ou(config.depots_uv)}.")
    elif not config.uv_en_ligne:
        if config.mode == "aucun" or config.uv_interne:
            cause = "uv est hors ligne (`UV_OFFLINE=1`)"
        elif publics_uv:
            cause = f"uv consulte aussi un dépôt public ({_hotes(publics_uv)}, dans {_ou(publics_uv)}), donc le kit le coupe du réseau"
        else:
            cause = "uv n'a pas de dépôt interne déclaré, donc le kit le coupe du réseau"
        lignes.append(f"- Paquets Python : {cause}. Il ne lit que son cache.")
    if config.mode != "public":
        if config.env.get("UV_PYTHON_DOWNLOADS") == "never":
            lignes.append("- Python : uv ne télécharge aucun interpréteur. Utilise un Python déjà installé.")
        else:
            lignes.append(f"- Python : uv télécharge les interpréteurs depuis {_hotes(config.miroirs_python)}.")
        permis, raison = config.pixi_permis()
        if permis:
            lignes.append(f"- Paquets conda : pixi passe par {_hotes(config.depots_pixi)}.")
        else:
            lignes.append(f"- Paquets conda : {raison}. Le kit n'exécute pas les notebooks en bac à sable pixi.")
    if config.resume_proxy():
        lignes.append(f"- Proxy : {config.resume_proxy()}.")
    certificats = [f"{nom}={valeur_affichable(nom, v)}" for nom in VARIABLES_CA if (v := config.env.get(nom))]
    if certificats:
        lignes.append("- Certificats : " + ", ".join(certificats) + ".")
    if config.mode != "public":
        lignes += [
            "",
            "À respecter :",
            "1. Installe un paquet seulement par uv ou pixi, avec la configuration en place. Ne passe jamais "
            "`--index-url`, `--extra-index-url` ni `--default-index`. N'utilise ni `pip install`, ni une source "
            "`git+https`, ni `npx`.",
            "2. Ne va pas chercher sur le web une page de documentation, un script ou un modèle. La documentation est "
            "sur le poste : `mak api <symbole>` pour marimo et ses règles de lint (`mak api MB002`), `mak widgets` pour "
            "wigglystuff, les dossiers `references/` des skills.",
            "3. Si un paquet ou une page manque, arrête-toi et dis à l'utilisateur ce qui manque. Ne contourne pas.",
        ]
        options = [o for o, actif in (("--offline", config.env.get("UV_OFFLINE") == "1"),
                                      ("--no-python-downloads", config.env.get("UV_PYTHON_DOWNLOADS") == "never")) if actif]
        if options:
            lignes.append(f"4. Les commandes uv et uvx que tu lances toi-même ne passent pas par le kit : ajoute-leur "
                          f"{' et '.join(f'`{o}`' for o in options)}.")
    if config.contexte:
        lignes += ["", "Consignes du poste :", *[f"- {phrase}" for phrase in config.contexte]]
    if config.problemes:
        lignes += ["", "Configuration à corriger (à signaler à l'utilisateur) :", *[f"- {p}" for p in config.problemes]]
    return "\n".join(lignes)


def detail_configuration(config: Configuration) -> str:
    lignes = [f"Mode réseau : {config.mode}", ""]
    if config.fichiers:
        lignes.append("Fichiers lus, le dernier l'emportant :")
        lignes += [f"  {origine} : {chemin}" for origine, chemin in config.fichiers]
    else:
        lignes.append(f"Aucun fichier {NOM_FICHIER} : ni dans le paquet, ni chez l'utilisateur, ni près du notebook.")
    if config.origines:
        lignes += ["", "Variables des fichiers :"]
        lignes += [f"  {nom}={valeur_affichable(nom, config.env.get(nom, ''))}  ← {origine}"
                   for nom, origine in sorted(config.origines.items())]
    forcees = {nom: config.env[nom] for nom in ("UV_OFFLINE", "UV_PYTHON_DOWNLOADS", *ENV_SOBRE) if nom in config.env}
    lignes += ["", "Posées par le kit sur ce qu'il lance :", *[f"  {nom}={valeur}" for nom, valeur in forcees.items()]]
    for titre, sources in (("Dépôts uv", config.depots_uv), ("Miroirs de Python pour uv", config.miroirs_python),
                           ("Dépôts pixi", config.depots_pixi)):
        lignes.append("")
        if sources:
            lignes.append(f"{titre} :")
            lignes += [f"  {'interne' if s.interne else 'PUBLIC '} {masquer(s.url)}  ← {s.ou}" for s in sources]
        else:
            lignes.append(f"{titre} : aucun déclaré.")
    if config.problemes:
        lignes += ["", "À corriger :", *[f"  {p}" for p in config.problemes]]
    return "\n".join(lignes)
