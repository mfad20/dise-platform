from datetime import datetime, date
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    Contribution, PaymentMethod, CampagneFinancement, User,
    ROLE_ETUDIANT, ROLE_ALUMNI,
)

finances_bp = Blueprint("finances", __name__)


def tresorier_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.peut_valider_paiements:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def _kpis_financiers():
    total_valide = db.session.query(db.func.coalesce(db.func.sum(
        Contribution.montant), 0)).filter_by(statut="valide").scalar()
    nb_cotisants = db.session.query(Contribution.user_id).filter(
        Contribution.statut == "valide",
        Contribution.type_contribution.in_(["cotisation_annuelle", "cotisation_exceptionnelle"]),
    ).distinct().count()
    nb_donateurs = db.session.query(Contribution.user_id).filter(
        Contribution.statut == "valide", Contribution.type_contribution == "don_libre",
    ).distinct().count()
    derniere = Contribution.query.filter_by(statut="valide").order_by(
        Contribution.date_paiement.desc()
    ).first()
    objectif_annuel = 5_000_000
    nb_projets = CampagneFinancement.query.count()
    taux = min(100, round(100 * total_valide / objectif_annuel)) if objectif_annuel else 0
    return dict(
        objectif_annuel=objectif_annuel, montant_collecte=total_valide,
        nb_cotisants=nb_cotisants, nb_donateurs=nb_donateurs,
        taux_realisation=taux, derniere_cotisation=derniere,
        nb_projets_finances=nb_projets,
    )


# ---------------------------------------------------------------------------
# 6.10.1 / 6.10.2 — Tableau de bord financier + Cotiser
# ---------------------------------------------------------------------------
@finances_bp.route("/")
def index():
    kpis = _kpis_financiers()
    moyens_paiement = PaymentMethod.query.filter_by(actif=True).all()
    campagnes = CampagneFinancement.query.filter_by(active=True).all()
    return render_template(
        "finances/index.html", kpis=kpis, moyens_paiement=moyens_paiement,
        campagnes=campagnes,
    )


