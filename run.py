import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # SÉCURITÉ : le mode debug (débogueur Werkzeug interactif) ne doit
    # JAMAIS être actif en production — il permettrait l'exécution de code
    # Python arbitraire depuis le navigateur en cas d'erreur 500. Il est
    # désormais désactivé par défaut et ne s'active qu'en développement via
    # la variable d'environnement FLASK_DEBUG=1.
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
