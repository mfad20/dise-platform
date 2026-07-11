from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    User, Contribution, Actualite, Evenement, Opportunite, MessageContact,
    ROLE_ADMIN, ROLE_BUREAU,
)

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = dict(
        nb_users=User.query.count(),
        nb_etudiants=User.query.filter_by(role="etudiant").count(),
        nb_alumni=User.query.filter_by(role="alumni").count(),
        nb_bureau=User.query.filter_by(role="bureau").count(),
        comptes_a_valider=User.query.filter_by(is_validated=False).count(),
        nb_actualites=Actualite.query.count(),
        nb_evenements=Evenement.query.count(),
        nb_opportunites=Opportunite.query.count(),
        contributions_a_traiter=Contribution.query.filter(
            Contribution.statut.in_(["en_attente", "verification"])
        ).count(),
        messages_non_traites=MessageContact.query.filter_by(traite=False).count(),
    )
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/utilisateurs")
@admin_required
def utilisateurs():
    role_filtre = request.args.get("role", "")
    query = User.query
    if role_filtre:
        query = query.filter_by(role=role_filtre)
    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/utilisateurs.html", users=users, role_filtre=role_filtre)


@admin_bp.route("/utilisateurs/<int:user_id>/valider", methods=["POST"])
@admin_required
def valider_utilisateur(user_id):
    user = User.query.get_or_404(user_id)
    user.is_validated = True
    db.session.commit()
    flash(f"Compte de {user.nom_complet} validé.", "success")
    return redirect(url_for("admin.utilisateurs"))


@admin_bp.route("/utilisateurs/<int:user_id>/role", methods=["POST"])
@admin_required
def changer_role(user_id):
    user = User.query.get_or_404(user_id)
    nouveau_role = request.form.get("role")
    if nouveau_role in ("etudiant", "alumni", "bureau", "admin"):
        user.role = nouveau_role
        if nouveau_role == "bureau":
            user.fonction_bureau = request.form.get("fonction_bureau", user.fonction_bureau)
        db.session.commit()
        flash(f"Rôle de {user.nom_complet} mis à jour : {nouveau_role}.", "success")
    return redirect(url_for("admin.utilisateurs"))


@admin_bp.route("/messages")
@admin_required
def messages():
    msgs = MessageContact.query.order_by(MessageContact.date_envoi.desc()).all()
    return render_template("admin/messages.html", messages=msgs)


@admin_bp.route("/messages/<int:msg_id>/traiter", methods=["POST"])
@admin_required
def traiter_message(msg_id):
    msg = MessageContact.query.get_or_404(msg_id)
    msg.traite = True
    db.session.commit()
    flash("Message marqué comme traité.", "success")
    return redirect(url_for("admin.messages"))
