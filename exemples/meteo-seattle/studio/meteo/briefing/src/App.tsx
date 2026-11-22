/// <reference path="./marimo-studio.d.ts" />

import { Deck, Slide } from "@revealjs/react";
import { useEffect, useRef, useSyncExternalStore } from "react";
import type { RevealApi } from "reveal.js";
import "reveal.js/reveal.css";

import {
  Annees,
  BarresMois,
  Calendrier,
  Intensite,
} from "./components/Graphiques.tsx";
import type { DonneesVues, Jour } from "./lib/donnees.ts";
import { date, nombre, pourcent } from "./lib/format.ts";
import { type MarimoTable, useMarimoValue } from "./lib/use-marimo-value.ts";

const keyboardCondition = (event: KeyboardEvent) =>
  !event.composedPath().some(
    (target) =>
      target instanceof Element && target.matches("marimo-cell, marimo-output"),
  );

/** Recentre les diapositives quand les résultats du notebook ont leur taille finale. */
const useSettledLayout = () => {
  const deck = useRef<RevealApi | null>(null);
  useEffect(() => {
    const layout = () => deck.current?.layout();
    document.addEventListener("marimo-studio:idle", layout);
    return () => document.removeEventListener("marimo-studio:idle", layout);
  }, []);
  return deck;
};

/** Sur un téléphone tenu droit, un canevas 16:9 devient illisible : on lit les diapositives à la suite. */
const PORTRAIT = "(max-width: 56rem) and (orientation: portrait)";
const usePortrait = () =>
  useSyncExternalStore(
    (changer) => {
      const media = globalThis.matchMedia(PORTRAIT);
      media.addEventListener("change", changer);
      return () => media.removeEventListener("change", changer);
    },
    () => globalThis.matchMedia(PORTRAIT).matches,
    () => false,
  );

const Pied = ({ numero, d }: { numero: string; d: DonneesVues }) => (
  <p className="pied-diapo">
    <span>{numero}</span>
    <span>
      Seattle, {d.synthese.annee === "Toutes"
        ? `${d.synthese.debut.slice(0, 4)}–${d.synthese.fin.slice(0, 4)}`
        : d.synthese.annee} · seuil {d.synthese.seuil}
    </span>
  </p>
);

const Diapos = ({ d, jours }: { d: DonneesVues; jours: Jour[] }) => {
  const s = d.synthese;
  return (
    <>
      <Slide className="couverture">
        <div className="couverture-grille">
          <div>
            <p className="surtitre">Point climat · relevés quotidiens NOAA</p>
            <h1>Seattle sous la pluie</h1>
            <p className="question">
              Combien de jours pleut-il, à quelle saison, et avec quelle
              intensité ?
            </p>
          </div>
          <div className="couverture-calendrier">
            <Calendrier jours={jours} classes={d.intensite} />
          </div>
        </div>
      </Slide>

      <Slide>
        <p className="surtitre">La réponse</p>
        <h2>{d.messages.titre}</h2>
        <div className="reponse">
          <strong className="grand-chiffre">{pourcent(s.part_pluie)}</strong>
          <p>{d.messages.chapeau}</p>
        </div>
        <Pied numero="01" d={d} />
      </Slide>

      <Slide>
        <p className="surtitre">Saison</p>
        <h2>{d.messages.saison}</h2>
        <BarresMois mois={d.mois} />
        <Pied numero="02" d={d} />
      </Slide>

      <Slide>
        <p className="surtitre">Intensité</p>
        <h2>{d.messages.intensite}</h2>
        <Intensite classes={d.intensite} />
        <Pied numero="03" d={d} />
      </Slide>

      <Slide>
        <p className="surtitre">Années</p>
        <h2>{d.messages.hauteur}</h2>
        <div className="deux-colonnes">
          <dl className="memo">
            <div>
              <dt>Année la plus humide</dt>
              <dd>{s.annee_plus_humide}</dd>
            </div>
            <div>
              <dt>Année la plus sèche</dt>
              <dd>{s.annee_plus_seche}</dd>
            </div>
          </dl>
          <Annees annees={d.annees} choisie={s.annee} />
        </div>
        <Pied numero="04" d={d} />
      </Slide>

      <Slide>
        <p className="surtitre">À vous de régler</p>
        <h2>Changer l'année ou le seuil</h2>
        <div className="deux-colonnes">
          <div className="reglage-direct">
            <marimo-cell name="controles" />
          </div>
          <dl className="memo">
            <div>
              <dt>Jours de pluie</dt>
              <dd>{s.jours_pluie} sur {s.jours}</dd>
            </div>
            <div>
              <dt>Hauteur annuelle</dt>
              <dd>{nombre(s.hauteur_annuelle_mm)} mm</dd>
            </div>
            <div>
              <dt>Plus longue suite de pluie</dt>
              <dd>
                {s.serie_pluie.jours} jours, dès le {date(s.serie_pluie.debut)}
              </dd>
            </div>
          </dl>
        </div>
        <Pied numero="05" d={d} />
      </Slide>

      <Slide>
        <p className="surtitre">Méthode</p>
        <h2>D'où viennent ces chiffres</h2>
        <ul className="methode">
          <li>
            {s.jours} relevés quotidiens, du {date(s.debut)} au {date(s.fin)}.
          </li>
          <li>Un jour est pluvieux à partir de {s.seuil} de pluie.</li>
          <li>Source : {d.source.nom}.</li>
          <li>
            Calculs dans le notebook marimo <code>meteo.py</code>, sans copie
            dans la présentation.
          </li>
        </ul>
        <Pied numero="06" d={d} />
      </Slide>
    </>
  );
};

export const App = () => {
  const deck = useSettledLayout();
  const donnees = useMarimoValue<DonneesVues>("donnees_vues");
  const jours = useMarimoValue<MarimoTable<Jour>>("jours_vue");
  const enAttente = donnees.value === undefined && !donnees.error;
  const portrait = usePortrait();
  return (
    <>
      <span id="donnees" ref={donnees.hostRef} hidden mo-value="donnees_vues" />
      <span id="jours" ref={jours.hostRef} hidden mo-value="jours_vue" />
      {donnees.error
        ? (
          <p className="erreur" role="alert">
            Les résultats du notebook n'ont pas pu être chargés :{" "}
            {donnees.error.message}
          </p>
        )
        : null}
      {enAttente
        ? <p className="attente" role="status">Préparation de la présentation…</p>
        : null}
      {donnees.value && portrait
        ? (
          <main className="lecteur" data-marimo-lens-inputs="donnees jours">
            <Diapos d={donnees.value} jours={jours.value?.toArray() ?? []} />
          </main>
        )
        : null}
      {donnees.value && !portrait
        ? (
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
            <Diapos d={donnees.value} jours={jours.value?.toArray() ?? []} />
          </Deck>
        )
        : null}
    </>
  );
};
