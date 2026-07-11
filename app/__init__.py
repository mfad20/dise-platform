from datetime import datetime

from flask import Flask, render_template, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Derrière le proxy inverse de Render (ou tout hébergeur similaire), la
    # requête WSGI arrive en HTTP côté application même si le client parle
    # en HTTPS : sans ProxyFix, url_for(..., _external=True) générerait des
    # liens http:// (ex. réinitialisation de mot de passe) et les cookies
    # "Secure" seraient mal évalués.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # --- Blueprints -----------------------------------------------------
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.annuaire import annuaire_bp
    from app.routes.finances import finances_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(annuaire_bp, url_prefix="/annuaire")
    app.register_blueprint(finances_bp, url_prefix="/finances")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # --- Compteur des visiteurs (section 6.1) ----------------------------
    # Ignore les fichiers statiques (CSS/JS/images) pour ne pas déclencher
    # une lecture de session + requête DB sur chaque asset d'une page.
    @app.before_request
    def compter_visite():
        if request.endpoint == "static":
            return
        if not session.get("_a_visite"):
            from app.models import CompteurVisites
            session["_a_visite"] = True
            compteur = CompteurVisites.get_ou_creer()
            compteur.total += 1
            db.session.commit()

    # --- Context globalement disponible dans les templates --------------
    @app.context_processor
    def inject_globals():
        from app.models import Evenement, Actualite
        prochains_evenements = (
            Evenement.query.filter(Evenement.date_debut >= datetime.utcnow())
            .order_by(Evenement.date_debut.asc())
            .limit(3)
            .all()
        )
        return dict(
            now=datetime.utcnow(),
            nav_prochains_evenements=prochains_evenements,
        )

    # --- Filtres Jinja utiles ---------------------------------------------
    @app.template_filter("fcfa")
    def fcfa_format(value):
        try:
            return f"{int(value):,}".replace(",", " ") + " FCFA"
        except (TypeError, ValueError):
            return value

    @app.template_filter("date_fr")
    def date_fr(value, fmt="%d %B %Y"):
        mois_fr = {
            "January": "janvier", "February": "février", "March": "mars",
            "April": "avril", "May": "mai", "June": "juin", "July": "juillet",
            "August": "août", "September": "septembre", "October": "octobre",
            "November": "novembre", "December": "décembre",
        }
        if not value:
            return ""
        s = value.strftime(fmt)
        for en, fr in mois_fr.items():
            s = s.replace(en, fr)
        return s

    with app.app_context():
        db.create_all()

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()  # évite qu'une transaction en échec ne pollue la requête suivante
        return render_template("errors/500.html"), 500

    return app
