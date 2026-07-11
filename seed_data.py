"""
Script de peuplement (seed) de la base de données du prototype DISE.
Usage : python seed_data.py
"""
from datetime import datetime, timedelta, date

from app import create_app
from app.extensions import db
from app.models import (
    User, Evenement, Actualite, Publication, Opportunite, ClubCommission,
    PaymentMethod, CampagneFinancement, Contribution,
    ROLE_ETUDIANT, ROLE_ALUMNI, ROLE_BUREAU, ROLE_ADMIN,
)

app = create_app()


def run():
    with app.app_context():
        print("Réinitialisation de la base…")
        db.drop_all()
        db.create_all()

        # -------------------------------------------------------------
        # Utilisateurs : Administrateur, Bureau, Alumni, Étudiants
        # -------------------------------------------------------------
        admin = User(
            nom="Koffi", prenoms="Admin", email="admin@dise.ci", role=ROLE_ADMIN,
            fonction_bureau="Administrateur système", is_validated=True,
        )
        admin.set_password("Admin2026!")

        tresorier = User(
            nom="Yao", prenoms="Marie-Claire", email="tresorier@dise.ci", role=ROLE_BUREAU,
            fonction_bureau="Trésorière DISE", promotion=2018, filiere="ISE",
            fonction_actuelle="Chargée d'études, BCEAO", entreprise="BCEAO",
            secteur_activite="Institution internationale", pays_residence="Côte d'Ivoire",
            ville_residence="Abidjan", is_validated=True,
        )
        tresorier.set_password("Bureau2026!")

        president = User(
            nom="N'Dré", prenoms="Lébé", email="president@dise.ci", role=ROLE_BUREAU,
            fonction_bureau="Président DISE", promotion=2017,
            fonction_actuelle="Économiste statisticien", entreprise="Banque Africaine de Développement",
            secteur_activite="Institution internationale", pays_residence="Côte d'Ivoire",
            ville_residence="Abidjan", is_validated=True,
            photo_url="bureau/president_dise_2025_2026.jpeg",
            bio="Chers étudiants, chers alumni, cette plateforme est la maison commune de la DISE : "
                "elle rassemble notre mémoire, valorise nos parcours et resserre les liens entre "
                "toutes les générations d'Ingénieurs Statisticiens Économistes. Je vous invite à "
                "vous y inscrire, à compléter votre fiche et à rester connectés à notre communauté.",
        )
        president.set_password("Bureau2026!")

        secretaire = User(
            nom="Bamba", prenoms="Awa", email="secretaire@dise.ci", role=ROLE_BUREAU,
            fonction_bureau="Secrétaire générale", promotion=2019,
            fonction_actuelle="Data Analyst", entreprise="Orange CI",
            secteur_activite="Télécommunications", pays_residence="Côte d'Ivoire",
            ville_residence="Abidjan", is_validated=True,
        )
        secretaire.set_password("Bureau2026!")

        alumni_demo = User(
            nom="Traoré", prenoms="Fatou", email="alumni@dise.ci", role=ROLE_ALUMNI,
            promotion=2015, annee_entree=2012, annee_sortie=2015, filiere="ISE",
            fonction_actuelle="Cheffe de projet Data Science", entreprise="Wave Mobile Money",
            secteur_activite="Fintech", pays_residence="Côte d'Ivoire", ville_residence="Abidjan",
            nationalite="Ivoirienne", domaine_expertise="Data Science, Économétrie, Scoring crédit",
            bio="Diplômée ISE 2015, j'accompagne aujourd'hui les équipes data de Wave sur les modèles de risque.",
            linkedin="https://linkedin.com/in/exemple-alumni", est_mentor=True,
            domaines_mentorat="Data Science, entretiens tech", visible_email=True, is_validated=True,
        )
        alumni_demo.set_password("Alumni2026!")

        etudiant_demo = User(
            nom="Kouassi", prenoms="Jean", email="etudiant@dise.ci", role=ROLE_ETUDIANT,
            promotion=2026, annee_entree=2024, annee_sortie=2027, filiere="ISE",
            nationalite="Ivoirienne", pays_residence="Côte d'Ivoire", ville_residence="Abidjan",
            domaine_expertise="Statistique, R, Python", is_validated=True,
        )
        etudiant_demo.set_password("Etudiant2026!")

        db.session.add_all([admin, tresorier, president, secretaire, alumni_demo, etudiant_demo])

        # -------------------------------------------------------------
        # Alumni supplémentaires pour peupler l'annuaire
        # -------------------------------------------------------------
        alumni_data = [
            ("Ouattara", "Salif", 2010, "Directeur des études", "Ministère de l'Économie et des Finances",
             "Administration publique", "Côte d'Ivoire", "Abidjan", "Ivoirienne",
             "Politique économique, Finances publiques", False),
            ("Koné", "Mariam", 2012, "Économiste pays", "Banque Mondiale",
             "Institution internationale", "Sénégal", "Dakar", "Ivoirienne",
             "Macroéconomie, Développement", False),
            ("N'Guessan", "Paul", 2013, "Actuaire senior", "NSIA Assurances",
             "Assurance", "Côte d'Ivoire", "Abidjan", "Ivoirienne",
             "Actuariat, Gestion des risques", False),
            ("Camara", "Aïcha", 2014, "Chargée d'études statistiques", "INS Côte d'Ivoire",
             "Administration publique", "Côte d'Ivoire", "Abidjan", "Ivoirienne",
             "Enquêtes ménages, EHCVM", False),
            ("Traoré", "Moussa", 2016, "Data Scientist", "Sanofi",
             "Pharmaceutique", "France", "Paris", "Ivoirienne",
             "Machine Learning, Santé publique", True),
            ("Yeo", "Ramata", 2017, "Chargée de portefeuille", "BAD",
             "Institution internationale", "Côte d'Ivoire", "Abidjan", "Burkinabé",
             "Financement de projets, Agriculture", False),
            ("Coulibaly", "Aboubacar", 2019, "Consultant risques", "Deloitte",
             "Conseil", "Côte d'Ivoire", "Abidjan", "Ivoirienne",
             "Audit, Risk Management", False),
            ("Bakayoko", "Nadège", 2020, "Chargée d'études", "BCEAO",
             "Institution internationale", "Côte d'Ivoire", "Abidjan", "Ivoirienne",
             "Politique monétaire, UEMOA", True),
            ("Sanogo", "Ibrahim", 2021, "Doctorant en économétrie", "Université Paris-Dauphine",
             "Académique", "France", "Paris", "Ivoirienne",
             "Économétrie des séries temporelles", False),
            ("Diallo", "Kadiatou", 2022, "Actuaire junior", "Allianz CI",
             "Assurance", "Côte d'Ivoire", "Abidjan", "Guinéenne",
             "Actuariat vie", False),
            ("Kamagaté", "Souleymane", 2023, "Data Analyst", "MTN Côte d'Ivoire",
             "Télécommunications", "Côte d'Ivoire", "Abidjan", "Ivoirienne",
             "Business Intelligence, SQL", False),
            ("Adjoumani", "Grace", 2024, "Chargée d'études marketing", "Nestlé CI",
             "Agroalimentaire", "Côte d'Ivoire", "Abidjan", "Ivoirienne",
             "Études de marché, Marketing analytics", False),
        ]
        # Témoignages (section 6.1 Accueil) : quelques bios courtes utilisées
        # comme citations d'anciens sur la page d'accueil.
        temoignages_bios = {
            0: "La DISE m'a offert un réseau qui dépasse largement les frontières de la Côte d'Ivoire "
               "— aujourd'hui encore, c'est vers mes camarades de promotion que je me tourne en premier.",
            4: "Rester connecté à la DISE depuis Paris grâce à cette plateforme me permet de suivre la vie "
               "de la division et d'échanger régulièrement avec les nouvelles promotions.",
            6: "Le mentorat DISE m'a permis d'accompagner de jeunes étudiants ISE dans leurs premiers pas "
               "professionnels ; c'est une des plus belles façons de rendre ce que la division m'a donné.",
        }

        for i, (nom, prenoms, promo, fonction, entreprise, secteur, pays, ville, nat, dom, doctorant) in enumerate(alumni_data):
            u = User(
                nom=nom, prenoms=prenoms, email=f"{prenoms.lower()}.{nom.lower()}{i}@dise-alumni.ci",
                role=ROLE_ALUMNI, promotion=promo, annee_entree=promo - 3, annee_sortie=promo,
                filiere="ISE", fonction_actuelle=fonction, entreprise=entreprise,
                secteur_activite=secteur, pays_residence=pays, ville_residence=ville,
                nationalite=nat, domaine_expertise=dom, doctorant=doctorant,
                sujet_these="Modélisation économétrique des chocs macroéconomiques" if doctorant else None,
                bio=temoignages_bios.get(i),
                linkedin="https://linkedin.com/in/exemple", is_validated=True,
            )
            u.set_password("Alumni2026!")
            db.session.add(u)

        # Étudiants supplémentaires
        etudiants_data = [
            ("Silué", "Bintou", 2026), ("Zamblé", "Kevin", 2027),
            ("Dosso", "Aminata", 2025), ("Gnahoua", "Éric", 2026),
        ]
        for nom, prenoms, promo in etudiants_data:
            u = User(
                nom=nom, prenoms=prenoms, email=f"{prenoms.lower()}.{nom.lower()}@ensea.ci",
                role=ROLE_ETUDIANT, promotion=promo, annee_entree=promo - 2, annee_sortie=promo + 1,
                filiere="ISE", nationalite="Ivoirienne", pays_residence="Côte d'Ivoire",
                ville_residence="Abidjan", is_validated=True,
            )
            u.set_password("Etudiant2026!")
            db.session.add(u)

        db.session.commit()

        # -------------------------------------------------------------
        # Moyens de paiement (section 6.10.3)
        # -------------------------------------------------------------
        moyens = [
            PaymentMethod(nom="Wave", numero="+225 07 00 00 00 01",
                          beneficiaire_nom="Yao Marie-Claire", beneficiaire_fonction="Trésorière DISE",
                          couleur="#00d2ff"),
            PaymentMethod(nom="Orange Money", numero="+225 07 00 00 00 02",
                          beneficiaire_nom="Yao Marie-Claire", beneficiaire_fonction="Trésorière DISE",
                          couleur="#ff7900"),
            PaymentMethod(nom="MTN Mobile Money", numero="+225 05 00 00 00 03",
                          beneficiaire_nom="Diabaté Ismaël", beneficiaire_fonction="Président DISE",
                          couleur="#ffcc00"),
            PaymentMethod(nom="Moov Money", numero="+225 01 00 00 00 04",
                          beneficiaire_nom="Bamba Awa", beneficiaire_fonction="Secrétaire générale",
                          couleur="#004b93"),
        ]
        db.session.add_all(moyens)

        # -------------------------------------------------------------
        # Campagnes de financement (section 6.10.7)
        # -------------------------------------------------------------
        campagnes = [
            CampagneFinancement(
                titre="Organisation de la Journée Scientifique DISE 2026",
                description="Financement de la location de salle, du traiteur et de la communication pour la Journée Scientifique annuelle.",
                objectif=2_500_000, montant_collecte=1_850_000, nb_donateurs=64,
                date_debut=date(2026, 4, 1), date_fin=date(2026, 8, 30),
            ),
            CampagneFinancement(
                titre="Bourse d'excellence pour 3 étudiants méritants",
                description="Soutenir les frais de scolarité et de vie de trois étudiants ISE en difficulté financière.",
                objectif=1_800_000, montant_collecte=650_000, nb_donateurs=21,
                date_debut=date(2026, 3, 1), date_fin=date(2026, 12, 31),
            ),
            CampagneFinancement(
                titre="Édition spéciale de l'ISE Mag — 20 ans de la DISE",
                description="Impression et diffusion d'un numéro spécial anniversaire de l'ISE Mag.",
                objectif=1_200_000, montant_collecte=1_200_000, nb_donateurs=48,
                date_debut=date(2025, 10, 1), date_fin=date(2026, 2, 1), active=False,
            ),
        ]
        db.session.add_all(campagnes)
        db.session.commit()

        # -------------------------------------------------------------
        # Actualités (section 6.4.1)
        # -------------------------------------------------------------
        actus = [
            Actualite(
                titre="Lancement officiel de la plateforme numérique de la DISE",
                chapo="La division se dote enfin d'un espace numérique unique pour son réseau.",
                contenu="Après plusieurs mois de travail, la DISE lance sa plateforme officielle.\n"
                        "Elle centralise désormais l'annuaire des alumni, les actualités, les événements, "
                        "les publications et le module de cotisations.\nUn grand pas pour la cohésion de notre communauté.",
                categorie="Vie de la division", auteur="Bureau de la DISE",
                date_publication=datetime.utcnow() - timedelta(days=2),
            ),
            Actualite(
                titre="La DISE représentée à la conférence BCEAO sur l'inclusion financière",
                chapo="Plusieurs alumni de la DISE ont pris part aux échanges à Dakar.",
                contenu="La délégation DISE a participé activement aux ateliers sur l'inclusion financière "
                        "et la digitalisation des paiements dans la zone UEMOA.",
                categorie="Alumni", auteur="Bureau de la DISE",
                date_publication=datetime.utcnow() - timedelta(days=10),
            ),
            Actualite(
                titre="Ouverture des candidatures pour le programme de mentorat 2026",
                chapo="Étudiants, inscrivez-vous dès maintenant pour être accompagnés par un alumni.",
                contenu="Le programme de mentorat DISE revient pour une nouvelle édition. "
                        "Coaching, correction de CV, simulation d'entretien : choisissez votre besoin "
                        "et un mentor vous accompagnera durant tout le semestre.",
                categorie="Vie de la division", auteur="Bureau de la DISE",
                date_publication=datetime.utcnow() - timedelta(days=18),
            ),
            Actualite(
                titre="Résultats du hackathon Data for Good ENSEA",
                chapo="L'équipe DISE remporte la première place du hackathon inter-écoles.",
                contenu="Félicitations à l'équipe d'étudiants ISE qui a remporté le hackathon Data for Good "
                        "organisé à l'ENSEA, avec un projet de scoring de crédit pour les kits solaires.",
                categorie="ENSEA", auteur="Bureau de la DISE",
                date_publication=datetime.utcnow() - timedelta(days=30),
            ),
        ]
        db.session.add_all(actus)

        # -------------------------------------------------------------
        # Événements (section 6.5)
        # -------------------------------------------------------------
        evenements = [
            Evenement(
                titre="Rendez-vous des Experts", categorie="Conférence",
                description="Une conférence pour rencontrer des experts statisticiens économistes et échanger sur les grands enjeux du secteur.",
                date_debut=datetime.utcnow() + timedelta(days=25), lieu="ENSEA Abidjan, Amphithéâtre principal",
                intervenants="Panel d'experts et d'alumni DISE",
                programme="09h00 — Ouverture\n10h00 — Table ronde avec les experts\n"
                          "14h00 — Ateliers thématiques\n16h30 — Networking alumni",
                affiche_url="annonces_activites/flyes_conference_rendez_vous_des_experts.jpg",
            ),
            Evenement(
                titre="Marathon des ISE", categorie="Compétition",
                description="Une course sportive et conviviale entre étudiants, alumni et amis de la DISE.",
                date_debut=datetime.utcnow() + timedelta(days=15), lieu="Abidjan",
                intervenants="Commission Sport DISE",
                affiche_url="annonces_activites/flyes_conference_maraton_des_ise.jpg",
            ),
            Evenement(
                titre="Journée Pause DISE", categorie="Détente",
                description="Une journée détente pour souffler ensemble entre deux périodes d'examens.",
                date_debut=datetime.utcnow() + timedelta(days=10), lieu="ENSEA Abidjan",
                affiche_url="annonces_activites/flyes_conference_pause.jpg",
            ),
            Evenement(
                titre="Assemblée générale annuelle de la DISE", categorie="Institutionnel",
                description="Bilan de l'année, élection du nouveau Bureau, présentation du rapport financier.",
                date_debut=datetime.utcnow() + timedelta(days=45), lieu="ENSEA Abidjan",
            ),
            Evenement(
                titre="Cérémonie de remise de diplômes — Promotion 2025", categorie="Cérémonie",
                description="Cérémonie officielle de remise des diplômes aux étudiants de la promotion 2025.",
                date_debut=datetime.utcnow() - timedelta(days=60), lieu="ENSEA Abidjan",
                replay_url="https://example.org/replay-ceremonie-2025",
                affiche_url="ensea/diplomation.jpg",
            ),
            Evenement(
                titre="ISE Championship", categorie="Compétition",
                description="Tournoi sportif inter-promotions organisé par la DISE.",
                date_debut=datetime.utcnow() - timedelta(days=35), lieu="ENSEA Abidjan",
                affiche_url="activites_passees/ISEchampionShip2025_image_sport_colective.jpeg",
            ),
            Evenement(
                titre="Grande Rentrée DISE", categorie="Vie de la division",
                description="Cérémonie de rentrée académique et accueil des nouveaux étudiants ISE.",
                date_debut=datetime.utcnow() - timedelta(days=90), lieu="ENSEA Abidjan",
                affiche_url="activites_passees/DISE_AKWABA.jpeg",
            ),
        ]
        db.session.add_all(evenements)

        # -------------------------------------------------------------
        # Publications (section 6.7)
        # -------------------------------------------------------------
        publications = [
            Publication(titre="ISE Mag — Numéro 12 : Spécial Fintech", type_publication="ISE Mag",
                        numero="12", annee=2026, auteur="Rédaction DISE",
                        resume="Dossier spécial sur la révolution fintech en Afrique de l'Ouest.",
                        couverture_url="ise_quinzaine/publication_ise_de_la_quinzaine1.jpg"),
            Publication(titre="Journal de la Quinzaine — Édition de janvier", type_publication="Journal de la Quinzaine",
                        numero="J-2026-01", annee=2026, auteur="Commission Communication",
                        resume="L'actualité de la division en un coup d'œil.",
                        couverture_url="ise_quinzaine/publication_ise_de_la_quinzaine2.jpg"),
            Publication(titre="Déterminants macroéconomiques de la circulation fiduciaire en zone UEMOA (2004–2025)",
                        type_publication="Bibliothèque", annee=2026, auteur="Mémoire de Master 2 ISE",
                        resume="Étude économétrique sur panel : cointégration, PCA et clustering appliqués à la zone UEMOA.",
                        couverture_url="ise_quinzaine/publication_ise_de_la_quinzaine3.jpg"),
            Publication(titre="ISE Mag — Numéro 11 : Portraits d'alumni", type_publication="ISE Mag",
                        numero="11", annee=2025, auteur="Rédaction DISE",
                        resume="Portraits de dix alumni marquants de la DISE.",
                        couverture_url="ise_quinzaine/publication_ise_de_la_quinzaine4.jpg"),
            Publication(titre="Guide de l'étudiant ISE 2026", type_publication="Bibliothèque",
                        annee=2026, auteur="Bureau de la DISE",
                        resume="Tout savoir sur la vie à l'ENSEA et le cursus ISE.",
                        couverture_url="ise_quinzaine/publication_ise_de_la_quinzaine5.jpg"),
        ]
        db.session.add_all(publications)

        # -------------------------------------------------------------
        # Opportunités (section 6.8)
        # -------------------------------------------------------------
        opportunites = [
            Opportunite(titre="Stage — Analyste Data Science", type_offre="Stage", entreprise="Wave Mobile Money",
                        pays="Côte d'Ivoire", domaine="Data Science", experience_requise="Débutant",
                        description="Stage de 6 mois sur les modèles de scoring crédit et la détection de fraude.",
                        date_limite=date.today() + timedelta(days=30)),
            Opportunite(titre="Économiste junior", type_offre="Emploi", entreprise="BCEAO",
                        pays="Sénégal", domaine="Politique monétaire", experience_requise="1-2 ans",
                        description="Poste au sein de la direction des études économiques et de la monnaie.",
                        date_limite=date.today() + timedelta(days=45)),
            Opportunite(titre="Bourse de Master en Data Science", type_offre="Bourse", entreprise="AFD / Campus France",
                        pays="France", domaine="Data Science", experience_requise="Bac+3/4",
                        description="Bourse complète pour un Master 2 en science des données en France.",
                        date_limite=date.today() + timedelta(days=60)),
            Opportunite(titre="Concours de recrutement — Institut National de la Statistique",
                        type_offre="Concours", entreprise="INS Côte d'Ivoire", pays="Côte d'Ivoire",
                        domaine="Statistique publique", experience_requise="Bac+5",
                        description="Concours direct pour le recrutement d'ingénieurs statisticiens.",
                        date_limite=date.today() + timedelta(days=20)),
        ]
        db.session.add_all(opportunites)

        # -------------------------------------------------------------
        # Clubs & Commissions (section 6.9.3)
        # -------------------------------------------------------------
        clubs = [
            ClubCommission(nom="Club Data Science & IA", responsable="Traoré Moussa", membres_count=34,
                            description="Ateliers pratiques, veille technologique et projets Kaggle entre étudiants et alumni."),
            ClubCommission(nom="Commission Finance & Entrepreneuriat", responsable="Coulibaly Aboubacar", membres_count=21,
                            description="Accompagnement des projets entrepreneuriaux et éducation financière des membres."),
            ClubCommission(nom="Club Sport DISE", responsable="Kamagaté Souleymane", membres_count=45,
                            description="Tournois inter-promotions et rencontres sportives entre étudiants et alumni."),
        ]
        db.session.add_all(clubs)
        db.session.commit()

        # -------------------------------------------------------------
        # Contributions de démonstration (section 6.10.4)
        # -------------------------------------------------------------
        contributions = [
            Contribution(user_id=alumni_demo.id, nom_declarant="Traoré", prenoms_declarant="Fatou",
                         email=alumni_demo.email, promotion=2015, type_contribution="cotisation_annuelle",
                         montant=15000, moyen_paiement="Wave", date_paiement=date.today() - timedelta(days=5),
                         reference_transaction="WAVE-88213", statut="valide",
                         date_creation=datetime.utcnow() - timedelta(days=5),
                         valide_par_id=tresorier.id, date_validation=datetime.utcnow() - timedelta(days=4)),
            Contribution(user_id=etudiant_demo.id, nom_declarant="Kouassi", prenoms_declarant="Jean",
                         email=etudiant_demo.email, promotion=2026, type_contribution="cotisation_annuelle",
                         montant=5000, moyen_paiement="Orange Money", date_paiement=date.today() - timedelta(days=2),
                         reference_transaction="OM-44921", statut="en_attente",
                         date_creation=datetime.utcnow() - timedelta(days=2)),
            Contribution(nom_declarant="Kouadio", prenoms_declarant="Serge", email="serge.k@example.com",
                         type_contribution="don_libre", montant=25000, moyen_paiement="MTN Mobile Money",
                         date_paiement=date.today() - timedelta(days=1), reference_transaction="MTN-10029",
                         statut="verification", date_creation=datetime.utcnow() - timedelta(days=1)),
        ]
        db.session.add_all(contributions)

        db.session.commit()
        print("Base de données peuplée avec succès : dise_platform/dise.db")
        print("Comptes de démonstration : voir /auth/connexion")


if __name__ == "__main__":
    run()
