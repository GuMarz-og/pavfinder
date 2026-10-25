#!/usr/bin/env python3
"""
scripts/collect.py
Télécharge les données brutes des Points d'Apport Volontaire (PAV)
de déchets alimentaires / biodéchets pour les 8 métropoles principales et les autres villes.

SOURCES ET URLS OFFICIELLES UTILISÉES :
--------------------------------------------------------------------------------
1. Métropoles principales (groupe: "principales") :
   - Paris :
     * Abri-bacs Déchets Alimentaires (PAVDA) :
       https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/dechets-menagers-pavda/exports/geojson
     * Stations Trilib' :
       https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/dechets-menagers-points-dapport-volontaire-stations-trilib/exports/geojson
   - Lyon :
     * Bornes à compost de la Métropole de Lyon :
       https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:gic_collecte.bornecompost&outputFormat=application/json&SRSNAME=EPSG:4326
   - Toulouse :
     * PAV Déchets et Moyens Techniques :
       https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/points-dapport-volontaire-dechets-et-moyens-techniques/exports/geojson
   - Nantes :
     * Points de collecte déchets alimentaires (biodéchet) :
       https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_point-collecte-dechets-alimentaires-biodechet-nantes/exports/geojson
   - Bordeaux :
     * Emplacements d'apport volontaire (en_empac_p) :
       https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/en_empac_p/exports/geojson
   - Montpellier :
     * Points d'apport volontaires de Montpellier 3M (MMM_MMM_Pav) :
       https://data.montpellier3m.fr/sites/default/files/ressources/MMM_MMM_Pav.json
   - Rennes :
     * Points d'apport volontaire (points-apport-volontaire) :
       https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/points-apport-volontaire/exports/geojson
   - Lille :
     * PAV Déchets Alimentaires (carte officielle pav-dechets-alimentaires.lillemetropole.fr) :
       https://geoserver.lillemetropole.fr/geoserver/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=Diffusion_RSMT:VOD_PAV_DECHET_ALIMENTAIRE&srsName=EPSG:4326&outputFormat=application/json
     * État du parc PAV MEL :
       https://data.lillemetropole.fr/geoserver/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=mel_environnement_energie:pav_etat_parc&outputFormat=application/json&SRSNAME=EPSG:4326

2. Autres villes (groupe: "autres", affichage en rouge) :
   - Strasbourg :
     * Bornes de déchets alimentaires (dc_pav_borne_dalim) :
       https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/dc_pav_borne_dalim/exports/geojson
   - Mulhouse (m2A) :
     * Bornes de biodéchets (m2a_borne_biodechet-m2a) :
       https://data.mulhouse-alsace.fr/api/explore/v2.1/catalog/datasets/m2a_borne_biodechet-m2a/exports/geojson
   - Marseille / Aix-en-Provence (AMP) :
     * PAV harmonisés (ol-pav-harmonise) :
       https://data.ampmetropole.fr/api/explore/v2.1/catalog/datasets/ol-pav-harmonise/exports/geojson
--------------------------------------------------------------------------------
"""

import os
import sys
import time
from pathlib import Path
import requests

USER_AGENT = "pavfinder/1.0 (https://github.com/guenole/pavfinder; open data collector)"
TIMEOUT_SECONDS = 60

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

