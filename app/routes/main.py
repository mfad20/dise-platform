from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user

from app.extensions import db
from app.models import (
    User, Evenement, Inscription, Actualite, Publication, Opportunite,
    ClubCommission, MessageContact, Contribution, DemandeMentorat, CompteurVisites,
    ROLE_ETUDIANT, ROLE_ALUMNI, ROLE_BUREAU,
)

main_bp = Blueprint("main", __name__)


# ---------------------------------------------------------------------------
# 6.1 Accueil
# ---------------------------------------------------------------------------
@main_bp.route("/")
def index():
    if not current_user.is_authenticated and not session.get("entree_choisie"):
        return render_template("entree.html")

    nb_alumni = User.query.filter(User.role.in_(["alumni"])).count()
    nb_etudiants = User.query.filter_by(role="etudiant").count()
    nb_promotions = db.session.query(User.promotion).filter(
        User.promotion.isnot(None)
    ).distinct().count()
    nb_pays = db.session.query(User.pays_residence).filter(
        User.pays_residence.isnot(None), User.pays_residence != ""
    ).distinct().count()
    nb_entreprises = db.session.query(User.entreprise).filter(
        User.entreprise.isnot(None), User.entreprise != ""
    ).distinct().count()
    nb_publications = Publication.query.count()

    dernieres_actus = Actualite.query.order_by(Actualite.date_publication.desc()).limit(3).all()
    prochains_evenements = (
        Evenement.query.filter(Evenement.date_debut >= datetime.utcnow())
        .order_by(Evenement.date_debut.asc()).limit(3).all()
    )
    publications_recentes = Publication.query.order_by(Publication.annee.desc()).limit(3).all()

    portraits_temoignages = User.query.filter_by(role="alumni").filter(
        User.bio.isnot(None), User.bio != ""
    ).order_by(User.id.desc()).limit(4).all()
    portrait_alumni = portraits_temoignages[0] if portraits_temoignages else None
    temoignages = portraits_temoignages[1:4]

    # "Président%" (et non "%président%") pour ne pas confondre avec
    # "Vice-Président" ; tri par id pour un résultat déterministe si
    # plusieurs bureaux se chevauchent en base.
    president = User.query.filter_by(role=ROLE_BUREAU).filter(
        User.fonction_bureau.ilike("président%")
    ).order_by(User.id.asc()).first()

    visiteurs = CompteurVisites.get_ou_creer()

    video_presentation_url = current_app.config.get("VIDEO_PRESENTATION_URL", "")
    video_est_externe = video_presentation_url.startswith(("http://", "https://"))

    kpis = dict(
        nb_alumni=nb_alumni, nb_etudiants=nb_etudiants, nb_promotions=nb_promotions,
        nb_pays=nb_pays, nb_entreprises=nb_entreprises, nb_publications=nb_publications,
    )
    return render_template(
        "index.html", kpis=kpis, actus=dernieres_actus, evenements=prochains_evenements,
        publications=publications_recentes, portrait=portrait_alumni,
        temoignages=temoignages, president=president, nb_visiteurs=visiteurs.total,
        video_presentation_url=video_presentation_url, video_est_externe=video_est_externe,
    )


@main_bp.route("/continuer")
def continuer_sans_compte():
    """Marque le choix « continuer sans compte » pour ne plus montrer
    la page d'entrée durant cette session navigateur."""
    session["entree_choisie"] = True
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# 6.2 La DISE
# ---------------------------------------------------------------------------
@main_bp.route("/la-dise")
def la_dise():
    bureau = User.query.filter_by(role="bureau").order_by(User.fonction_bureau).all()
    hall_of_fame = User.query.filter_by(role="alumni").filter(
        User.fonction_actuelle.isnot(None)
    ).order_by(User.id.desc()).limit(6).all()

    # Photos officielles du Bureau 2025-2026 (fournies par l'utilisateur).
    # Aucun nom n'est inventé : seule la fonction est affichée, les noms
    # réels devront être complétés par le Bureau lors de la mise en ligne.
    bureau_officiel = [
        {"role": "Président de la DISE", "nom": "N'Dré Lébé", "photo": "bureau/president_dise_2025_2026.jpeg"},
        {"role": "Vice-Président", "photo": "bureau/Vice_president.jpeg"},
        {"role": "Secrétaire Général", "photo": "bureau/secretaire_general.jpeg"},
        {"role": "Secrétaire Générale Adjointe", "photo": "bureau/secretaire_adjointe.jpeg"},
        {"role": "Trésorière Générale", "photo": "bureau/tresoriere_principale.jpeg"},
        {"role": "Trésorière Adjointe", "photo": "bureau/tresoriere_adjointe.jpeg"},
    ]

    return render_template(
        "la_dise.html", bureau=bureau, hall_of_fame=hall_of_fame,
        bureau_officiel=bureau_officiel,
    )


