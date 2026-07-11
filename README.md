# Plateforme numérique DISE — Prototype Flask

Prototype fonctionnel de la plateforme numérique officielle de la **DISE**
(Division des Ingénieurs Statisticiens Économistes — ENSEA Abidjan), construit
à partir du *Cahier des charges — Plateforme Numérique Officielle de la DISE
(v2.0)*.

Ce n'est pas une simple maquette statique : c'est une vraie application
Flask avec base de données (SQLite), authentification, rôles, annuaire
filtrable, et module Finances avec déclarations de paiement persistées.

## Aperçu des modules couverts

- **Accueil** — hero, chiffres clés, actualités, événements, publications, portrait alumni
- **La DISE** — présentation, bureau, organigramme, historique, Hall of Fame
- **Annuaire des alumni** ⭐ — fiche complète, recherche + filtres multicritères, export
- **Vie de la DISE** — actualités (catégories, recherche), grandes activités
- **Événements** — fiche complète, inscription en ligne, replay
- **Archives** — classement par événement / promotion
- **Publications** — ISE Mag, Journal de la Quinzaine, Bibliothèque
- **Opportunités** — stages, emplois, bourses, concours (filtres pays/type)
- **Communauté & Mentorat** — mentors, demandes de mentorat, clubs/commissions
- **Finances & Cotisations** — tableau de bord financier, moyens de paiement
  (Wave, Orange Money, MTN, Moov), déclaration de paiement, dons, campagnes de
  financement, transparence financière, tableau de bord du Trésorier
- **Galerie** — albums par événement
- **Contact** — formulaire, FAQ
- **Tableau de bord personnel** — profil, historique financier, mentorat
- **Administration (back-office)** — utilisateurs & rôles, validation des
  comptes Bureau, messages de contact

Rôles gérés : **Visiteur** (non connecté), **Étudiant ISE**, **Alumni**,
**Bureau / Particulier privilégié**, **Administrateur** — avec la matrice de
permissions du cahier des charges (section 3.3).

## Installation

```bash
python3 -m venv venv
source venv/bin/activate          # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Peupler la base de données de démonstration

```bash
python3 seed_data.py
```

Ce script réinitialise `dise.db` (à la racine du projet) et crée des
utilisateurs, alumni, événements, actualités, publications, opportunités,
campagnes et déclarations de paiement de démonstration.

Une base déjà peuplée est fournie avec ce prototype : vous pouvez lancer le
serveur directement (étape suivante) sans relancer ce script, ou le relancer
à tout moment pour repartir d'une base propre.

## Lancer le serveur

```bash
python3 run.py
```

Puis ouvrez **http://127.0.0.1:5000**.

## Comptes de démonstration

| Rôle | E-mail | Mot de passe |
|---|---|---|
| Étudiant | etudiant@dise.ci | Etudiant2026! |
| Alumni (mentor) | alumni@dise.ci | Alumni2026! |
| Bureau — Trésorière | tresorier@dise.ci | Bureau2026! |
| Bureau — Président | president@dise.ci | Bureau2026! |
| Administrateur | admin@dise.ci | Admin2026! |

## Structure du projet

```
dise_platform/
  app/
    __init__.py          # factory Flask, filtres Jinja, gestion d'erreurs
    extensions.py         # db, login_manager, csrf
    models.py              # modèles SQLAlchemy (User, Evenement, Contribution...)
    routes/
      main.py             # accueil, La DISE, actualités, événements, archives,
                          # publications, opportunités, communauté, galerie,
                          # contact, tableau de bord personnel
      auth.py             # connexion, inscription, mot de passe oublié
      annuaire.py         # annuaire des alumni (recherche, filtres, export)
      finances.py         # cotisations, dons, campagnes, trésorier
      admin.py            # back-office (utilisateurs, rôles, messages)
    templates/            # Jinja2 (charte graphique DISE)
    static/
      css/style.css       # bleu institutionnel + or, Poppins/Inter/IBM Plex Mono
      js/main.js          # menu mobile, copie de numéros, sparklines
  config.py
  run.py
  seed_data.py
  requirements.txt
