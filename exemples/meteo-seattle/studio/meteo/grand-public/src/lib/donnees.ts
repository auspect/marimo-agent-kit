/** Forme de `donnees_vues`, la valeur que la cellule `restitution` prépare pour les vues. */

export type Serie = { jours: number; debut: string; fin: string };

export type Synthese = {
  annee: string;
  seuil: string;
  seuil_mm: number;
  debut: string;
  fin: string;
  jours: number;
  jours_pluie: number;
  part_pluie: number;
  hauteur_annuelle_mm: number;
  mois_humide: string;
  part_mois_humide: number;
  mois_sec: string;
  part_mois_sec: number;
  part_jours_legers: number;
  part_volume_forts: number;
  legers_mm: number;
  forts_mm: number;
  serie_pluie: Serie;
  serie_seche: Serie;
  annee_plus_humide: number;
  annee_plus_seche: number;
};

export type Messages = {
  periode: string;
  titre: string;
  chapeau: string;
  saison: string;
  intensite: string;
  series: string;
  hauteur: string;
};

export type Mois = {
  mois: number;
  nom: string;
  part_pluie: number;
  hauteur_mm: number;
  temp_max: number;
  temp_min: number;
};

export type Annee = {
  annee: number;
  hauteur_mm: number;
  jours_pluie: number;
  part_pluie: number;
  temp_max: number;
};

export type Classe = {
  bas_mm: number;
  haut_mm: number | null;
  classe: string;
  jours: number;
  part_jours: number;
  part_volume: number;
};

/** Une ligne de `jours_vue`, un tableau Arrow que le notebook projette à part. */
export type Jour = {
  date: string;
  precipitation: number;
  pluie: boolean;
};

export type DonneesVues = {
  synthese: Synthese;
  messages: Messages;
  mois: Mois[];
  annees: Annee[];
  intensite: Classe[];
  source: { nom: string; lien: string };
};
