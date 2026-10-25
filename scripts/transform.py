#!/usr/bin/env python3
"""
scripts/transform.py
Nettoie, filtre, normalise et fusionne les données brutes des 8 métropoles principales
et des autres villes en un seul fichier GeoJSON normalisé : data/pav.geojson.

PÉRIMÈTRE STRICT : Uniquement les bornes d'apport volontaire (PAV) de déchets alimentaires / biodéchets.
Exclusion des composteurs partagés et collectifs (sauf jeux parisiens/lyonnais spécifiés).

Groupes :
- "principales" : Paris, Lyon, Toulouse, Nantes, Bordeaux, Montpellier, Rennes, Lille (couleur verte)
- "autres" : Strasbourg, Mulhouse, Marseille / Aix-en-Provence, etc. (couleur rouge)

Schéma normalisé par Feature :
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [lon, lat]  # EPSG:4326 / WGS84 arrondi à 5 décimales
  },
  "properties": {
    "ville": "lyon",
    "nom": "Bornes à compost — Parc de la Tête d'Or",
    "adresse": "...",
    "type": "borne_compost",
    "source": "data.grandlyon.com",
    "source_url": "https://...",
    "groupe": "principales"     # "principales" | "autres"
  }
}
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from pyproj import Transformer

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "pav.geojson"

# Transformateur Lambert-93 (EPSG:2154) -> WGS84 (EPSG:4326)
transformer_2154_to_4326 = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)


def parse_coords(geom, props=None):
    """
    Extrait [lon, lat] en WGS84, convertit si Lambert-93,
    vérifie la validité des coordonnées en France métropolitaine.
    """
    if not geom or not isinstance(geom, dict):
        return None
    coords = geom.get("coordinates")
    if not coords:
        return None

    gtype = geom.get("type", "")
    if gtype == "Point":
        if len(coords) < 2 or coords[0] is None or coords[1] is None:
            return None
        x, y = float(coords[0]), float(coords[1])
    elif gtype == "MultiPoint" and len(coords) > 0 and len(coords[0]) >= 2:
        x, y = float(coords[0][0]), float(coords[0][1])
    else:
        return None

    # Détection Lambert-93 (coordonnées en mètres, > 100 000)
    if x > 100000 or y > 100000:
        lon, lat = transformer_2154_to_4326.transform(x, y)
    else:
        lon, lat = x, y

    # Vérification d'emprise géographique (France métropolitaine)
    if not (-6.0 <= lon <= 11.0 and 41.0 <= lat <= 52.0):
        return None

    return round(lon, 5), round(lat, 5)


def clean_text(text: str) -> str:
    """Nettoie les espaces multiples et caractères indésirables."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text


def load_raw_json(filename: str):
    path = RAW_DIR / filename
    if not path.exists():
        print(f"   [AVERTISSEMENT] Fichier manquant : {filename}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"   [ERREUR] Lecture de {filename}: {e}")
        return None


# =============================================================================
# 1. MÉTROPOLES PRINCIPALES (groupe: "principales")
# =============================================================================

def transform_paris():
    features = []

    # 1.1 PAVDA (Abri-bacs Déchets Alimentaires)
    pavda_data = load_raw_json("paris_pavda.geojson")
    if pavda_data:
        for ft in pavda_data.get("features", []):
            props = ft.get("properties", {})
            etat = clean_text(props.get("pavda_etat", "")).upper()
            if etat in ["SUPPRIME", "ABANDONNE"]:
                continue

            coords = parse_coords(ft.get("geometry"), props)
            if not coords:
                continue

            idt = clean_text(props.get("pavda_idt", ""))
            adr = clean_text(props.get("adr", ""))
            arrdt = clean_text(props.get("arrdt", ""))
            full_addr = f"{adr}, {arrdt} Paris".strip(", ")

            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coords)},
                "properties": {
                    "ville": "paris",
                    "nom": f"Abri-bac Déchets Alimentaires ({idt})" if idt else "Abri-bac Déchets Alimentaires",
                    "adresse": full_addr,
                    "type": "abri_bac",
                    "source": "opendata.paris.fr",
                    "source_url": "https://opendata.paris.fr/explore/dataset/dechets-menagers-pavda/",
                    "groupe": "principales"
                }
            })

    # 1.2 Stations Trilib'
    trilib_data = load_raw_json("paris_trilib.geojson")
    if trilib_data:
        for ft in trilib_data.get("features", []):
            props = ft.get("properties", {})
            statut = clean_text(props.get("emplacement_statut", "")).lower()
            if "retir" in statut or "hors service" in statut:
                continue

            coords = parse_coords(ft.get("geometry"), props)
            if not coords:
                continue

            identifiant = clean_text(props.get("identifiant", ""))
            adr = clean_text(props.get("adr", ""))
            arrdt = clean_text(props.get("arrdt", ""))
            full_addr = f"{adr}, {arrdt} Paris".strip(", ")

            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coords)},
                "properties": {
                    "ville": "paris",
                    "nom": f"Station Trilib' ({identifiant})" if identifiant else "Station Trilib'",
                    "adresse": full_addr,
                    "type": "pav_biodechets",
                    "source": "opendata.paris.fr",
                    "source_url": "https://opendata.paris.fr/explore/dataset/dechets-menagers-points-dapport-volontaire-stations-trilib/",
                    "groupe": "principales"
                }
            })

    return features


