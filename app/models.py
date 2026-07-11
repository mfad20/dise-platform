from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager

# ---------------------------------------------------------------------------
# Rôles reconnus par la plateforme (voir Cahier des charges, section 3.1)
# ---------------------------------------------------------------------------
ROLE_VISITEUR = "visiteur"          # non authentifié — non stocké en base
ROLE_ETUDIANT = "etudiant"
ROLE_ALUMNI = "alumni"
ROLE_BUREAU = "bureau"              # "Particulier privilégié"
ROLE_ADMIN = "admin"

ROLES = [ROLE_ETUDIANT, ROLE_ALUMNI, ROLE_BUREAU, ROLE_ADMIN]

STATUT_CONTRIBUTION = ["en_attente", "verification", "valide", "refuse"]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    Modèle unique couvrant Étudiant / Alumni / Bureau / Administrateur.
    Le rôle "Visiteur" correspond simplement à l'absence de connexion.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # --- Authentification (section 3.2) ---
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telephone = db.Column(db.String(30), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_ETUDIANT)
    is_active_account = db.Column(db.Boolean, default=True)  # activation email
    is_validated = db.Column(db.Boolean, default=True)  # validation manuelle Bureau/Admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Identité (fiche annuaire, section 6.3.1) ---
    nom = db.Column(db.String(80), nullable=False)
    prenoms = db.Column(db.String(120), nullable=False)
    photo_url = db.Column(db.String(255), default="img/avatars/default.svg")
    nationalite = db.Column(db.String(80))
    promotion = db.Column(db.Integer, index=True)  # année de promotion ISE
    annee_entree = db.Column(db.Integer)
    annee_sortie = db.Column(db.Integer)
    filiere = db.Column(db.String(120), default="ISE")
    etablissement_actuel = db.Column(db.String(180))  # si thèse / études ailleurs
    fonction_actuelle = db.Column(db.String(150))
    entreprise = db.Column(db.String(150))
    secteur_activite = db.Column(db.String(100))
    pays_residence = db.Column(db.String(80))
    ville_residence = db.Column(db.String(80))
    doctorant = db.Column(db.Boolean, default=False)
    sujet_these = db.Column(db.String(255))
    domaine_expertise = db.Column(db.String(255))  # mots-clés séparés par virgules
    bio = db.Column(db.Text)
    linkedin = db.Column(db.String(255))
    autres_liens = db.Column(db.String(255))  # GitHub, Scholar, ORCID...
    fonction_bureau = db.Column(db.String(120))  # ex. "Trésorier", "Président" si role=bureau

    # --- Confidentialité (section 6.3.4) ---
    visible_email = db.Column(db.Boolean, default=False)
    visible_telephone = db.Column(db.Boolean, default=False)
    visible_localisation = db.Column(db.Boolean, default=True)

    # --- Mentorat ---
    est_mentor = db.Column(db.Boolean, default=False)
    domaines_mentorat = db.Column(db.String(255))

    contributions = db.relationship(
        "Contribution", backref="auteur", lazy="dynamic",
        foreign_keys="Contribution.user_id",
    )
    inscriptions = db.relationship("Inscription", backref="participant", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def nom_complet(self):
        return f"{self.prenoms} {self.nom}"

    @property
    def is_bureau_or_admin(self):
        return self.role in (ROLE_BUREAU, ROLE_ADMIN)

    @property
    def peut_valider_paiements(self):
        return self.role in (ROLE_BUREAU, ROLE_ADMIN)


class Evenement(db.Model):
    __tablename__ = "evenements"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text)
    date_debut = db.Column(db.DateTime, nullable=False)
    lieu = db.Column(db.String(180))
    affiche_url = db.Column(db.String(255))
    intervenants = db.Column(db.String(255))
    programme = db.Column(db.Text)
    inscription_requise = db.Column(db.Boolean, default=True)
    replay_url = db.Column(db.String(255))
    categorie = db.Column(db.String(80), default="Conférence")

    inscriptions = db.relationship("Inscription", backref="evenement", lazy="dynamic")

    @property
    def est_passe(self):
        return self.date_debut < datetime.utcnow()


class Inscription(db.Model):
    __tablename__ = "inscriptions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    evenement_id = db.Column(db.Integer, db.ForeignKey("evenements.id"), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)


class Actualite(db.Model):
    __tablename__ = "actualites"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(180), nullable=False)
    chapo = db.Column(db.String(300))
    contenu = db.Column(db.Text)
    categorie = db.Column(db.String(80), default="Vie de la division")
    image_url = db.Column(db.String(255))
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)
    auteur = db.Column(db.String(120), default="Bureau de la DISE")


