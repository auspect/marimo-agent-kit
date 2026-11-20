"""Le rapport dans le notebook lui-même : une cellule `mak.audit()` montre ce qui cloche.

C'est la face humaine du kit : tu vois ce que l'agent a laissé passer, et tu as le message
à lui renvoyer. La cellule lit le fichier sur le disque ; relance-la après une modification.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .verifier import verifier

COULEUR = {"erreur": "danger", "avertissement": "warn"}


def _fichier_appelant() -> Path | None:
    cadre = sys._getframe(2)
    nom = cadre.f_globals.get("__file__")
    return Path(nom) if nom else None


def message_pour_agent(rapport) -> str:
    lignes = [f"Corrige ces problèmes dans {Path(rapport.chemin).name}, puis relance `mak verifier {rapport.chemin}` :"]
    for d in rapport.diagnostics:
        if d.gravite == "conseil":
            continue
        ou = f"{d.etiquette}, ligne {d.ligne}" if d.ligne else d.etiquette
        lignes.append(f"- {d.code} ({ou}) : {d.message} Correction : {d.correction}")
    return "\n".join(lignes)


def audit(chemin: str | Path | None = None, executer: bool = False, conseils: bool = True):
    """Vérifie un notebook (par défaut celui qui appelle) et rend une vue marimo du rapport."""
    import marimo as mo

    chemin = Path(chemin) if chemin else _fichier_appelant()
    if chemin is None:
        return mo.callout(mo.md("Donne le chemin du notebook : `mak.audit(\"notebook.py\")`."), kind="warn")
    rapport = verifier(chemin, executer=executer)
    compte = rapport.compte()
    etapes = " · ".join(f"{e.nom} : {e.etat}" for e in rapport.etapes)
    resume = mo.md(
        f"**{chemin.name} — {rapport.statut}.** {compte['erreur']} erreur(s), {compte['avertissement']} "
        f"avertissement(s), {compte['conseil']} conseil(s).\n\n<small>{etapes}</small>"
    )
    genre = "danger" if compte["erreur"] else "warn" if compte["avertissement"] else "success"
    lignes = [
        {"gravité": d.gravite, "règle": f"{d.code} {d.nom}", "où": d.etiquette, "ligne": d.ligne or "",
         "constat": d.message, "correction": d.correction}
        for d in rapport.diagnostics if conseils or d.gravite != "conseil"
    ]
    morceaux = [mo.callout(resume, kind=genre)]
    if lignes:
        morceaux.append(mo.ui.table(lignes, selection=None, pagination=True, page_size=10, show_column_summaries=False,
                                    label="Constats"))
    if compte["erreur"] or compte["avertissement"]:
        morceaux.append(mo.accordion({"Message à renvoyer à ton agent": mo.md(f"```text\n{message_pour_agent(rapport)}\n```")}))
    return mo.vstack(morceaux)