def transform_lyon():
    features = []
    data = load_raw_json("lyon_bornes_compost.geojson")
    if not data:
        return features

    for ft in data.get("features", []):
        props = ft.get("properties", {})
        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        identifiant = clean_text(props.get("identifiant") or props.get("idemplacementsilo", ""))
        adr = clean_text(props.get("adresse", ""))
        commune = clean_text(props.get("commune", ""))
        full_addr = f"{adr}, {commune}".strip(", ")

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "lyon",
                "nom": f"Borne à compost ({identifiant})" if identifiant else "Borne à compost",
                "adresse": full_addr,
                "type": "borne_compost",
                "source": "data.grandlyon.com",
                "source_url": "https://data.grandlyon.com/jeux-de-donnees/bornes-compost-metropole-lyon/donnees",
                "groupe": "principales"
            }
        })
    return features


def transform_toulouse():
    features = []
    data = load_raw_json("toulouse_pav.geojson")
    if not data:
        return features

    for ft in data.get("features", []):
        props = ft.get("properties", {})
        type_flux = clean_text(props.get("type_flux", "")).lower()

        if not any(k in type_flux for k in ["alimentaire", "compost", "biodéchet", "biodechet"]):
            continue

        etat = clean_text(props.get("etat_fonctionnement", "")).lower()
        if "supprim" in etat or "hors service" in etat:
            continue

        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        id_metier = clean_text(props.get("id_metier", ""))
        numero = clean_text(props.get("numero_voie", "")).replace("NNNN", "").strip()
        voie = clean_text(props.get("voie", ""))
        cp = clean_text(props.get("code_postal", ""))
        commune = clean_text(props.get("commune", ""))

        rue = f"{numero} {voie}".strip()
        ville_cp = f"{cp} {commune}".strip()
        full_addr = f"{rue}, {ville_cp}".strip(", ")

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "toulouse",
                "nom": f"PAV Déchets Alimentaires ({id_metier})" if id_metier else "PAV Déchets Alimentaires",
                "adresse": full_addr,
                "type": "borne_compost",
                "source": "data.toulouse-metropole.fr",
                "source_url": "https://data.toulouse-metropole.fr/explore/dataset/points-dapport-volontaire-dechets-et-moyens-techniques/",
                "groupe": "principales"
            }
        })
    return features


def transform_nantes():
    features = []
    bio_data = load_raw_json("nantes_biodechets.geojson")
    if not bio_data:
        return features

    for ft in bio_data.get("features", []):
        props = ft.get("properties", {})
        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        adr = clean_text(props.get("adresse", ""))
        commune = clean_text(props.get("commune", ""))
        full_addr = f"{adr}, {commune}".strip(", ")

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "nantes",
                "nom": "Point d'apport biodéchets",
                "adresse": full_addr,
                "type": "colonne_biodechets",
                "source": "data.nantesmetropole.fr",
                "source_url": "https://data.nantesmetropole.fr/explore/dataset/244400404_point-collecte-dechets-alimentaires-biodechet-nantes/",
                "groupe": "principales"
            }
        })
    return features


