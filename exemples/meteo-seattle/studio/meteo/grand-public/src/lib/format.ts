/** Mise en forme française des nombres et des dates. Aucun chiffre de l'analyse ici. */

// Sans séparateur de milliers, comme les phrases que rédige le notebook.
const entier = new Intl.NumberFormat("fr-FR", {
  maximumFractionDigits: 0,
  useGrouping: false,
});
const pourcentage = new Intl.NumberFormat("fr-FR", {
  style: "percent",
  maximumFractionDigits: 0,
});
const jourMois = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});

export const nombre = (valeur: number) => entier.format(valeur);
export const pourcent = (part: number) => pourcentage.format(part);
export const date = (iso: string) => jourMois.format(new Date(`${iso}T00:00:00Z`));
const MOIS_COURTS = [
  "janv.", "févr.", "mars", "avr.", "mai", "juin",
  "juil.", "août", "sept.", "oct.", "nov.", "déc.",
];
export const abrege = (mois: number) => MOIS_COURTS[mois - 1] ?? String(mois);

/** Couleur d'un jour sec, puis une couleur par classe de hauteur, de la plus faible à la plus forte. */
export const COULEUR_SEC = "var(--sec)";
const COULEURS_CLASSES = [
  "var(--pluie-1)",
  "var(--pluie-2)",
  "var(--pluie-3)",
  "var(--pluie-4)",
  "var(--pluie-5)",
];
export const couleurClasse = (rang: number) =>
  COULEURS_CLASSES[Math.min(rang, COULEURS_CLASSES.length - 1)];

/** Les bornes viennent des classes du notebook (`haut_mm`, `null` pour la dernière). */
export const couleurPluie = (
  mm: number,
  classes: readonly { haut_mm: number | null }[],
) => {
  if (mm <= 0) return COULEUR_SEC;
  const rang = classes.findIndex((c) => c.haut_mm === null || mm < c.haut_mm);
  return couleurClasse(rang === -1 ? classes.length - 1 : rang);
};