class Publication(db.Model):
    __tablename__ = "publications"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(180), nullable=False)
    type_publication = db.Column(db.String(50))  # ISE Mag / Journal de la Quinzaine / Bibliothèque
    numero = db.Column(db.String(50))
    auteur = db.Column(db.String(150))
    annee = db.Column(db.Integer)
    resume = db.Column(db.Text)
    fichier_url = db.Column(db.String(255))
    couverture_url = db.Column(db.String(255))


class Opportunite(db.Model):
    __tablename__ = "opportunites"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(180), nullable=False)
    type_offre = db.Column(db.String(50))  # Stage / Emploi / Bourse / Concours
    entreprise = db.Column(db.String(150))
    pays = db.Column(db.String(80))
    domaine = db.Column(db.String(120))
    description = db.Column(db.Text)
    date_limite = db.Column(db.Date)
    lien = db.Column(db.String(255))
    experience_requise = db.Column(db.String(80))


class ClubCommission(db.Model):
    __tablename__ = "clubs"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    responsable = db.Column(db.String(150))
    membres_count = db.Column(db.Integer, default=0)


class PaymentMethod(db.Model):
    """Section 6.10.3 — moyens de paiement affichés."""
    __tablename__ = "payment_methods"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)  # Wave, Orange Money, MTN, Moov, Banque
    numero = db.Column(db.String(60))
    beneficiaire_nom = db.Column(db.String(120))
    beneficiaire_fonction = db.Column(db.String(120))
    qr_code_url = db.Column(db.String(255))
    couleur = db.Column(db.String(20))  # pour le badge visuel
    actif = db.Column(db.Boolean, default=True)


class CampagneFinancement(db.Model):
    __tablename__ = "campagnes"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text)
    objectif = db.Column(db.Float, nullable=False)
    montant_collecte = db.Column(db.Float, default=0)
    nb_donateurs = db.Column(db.Integer, default=0)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True)

    @property
    def taux(self):
        if not self.objectif:
            return 0
        return min(100, round(100 * self.montant_collecte / self.objectif))


class Contribution(db.Model):
    """
    Déclaration de cotisation ou de don (section 6.10.4).
    La plateforme n'effectue AUCUNE transaction : elle enregistre une
    déclaration que le Trésorier valide manuellement après réception réelle
    des fonds sur Wave / Orange Money / MTN / Moov / Banque.
    """
    __tablename__ = "contributions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    nom_declarant = db.Column(db.String(80), nullable=False)
    prenoms_declarant = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    promotion = db.Column(db.Integer, nullable=True)

    type_contribution = db.Column(db.String(50), nullable=False)
    # cotisation_annuelle / cotisation_exceptionnelle / projet / don_libre
    campagne_id = db.Column(db.Integer, db.ForeignKey("campagnes.id"), nullable=True)

    montant = db.Column(db.Float, nullable=False)
    moyen_paiement = db.Column(db.String(50), nullable=False)
    date_paiement = db.Column(db.Date, nullable=False)
    reference_transaction = db.Column(db.String(120))
    capture_ecran_url = db.Column(db.String(255))
    commentaire = db.Column(db.Text)

    statut = db.Column(db.String(20), default="en_attente")
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    valide_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    date_validation = db.Column(db.DateTime, nullable=True)

    campagne = db.relationship("CampagneFinancement", backref="contributions")


class CompteurVisites(db.Model):
    """
    Compteur de visiteurs du site (section 6.1 — Compteur des visiteurs).
    Ligne unique (singleton) incrémentée une fois par session navigateur.
    """
    __tablename__ = "compteur_visites"
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, default=0, nullable=False)

    @classmethod
    def get_ou_creer(cls):
        compteur = cls.query.first()
        if compteur is None:
            compteur = cls(total=0)
            db.session.add(compteur)
            db.session.commit()
        return compteur


class MessageContact(db.Model):
    __tablename__ = "messages_contact"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    sujet = db.Column(db.String(180))
    message = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    traite = db.Column(db.Boolean, default=False)


class DemandeMentorat(db.Model):
    __tablename__ = "demandes_mentorat"
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sujet = db.Column(db.String(50))  # coaching / cv / entretien / orientation
    message = db.Column(db.Text)
    statut = db.Column(db.String(30), default="en_attente")  # en_attente/acceptee/refusee/terminee
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    etudiant = db.relationship("User", foreign_keys=[etudiant_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])