def transform_bordeaux():
    features = []
    empac_data = load_raw_json("bordeaux_empac.geojson")
    if not empac_data:
        return features

    for ft in empac_data.get("features", []):
        props = ft.get("properties", {})
        nature = clean_text(props.get("nature", "")).lower()
        if not any(k in nature for k in ["biod", "compost", "alimentaire"]):
            continue

        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        ident = clean_text(props.get("ident", ""))
        adr = clean_text(props.get("adresse", ""))

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "bordeaux",
                "nom": f"PAV Biodéchets ({ident})" if ident else "PAV Biodéchets",
                "adresse": adr,
                "type": "borne_compost",
                "source": "datahub.bordeaux-metropole.fr",
                "source_url": "https://datahub.bordeaux-metropole.fr/explore/dataset/en_empac_p/",
                "groupe": "principales"
            }
        })
    return features


def transform_montpellier():
    features = []
    pav_data = load_raw_json("montpellier_pav.json")
    if not pav_data:
        return features

    for ft in pav_data.get("features", []):
        props = ft.get("properties", {})
        flux = clean_text(props.get("flux", "")).lower()
        if not any(k in flux for k in ["biod", "compost", "alimentaire"]):
            continue

        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        num_col = clean_text(props.get("num_col", ""))
        adr = clean_text(props.get("adresse", ""))
        commune = clean_text(props.get("commune", ""))
        full_addr = f"{adr}, {commune}".strip(", ")

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "montpellier",
                "nom": f"PAV Biodéchets ({num_col})" if num_col else "PAV Biodéchets",
                "adresse": full_addr,
                "type": "borne_compost",
                "source": "data.montpellier3m.fr",
                "source_url": "https://data.montpellier3m.fr/dataset/points-dapport-volontaires-de-montpellier-mediterranee-metropole",
                "groupe": "principales"
            }
        })
    return features


def transform_rennes():
    features = []
    data = load_raw_json("rennes_pav.geojson")
    if not data:
        return features

    for ft in data.get("features", []):
        props = ft.get("properties", {})
        is_da = (
            props.get("flux_da") == 1
            or "da" in clean_text(props.get("code_carto", "")).lower().split("-")
            or "alimentaire" in clean_text(props.get("contenu", "")).lower()
        )
        if not is_da:
            continue

        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        id_pav = clean_text(props.get("id_pav", ""))
        adr = clean_text(props.get("adresse_complete", ""))

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "rennes",
                "nom": f"PAV Déchets Alimentaires ({id_pav})" if id_pav else "PAV Déchets Alimentaires",
                "adresse": adr,
                "type": "borne_compost",
                "source": "data.rennesmetropole.fr",
                "source_url": "https://data.rennesmetropole.fr/explore/dataset/points-apport-volontaire/",
                "groupe": "principales"
            }
        })
    return features


def transform_lille():
    features = []

    # Couche officielle pav-dechets-alimentaires.lillemetropole.fr
    da_data = load_raw_json("lille_pav_da.geojson")
    if da_data:
        for ft in da_data.get("features", []):
            props = ft.get("properties", {})
            coords = parse_coords(ft.get("geometry"), props)
            if not coords:
                continue

            identifiant = clean_text(props.get("IDENTIFIANT_PAV", ""))
            adr = clean_text(props.get("ADRESSE", ""))
            commune = clean_text(props.get("COMMUNE", ""))
            full_addr = f"{adr}, {commune}".strip(", ")

            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coords)},
                "properties": {
                    "ville": "lille",
                    "nom": f"PAV Déchets Alimentaires ({identifiant})" if identifiant else "PAV Déchets Alimentaires",
                    "adresse": full_addr,
                    "type": "borne_compost",
                    "source": "pav-dechets-alimentaires.lillemetropole.fr",
                    "source_url": "https://pav-dechets-alimentaires.lillemetropole.fr/",
                    "groupe": "principales"
                }
            })

    # État du parc PAV MEL (si flux biodéchets)
    general_data = load_raw_json("lille_pav_general.geojson")
    if general_data:
        for ft in general_data.get("features", []):
            props = ft.get("properties", {})
            tf = clean_text(props.get("type_flux", "")).lower()
            if not any(k in tf for k in ["alimentaire", "compost", "biodéchet", "biodechet"]):
                continue

            coords = parse_coords(ft.get("geometry"), props)
            if not coords:
                continue

            identifiant = clean_text(props.get("identifiant_pav", ""))
            adr = clean_text(props.get("adresse", ""))
            commune = clean_text(props.get("commune", ""))
            full_addr = f"{adr}, {commune}".strip(", ")

            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coords)},
                "properties": {
                    "ville": "lille",
                    "nom": f"PAV Déchets Alimentaires ({identifiant})" if identifiant else "PAV Déchets Alimentaires",
                    "adresse": full_addr,
                    "type": "borne_compost",
                    "source": "data.lillemetropole.fr",
                    "source_url": "https://data.lillemetropole.fr/",
                    "groupe": "principales"
                }
            })

    return features


