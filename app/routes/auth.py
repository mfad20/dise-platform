from datetime import datetime
import re

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.extensions import db
from app.models import User, ROLE_ETUDIANT, ROLE_ALUMNI, ROLE_BUREAU

auth_bp = Blueprint("auth", __name__)

RESET_TOKEN_MAX_AGE = 3600  # 1 heure, conforme au message affiché à l'utilisateur
RESET_TOKEN_SALT = "reinitialisation-mot-de-passe"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _generer_token_reset(user):
    return _serializer().dumps({"user_id": user.id}, salt=RESET_TOKEN_SALT)


def _verifier_token_reset(token):
    """Retourne l'utilisateur correspondant au token, ou None s'il est invalide/expiré."""
    try:
        data = _serializer().loads(token, salt=RESET_TOKEN_SALT, max_age=RESET_TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    return User.query.get(data.get("user_id"))


# ---------------------------------------------------------------------------
# 3.2.1 Connexion
# ---------------------------------------------------------------------------
@auth_bp.route("/connexion", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        identifiant = request.form.get("identifiant", "").strip().lower()
        password = request.form.get("password", "")
        remember = "remember" in request.form

        user = User.query.filter(
            (User.email == identifiant) | (User.telephone == identifiant)
        ).first()

        # Message générique : on ne révèle jamais si l'email existe (sécurité)
        if user is None or not user.check_password(password):
            flash("Identifiants incorrects. Merci de réessayer.", "danger")
            return render_template("auth/login.html")

        if not user.is_active_account:
            flash("Votre adresse e-mail n'est pas encore confirmée.", "warning")
            return render_template("auth/login.html")

        if not user.is_validated:
            flash(
                "Votre compte « Particulier privilégié » est en attente de "
                "validation par un Administrateur.", "warning"
            )
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        flash(f"Bienvenue, {user.prenoms} !", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/connexion/google")
def login_google():
    # Prototype : l'intégration OAuth Google réelle sera branchée en production.
    flash(
        "Connexion via Google — à brancher sur un vrai fournisseur OAuth "
        "(Google Identity Services) en production.", "info"
    )
    return redirect(url_for("auth.login"))


@auth_bp.route("/deconnexion")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# 3.2.2 Inscription
# ---------------------------------------------------------------------------
@auth_bp.route("/inscription", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenoms = request.form.get("prenoms", "").strip()
        email = request.form.get("email", "").strip().lower()
        telephone = request.form.get("telephone", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        profil = request.form.get("profil")  # etudiant / alumni / autre
        promotion = request.form.get("promotion")
        cgu = "cgu" in request.form

        erreurs = []
        if not all([nom, prenoms, email, password]):
            erreurs.append("Merci de renseigner tous les champs obligatoires.")
        if email and not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            erreurs.append("Merci d'indiquer une adresse e-mail valide.")
        if password != password_confirm:
            erreurs.append("Les deux mots de passe ne correspondent pas.")
        if len(password) < 8:
            erreurs.append("Le mot de passe doit contenir au moins 8 caractères.")
        if not cgu:
            erreurs.append(
                "Vous devez accepter les conditions d'utilisation et la "
                "politique de confidentialité."
            )
        if User.query.filter_by(email=email).first():
            erreurs.append("Un compte existe déjà avec cet e-mail.")
        if telephone and User.query.filter_by(telephone=telephone).first():
            erreurs.append("Un compte existe déjà avec ce numéro de téléphone.")

        if erreurs:
            for e in erreurs:
                flash(e, "danger")
            return render_template("auth/register.html")

        role = ROLE_ETUDIANT if profil == "etudiant" else (
            ROLE_ALUMNI if profil == "alumni" else ROLE_BUREAU
        )
        promotion_valeur = int(promotion) if promotion and promotion.isdigit() else None
        user = User(
            nom=nom, prenoms=prenoms, email=email, telephone=telephone or None,
            role=role,
            promotion=promotion_valeur,
            is_active_account=True,   # simulé : en prod, activation par lien e-mail
            is_validated=(role != ROLE_BUREAU),  # comptes Bureau validés manuellement
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == ROLE_BUREAU:
            flash(
                "Votre compte a été créé et est en attente de validation "
                "par un Administrateur (profil Particulier privilégié).", "info"
            )
        else:
            flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ---------------------------------------------------------------------------
# 3.2.3 Mot de passe oublié
# ---------------------------------------------------------------------------
@auth_bp.route("/mot-de-passe-oublie", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        identifiant = request.form.get("identifiant", "").strip().lower()
        user = User.query.filter(
            (User.email == identifiant) | (User.telephone == identifiant)
        ).first()

        # On ne révèle jamais si le compte existe via le message affiché à
        # l'utilisateur (protection contre l'énumération de comptes). En
        # l'absence de serveur e-mail configuré sur cette plateforme de
        # démonstration, le lien est journalisé côté serveur : à un
        # administrateur de le relayer manuellement (en production, il
        # partirait par e-mail).
        if user is not None:
            token = _generer_token_reset(user)
            lien = url_for("auth.reset_password", token=token, _external=True)
            current_app.logger.info(
                "Lien de réinitialisation pour %s (%s) : %s", user.email, user.id, lien
            )

        flash(
            "Si un compte correspond à ces informations, un lien de "
            "réinitialisation valable 1 heure vient d'être envoyé.", "success"
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html")


@auth_bp.route("/reinitialiser-mot-de-passe/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = _verifier_token_reset(token)
    if user is None:
        flash(
            "Ce lien de réinitialisation est invalide ou a expiré. "
            "Merci de refaire une demande.", "danger"
        )
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if password != password_confirm:
            flash("Les deux mots de passe ne correspondent pas.", "danger")
            return render_template("auth/reset_password.html", token=token)
        if len(password) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.", "danger")
            return render_template("auth/reset_password.html", token=token)

        user.set_password(password)
        db.session.commit()
        flash("Mot de passe réinitialisé avec succès. Vous pouvez vous connecter.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)
