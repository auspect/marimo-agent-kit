"""`mak` : la ligne de commande du kit.

    mak verifier notebook.py [--sans-execution] [--conseils] [--json]
    mak cellules --notebook notebook.py < cellules.json     (liste JSON de corps de cellules)
    mak api mo.ui.slider            mak api --chercher cache
    mak regles [--reference]
    mak sonde-llm https://llm.interne/v1 mon-modele --cle-env VARIABLE   (LLM pour l'assistant de marimo)
    mak mcp                         serveur MCP en entrée/sortie standard
    mak hook [--executer]           hook après écriture (Claude Code, Copilot)
    mak installer --skill agents --marimo [--hook-claude] [--mcp-claude] [--appliquer]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__


def _codes(texte: str | None) -> set[str] | None:
    return {c.strip() for c in texte.split(",") if c.strip()} if texte else None


def main(argv: list[str] | None = None) -> int:
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")
    parseur = argparse.ArgumentParser(prog="mak", description="Outils pour que les agents écrivent de bons notebooks marimo.")
    parseur.add_argument("--version", action="version", version=f"marimo-agent-kit {__version__}")
    sous = parseur.add_subparsers(dest="commande", required=True)

    p = sous.add_parser("verifier", help="marimo check --strict, règles d'agent, exécution")
    p.add_argument("notebooks", nargs="+", type=Path)
    p.add_argument("--sans-execution", action="store_true", help="ne pas exécuter les cellules")
    p.add_argument("--conseils", action="store_true", help="lister aussi les conseils de lisibilité")
    p.add_argument("--json", action="store_true")
    p.add_argument("--selection", help="codes ou préfixes à garder, ex. AG0,AG101")
    p.add_argument("--ignorer", help="codes ou préfixes à écarter, ex. AG203")
    p.add_argument("--marimo", help="commande qui lance marimo (défaut : celle du projet, sinon uvx marimo)")
    p.add_argument("--delai", type=int, default=300, help="secondes avant d'abandonner l'exécution")
    p.add_argument("--bac-a-sable", choices=["auto", "uv", "pixi", "non"], default="auto")

    p = sous.add_parser("cellules", help="vérifier des corps de cellules avant de les insérer")
    p.add_argument("entree", nargs="?", default="-", help="fichier JSON (liste de chaînes), ou - pour l'entrée standard")
    p.add_argument("--notebook", type=Path, help="le notebook où les cellules iront")
    p.add_argument("--texte", action="store_true", help="l'entrée est le corps d'une seule cellule, pas du JSON")
    p.add_argument("--conseils", action="store_true")
    p.add_argument("--json", action="store_true")

    p = sous.add_parser("api", help="signature et documentation d'un symbole de marimo installé")
    p.add_argument("symbole")
    p.add_argument("--chercher", action="store_true", help="chercher le mot dans les noms et les résumés")
    p.add_argument("--json", action="store_true")

    p = sous.add_parser("regles", help="le contrat d'écriture (court) ou la référence des règles")
    p.add_argument("--reference", action="store_true")

    p = sous.add_parser("sonde-llm", help="ce qu'un LLM compatible OpenAI accepte des requêtes de marimo")
    p.add_argument("base_url", help="ex. https://llm.interne/v1 (marimo y ajoute /chat/completions)")
    p.add_argument("modele", help="nom du modèle tel que le point d'accès l'attend")
    p.add_argument("--cle-env", help="variable d'environnement qui contient la clé (jamais la clé elle-même)")
    p.add_argument("--entete", action="append", default=[], metavar="NOM:VALEUR", help="en-tête en plus (répétable)")
    p.add_argument("--ca", help="fichier de certificats de l'entreprise (ca_bundle_path de marimo)")
    p.add_argument("--sans-verification-tls", action="store_true", help="ne vérifier aucun certificat (essai seulement)")
    p.add_argument("--nom", default="interne", help="nom du fournisseur dans marimo")
    p.add_argument("--delai", type=int, default=60)

    sous.add_parser("mcp", help="serveur MCP en entrée/sortie standard")

    p = sous.add_parser("hook", help="hook après écriture pour Claude Code ou Copilot")
    p.add_argument("--executer", action="store_true", help="exécuter aussi les cellules (plus lent)")

    p = sous.add_parser("installer", help="poser le skill, la configuration de marimo, le hook ou le serveur MCP")
    p.add_argument("--dossier", type=Path, default=Path("."))
    p.add_argument("--skill", choices=["agents", "claude", "github"])
    p.add_argument("--marimo", action="store_true", help="contrat et serveur MCP dans [tool.marimo] de pyproject.toml")
    p.add_argument("--hook-claude", action="store_true")
    p.add_argument("--mcp-claude", action="store_true")
    p.add_argument("--source", help="d'où uvx installe le kit (chemin ou git+https://…#subdirectory=marimo-agent-kit)")
    p.add_argument("--remplacer", action="store_true", help="remplacer les fichiers du skill qui diffèrent")
    p.add_argument("--appliquer", action="store_true", help="écrire ; sans lui, l'installateur dit seulement ce qu'il ferait")

    args = parseur.parse_args(argv)

    if args.commande == "verifier":
        from .verifier import verifier

        rapports = [verifier(n, executer=not args.sans_execution, marimo=args.marimo, delai=args.delai,
                             selection=_codes(args.selection), ignorer=_codes(args.ignorer),
                             bac_a_sable=None if args.bac_a_sable == "non" else args.bac_a_sable)
                    for n in args.notebooks]
        if args.json:
            print(json.dumps([r.en_dict(conseils=args.conseils) for r in rapports], ensure_ascii=False, indent=1))
        else:
            print("\n\n".join(r.en_texte(conseils=args.conseils) for r in rapports))
        return 0 if all(r.ok for r in rapports) else 1

    if args.commande == "cellules":
        from .verifier_cellules import verifier_cellules

        brut = sys.stdin.read() if args.entree == "-" else Path(args.entree).read_text(encoding="utf-8")
        cellules = [brut] if args.texte else json.loads(brut)
        if not isinstance(cellules, list) or not all(isinstance(c, str) for c in cellules):
            print("L'entrée doit être une liste JSON de chaînes (ou utilise --texte).", file=sys.stderr)
            return 2
        rapport = verifier_cellules(cellules, args.notebook)
        print(json.dumps(rapport.en_dict(args.conseils), ensure_ascii=False, indent=1) if args.json
              else rapport.en_texte(args.conseils))
        return 0 if rapport.ok else 1

    if args.commande == "api":
        from .api import en_texte, interroger

        resultat = interroger(args.symbole, "chercher" if args.chercher else "decrire")
        print(json.dumps(resultat, ensure_ascii=False, indent=1) if args.json else en_texte(resultat))
        return 1 if "erreur" in resultat or "introuvable" in resultat else 0

    if args.commande == "regles":
        from .contrat import contrat_court, reference_regles

        print(reference_regles() if args.reference else contrat_court(), end="")
        return 0

    if args.commande == "sonde-llm":
        from .sonde_llm import bloc_configuration, cle_depuis, en_texte, sonder

        entetes = dict(e.split(":", 1) for e in args.entete if ":" in e)
        entetes = {k.strip(): v.strip() for k, v in entetes.items()}
        essais = sonder(args.base_url, args.modele, cle_depuis(args.cle_env), entetes, args.ca,
                        not args.sans_verification_tls, args.delai)
        print(en_texte(essais, bloc_configuration(args.nom, args.base_url, args.modele, args.cle_env,
                                                  {k: v for k, v in entetes.items() if k.lower() != "authorization"},
                                                  args.ca)))
        return 0 if all(e.ok for e in essais) else 1

    if args.commande == "mcp":
        from .mcp_serveur import servir

        servir()
        return 0

    if args.commande == "hook":
        from .hook import principal

        return principal(executer=args.executer)

    if args.commande == "installer":
        from .installer import installer

        actions = installer(args.dossier.resolve(), args.skill, args.marimo, args.hook_claude, args.mcp_claude,
                            args.appliquer, args.remplacer, args.source)
        if not actions:
            print("Rien de demandé : choisis --skill, --marimo, --hook-claude ou --mcp-claude.")
            return 2
        for action in actions:
            print(f"[{action.etat}] {action.cible}" + (f"\n    {action.detail}" if action.detail else ""))
        if not args.appliquer:
            print("\nRien n'a été écrit. Relance avec --appliquer pour le faire.")
        return 0
    return 2