# ---------------------------------------------------------------------------
# 6.4 Vie de la DISE — Actualités
# ---------------------------------------------------------------------------
@main_bp.route("/actualites")
def actualites():
    categorie = request.args.get("categorie", "")
    q = request.args.get("q", "").strip()
    query = Actualite.query
    if categorie:
        query = query.filter_by(categorie=categorie)
    if q:
        query = query.filter(Actualite.titre.ilike(f"%{q}%"))
    actus = query.order_by(Actualite.date_publication.desc()).all()
    categories = [c[0] for c in db.session.query(Actualite.categorie).distinct().all()]
    return render_template("actualites.html", actus=actus, categories=categories,
                            categorie=categorie, q=q)


@main_bp.route("/actualites/<int:actu_id>")
def actualite_detail(actu_id):
    actu = Actualite.query.get_or_404(actu_id)
    autres = Actualite.query.filter(Actualite.id != actu_id).order_by(
        Actualite.date_publication.desc()
    ).limit(3).all()
    return render_template("actualite_detail.html", actu=actu, autres=autres)


# ---------------------------------------------------------------------------
# 6.5 Événements
# ---------------------------------------------------------------------------
@main_bp.route("/evenements")
def evenements():
    a_venir = Evenement.query.filter(Evenement.date_debut >= datetime.utcnow()).order_by(
        Evenement.date_debut.asc()
    ).all()
    passes = Evenement.query.filter(Evenement.date_debut < datetime.utcnow()).order_by(
        Evenement.date_debut.desc()
    ).all()
    return render_template("evenements.html", a_venir=a_venir, passes=passes)


@main_bp.route("/evenements/<int:evt_id>")
def evenement_detail(evt_id):
    evt = Evenement.query.get_or_404(evt_id)
    nb_inscrits = evt.inscriptions.count()
    deja_inscrit = False
    if current_user.is_authenticated:
        deja_inscrit = Inscription.query.filter_by(
            user_id=current_user.id, evenement_id=evt_id
        ).first() is not None
    return render_template("evenement_detail.html", evt=evt, nb_inscrits=nb_inscrits,
                            deja_inscrit=deja_inscrit)


@main_bp.route("/evenements/<int:evt_id>/inscription", methods=["POST"])
@login_required
def evenement_inscription(evt_id):
    evt = Evenement.query.get_or_404(evt_id)
    existe = Inscription.query.filter_by(user_id=current_user.id, evenement_id=evt_id).first()
    if existe:
        flash("Vous êtes déjà inscrit à cet événement.", "info")
    else:
        db.session.add(Inscription(user_id=current_user.id, evenement_id=evt_id))
        db.session.commit()
        flash(f"Inscription confirmée pour « {evt.titre} ». À bientôt !", "success")
    return redirect(url_for("main.evenement_detail", evt_id=evt_id))


# ---------------------------------------------------------------------------
# 6.6 Archives
# ---------------------------------------------------------------------------
@main_bp.route("/archives")
def archives():
    evenements_passes = Evenement.query.filter(
        Evenement.date_debut < datetime.utcnow()
    ).order_by(Evenement.date_debut.desc()).all()
    promotions = sorted({u.promotion for u in User.query.filter(
        User.promotion.isnot(None)).all()}, reverse=True)
    return render_template("archives.html", evenements=evenements_passes, promotions=promotions)


# ---------------------------------------------------------------------------
# 6.7 Publications
# ---------------------------------------------------------------------------
@main_bp.route("/publications")
def publications():
    type_filtre = request.args.get("type", "")
    query = Publication.query
    if type_filtre:
        query = query.filter_by(type_publication=type_filtre)
    pubs = query.order_by(Publication.annee.desc()).all()
    return render_template("publications.html", publications=pubs, type_filtre=type_filtre)


# ---------------------------------------------------------------------------
# 6.8 Opportunités
# ---------------------------------------------------------------------------
@main_bp.route("/opportunites")
def opportunites():
    type_filtre = request.args.get("type", "")
    pays_filtre = request.args.get("pays", "")
    query = Opportunite.query
    if type_filtre:
        query = query.filter_by(type_offre=type_filtre)
    if pays_filtre:
        query = query.filter_by(pays=pays_filtre)
    offres = query.order_by(Opportunite.date_limite.asc()).all()
    pays_list = [p[0] for p in db.session.query(Opportunite.pays).distinct().all()]
    return render_template("opportunites.html", offres=offres, pays_list=pays_list,
                            type_filtre=type_filtre, pays_filtre=pays_filtre,
                            today=date.today())


# ---------------------------------------------------------------------------
# 6.9 Communauté et Mentorat
# ---------------------------------------------------------------------------
@main_bp.route("/communaute")
def communaute():
    mentors = User.query.filter_by(est_mentor=True).all()
    clubs = ClubCommission.query.all()
    return render_template("communaute.html", mentors=mentors, clubs=clubs)