```

## Design & médias

Le design visuel de cette plateforme est dérivé du site **La Relève** (liste
candidate à l'élection DISE 2026-2027) fourni par l'utilisateur :
- `app/static/css/lareleve.css` et `photos.css` — repris tels quels (palette
  bleu nuit `#071A52` / or `#D4AF37`, typographies Playfair Display + Inter +
  Space Grotesk, composants navbar/hero/footer/cartes).
- Le canvas **Three.js** et le système de **particules** du site d'origine
  ont volontairement été retirés, comme demandé — remplacés par les auroras
  CSS déjà présentes dans la feuille de style (aucune dépendance JS lourde).
- `app/static/js/main.js` est une version allégée du script d'origine
  (loader, navbar, AOS, compteurs, carrousel hero, back-to-top), sans
  Three.js ni Vanilla Tilt.
- `app/static/css/style.css` habille les composants propres à DISE
  (annuaire, finances, tableaux, formulaires) avec les mêmes tokens de
  couleur/typographie pour une identité visuelle unifiée.

Toutes les images fournies (`ImagesSiteDISE.zip`) ont été redimensionnées et
compressées pour le web, puis réparties dans `app/static/img/` :
- `brand/` — logo DISE, logo ENSEA, logo AES, photos d'équipe par pôle
- `bureau/` — photos officielles du Bureau 2025-2026 (voir note ci-dessous)
- `ensea/` — photos de campus (cours, diplômation) utilisées dans le hero
- `activites_passees/`, `annonces_activites/` — flyers et photos d'activités,
  utilisés comme affiches d'événements
- `ise_quinzaine/` — couvertures utilisées pour les publications

**Note sur les photos du Bureau** : les photos réelles du Bureau 2025-2026
sont affichées sur la page *La DISE*, mais **aucun nom n'a été inventé** —
seule la fonction (Président, Secrétaire Général, Trésorière…) est indiquée.
Le Bureau devra compléter les noms réels directement dans
`app/routes/main.py` (variable `bureau_officiel`) ou via un futur back-office.

Les flyers d'anniversaire individuels (`Anniverssaire/`) n'ont volontairement
pas été réutilisés sur le site public par respect de la vie privée des
personnes concernées ; ils restent disponibles si besoin mais ne sont
référencés dans aucun template.

## Ce qui est simulé (à brancher en production)


- **Paiements** : la plateforme n'effectue aucune transaction ; elle
  enregistre des déclarations validées manuellement par le Trésorier — les
  QR Codes affichés sont des emplacements réservés à remplacer par les vrais
  QR Codes Wave/Orange Money/MTN/Moov.
- **Connexion Google (OAuth)** : bouton présent, intégration réelle
  (Google Identity Services) à brancher.
- **E-mails transactionnels** (confirmation de compte, réinitialisation de
  mot de passe) : simulés côté serveur, à connecter à un service d'envoi
  (ex. SendGrid, Mailjet, SMTP ENSEA).
- **Upload de captures d'écran de transaction** et **export PDF réel** des
  fiches annuaire : prévus dans le modèle de données, à activer avec un
  stockage de fichiers (local ou S3) et une librairie PDF (WeasyPrint).
- **Carte mondiale interactive** des alumni : la répartition par pays est
  déjà calculée côté serveur ; il reste à l'afficher avec une librairie de
  cartographie (Leaflet.js) en remplacement du récapitulatif textuel actuel.

## Prochaines étapes suggérées

1. Recueillir les retours du Bureau de la DISE sur ce prototype.
2. Remplacer les couleurs/typographies par les codes exacts de La Relève si
   souhaité (actuellement une palette bleu institutionnel + or cohérente
   avec le cahier des charges).
3. Migrer vers PostgreSQL et un serveur de production (Gunicorn + Nginx) pour
   le déploiement.
