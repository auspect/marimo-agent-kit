#import "marimo.typ": marimo_output, marimo_region, marimo_value

#let synthese = marimo_value("donnees_vues.synthese", default: none)
#let messages = marimo_value("donnees_vues.messages", default: none)
#let mois = marimo_value("donnees_vues.mois", default: ())
#let annees = marimo_value("donnees_vues.annees", default: ())
#let intensite = marimo_value("donnees_vues.intensite", default: ())
#let source = marimo_value("donnees_vues.source", default: (nom: "—", lien: ""))
#let pret = synthese != none and messages != none

#let encre = rgb("#17202a")
#let discret = rgb("#6b7680")
#let bleu = rgb("#2b5f9f")
#let filet = rgb("#cfcac0")

// Mise en forme française. Les nombres viennent tous du notebook.
#let fr(x, chiffres: 0) = {
  let texte = str(calc.round(float(x), digits: chiffres))
  if chiffres > 0 and not texte.contains(".") { texte += "." + "0" * chiffres }
  texte.replace(".", ",")
}
#let pct(part) = fr(100 * part) + sym.space.nobreak + "%"
#let jour(iso) = {
  let (a, m, j) = iso.split("-").map(int)
  let noms = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
    "août", "septembre", "octobre", "novembre", "décembre")
  [#j #noms.at(m - 1) #a]
}

#set document(title: "Seattle sous la pluie : note technique", author: "meteo.py")
#set page(
  paper: "a4",
  margin: (x: 2.3cm, top: 2.2cm, bottom: 2.4cm),
  footer: context {
    set text(7.5pt, fill: discret)
    grid(
      columns: (1fr, auto),
      [Seattle sous la pluie · note technique],
      counter(page).display("1 / 1", both: true),
    )
  },
)
#set text(font: "Libertinus Serif", size: 10.5pt, fill: encre, lang: "fr", number-width: "tabular")
#set par(justify: true, leading: 0.64em, spacing: 1em)
#set heading(numbering: "1.")
#show heading.where(level: 1): it => block(above: 1.6em, below: 0.8em, text(size: 13pt, weight: "bold", it))
#show figure.caption: it => align(left, text(size: 8.5pt, fill: discret)[*#it.supplement #context it.counter.display(it.numbering).* #it.body])
#show figure: set block(above: 1.4em, below: 1.4em)
#set table(stroke: none)

#text(size: 8pt, tracking: 0.14em, fill: bleu, weight: "bold")[NOTE TECHNIQUE · CLIMAT URBAIN]
#v(0.3em)
#text(size: 22pt, weight: "bold")[Seattle sous la pluie]
#v(0.1em)
#text(size: 12pt, style: "italic", fill: discret)[Fréquence, saison et intensité des jours de pluie]
#v(1.2em)