DATASETS = [
    # --- 1. MÉTROPOLES PRINCIPALES ---
    {
        "ville": "paris",
        "nom": "paris_pavda",
        "url": "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/dechets-menagers-pavda/exports/geojson",
        "filename": "paris_pavda.geojson",
        "source": "opendata.paris.fr",
    },
    {
        "ville": "paris",
        "nom": "paris_trilib",
        "url": "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/dechets-menagers-points-dapport-volontaire-stations-trilib/exports/geojson",
        "filename": "paris_trilib.geojson",
        "source": "opendata.paris.fr",
    },
    {
        "ville": "lyon",
        "nom": "lyon_bornes_compost",
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:gic_collecte.bornecompost&outputFormat=application/json&SRSNAME=EPSG:4326",
        "filename": "lyon_bornes_compost.geojson",
        "source": "data.grandlyon.com",
    },
    {
        "ville": "toulouse",
        "nom": "toulouse_pav",
        "url": "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/points-dapport-volontaire-dechets-et-moyens-techniques/exports/geojson",
        "filename": "toulouse_pav.geojson",
        "source": "data.toulouse-metropole.fr",
    },
    {
        "ville": "nantes",
        "nom": "nantes_biodechets",
        "url": "https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_point-collecte-dechets-alimentaires-biodechet-nantes/exports/geojson",
        "filename": "nantes_biodechets.geojson",
        "source": "data.nantesmetropole.fr",
    },
    {
        "ville": "bordeaux",
        "nom": "bordeaux_empac",
        "url": "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/en_empac_p/exports/geojson",
        "filename": "bordeaux_empac.geojson",
        "source": "datahub.bordeaux-metropole.fr",
    },
    {
        "ville": "montpellier",
        "nom": "montpellier_pav",
        "url": "https://data.montpellier3m.fr/sites/default/files/ressources/MMM_MMM_Pav.json",
        "filename": "montpellier_pav.json",
        "source": "data.montpellier3m.fr",
    },
    {
        "ville": "rennes",
        "nom": "rennes_pav",
        "url": "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/points-apport-volontaire/exports/geojson",
        "filename": "rennes_pav.geojson",
        "source": "data.rennesmetropole.fr",
    },
    {
        "ville": "lille",
        "nom": "lille_pav_da",
        "url": "https://geoserver.lillemetropole.fr/geoserver/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=Diffusion_RSMT:VOD_PAV_DECHET_ALIMENTAIRE&srsName=EPSG:4326&outputFormat=application/json",
        "filename": "lille_pav_da.geojson",
        "source": "pav-dechets-alimentaires.lillemetropole.fr",
    },
    {
        "ville": "lille",
        "nom": "lille_pav_general",
        "url": "https://data.lillemetropole.fr/geoserver/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=mel_environnement_energie:pav_etat_parc&outputFormat=application/json&SRSNAME=EPSG:4326",
        "filename": "lille_pav_general.geojson",
        "source": "data.lillemetropole.fr",
    },

    # --- 2. AUTRES VILLES ---
    {
        "ville": "strasbourg",
        "nom": "strasbourg_pav_da",
        "url": "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/dc_pav_borne_dalim/exports/geojson",
        "filename": "strasbourg_pav_da.geojson",
        "source": "data.strasbourg.eu",
    },
    {
        "ville": "mulhouse",
        "nom": "mulhouse_pav_da",
        "url": "https://data.mulhouse-alsace.fr/api/explore/v2.1/catalog/datasets/m2a_borne_biodechet-m2a/exports/geojson",
        "filename": "mulhouse_pav_da.geojson",
        "source": "data.mulhouse-alsace.fr",
    },
    {
        "ville": "marseille",
        "nom": "marseille_pav_da",
        "url": "https://data.ampmetropole.fr/api/explore/v2.1/catalog/datasets/ol-pav-harmonise/exports/geojson",
        "filename": "marseille_pav_da.geojson",
        "source": "data.ampmetropole.fr",
    },
    {
        "ville": "tours",
        "nom": "tours_pav_da",
        "url": "https://data.tours-metropole.fr/api/explore/v2.1/catalog/datasets/dechets_alimentaires/exports/geojson",
        "filename": "tours_pav_da.geojson",
        "source": "data.tours-metropole.fr",
    },
    {
        "ville": "gpso",
        "nom": "gpso_abri_bac",
        "url": "https://data.seineouest.fr/api/explore/v2.1/catalog/datasets/abri-bac/exports/geojson",
        "filename": "gpso_abri_bac.geojson",
        "source": "data.seineouest.fr",
    },
    {
        "ville": "rouen",
        "nom": "rouen_pav",
        "url": "https://data.metropole-rouen-normandie.fr/api/explore/v2.1/catalog/datasets/donmetdec_pav/exports/geojson",
        "filename": "rouen_pav.geojson",
        "source": "data.metropole-rouen-normandie.fr",
    },
    {
        "ville": "orleans",
        "nom": "orleans_pav",
        "url": "https://data.orleans-metropole.fr/api/explore/v2.1/catalog/datasets/dechets_pav/exports/geojson",
        "filename": "orleans_pav.geojson",
        "source": "data.orleans-metropole.fr",
    },
    {
        "ville": "metz",
        "nom": "metz_pav",
        "url": "https://maps.eurometropolemetz.eu/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=public:pub_pro_pav&outputFormat=application/json",
        "filename": "metz_pav.geojson",
        "source": "maps.eurometropolemetz.eu",
    },
]


def collect_dataset(ds: dict) -> bool:
    name = ds["nom"]
    url = ds["url"]
    dest = RAW_DIR / ds["filename"]
    print(f"-> Téléchargement de [{ds['ville'].upper()}] {name}...")
    headers = {"User-Agent": USER_AGENT}

    try:
        t0 = time.time()
        response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        elapsed = time.time() - t0

        if response.status_code == 200:
            content = response.content
            with open(dest, "wb") as f:
                f.write(content)
            size_kb = len(content) / 1024
            print(f"   [OK] Sauvegardé dans {dest.name} ({size_kb:.1f} Ko en {elapsed:.2f}s)")
            return True
        else:
            print(f"   [ERREUR HTTP {response.status_code}] Échec pour {url}")
            return False
    except requests.RequestException as e:
        print(f"   [ERREUR RESEAU] {name}: {e}")
        return False


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 68)
    print("PAVfinder - Collecte des PAV de biodéchets (8 métropoles + autres villes)")
    print("=" * 68)

    success_count = 0
    total = len(DATASETS)

    for ds in DATASETS:
        if collect_dataset(ds):
            success_count += 1

    print("\n" + "=" * 68)
    print(f"Collecte terminée : {success_count}/{total} jeux de données récupérés.")
    print(f"Dossier brut : {RAW_DIR}")
    print("=" * 68)


if __name__ == "__main__":
    main()
