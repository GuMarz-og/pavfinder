#!/usr/bin/env python3
"""
scripts/collect.py
Télécharge les données brutes des Points d'Apport Volontaire (PAV)
de déchets alimentaires / biodéchets pour les 8 métropoles cibles :
  - Paris
  - Lyon
  - Toulouse
  - Nantes
  - Bordeaux
  - Montpellier
  - Rennes
  - Lille

SOURCES ET URLS OFFICIELLES UTILISÉES :
--------------------------------------------------------------------------------
1. Paris:
   - Abri-bacs Déchets Alimentaires (PAVDA):
     https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/dechets-menagers-pavda/exports/geojson
   - Stations Trilib (PAV):
     https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/dechets-menagers-points-dapport-volontaire-stations-trilib/exports/geojson

2. Lyon:
   - Bornes à compost de la Métropole de Lyon (WFS GeoJSON):
     https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:gic_collecte.bornecompost&outputFormat=application/json&SRSNAME=EPSG:4326

3. Toulouse:
   - Points d'apport volontaire - Déchets et Moyens Techniques:
     https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/points-dapport-volontaire-dechets-et-moyens-techniques/exports/geojson

4. Nantes:
   - Points de collecte déchets alimentaires (biodéchet):
     https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_point-collecte-dechets-alimentaires-biodechet-nantes/exports/geojson

5. Bordeaux:
   - Emplacements d'apport volontaire (en_empac_p - PAV):
     https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/en_empac_p/exports/geojson

6. Montpellier:
   - Points d'apport volontaires de Montpellier Méditerranée Métropole (PAV):
     https://data.montpellier3m.fr/sites/default/files/ressources/MMM_MMM_Pav.json

7. Rennes:
   - Points d'apport volontaire des déchets ménagers sur Rennes Métropole (PAV):
     https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/points-apport-volontaire/exports/geojson

8. Lille:
   - PAV Déchets Alimentaires (couche officielle pav-dechets-alimentaires.lillemetropole.fr):
     https://geoserver.lillemetropole.fr/geoserver/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=Diffusion_RSMT:VOD_PAV_DECHET_ALIMENTAIRE&srsName=EPSG:4326&outputFormat=application/json
   - État du parc de PAV (MEL dataMEL - flux général):
     https://data.lillemetropole.fr/geoserver/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=mel_environnement_energie:pav_etat_parc&outputFormat=application/json&SRSNAME=EPSG:4326
--------------------------------------------------------------------------------
"""

import os
import sys
import time
from pathlib import Path
import requests

USER_AGENT = "pavfinder/1.0 (https://github.com/guenole/pavfinder; open data collector)"
TIMEOUT_SECONDS = 45

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

DATASETS = [
    # 1. PARIS
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

    # 2. LYON
    {
        "ville": "lyon",
        "nom": "lyon_bornes_compost",
        "url": "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=metropole-de-lyon:gic_collecte.bornecompost&outputFormat=application/json&SRSNAME=EPSG:4326",
        "filename": "lyon_bornes_compost.geojson",
        "source": "data.grandlyon.com",
    },

    # 3. TOULOUSE
    {
        "ville": "toulouse",
        "nom": "toulouse_pav",
        "url": "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/points-dapport-volontaire-dechets-et-moyens-techniques/exports/geojson",
        "filename": "toulouse_pav.geojson",
        "source": "data.toulouse-metropole.fr",
    },

    # 4. NANTES
    {
        "ville": "nantes",
        "nom": "nantes_biodechets",
        "url": "https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_point-collecte-dechets-alimentaires-biodechet-nantes/exports/geojson",
        "filename": "nantes_biodechets.geojson",
        "source": "data.nantesmetropole.fr",
    },

    # 5. BORDEAUX
    {
        "ville": "bordeaux",
        "nom": "bordeaux_empac",
        "url": "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/en_empac_p/exports/geojson",
        "filename": "bordeaux_empac.geojson",
        "source": "datahub.bordeaux-metropole.fr",
    },

    # 6. MONTPELLIER
    {
        "ville": "montpellier",
        "nom": "montpellier_pav",
        "url": "https://data.montpellier3m.fr/sites/default/files/ressources/MMM_MMM_Pav.json",
        "filename": "montpellier_pav.json",
        "source": "data.montpellier3m.fr",
    },

    # 7. RENNES
    {
        "ville": "rennes",
        "nom": "rennes_pav",
        "url": "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/points-apport-volontaire/exports/geojson",
        "filename": "rennes_pav.geojson",
        "source": "data.rennesmetropole.fr",
    },

    # 8. LILLE
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
    print("PAVfinder - Collecte des PAV de biodéchets (8 métropoles)")
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