@main_bp.route("/communaute/mentorat/<int:mentor_id>/demande", methods=["POST"])
@login_required
def demande_mentorat(mentor_id):
    mentor = User.query.get_or_404(mentor_id)
    sujet = request.form.get("sujet")
    message = request.form.get("message", "")
    demande = DemandeMentorat(
        etudiant_id=current_user.id, mentor_id=mentor_id, sujet=sujet, message=message
    )
    db.session.add(demande)
    db.session.commit()
    flash(f"Votre demande de mentorat a été envoyée à {mentor.nom_complet}.", "success")
    return redirect(url_for("main.communaute"))


# ---------------------------------------------------------------------------
# 6.11 Galerie
# ---------------------------------------------------------------------------
@main_bp.route("/galerie")
def galerie():
    evenements_avec_photos = Evenement.query.filter(
        Evenement.affiche_url.isnot(None)
    ).order_by(Evenement.date_debut.desc()).all()
    albums_supplementaires = [
        {"titre": "ISE Championship 2025", "photo": "activites_passees/ISEchampionShip2025_image_famille.jpeg"},
        {"titre": "ISE Championship — Édition précédente", "photo": "activites_passees/ise_championship2.jpg"},
        {"titre": "Grande Rentrée des ISE — Akwaba", "photo": "activites_passees/Grande_rentree_image_famille_ise3.jpeg"},
        {"titre": "Rendez-vous des Experts — Coulisses", "photo": "annonces_activites/Rendez_des_experts_image_famille.jpeg"},
        {"titre": "Anniversaires DISE", "photo": "anniversaires/flyes_aniverssaire_dimi.jpeg"},
        {"titre": "Communauté DISE au complet", "photo": "brand/equipe_complet.jpg"},
        {"titre": "Remerciements de la promotion", "photo": "brand/photo_remerciement.jpg"},
        {"titre": "Goodies & gadgets DISE", "photo": "brand/gadgets.jpeg"},
    ]
    return render_template(
        "galerie.html", evenements=evenements_avec_photos,
        albums_supplementaires=albums_supplementaires,
    )


# ---------------------------------------------------------------------------
# 6.12 Contact
# ---------------------------------------------------------------------------
@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        sujet = request.form.get("sujet", "").strip()
        message = request.form.get("message", "").strip()

        erreurs = []
        if not nom:
            erreurs.append("Merci d'indiquer votre nom.")
        if not email or "@" not in email:
            erreurs.append("Merci d'indiquer une adresse e-mail valide.")
        if not message:
            erreurs.append("Merci de renseigner un message.")

        if erreurs:
            for e in erreurs:
                flash(e, "danger")
            return render_template("contact.html")

        msg = MessageContact(nom=nom, email=email, sujet=sujet or None, message=message)
        db.session.add(msg)
        db.session.commit()
        flash("Votre message a bien été envoyé au Bureau de la DISE. Merci !", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html")


# ---------------------------------------------------------------------------
# 6.13 Tableau de bord personnel
# ---------------------------------------------------------------------------
@main_bp.route("/tableau-de-bord")
@login_required
def dashboard():
    mes_contributions = Contribution.query.filter_by(user_id=current_user.id).order_by(
        Contribution.date_creation.desc()
    ).all()
    mes_evenements = (
        Evenement.query.join(Inscription).filter(Inscription.user_id == current_user.id)
        .order_by(Evenement.date_debut.desc()).all()
    )
    mes_demandes_mentorat = DemandeMentorat.query.filter_by(
        etudiant_id=current_user.id
    ).order_by(DemandeMentorat.date_creation.desc()).all()
    demandes_recues = []
    if current_user.est_mentor:
        demandes_recues = DemandeMentorat.query.filter_by(
            mentor_id=current_user.id
        ).order_by(DemandeMentorat.date_creation.desc()).all()
    return render_template(
        "dashboard.html", contributions=mes_contributions, evenements=mes_evenements,
        demandes=mes_demandes_mentorat, demandes_recues=demandes_recues,
    )


@main_bp.route("/tableau-de-bord/profil", methods=["POST"])
@login_required
def update_profil():
    champs_texte = [
        "fonction_actuelle", "entreprise", "secteur_activite", "pays_residence",
        "ville_residence", "bio", "domaine_expertise",
    ]
    for champ in champs_texte:
        valeur = request.form.get(champ)
        if valeur is not None:
            setattr(current_user, champ, valeur.strip())

    # Champs URL : on n'accepte que http(s) pour empêcher l'injection de
    # liens "javascript:" ou autres schémas dangereux dans les hyperliens
    # affichés sur la fiche annuaire (auto-XSS via href).
    for champ in ("linkedin", "autres_liens"):
        valeur = (request.form.get(champ) or "").strip()
        if not valeur:
            setattr(current_user, champ, None)
        elif valeur.startswith(("http://", "https://")):
            setattr(current_user, champ, valeur)
        else:
            flash(
                f"Le lien « {valeur} » a été ignoré : seules les adresses "
                "commençant par http:// ou https:// sont acceptées.", "warning"
            )

    current_user.visible_email = "visible_email" in request.form
    current_user.visible_telephone = "visible_telephone" in request.form
    db.session.commit()
    flash("Profil mis à jour avec succès.", "success")
    return redirect(url_for("main.dashboard"))
