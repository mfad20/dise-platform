"""
Coordonnées approximatives (latitude, longitude) des pays, utilisées pour
la carte des anciens de l'annuaire (section « carte des anciens »).
Une centaine de pays courants sont couverts ; un pays absent de ce
dictionnaire est simplement ignoré sur la carte (il reste néanmoins
filtrable via le champ "Pays de résidence" de l'annuaire).
"""

PAYS_COORDS = {
    "Côte d'Ivoire": (7.54, -5.55),
    "Sénégal": (14.50, -14.45),
    "Burkina Faso": (12.24, -1.56),
    "Mali": (17.57, -3.99),
    "Guinée": (9.95, -9.70),
    "Bénin": (9.31, 2.32),
    "Togo": (8.62, 0.82),
    "Niger": (17.61, 8.08),
    "Ghana": (7.95, -1.02),
    "Nigeria": (9.08, 8.68),
    "Cameroun": (7.37, 12.35),
    "Gabon": (-0.80, 11.61),
    "Congo": (-0.23, 15.83),
    "République Démocratique du Congo": (-4.04, 21.76),
    "Tchad": (15.45, 18.73),
    "Mauritanie": (21.01, -10.94),
    "Guinée-Bissau": (11.80, -15.18),
    "Guinée Équatoriale": (1.65, 10.27),
    "Rwanda": (-1.94, 29.87),
    "Burundi": (-3.37, 29.92),
    "Kenya": (-0.02, 37.91),
    "Éthiopie": (9.15, 40.49),
    "Maroc": (31.79, -7.09),
    "Algérie": (28.03, 1.66),
    "Tunisie": (33.89, 9.54),
    "Égypte": (26.82, 30.80),
    "Afrique du Sud": (-30.56, 22.94),
    "France": (46.60, 2.21),
    "Belgique": (50.50, 4.47),
    "Allemagne": (51.17, 10.45),
    "Royaume-Uni": (55.38, -3.44),
    "Suisse": (46.82, 8.23),
    "Espagne": (40.46, -3.75),
    "Italie": (41.87, 12.57),
    "Pays-Bas": (52.13, 5.29),
    "Portugal": (39.40, -8.22),
    "Canada": (56.13, -106.35),
    "États-Unis": (37.09, -95.71),
    "Chine": (35.86, 104.20),
    "Émirats Arabes Unis": (23.42, 53.85),
    "Qatar": (25.35, 51.18),
    "Arabie Saoudite": (23.89, 45.08),
    "Inde": (20.59, 78.96),
}


def coords_pays(nom_pays):
    """Retourne (lat, lng) pour un pays donné, ou None si inconnu."""
    if not nom_pays:
        return None
    return PAYS_COORDS.get(nom_pays.strip())