#if not pret {
  block(width: 100%, inset: 14pt, fill: luma(244), radius: 2pt)[
    *Le notebook n'a pas encore fourni ses résultats.* Ce document se
    compose de nouveau dès que `donnees_vues` est disponible.
  ]
} else [
  #block(inset: (x: 1.5em), above: 0em)[
    #set text(size: 9.8pt)
    #align(center, text(size: 8pt, weight: "bold", tracking: 0.1em)[RÉSUMÉ])
    #v(0.2em)
    #messages.chapeau #messages.saison #messages.intensite #messages.series
  ]

  #v(0.8em)
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    gutter: 10pt,
    ..(
      ("donnees_vues.synthese.part_pluie", pct(synthese.part_pluie), [jours de pluie]),
      ("donnees_vues.synthese.hauteur_annuelle_mm", fr(synthese.hauteur_annuelle_mm) + " mm", [par an en moyenne]),
      ("donnees_vues.synthese.part_mois_humide", pct(synthese.part_mois_humide), [des jours en #synthese.mois_humide]),
      ("donnees_vues.synthese.part_volume_forts", pct(synthese.part_volume_forts), [du volume en jours de #fr(synthese.forts_mm) mm et plus]),
    ).map(((selecteur, valeur, libelle)) => block(
      width: 100%,
      inset: (top: 7pt),
      stroke: (top: 1pt + encre),
    )[
      #marimo_region(selecteur, text(17pt, valeur)) \
      #text(8pt, fill: discret, libelle)
    ]),
  )

  = Données et méthode

  Le jeu couvre #synthese.jours relevés quotidiens, du #jour(synthese.debut) au
  #jour(synthese.fin). Chaque ligne donne la hauteur de pluie du jour en
  millimètres et les températures extrêmes. Source : #link(source.lien)[#source.nom].

  Un jour compte comme pluvieux s'il reçoit au moins #synthese.seuil de pluie.
  La hauteur annuelle est la somme des hauteurs quotidiennes divisée par le
  nombre d'années retenues. Les classes d’intensité portent sur les jours mouillés,
  ceux où il est tombé de la pluie. Tous les calculs sont faits dans le notebook
  marimo `meteo.py`. Ce document les met en page sans les recopier.

  = Saisonnalité

  #messages.saison Le @tab-mois donne le détail par mois, et la @fig-saison montre
  la part des jours de pluie.

  #figure(
    marimo_output("figure_saison", width: 100%),
    caption: [Part des jours de pluie par mois, seuil #synthese.seuil.],
  ) <fig-saison>

  #figure(
    table(
      columns: (auto, 1fr, 1fr, 1fr, 1fr),
      align: (left, right, right, right, right),
      inset: (x: 7pt, y: 4.2pt),
      table.hline(stroke: 0.8pt + encre),
      table.header([Mois], [Jours de pluie], [Hauteur (mm)], [T. max (°C)], [T. min (°C)]),
      table.hline(stroke: 0.4pt + encre),
      ..mois.enumerate().map(((rang, m)) => {
        let fort = m.nom == synthese.mois_humide or m.nom == synthese.mois_sec
        let cellule(corps) = if fort { text(fill: bleu, weight: "bold", corps) } else { corps }
        (
          cellule(m.nom),
          marimo_region("donnees_vues.mois[" + str(rang) + "].part_pluie", cellule(pct(m.part_pluie))),
          cellule(fr(m.hauteur_mm)),
          cellule(fr(m.temp_max, chiffres: 1)),
          cellule(fr(m.temp_min, chiffres: 1)),
        )
      }).flatten(),
      table.hline(stroke: 0.8pt + encre),
    ),
    caption: [Climat mensuel moyen. Le mois le plus humide et le plus sec sont en bleu.],
  ) <tab-mois>

  = Intensité

  #messages.intensite Le @tab-intensite oppose la part des jours de chaque
  classe à la part du volume qu'elle apporte.

  #grid(
    columns: (1fr, 1fr),
    gutter: 16pt,
    [#figure(
      table(
        columns: (auto, 1fr, 1fr, 1fr),
        align: (left, right, right, right),
        inset: (x: 6pt, y: 4.2pt),
        table.hline(stroke: 0.8pt + encre),
        table.header([Classe], [Jours], [Part], [Volume]),
        table.hline(stroke: 0.4pt + encre),
        ..intensite.enumerate().map(((rang, c)) => (
          c.classe,
          str(c.jours),
          pct(c.part_jours),
          marimo_region("donnees_vues.intensite[" + str(rang) + "].part_volume", pct(c.part_volume)),
        )).flatten(),
        table.hline(stroke: 0.8pt + encre),
      ),
      caption: [Jours mouillés par classe de hauteur.],
    ) <tab-intensite>],
    [#figure(
      marimo_output("figure_pluie", width: 100%),
      caption: [Part des jours et du volume par classe.],
    ) <fig-intensite>],
  )

  = Variabilité d'une année à l'autre

  #messages.hauteur L'année la plus humide est #synthese.annee_plus_humide, la
  plus sèche #synthese.annee_plus_seche. #messages.series

  #figure(
    table(
      columns: (auto, 1fr, 1fr, 1fr, 1fr),
      align: (left, right, right, right, right),
      inset: (x: 7pt, y: 4.2pt),
      table.hline(stroke: 0.8pt + encre),
      table.header([Année], [Hauteur (mm)], [Jours de pluie], [Part], [T. max (°C)]),
      table.hline(stroke: 0.4pt + encre),
      ..annees.map(a => (
        str(a.annee),
        fr(a.hauteur_mm),
        str(a.jours_pluie),
        pct(a.part_pluie),
        fr(a.temp_max, chiffres: 1),
      )).flatten(),
      table.hline(stroke: 0.8pt + encre),
    ),
    caption: [Bilan de chaque année, seuil #synthese.seuil.],
  ) <tab-annees>

  = Limites

  Quelques années de relevés ne font pas une normale climatique, qui se calcule sur trente
  ans. Le type de temps du jeu d'origine est synthétique et n'est pas utilisé
  ici. Le seuil d'un jour de pluie change fortement la fréquence : c'est un
  réglage du notebook, à fixer avant toute comparaison avec une autre ville.
]
