# Source de cette documentation

- wigglystuff 0.6.0 (paquet installé), dépôt koaning/wigglystuff au commit 3b58e91 2026-11-16.
- Pages : `docs/reference/*.md`, démos : `demos/*.py`, sous licence MIT (`LICENSE-wigglystuff`).
- Signatures, docstrings et traitlets : lus dans le paquet installé, pas sur le site.
- 78 classes ou fonctions, 71 pages, 93 démos.

## Écarts entre la doc et le paquet

- keystroke.md : altKey, code, ctrlKey, key, metaKey, shiftKey, timestamp ne sont pas des traitlets du paquet (champs d'un dict, propriétés, ou doc en retard : vérifier avant usage)
- parallel-coords.md : filtered_indices, selected_indices ne sont pas des traitlets du paquet (champs d'un dict, propriétés, ou doc en retard : vérifier avant usage)