# =============================================================================
# 2. AUTRES VILLES (groupe: "autres", affichage en ROUGE)
# =============================================================================

def transform_strasbourg():
    features = []
    data = load_raw_json("strasbourg_pav_da.geojson")
    if not data:
        return features

    for ft in data.get("features", []):
        props = ft.get("properties", {})
        statut = clean_text(props.get("statut", "")).lower()
        if "supprim" in statut or "hors" in statut:
            continue

        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        num_empl = clean_text(props.get("num_empl_bio", ""))
        loc = clean_text(props.get("localisation", ""))
        quartier = clean_text(props.get("quartier", ""))
        commune = clean_text(props.get("commune", "")) or "Strasbourg"

        loc_parts = [p for p in [loc, quartier, commune] if p]
        full_addr = ", ".join(loc_parts)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "strasbourg",
                "nom": f"Borne Déchets Alimentaires ({num_empl})" if num_empl else "Borne Déchets Alimentaires",
                "adresse": full_addr,
                "type": "borne_compost",
                "source": "data.strasbourg.eu",
                "source_url": "https://data.strasbourg.eu/explore/dataset/dc_pav_borne_dalim/",
                "groupe": "principales"
            }
        })
    return features


def transform_mulhouse():
    features = []
    data = load_raw_json("mulhouse_pav_da.geojson")
    if not data:
        return features

    for ft in data.get("features", []):
        props = ft.get("properties", {})
        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        id_borne = clean_text(props.get("id", ""))
        adr = clean_text(props.get("adresse", ""))
        commune = clean_text(props.get("com_nom", "")) or "Mulhouse"
        full_addr = f"{adr}, {commune}".strip(", ")

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "mulhouse",
                "nom": f"Borne Biodéchets ({id_borne})" if id_borne else "Borne Biodéchets",
                "adresse": full_addr,
                "type": "borne_compost",
                "source": "data.mulhouse-alsace.fr",
                "source_url": "https://data.mulhouse-alsace.fr/explore/dataset/m2a_borne_biodechet-m2a/",
                "groupe": "autres"
            }
        })
    return features


def transform_marseille():
    features = []
    data = load_raw_json("marseille_pav_da.geojson")
    if not data:
        return features

    for ft in data.get("features", []):
        props = ft.get("properties", {})
        type_flux = clean_text(props.get("type_flux", "")).lower()

        # Filtrer uniquement sur les biodéchets
        if not any(k in type_flux for k in ["biodechet", "biodéchet", "alimentaire"]):
            continue

        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue

        num_pav = clean_text(props.get("num_pav") or props.get("id", ""))
        adr = clean_text(props.get("signalement_1", ""))
        commune = clean_text(props.get("commune", "")) or "Marseille"
        full_addr = f"{adr}, {commune}".strip(", ")

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "marseille",
                "nom": f"PAV Biodéchets ({num_pav})" if num_pav else "PAV Biodéchets",
                "adresse": full_addr,
                "type": "borne_compost",
                "source": "data.ampmetropole.fr",
                "source_url": "https://data.ampmetropole.fr/explore/dataset/ol-pav-harmonise/",
                "groupe": "principales"
            }
        })
    return features


def transform_tours():
    features = []
    data = load_raw_json("tours_pav_da.geojson")
    if not data:
        return features
    for ft in data.get("features", []):
        props = ft.get("properties", {})
        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue
        num = clean_text(props.get("numerotation", ""))
        adr = clean_text(props.get("adresse", ""))
        commune = clean_text(props.get("commune", "")) or "Tours"
        full_addr = f"{adr}, {commune}".strip(", ")
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "tours",
                "nom": f"Abri-bac {num} — Déchets alimentaires" if num else "Abri-bac Déchets Alimentaires",
                "adresse": full_addr,
                "type": "abri_bac",
                "source": "data.tours-metropole.fr",
                "source_url": "https://data.tours-metropole.fr/explore/dataset/dechets_alimentaires/",
                "groupe": "principales"
            }
        })
    return features