# ---------------------------------------------------------------------------
# 6.10.4 — Déclaration de paiement
# ---------------------------------------------------------------------------
@finances_bp.route("/declarer", methods=["GET", "POST"])
def declarer():
    moyens_paiement = PaymentMethod.query.filter_by(actif=True).all()
    campagnes = CampagneFinancement.query.filter_by(active=True).all()

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenoms = request.form.get("prenoms", "").strip()
        email = request.form.get("email", "").strip()
        type_contribution = request.form.get("type_contribution", "").strip()
        moyen_paiement = request.form.get("moyen_paiement", "").strip()

        try:
            montant = float(request.form.get("montant", "0").replace(",", "."))
        except ValueError:
            montant = 0

        date_paiement_str = request.form.get("date_paiement")
        try:
            date_paiement = datetime.strptime(date_paiement_str, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            date_paiement = date.today()

        promotion_brute = request.form.get("promotion", "").strip()
        promotion = int(promotion_brute) if promotion_brute.isdigit() else None

        campagne_brute = request.form.get("campagne_id", "").strip()
        campagne_id = int(campagne_brute) if campagne_brute.isdigit() else None

        erreurs = []
        if not nom:
            erreurs.append("Merci d'indiquer votre nom.")
        if not prenoms:
            erreurs.append("Merci d'indiquer vos prénoms.")
        if not email or "@" not in email:
            erreurs.append("Merci d'indiquer une adresse e-mail valide.")
        if montant <= 0:
            erreurs.append("Merci d'indiquer un montant valide.")
        if not type_contribution:
            erreurs.append("Merci de choisir un type de contribution.")
        if not moyen_paiement:
            erreurs.append("Merci de choisir un moyen de paiement.")

        if erreurs:
            for e in erreurs:
                flash(e, "danger")
            return render_template(
                "finances/declarer.html", moyens_paiement=moyens_paiement, campagnes=campagnes
            )

        contribution = Contribution(
            user_id=current_user.id if current_user.is_authenticated else None,
            nom_declarant=nom,
            prenoms_declarant=prenoms,
            email=email,
            promotion=promotion,
            type_contribution=type_contribution,
            campagne_id=campagne_id,
            montant=montant,
            moyen_paiement=moyen_paiement,
            date_paiement=date_paiement,
            reference_transaction=request.form.get("reference_transaction", "").strip() or None,
            commentaire=request.form.get("commentaire", "").strip() or None,
            statut="en_attente",
        )
        db.session.add(contribution)
        db.session.commit()
        flash(
            "Votre déclaration de paiement a bien été enregistrée. Le "
            "Trésorier de la DISE va vérifier la réception des fonds avant "
            "validation.", "success"
        )
        return redirect(url_for("finances.index"))

    return render_template(
        "finances/declarer.html", moyens_paiement=moyens_paiement, campagnes=campagnes
    )


# ---------------------------------------------------------------------------
# 6.10.6 — Faire un don
# ---------------------------------------------------------------------------
@finances_bp.route("/don")
def don():
    causes = [
        ("don_libre", "Don libre au bénéfice de la DISE"),
        ("bourse", "Bourse étudiante"),
        ("evenement", "Soutien à un événement"),
        ("publication", "Soutien à une publication"),
        ("projet_etudiant", "Soutien à un projet étudiant"),
        ("urgence", "Fonds d'urgence"),
    ]
    moyens_paiement = PaymentMethod.query.filter_by(actif=True).all()
    return render_template("finances/don.html", causes=causes, moyens_paiement=moyens_paiement)


# ---------------------------------------------------------------------------
# 6.10.7 — Campagnes de financement
# ---------------------------------------------------------------------------
@finances_bp.route("/campagnes")
def campagnes():
    toutes = CampagneFinancement.query.order_by(CampagneFinancement.date_debut.desc()).all()
    return render_template("finances/campagnes.html", campagnes=toutes)


@finances_bp.route("/campagnes/<int:campagne_id>")
def campagne_detail(campagne_id):
    campagne = CampagneFinancement.query.get_or_404(campagne_id)
    return render_template("finances/campagne_detail.html", campagne=campagne)


# ---------------------------------------------------------------------------
# 6.10.8 — Transparence financière
# ---------------------------------------------------------------------------
@finances_bp.route("/transparence")
def transparence():
    depenses = [
        ("Événements", 35), ("Publications", 22), ("Communication", 18),
        ("Fonctionnement", 15), ("Divers", 10),
    ]
    kpis = _kpis_financiers()
    return render_template("finances/transparence.html", depenses=depenses, kpis=kpis)


# ---------------------------------------------------------------------------
# 6.10.5 — Historique personnel
# ---------------------------------------------------------------------------
@finances_bp.route("/historique")
@login_required
def historique():
    mes_contributions = Contribution.query.filter_by(user_id=current_user.id).order_by(
        Contribution.date_creation.desc()
    ).all()
    return render_template("finances/historique.html", contributions=mes_contributions)


# ---------------------------------------------------------------------------
# 6.10.9 — Tableau de bord du Trésorier (Bureau / Admin uniquement)
# ---------------------------------------------------------------------------
@finances_bp.route("/tresorier")
@tresorier_required
def tresorier():
    en_attente = Contribution.query.filter(
        Contribution.statut.in_(["en_attente", "verification"])
    ).order_by(Contribution.date_creation.asc()).all()
    validees = Contribution.query.filter_by(statut="valide").order_by(
        Contribution.date_validation.desc()
    ).limit(20).all()

    kpis = _kpis_financiers()

    repartition_moyen = {}
    repartition_promotion = {}
    repartition_type = {}
    for c in Contribution.query.filter_by(statut="valide").all():
        repartition_moyen[c.moyen_paiement] = repartition_moyen.get(c.moyen_paiement, 0) + c.montant
        if c.promotion:
            repartition_promotion[c.promotion] = repartition_promotion.get(c.promotion, 0) + c.montant
        repartition_type[c.type_contribution] = repartition_type.get(c.type_contribution, 0) + c.montant

    return render_template(
        "finances/tresorier.html", en_attente=en_attente, validees=validees, kpis=kpis,
        repartition_moyen=repartition_moyen, repartition_promotion=repartition_promotion,
        repartition_type=repartition_type,
    )


@finances_bp.route("/tresorier/<int:contrib_id>/valider", methods=["POST"])
@tresorier_required
def valider_contribution(contrib_id):
    contribution = Contribution.query.get_or_404(contrib_id)
    contribution.statut = "valide"
    contribution.valide_par_id = current_user.id
    contribution.date_validation = datetime.utcnow()
    if contribution.campagne:
        contribution.campagne.montant_collecte += contribution.montant
        contribution.campagne.nb_donateurs += 1
    db.session.commit()
    flash("Déclaration validée avec succès.", "success")
    return redirect(url_for("finances.tresorier"))


@finances_bp.route("/tresorier/<int:contrib_id>/refuser", methods=["POST"])
@tresorier_required
def refuser_contribution(contrib_id):
    contribution = Contribution.query.get_or_404(contrib_id)
    contribution.statut = "refuse"
    contribution.valide_par_id = current_user.id
    contribution.date_validation = datetime.utcnow()
    db.session.commit()
    flash("Déclaration refusée.", "info")
    return redirect(url_for("finances.tresorier"))
