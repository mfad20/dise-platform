import os
import warnings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_SECRET_KEY = "dise-dev-secret-key-change-me"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", _DEFAULT_SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'dise.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 Mo, pour les captures d'écran de paiement
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")

    # --- Sécurité des cookies de session ---------------------------------
    # SESSION_COOKIE_SECURE doit être activé (via l'env HTTPS_ONLY=1) dès que
    # le site est servi en HTTPS, pour empêcher tout envoi du cookie de
    # session en clair sur une connexion non chiffrée.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("HTTPS_ONLY", "0") == "1"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"

    # Vidéo de présentation affichée en page d'accueil (section 6.1).
    # Soit une URL d'intégration externe (YouTube/Vimeo "embed", commençant
    # par http/https), soit un chemin relatif au dossier static/ pour un
    # fichier vidéo local (ex. "img/annonces_activites/presentationdise.mp4").
    VIDEO_PRESENTATION_URL = os.environ.get(
        "VIDEO_PRESENTATION_URL", "img/annonces_activites/presentationdise.mp4"
    )


if Config.SECRET_KEY == _DEFAULT_SECRET_KEY:
    warnings.warn(
        "SECRET_KEY par défaut utilisée — à changer impérativement en "
        "production via la variable d'environnement SECRET_KEY (sinon les "
        "sessions et jetons de réinitialisation de mot de passe peuvent "
        "être falsifiés).",
        RuntimeWarning,
    )
