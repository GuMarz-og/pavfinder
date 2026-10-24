# ♻️ PAVfinder — Carte des PAV de Déchets Alimentaires & Biodéchets

**PAVfinder** est une application web statique, légère et interactive hébergée sur **GitHub Pages**, répertoriant exclusivement les **Points d'Apport Volontaire (PAV)** de déchets alimentaires et biodéchets dans 8 grandes métropoles françaises : **Paris, Lyon, Toulouse, Nantes, Bordeaux, Montpellier, Rennes et Lille**.

L'application facilite le tri à la source des biodéchets (généralisé conformément à la loi AGEC) en permettant aux habitants de repérer en quelques secondes la borne de collecte la plus proche.

> **Périmètre strict :** Uniquement les bornes, colonnes et abri-bacs d'apport volontaire sur l'espace public dédiés aux déchets alimentaires / biodéchets. Les composteurs collectifs et partagés de quartier sont exclus du projet.

---

## 🚀 Fonctionnalités

- **Carte interactive plein écran** basée sur [Leaflet](https://leafletjs.com/) et [OpenStreetMap](https://www.openstreetmap.org/).
- **Unicité visuelle** : Tous les PAV partagent la même icône végétale et couleur verte harmonisée.
- **Clustering haute performance** avec [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) pour afficher de manière ultra-fluide près de **12 000 bornes**.
- **Filtre par métropole** en un clic avec centrage et zoom automatique sur les limites de chaque agglomération.
- **Géolocalisation (« Autour de moi »)** : repère la position de l'utilisateur (`navigator.geolocation`) et calcule automatiquement la distance du PAV le plus proche.
- **Fiches détails (Popups)** : nom, adresse, lien direct d'itinéraire vers Google Maps et lien vers le portail source officiel.
- **Mobile-first & 100% statique** : un seul fichier `index.html` (sans framework, sans bundler, sans backend).

---

## 📊 Données consolidées (11 973 PAV)

| Métropole | Équipements retenus | Nombre de PAV | Source Open Data | Licence |
|---|---|---:|---|---|
| **Paris** | Abri-bacs (PAVDA) & Stations Trilib | 906 | [opendata.paris.fr](https://opendata.paris.fr) | Licence Ouverte |
| **Lyon** | Bornes à compost de la Métropole de Lyon | 2 662 | [data.grandlyon.com](https://data.grandlyon.com) | Licence Ouverte |
| **Toulouse** | PAV déchets alimentaires & abri-bacs | 618 | [data.toulouse-metropole.fr](https://data.toulouse-metropole.fr) | Licence Ouverte |
| **Nantes** | Points de collecte déchets alimentaires (biodéchet) | 4 299 | [data.nantesmetropole.fr](https://data.nantesmetropole.fr) | Licence Ouverte |
| **Bordeaux** | Emplacements PAV biodéchets (`en_empac_p` uniquement) | 1 465 | [datahub.bordeaux-metropole.fr](https://datahub.bordeaux-metropole.fr) | Licence Ouverte |
| **Montpellier** | PAV biodéchets (MMM_MMM_Pav uniquement) | 981 | [data.montpellier3m.fr](https://data.montpellier3m.fr) | ODbL |
| **Rennes** | Points d'apport volontaire (flux DA / Déchets alimentaires) | 717 | [data.rennesmetropole.fr](https://data.rennesmetropole.fr) | Licence Ouverte |
| **Lille** | PAV déchets alimentaires (carte officielle dataMEL) | 325 | [pav-dechets-alimentaires.lillemetropole.fr](https://pav-dechets-alimentaires.lillemetropole.fr/) | Licence Ouverte |
| **TOTAL** | | **11 973** | | |

---

## 📁 Structure du projet

```text
pavfinder/
├── index.html          # Page unique autonome (HTML + CSS + JS inline)
├── data/
│   ├── pav.geojson     # Données consolidées et normalisées (~4.1 Mo, servi par GitHub Pages)
│   └── raw/            # Exports bruts téléchargés depuis les API open data (ignoré par Git)
├── scripts/
│   ├── collect.py      # Télécharge les données brutes de chaque métropole
│   └── transform.py    # Nettoie, filtre, projette en WGS84 et fusionne en GeoJSON
└── README.md           # Documentation, sources et instructions
```

---

## 🛠️ Mise à jour des données (hors-ligne)

Les scripts Python sont exécutés hors-ligne par le développeur avant chaque commit. Le navigateur ne fait aucune requête directe aux API open data (aucun problème de CORS et disponibilité permanente).

### Prérequis

- Python 3.10+
- Bibliothèques requises : `requests`, `pyproj`

```bash
pip install requests pyproj
```

### 1. Collecter les données brutes

```bash
python scripts/collect.py
```
Ce script télécharge les flux GeoJSON / JSON / WFS officiels des 8 métropoles et les stocke dans `data/raw/`.

### 2. Transformer et fusionner

```bash
python scripts/transform.py
```
Ce script effectue :
1. La projection géographique en **WGS84** (EPSG:4326) si nécessaire (conversion Lambert-93).
2. Le filtrage strict pour ne conserver **que les PAV de biodéchets / déchets alimentaires** (exclusion systématique des flux verre, ordures ménagères, emballages et composteurs collectifs).
3. La déduplication des points (arrondi des coordonnées à 5 décimales et contrôle d'adresse).
4. La normalisation vers le schéma commun :
   ```json
   {
     "type": "Feature",
     "geometry": { "type": "Point", "coordinates": [lon, lat] },
     "properties": {
       "ville": "lyon",
       "nom": "Borne à compost (B1921)",
       "adresse": "10 Rue du 19 Mars 1962, Vaulx-en-Velin",
       "type": "borne_compost",
       "source": "data.grandlyon.com",
       "source_url": "https://..."
     }
   }
   ```
5. La génération du fichier compact `data/pav.geojson`.

---

## 💻 Tester localement

Lancez un simple serveur HTTP local :

```bash
python -m http.server 8000
```

Puis ouvrez votre navigateur à l'adresse : **[http://localhost:8000](http://localhost:8000)**.

---

## 🌐 Déploiement sur GitHub Pages

1. Commitez et poussez le dépôt sur GitHub :
   ```bash
   git add .
   git commit -m "feat: alignement perimetre PAV biodechets 8 metropoles"
   git push origin main
   ```
2. Sur GitHub, rendez-vous dans votre dépôt :
   - Allez dans **Settings** > **Pages**
   - Sous **Build and deployment** / **Source**, sélectionnez **Deploy from a branch**
   - Choisissez la branche `main` et le dossier `/ (root)`
   - Cliquez sur **Save**
3. Votre site sera accessible en quelques minutes à l'adresse `https://<votre-pseudo>.github.io/<nom-du-repo>/`.

---

## 📜 Licences et Références

- **Code source** : Sous licence libre [MIT](https://opensource.org/licenses/MIT).
- **Données ouvertes** : Les données utilisées proviennent des plateformes open data des métropoles sous **Licence Ouverte Etalab v2.0** ou **Open Database License (ODbL)**.
- **Cartographie** : Données cartographiques © les contributeurs d'[OpenStreetMap](https://www.openstreetmap.org/copyright) (ODbL).