def transform_gpso():
    features = []
    data = load_raw_json("gpso_abri_bac.geojson")
    if not data:
        return features
    for ft in data.get("features", []):
        props = ft.get("properties", {})
        contenu = clean_text(props.get("contenu", "")).lower()
        if "alimentaire" not in contenu and "biodechet" not in contenu:
            continue
        coords = parse_coords(ft.get("geometry"), props)
        if not coords:
            continue
        pav_id = clean_text(props.get("id", ""))
        loc = clean_text(props.get("localisation", ""))
        commune = clean_text(props.get("commune", "")).title() or "GPSO"
        full_addr = f"{loc}, {commune}".strip(", ")
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(coords)},
            "properties": {
                "ville": "gpso",
                "nom": f"Abri-bac {pav_id} — Déchets alimentaires" if pav_id else "Abri-bac Déchets Alimentaires",
                "adresse": full_addr,
                "type": "abri_bac",
                "source": "data.seineouest.fr",
                "source_url": "https://data.seineouest.fr/explore/dataset/abri-bac/",
                "groupe": "principales"
            }
        })
    return features


def transform_rouen():
    features = []
    data = load_raw_json("rouen_pav.geojson")
    if not data:
        return features
    for ft in data.get("features", []):
        props = ft.get("properties", {})
        typ = clean_text(props.get("pavtyp", "")).lower()
        if any(k in typ for k in ["biod", "alimentaire", "compost"]):
            coords = parse_coords(ft.get("geometry"), props)
            if not coords:
                continue
            nom = clean_text(props.get("pavnom", "PAV Biodéchets"))
            adr = clean_text(props.get("adresse", ""))
            commune = clean_text(props.get("commune", ""))
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coords)},
                "properties": {
                    "ville": "rouen",
                    "nom": nom,
                    "adresse": f"{adr}, {commune}".strip(", "),
                    "type": "pav_biodechets",
                    "source": "data.metropole-rouen-normandie.fr",
                    "source_url": "https://data.metropole-rouen-normandie.fr/explore/dataset/donmetdec_pav/",
                    "groupe": "autres"
                }
            })
    return features


def transform_orleans():
    features = []
    data = load_raw_json("orleans_pav.geojson")
    if not data:
        return features
    for ft in data.get("features", []):
        props = ft.get("properties", {})
        typ = clean_text(props.get("garbage_types", "")).lower()
        if any(k in typ for k in ["biod", "alimentaire", "compost", "bio"]):
            coords = parse_coords(ft.get("geometry"), props)
            if not coords:
                continue
            adr = clean_text(props.get("street_name", ""))
            city = clean_text(props.get("city_name", ""))
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coords)},
                "properties": {
                    "ville": "orleans",
                    "nom": "PAV Biodéchets",
                    "adresse": f"{adr}, {city}".strip(", "),
                    "type": "colonne_biodechets",
                    "source": "data.orleans-metropole.fr",
                    "source_url": "https://data.orleans-metropole.fr/explore/dataset/dechets_pav/",
                    "groupe": "autres"
                }
            })
    return features


def transform_metz():
    features = []
    data = load_raw_json("metz_pav.geojson")
    if not data:
        return features
    for ft in data.get("features", []):
        props = ft.get("properties", {})
        contenu = clean_text(props.get("contenu", "")).lower()
        if any(k in contenu for k in ["biod", "alimentaire", "compost"]):
            coords = parse_coords(ft.get("geometry"), props)
            if not coords:
                continue
            rue = clean_text(props.get("rue", ""))
            comm = clean_text(props.get("comm", ""))
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(coords)},
                "properties": {
                    "ville": "metz",
                    "nom": "PAV Déchets Alimentaires",
                    "adresse": f"{rue}, {comm}".strip(", "),
                    "type": "pav_biodechets",
                    "source": "data.gouv.fr",
                    "source_url": "https://www.data.gouv.fr/fr/datasets/point-dapport-volontaire-eurometropole-de-metz/",
                    "groupe": "autres"
                }
            })
    return features


