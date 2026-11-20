"""marimo-agent-kit : ce qu'il faut à un agent pour écrire des notebooks marimo justes et lisibles.

- `verifier(chemin)` : marimo check --strict, les règles d'agent, l'exécution ;
- `verifier_cellules(codes, notebook)` : des cellules jugées avant d'être insérées ;
- `audit()` : le rapport, rendu dans une cellule du notebook.
"""

__version__ = "0.1.0"

from .audit import audit  # noqa: E402
from .verifier import verifier  # noqa: E402
from .verifier_cellules import verifier_cellules  # noqa: E402

__all__ = ["__version__", "audit", "verifier", "verifier_cellules"]
