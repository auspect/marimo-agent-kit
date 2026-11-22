import "./graphiques.css";

import type { Annee, Classe, Jour, Mois } from "../lib/donnees.ts";
import {
  abrege,
  COULEUR_SEC,
  couleurClasse,
  couleurPluie,
  date,
  nombre,
  pourcent,
} from "../lib/format.ts";

const SOURCE = JSON.stringify({ path: "src/components/Graphiques.tsx" });

/** Un carré par jour, une ligne de semaines par année, coloré selon la classe de hauteur du notebook. */
export const Calendrier = (
  { jours, classes }: { jours: Jour[]; classes: Classe[] },
) => {
  const parAnnee = new Map<string, Jour[]>();
  for (const jour of jours) {
    const annee = jour.date.slice(0, 4);
    parAnnee.set(annee, [...(parAnnee.get(annee) ?? []), jour]);
  }
  const cote = 11;
  const pas = 13;
  const marge = 44;
  const hauteurAnnee = 7 * pas + 18;
  const annees = [...parAnnee.entries()];
  return (
    <figure
      className="graphique calendrier"
      data-marimo-lens-inputs="jours donnees"
      data-marimo-lens-label="Calendrier des jours de pluie"
      data-marimo-lens-detail="Un carré par jour, couleur selon la hauteur de pluie en mm"
      data-marimo-lens-render-source={SOURCE}
    >
      <div className="defilement">
      <svg
        viewBox={`0 0 ${marge + 54 * pas} ${annees.length * hauteurAnnee}`}
        role="img"
        aria-label="Calendrier de la pluie, un carré par jour"
      >
        {annees.map(([annee, liste], rang) => {
          const premier = new Date(`${annee}-01-01T00:00:00Z`);
          const decalage = (premier.getUTCDay() + 6) % 7;
          return (
            <g key={annee} transform={`translate(0 ${rang * hauteurAnnee})`}>
              <text className="etiquette-annee" x={0} y={4 * pas}>
                {annee}
              </text>
              {liste.map((jour) => {
                const jourDate = new Date(`${jour.date}T00:00:00Z`);
                const quantieme = Math.round(
                  (jourDate.getTime() - premier.getTime()) / 86_400_000,
                );
                const semaine = Math.floor((quantieme + decalage) / 7);
                const jourSemaine = (jourDate.getUTCDay() + 6) % 7;
                return (
                  <rect
                    key={jour.date}
                    x={marge + semaine * pas}
                    y={jourSemaine * pas}
                    width={cote}
                    height={cote}
                    rx={2}
                    fill={couleurPluie(jour.precipitation, classes)}
                  >
                    <title>
                      {`${date(jour.date)} : ${
                        jour.precipitation.toLocaleString("fr-FR")
                      } mm`}
                    </title>
                  </rect>
                );
              })}
            </g>
          );
        })}
      </svg>
      </div>
      <figcaption>
        <ul className="legende">
          <li>
            <span style={{ background: COULEUR_SEC }} />
            sec
          </li>
          {classes.map((classe, rang) => (
            <li key={classe.classe}>
              <span style={{ background: couleurClasse(rang) }} />
              {classe.classe}
            </li>
          ))}
        </ul>
      </figcaption>
    </figure>
  );
};

/** Part des jours de pluie de chaque mois, le mois le plus humide en évidence. */
export const BarresMois = ({ mois }: { mois: Mois[] }) => {
  const plusHumide = Math.max(...mois.map((m) => m.part_pluie));
  return (
    <figure
      className="graphique mois"
      role="img"
      aria-label="Part des jours de pluie pour chaque mois"
      data-marimo-lens-inputs="donnees"
      data-marimo-lens-label="Part des jours de pluie par mois"
      data-marimo-lens-render-source={SOURCE}
    >
      {mois.map((m) => (
        <div className="mois-colonne" key={m.mois} title={`${m.nom} : ${pourcent(m.part_pluie)}`}>
          <span className="mois-piste">
            <span
              className={m.part_pluie === plusHumide ? "barre forte" : "barre"}
              style={{ height: `${100 * m.part_pluie}%` }}
            >
              <span className="mois-valeur">{pourcent(m.part_pluie)}</span>
            </span>
          </span>
          <span className="mois-nom">{abrege(m.mois)}</span>
        </div>
      ))}
    </figure>
  );
};

/** Pour chaque classe de hauteur : la part des jours mouillés et la part du volume. */
export const Intensite = ({ classes }: { classes: Classe[] }) => (
  <figure
    className="graphique intensite"
    data-marimo-lens-inputs="donnees"
    data-marimo-lens-label="Jours de pluie et volume par classe de hauteur"
    data-marimo-lens-render-source={SOURCE}
  >
    <div className="intensite-entete" aria-hidden="true">
      <span />
      <span className="cle jours">Part des jours mouillés</span>
      <span className="cle volume">Part du volume tombé</span>
    </div>
    {classes.map((c) => (
      <div className="intensite-ligne" key={c.classe}>
        <span className="intensite-classe">{c.classe}</span>
        <span className="piste">
          <span className="jauge jours" style={{ width: `${100 * c.part_jours}%` }} />
          <b>{pourcent(c.part_jours)}</b>
        </span>
        <span className="piste">
          <span className="jauge volume" style={{ width: `${100 * c.part_volume}%` }} />
          <b>{pourcent(c.part_volume)}</b>
        </span>
      </div>
    ))}
  </figure>
);

/** Hauteur annuelle de chaque année, l'année choisie en évidence. */
export const Annees = (
  { annees, choisie }: { annees: Annee[]; choisie: string },
) => {
  const plusHaute = Math.max(...annees.map((a) => a.hauteur_mm));
  return (
    <figure
      className="graphique annees"
      data-marimo-lens-inputs="donnees"
      data-marimo-lens-label="Hauteur de pluie de chaque année"
      data-marimo-lens-render-source={SOURCE}
    >
      {annees.map((a) => (
        <div
          key={a.annee}
          className={choisie === "Toutes" || choisie === String(a.annee)
            ? "annee active"
            : "annee"}
        >
          <span className="annee-nom">{a.annee}</span>
          <span className="annee-piste">
            <span style={{ width: `${(100 * a.hauteur_mm) / plusHaute}%` }} />
          </span>
          <span className="annee-valeur">{nombre(a.hauteur_mm)} mm</span>
          <span className="annee-jours">{a.jours_pluie} jours de pluie</span>
        </div>
      ))}
    </figure>
  );
};
