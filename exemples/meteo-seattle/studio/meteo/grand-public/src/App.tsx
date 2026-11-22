/// <reference path="./marimo-studio.d.ts" />

import {
  Annees,
  BarresMois,
  Calendrier,
  Intensite,
} from "./components/Graphiques.tsx";
import type { DonneesVues, Jour } from "./lib/donnees.ts";
import { date, nombre, pourcent } from "./lib/format.ts";
import { type MarimoTable, useMarimoValue } from "./lib/use-marimo-value.ts";

const Chiffre = (
  { valeur, libelle, region }: {
    valeur: string;
    libelle: string;
    region: string;
  },
) => (
  <div
    className="chiffre"
    data-marimo-lens-inputs="donnees"
    data-marimo-lens-label={libelle}
    data-marimo-lens-detail={region}
    data-marimo-lens-render-source={JSON.stringify({ path: "src/App.tsx" })}
  >
    <strong>{valeur}</strong>
    <span>{libelle}</span>
  </div>
);

const Page = ({ d, jours }: { d: DonneesVues; jours: Jour[] }) => {
  const s = d.synthese;
  const periode = s.annee === "Toutes" ? `${s.debut.slice(0, 4)}–${s.fin.slice(0, 4)}` : s.annee;
  return (
    <>
      <header className="une">
        <p className="surtitre">Seattle · relevés quotidiens {periode}</p>
        <h1>{d.messages.titre}</h1>
        <p className="chapeau">{d.messages.chapeau}</p>
        <div className="chiffres">
          <Chiffre
            valeur={pourcent(s.part_pluie)}
            libelle="des jours sont pluvieux"
            region={`seuil ${s.seuil}`}
          />
          <Chiffre
            valeur={`${nombre(s.hauteur_annuelle_mm)} mm`}
            libelle="de pluie par an"
            region="moyenne des années retenues"
          />
          <Chiffre
            valeur={`${s.serie_pluie.jours} jours`}
            libelle="de pluie d'affilée, au plus"
            region={`du ${date(s.serie_pluie.debut)} au ${date(s.serie_pluie.fin)}`}
          />
          <Chiffre
            valeur={`${s.serie_seche.jours} jours`}
            libelle="secs d'affilée, au plus"
            region={`du ${date(s.serie_seche.debut)} au ${date(s.serie_seche.fin)}`}
          />
        </div>
      </header>

      <section className="bloc large" aria-labelledby="titre-calendrier">
        <div className="texte">
          <h2 id="titre-calendrier">Chaque jour, un carré</h2>
          <p>
            Les carrés clairs sont des jours secs. Plus le bleu est foncé, plus
            il est tombé de pluie ce jour-là. {d.messages.series}
          </p>
        </div>
        <Calendrier jours={jours} classes={d.intensite} />
      </section>

      <section className="bloc" aria-labelledby="titre-saison">
        <div className="texte">
          <h2 id="titre-saison">La saison fait tout</h2>
          <p>{d.messages.saison}</p>
        </div>
        <BarresMois mois={d.mois} />
      </section>

      <section className="bloc" aria-labelledby="titre-intensite">
        <div className="texte">
          <h2 id="titre-intensite">Souvent, mais peu à la fois</h2>
          <p>{d.messages.intensite}</p>
        </div>
        <Intensite classes={d.intensite} />
      </section>

      <section className="bloc" aria-labelledby="titre-annees">
        <div className="texte">
          <h2 id="titre-annees">D'une année à l'autre</h2>
          <p>{d.messages.hauteur}</p>
        </div>
        <Annees annees={d.annees} choisie={s.annee} />
      </section>

      <footer className="pied">
        <p>
          Source : <a href={d.source.lien}>{d.source.nom}</a>. Un jour compte
          comme pluvieux à partir de {s.seuil}. Calculs dans le notebook
          {" "}
          <code>meteo.py</code>.
        </p>
      </footer>
    </>
  );
};

export const App = () => {
  const donnees = useMarimoValue<DonneesVues>("donnees_vues");
  const jours = useMarimoValue<MarimoTable<Jour>>("jours_vue");
  const enAttente = donnees.value === undefined && !donnees.error;
  return (
    <div className="page" aria-busy={enAttente}>
      <span
        id="donnees"
        ref={donnees.hostRef}
        hidden
        mo-value="donnees_vues"
      />
      <span id="jours" ref={jours.hostRef} hidden mo-value="jours_vue" />
      <div className="reglages" aria-label="Réglages de l'analyse">
        <marimo-cell name="controles" />
      </div>
      {donnees.error
        ? (
          <p className="erreur" role="alert">
            Les résultats du notebook n'ont pas pu être chargés :{" "}
            {donnees.error.message}
          </p>
        )
        : null}
      {enAttente
        ? <p className="attente" role="status">Chargement des relevés…</p>
        : null}
      {donnees.value
        ? <Page d={donnees.value} jours={jours.value?.toArray() ?? []} />
        : null}
    </div>
  );
};