# Villes du plan en attente de flux biodéchets ouvert
VILLES_SANS_DONNEES = [
    {"id": "nice", "nom": "Nice (Métropole NCA)", "statut": "Flux biodéchets non séparé en open data"},
    {"id": "grenoble", "nom": "Grenoble-Alpes-Métropole", "statut": "Flux biodéchets non publié en open data"},
    {"id": "montreuil", "nom": "Montreuil", "statut": "Composteurs collectifs uniquement (hors périmètre PAV)"},
    {"id": "rouen", "nom": "Métropole Rouen Normandie", "statut": "PAV verre/emballages/OM uniquement"},
    {"id": "dunkerque", "nom": "Dunkerque (CUD)", "statut": "Données géolocalisées non publiées"},
    {"id": "orleans", "nom": "Orléans Métropole", "statut": "PAV verre/emballages/OM uniquement"},
    {"id": "metz", "nom": "Eurométropole de Metz", "statut": "Collecte expérimentale sans flux dédié"},
    {"id": "versailles", "nom": "Versailles Grand Parc", "statut": "Données géolocalisées non publiées"},
    {"id": "besancon", "nom": "Grand Besançon Métropole", "statut": "Données ouvertes non disponibles"},
    {"id": "lemans", "nom": "Le Mans Métropole", "statut": "Viewer sans API ouverte"}
]


def deduplicate_features(features):
    """
    Déduplique les points identiques selon la règle :
    arrondi des coordonnées à 5 décimales + adresse normalisée.
    """
    seen = set()
    unique = []
    duplicates = 0

    for ft in features:
        lon, lat = ft["geometry"]["coordinates"]
        props = ft["properties"]
        norm_addr = clean_text(props.get("adresse", "")).lower()
        key = (round(lon, 5), round(lat, 5), norm_addr)

        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique.append(ft)

    return unique, duplicates


def main():
    print("=" * 68)
    print("PAVfinder - Transformation et consolidation GeoJSON")
    print("=" * 68)

    raw_features = []
    villes_stats = {}
    groupes_stats = {"principales": 0, "autres": 0}

    transformers = [
        # Principales (8)
        ("paris", transform_paris),
        ("lyon", transform_lyon),
        ("toulouse", transform_toulouse),
        ("nantes", transform_nantes),
        ("bordeaux", transform_bordeaux),
        ("montpellier", transform_montpellier),
        ("rennes", transform_rennes),
        ("lille", transform_lille),
        # Autres villes avec PAV actifs
        ("strasbourg", transform_strasbourg),
        ("mulhouse", transform_mulhouse),
        ("marseille", transform_marseille),
        ("tours", transform_tours),
        ("gpso", transform_gpso),
        # Contrôle des jeux candidats (Rouen, Orléans, Metz)
        ("rouen", transform_rouen),
        ("orleans", transform_orleans),
        ("metz", transform_metz),
    ]

    for ville, func in transformers:
        fts = func()
        villes_stats[ville] = len(fts)
        grp = fts[0]["properties"]["groupe"] if fts else "autres"
        status_txt = f"{len(fts):5} PAV extraits" if fts else "    0 PAV (pas de flux biodéchets)"
        print(f"-> {ville.capitalize():14} [{grp.upper():11}] : {status_txt}")
        raw_features.extend(fts)

    # Déduplication
    unique_features, dup_count = deduplicate_features(raw_features)
    print(f"\nDéduplication : {dup_count} doublons supprimés sur {len(raw_features)} points bruts.")
    print(f"Total final   : {len(unique_features)} PAV uniques retenus.")

    # Recalcul des stats par ville et par groupe après déduplication
    final_stats = {}
    for ft in unique_features:
        v = ft["properties"]["ville"]
        grp = ft["properties"]["groupe"]
        final_stats[v] = final_stats.get(v, 0) + 1
        groupes_stats[grp] = groupes_stats.get(grp, 0) + 1

    # Date de génération ISO UTC
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    geojson_output = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "Points d'Apport Volontaire (PAV) de déchets alimentaires et biodéchets",
            "generator": "PAVfinder scripts/transform.py",
            "updated_at": now_iso,
            "total_count": len(unique_features),
            "groupes": groupes_stats,
            "villes": final_stats,
            "villes_sans_donnees": VILLES_SANS_DONNEES
        },
        "features": unique_features
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(geojson_output, f, ensure_ascii=False, separators=(",", ":"))

    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Fichier GeoJSON généré : {OUTPUT_FILE}")
    print(f"Taille du fichier : {size_mb:.2f} Mo")
    print(f"Groupes : {groupes_stats}")
    print(f"Répartition par ville : {final_stats}")
    print("=" * 68)


if __name__ == "__main__":
    main()
