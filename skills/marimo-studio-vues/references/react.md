# Recette : une page React

Modèle : `exemples/meteo-seattle/studio/meteo/grand-public/` dans le dépôt, et l'exemple officiel
`exemples/studio/earthquakes/briefing/src/App.tsx` de ce dossier pour une application plus riche.

## Structure du projet

```text
grand-public/
  AGENTS.md            gabarit de Studio, section « Project intent » remplie
  DESIGN.md            public, tâche, système visuel, largeurs vérifiées
  deno.json, deno.lock dépendances figées ; Studio construit avec le lockfile gelé
  states.yaml          états préparés pour l'export statique
  src/
    App.tsx            hôtes de valeurs, états de chargement et d'erreur, composition
    components/        graphiques, avec leur feuille de style
    lib/donnees.ts     types de la valeur du notebook
    lib/format.ts      mise en forme française (Intl), aucune donnée
    lib/use-marimo-value.ts, marimo-studio.d.ts   fournis par le starter, inchangés
    index.html, main.tsx, style.css
```

`src/` peut grandir librement : Studio découvre les fichiers importés. Un composant partagé entre
deux vues se copie dans chacune : une vue ne construit qu'à partir de ses propres fichiers
(`module-path-outside-project` sinon).

## Lire les valeurs du notebook

Un hôte `mo-value` reste écrit dans le JSX, pour que Studio autorise le sélecteur. Le hook du
starter le relie à l'état React :

```tsx
const donnees = useMarimoValue<DonneesVues>("donnees_vues");
const jours = useMarimoValue<MarimoTable<Jour>>("jours_vue");
const enAttente = donnees.value === undefined && !donnees.error;

return (
  <div className="page" aria-busy={enAttente}>
    <span id="donnees" ref={donnees.hostRef} hidden mo-value="donnees_vues" />
    <span id="jours" ref={jours.hostRef} hidden mo-value="jours_vue" />
    <div className="reglages"><marimo-cell name="controles" /></div>
    {donnees.error ? <p role="alert">{donnees.error.message}</p> : null}
    {enAttente ? <p role="status">Chargement des relevés…</p> : null}
    {donnees.value ? <Page d={donnees.value} jours={jours.value?.toArray() ?? []} /> : null}
  </div>
);
```

- Un dictionnaire arrive tel quel. Un DataFrame arrive comme un tableau Arrow : `toArray()` donne
  des objets ligne, `getChild("colonne")` une colonne.
- Les contrôles du notebook se projettent avec `<marimo-cell name="controles" />`. Changer un
  contrôle relance le notebook, ou charge l'état préparé dans un export, puis met à jour toutes
  les valeurs.
- Thème des sorties natives : variables CSS sur l'hôte, comme `--marimo-cell-font` et
  `--marimo-cell-accent`.

## Graphiques

L'exemple dessine ses graphiques en SVG et en CSS, sans bibliothèque : un calendrier d'un carré
par jour, des barres mensuelles, des jauges appariées. Pour D3 ou Observable Plot, suis la
section « Add dependencies » de l'`AGENTS.md` de la vue : la mise à jour de `deno.json` et de
`deno.lock` se fait par le Deno de l'environnement. Non essayé dans l'exemple.

- Les étiquettes en `rem` et en HTML restent lisibles sur téléphone ; un SVG mis à l'échelle
  rapetisse son texte. L'exemple a remplacé un SVG de barres par une grille CSS pour cette raison.
- Un graphique trop large pour un téléphone défile dans son conteneur (`overflow-x: auto`) au lieu
  de faire déborder la page.
- Les bornes et les libellés des classes viennent du notebook ; la vue n'a que les couleurs.

## Lens et traçabilité

Chaque région dessinée par la vue déclare ses entrées, un libellé et sa source de rendu :

```tsx
<figure
  data-marimo-lens-inputs="jours donnees"
  data-marimo-lens-label="Calendrier des jours de pluie"
  data-marimo-lens-render-source={JSON.stringify({ path: "src/components/Graphiques.tsx" })}
>
```

Les identifiants cités (`jours`, `donnees`) sont ceux des hôtes `mo-value`. Ces attributs servent
même sans Lens installé.

## Polices et mise en page

Les polices distantes se chargent par `<link rel="stylesheet">` dans `src/index.html`, avec une
pile de repli dans le CSS. Un `@import` CSS de Google Fonts ne passe pas par le bundler de Deno.
Vérifie à 1280 et à 390 pixels : grilles qui passent en une colonne, contrôles collés en haut
(`position: sticky`), pas de débordement horizontal de la page.

## Construire

```bash
pixi run marimo-studio view build grand-public --target notebook.py
```

La construction vérifie les types TypeScript avant d'assembler. Une erreur de type arrête la
construction et la vue garde l'artefact précédent : lis le message, corrige, reconstruis.
