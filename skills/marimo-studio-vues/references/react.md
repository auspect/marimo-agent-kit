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

### Les nombres d'un tableau Arrow

Une colonne entière `Int64` de polars peut arriver en `BigInt` JavaScript dans l'export Prepared
alors qu'elle arrivait en nombre en direct. `Math.max(...)` ou une division lèvent alors
`TypeError: Cannot convert a BigInt value to a number`, dans l'export seulement (constaté sur un
essai du skill avec gapminder). Deux parades, la première d'abord :

- dans le notebook, projette des types sans ambiguïté : `pl.col("pop").cast(pl.Float64)`, ou
  `pl.Int32` pour un compte ;
- dans la vue, convertis à la frontière, une fois, avant tout calcul :

  ```tsx
  const lignes = (pays.value?.toArray() ?? []).map((r) => ({ ...r, pop: Number(r.pop), annee: Number(r.annee) }));
  ```

Exporte une première fois dès que la vue lit un tableau Arrow, et regarde l'export servi en HTTP
(`references/exports.md`) : le direct ne prouve rien pour le Prepared.

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

## Tableau de bord : ce qui le distingue d'une page

Une page se lit de haut en bas. Un tableau de bord se manipule : le lecteur compare, trie,
choisit un élément et le situe. Quatre patrons, pris d'un essai sur le mix électrique européen
(un tableau de pays par année). Le notebook calcule ; le navigateur ne fait que trier, filtrer et
sélectionner parmi les lignes déjà projetées, donc sans état préparé de plus.

**Cartes d'indicateurs.** Trois ou quatre cartes en tête : une valeur, son unité, et son écart à
une référence (« −18 % depuis 2015 »). Valeurs et écarts viennent d'un dictionnaire du notebook,
par exemple `kpi` ; la vue ne calcule pas l'écart. Chiffres en `font-variant-numeric:
tabular-nums`.

**Classement cliquable.** Un tableau dont chaque en-tête trie, et dont chaque ligne sélectionne :

```tsx
const [tri, setTri] = useState<{ col: Colonne; asc: boolean }>({ col: "intensite", asc: true });
const [choisi, setChoisi] = useState<string | null>(null);
const basculer = (col: Colonne) => setTri((t) => (t.col === col ? { col, asc: !t.asc } : { col, asc: true }));

<th aria-sort={tri.col === "intensite" ? (tri.asc ? "ascending" : "descending") : "none"}>
  <button type="button" onClick={() => basculer("intensite")}>gCO2/kWh</button>
</th>
<tr className={l.pays === actif?.pays ? "selectionne" : ""}>
  <td><button type="button" onClick={() => setChoisi(l.pays)}>{l.pays}</button></td>
```

Le bouton dans la cellule rend la sélection accessible au clavier. Par défaut, la ligne active
est la première du classement : le panneau de détail n'est jamais vide.

**Filtre côté navigateur.** Un bouton à bascule (`aria-pressed`) qui restreint les lignes déjà
là, sans relancer le notebook, et nommé comme tel (« Filtre de la page ») pour ne pas le
confondre avec un contrôle du notebook. Son seuil vient du notebook, comme tout chiffre. Prévois
l'état vide : « Aucun pays ne correspond au filtre. »

```tsx
const visibles = useMemo(() => {
  const lignes = filtre ? pays.filter((p) => p.bas_carbone_pct >= d.seuils.bas_carbone) : pays;
  return [...lignes].sort((a, b) => (tri.asc ? 1 : -1) * comparer(a[tri.col], b[tri.col]));
}, [pays, filtre, tri, d.seuils]);
const actif = visibles.find((p) => p.pays === choisi) ?? visibles[0] ?? null;
```

**Comparer la sélection à une moyenne.** Le graphique principal trace la série de l'élément
choisi contre la moyenne du périmètre, que le notebook projette en tableau à part
(`serie_moyenne`), avec la même échelle et les mêmes unités ; une fiche à côté donne les écarts
de l'élément à cette moyenne. Changer de ligne change la courbe et la fiche, sans aller-retour au
noyau.

Contrôle à la capture : trier, cliquer une ligne, activer le filtre, et vérifier que le titre du
panneau de détail, la courbe et la fiche suivent.

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

L'exemple n'utilise que des polices du système, en piles nommées dans `:root` : une serif de
livre pour les titres (`"Iowan Old Style", "Palatino Linotype", Palatino, "URW Palladio L",
P052, Georgia, serif`) et `system-ui` pour le texte. Rien ne se télécharge, la vue reste lisible
hors ligne et dans la page autonome, et aucune requête ne part vers un service de polices. Une
police distante se charge par `<link rel="stylesheet">` dans `src/index.html` ; un `@import` CSS
ne passe pas par le bundler de Deno. Évite les paires vues partout, comme Fraunces avec Inter.
Vérifie à 1280 et à 390 pixels : grilles qui passent en une colonne, contrôles collés en haut
(`position: sticky`), pas de débordement horizontal de la page.

## Construire

```bash
pixi run marimo-studio view build grand-public --target notebook.py
```

La construction vérifie les types TypeScript avant d'assembler. Une erreur de type arrête la
construction et la vue garde l'artefact précédent : lis le message, corrige, reconstruis.
