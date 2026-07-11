import unicodedata

from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user

from app.models import User, ROLE_ETUDIANT, ROLE_ALUMNI, ROLE_BUREAU, ROLE_ADMIN

annuaire_bp = Blueprint("annuaire", __name__)


CHAMPS_RECHERCHE = [
    "nom", "prenoms", "fonction_actuelle", "entreprise", "domaine_expertise",
    "secteur_activite", "pays_residence", "ville_residence", "filiere",
    "bio", "sujet_these", "promotion",
]


def _sans_accents(valeur):
    if valeur is None or valeur == "":
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(valeur))
        if not unicodedata.combining(c)
    ).lower()


def _correspond_recherche(user, termes_normalises):
    """
    Recherche « intelligente » : chaque terme doit correspondre à au moins
    un champ du profil (ET entre termes, OU entre champs), insensible à la
    casse ET aux accents — « economiste abidjan » retrouve ainsi un profil
    dont la fonction est « Économiste » basé à « Abidjan ».
    """
    valeurs = [_sans_accents(getattr(user, champ, None)) for champ in CHAMPS_RECHERCHE]
    valeurs.append(_sans_accents(user.nom_complet))
    return all(any(terme in valeur for valeur in valeurs) for terme in termes_normalises)


def _query_filtree(args):
    query = User.query.filter(User.role.in_([ROLE_ETUDIANT, ROLE_ALUMNI, ROLE_BUREAU, ROLE_ADMIN]))

    for champ, colonne in [
        ("promotion", User.promotion), ("pays", User.pays_residence),
        ("secteur", User.secteur_activite), ("fonction", User.fonction_actuelle),
        ("filiere", User.filiere), ("entreprise", User.entreprise),
    ]:
        valeur = args.get(champ, "").strip()
        if valeur:
            if champ == "promotion":
                if valeur.isdigit():
                    query = query.filter(colonne == int(valeur))
            else:
                query = query.filter(colonne == valeur)

    if args.get("doctorant") == "1":
        query = query.filter(User.doctorant.is_(True))

    return query


RESULTATS_PAR_PAGE = 24


@annuaire_bp.route("/")
def liste():
    query = _query_filtree(request.args)
    tri = request.args.get("tri", "promotion")
    if tri == "nom":
        query = query.order_by(User.nom.asc())
    else:
        query = query.order_by(User.promotion.desc().nullslast(), User.nom.asc())

    alumni = query.all()

    q = request.args.get("q", "").strip()
    if q:
        termes_normalises = [_sans_accents(t) for t in q.split()]
        alumni = [u for u in alumni if _correspond_recherche(u, termes_normalises)]

    nb_resultats = len(alumni)

    # Pagination manuelle : le filtrage textuel ci-dessus s'effectue en
    # Python (recherche insensible aux accents sur plusieurs champs), la
    # pagination doit donc aussi être appliquée en Python, après filtrage.
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    nb_pages = max(1, (nb_resultats + RESULTATS_PAR_PAGE - 1) // RESULTATS_PAR_PAGE)
    page = min(page, nb_pages)
    debut = (page - 1) * RESULTATS_PAR_PAGE
    alumni_page = alumni[debut:debut + RESULTATS_PAR_PAGE]

    # Facettes pour les filtres (valeurs distinctes existantes en base)
    promotions = sorted({u.promotion for u in User.query.filter(
        User.promotion.isnot(None)).all()}, reverse=True)
    pays = sorted({u.pays_residence for u in User.query.filter(
        User.pays_residence.isnot(None), User.pays_residence != "").all()})
    secteurs = sorted({u.secteur_activite for u in User.query.filter(
        User.secteur_activite.isnot(None), User.secteur_activite != "").all()})
    fonctions = sorted({u.fonction_actuelle for u in User.query.filter(
        User.fonction_actuelle.isnot(None), User.fonction_actuelle != "").all()})

    # Répartition par promotion et par pays (mini data-center annuaire, §7)
    repartition_promotion = {}
    repartition_pays = {}
    for u in User.query.filter(User.role.in_([ROLE_ETUDIANT, ROLE_ALUMNI])).all():
        if u.promotion:
            repartition_promotion[u.promotion] = repartition_promotion.get(u.promotion, 0) + 1
        if u.pays_residence and u.visible_localisation:
            repartition_pays[u.pays_residence] = repartition_pays.get(u.pays_residence, 0) + 1

    return render_template(
        "annuaire/liste.html", alumni=alumni_page, promotions=promotions, pays=pays,
        secteurs=secteurs, fonctions=fonctions, args=request.args,
        repartition_promotion=sorted(repartition_promotion.items(), reverse=True),
        repartition_pays=sorted(repartition_pays.items(), key=lambda x: -x[1]),
        nb_resultats=nb_resultats, page=page, nb_pages=nb_pages,
    )


@annuaire_bp.route("/carte")
def carte():
    """Carte des anciens : répartition géographique par pays de résidence."""
    from app.geo import coords_pays

    repartition_pays = {}
    for u in User.query.filter(
        User.role.in_([ROLE_ETUDIANT, ROLE_ALUMNI, ROLE_BUREAU, ROLE_ADMIN]),
        User.pays_residence.isnot(None), User.pays_residence != "",
        User.visible_localisation.is_(True),
    ).all():
        repartition_pays[u.pays_residence] = repartition_pays.get(u.pays_residence, 0) + 1

    points = []
    pays_non_localises = []
    for nom_pays, effectif in repartition_pays.items():
        coords = coords_pays(nom_pays)
        if coords:
            points.append({"pays": nom_pays, "lat": coords[0], "lng": coords[1], "effectif": effectif})
        else:
            pays_non_localises.append((nom_pays, effectif))

    return render_template(
        "annuaire/carte.html", points=points,
        pays_non_localises=sorted(pays_non_localises, key=lambda x: -x[1]),
        nb_pays=len(repartition_pays), nb_alumni_localises=sum(p["effectif"] for p in points),
    )


@annuaire_bp.route("/<int:user_id>")
def fiche(user_id):
    alumnus = User.query.get_or_404(user_id)
    peut_voir_contact = False
    if current_user.is_authenticated:
        peut_voir_contact = current_user.is_bureau_or_admin or alumnus.visible_email
    return render_template(
        "annuaire/fiche.html", alumnus=alumnus, peut_voir_contact=peut_voir_contact
    )


@annuaire_bp.route("/<int:user_id>/export.pdf")
@login_required
def export_fiche(user_id):
    """
    Export simplifié de la fiche (texte brut). Un vrai export PDF
    (WeasyPrint / ReportLab) peut être branché ici en production.
    """
    alumnus = User.query.get_or_404(user_id)
    contenu = (
        f"FICHE ANNUAIRE DISE\n\n"
        f"Nom : {alumnus.nom_complet}\n"
        f"Promotion : {alumnus.promotion or '-'}\n"
        f"Fonction : {alumnus.fonction_actuelle or '-'}\n"
        f"Entreprise : {alumnus.entreprise or '-'}\n"
        f"Secteur : {alumnus.secteur_activite or '-'}\n"
        f"Pays : {alumnus.pays_residence or '-'}\n"
        f"Domaines d'expertise : {alumnus.domaine_expertise or '-'}\n"
    )
    response = make_response(contenu)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=fiche_{alumnus.nom}.txt"
    )
    return response
