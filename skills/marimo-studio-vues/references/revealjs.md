# Recette : un diaporama reveal.js

Modèle : `exemples/meteo-seattle/studio/meteo/briefing/` dans le dépôt, et l'exemple officiel
`exemples/studio/earthquakes/briefing/` de ce dossier (`DESIGN.md`, `src/App.tsx`).

Le starter `marimo-studio/react:reveal` crée un projet React avec `@revealjs/react` et une
diapositive par cellule. Remplace cette liste par une argumentation.

## Une diapositive, un constat

- Le titre de chaque diapositive est un message du notebook : `<h2>{d.messages.saison}</h2>`.
  Le surtitre nomme le thème, la figure prouve le titre.
- Sept diapositives au plus pour dix minutes : couverture, réponse, trois preuves, réglages en
  direct, méthode.
- Le pied rappelle l'état courant (période, seuil), calculé depuis les valeurs du notebook.

## Configuration du Deck

```tsx
<Deck
  className="studio-deck"
  deckRef={deck}
  config={{
    controls: true,
    keyboardCondition,
    progress: true,
    hash: false,
    width: 1440,
    height: 810,
    margin: 0.03,
    center: false,
    slideNumber: "c/t",
    scrollActivationWidth: 0,
    transition: "fade",
  }}
>
```

- Garde `scrollActivationWidth: 0` et `keyboardCondition` du starter : la vue de défilement de
  Reveal lit `sessionStorage`, absent du cadre isolé de Studio, et les flèches ne doivent pas
  changer de diapositive quand le lecteur manipule un contrôle.
- Garde `useSettledLayout()` du starter : il recentre le deck quand Studio émet
  `marimo-studio:idle`.
- `reveal.js/reveal.css` ne donne que la structure. Pose toi-même la police des titres
  (`font-family` sur `.reveal h1, .reveal h2`) et le fond (`.reveal-viewport`) : les variables
  `--r-heading-font` restent sans effet sans thème Reveal.

## Taille des graphiques et des contrôles

Le canevas 1440 × 810 est mis à l'échelle d'un bloc. Des composants dimensionnés en `rem` pour
une page paraissent petits : agrandis-les par `zoom` sur la diapositive, comme le conseille
l'`AGENTS.md` du starter pour les contrôles.

```css
.reveal.studio-deck section:not(.couverture) .graphique { zoom: 1.45; font-size: 16px; }
.reglage-direct { zoom: 1.6; }
```

## Téléphone tenu droit

Un canevas 16:9 sur 390 pixels de large donne un texte illisible. Comme l'exemple officiel,
rends les mêmes diapositives à la suite, sans `Deck`, quand l'écran est étroit et vertical :

```tsx
const PORTRAIT = "(max-width: 56rem) and (orientation: portrait)";
const portrait = useSyncExternalStore(abonner, () => matchMedia(PORTRAIT).matches, () => false);

{portrait ? <main className="lecteur"><Diapos d={d} /></main> : <Deck ...><Diapos d={d} /></Deck>}
```

La classe `.lecteur` remet chaque diapositive dans le flux, en une colonne. L'exemple le vérifie
par une capture à 390 × 844.

## Contrôler et exporter

```bash
uv run --no-project --with playwright python scripts/capturer.py "<URL>" --sortie diapo-2.png --ecran --largeur 1440 --hauteur 810 --attendre ".reveal .slides section" --touche ArrowRight --touche ArrowRight
uv run --no-project --with playwright python scripts/capturer.py "<URL>" --diapos 7 --pdf briefing.pdf --largeur 1440 --hauteur 810 --attendre ".reveal .slides section"
```

`--diapos 7` passe d'une diapositive à l'autre et réunit les captures dans un PDF d'une page par
diapositive. Les pages sont des images. L'impression `?print-pdf` de Reveal a été essayée sur
l'export : seule la première diapositive s'imprime, les autres pages sortent blanches, car
Reveal leur laisse l'attribut `hidden`.
