# ♻️ OùJeterMesBiodéchets.fr — Carte des PAV de Déchets Alimentaires & Biodéchets

**OùJeterMesBiodéchets.fr** est une application web statique, légère et interactive hébergée sur **GitHub Pages**, répertoriant exclusivement les **Points d'Apport Volontaire (PAV)** de déchets alimentaires et biodéchets dans les métropoles et villes françaises disposant de données ouvertes.

L'application facilite le tri à la source des biodéchets (généralisé conformément à la loi AGEC) en permettant aux habitants de repérer en quelques secondes la borne de collecte la plus proche.

> **Périmètre strict :** Uniquement les bornes, colonnes et abri-bacs d'apport volontaire sur l'espace public dédiés aux déchets alimentaires / biodéchets. Les composteurs collectifs et partagés de quartier sont exclus du projet.

---

## 🚀 Fonctionnalités

- **Mise en page épurée avec colonne latérale gauche (sidebar)** :
  - **Pas de bandeau supérieur horizontal** encombrant : la carte occupe tout l'espace disponible à droite de la sidebar.
  - **En-tête de la sidebar** : Nom de l'application (**OùJeterMesBiodéchets.fr**), compteur de PAV affichés mis à jour dynamiquement selon la sélection, et bouton **« À propos »** ouvrant une modale explicative complète (sources, licences, date, GitHub).
  - **Barre de recherche d'adresse** : Autocomplétion officielle instantanée basée sur l'API nationale de la Base Adresse Nationale ([adresse.data.gouv.fr](https://adresse.data.gouv.fr/)), avec zoom et calcul de distance jusqu'à la borne la plus proche.
  - **Bouton « Autour de moi »** : Positionné immédiatement à côté du champ de recherche dans la sidebar pour géolocaliser l'usager (`navigator.geolocation`) sans jamais empiéter sur les contrôles de zoom de Leaflet.
  - **Liste des villes en colonne** : Défilement vertical fluide, bouton « Toutes les villes » en tête de liste, distinction entre les villes principales et les autres villes avec compteurs individuels.
  - **Pied de sidebar avec légende** : Explication claire à 2 entrées (vert pour les villes principales, rouge pour les autres villes) et rappel du périmètre strict.
- **Carte interactive plein écran** basée sur [Leaflet](https://leafletjs.com/) et [OpenStreetMap](https://www.openstreetmap.org/).
- **Codes couleur & distinction géographique** :
  - 🟢 **Vert** : Les villes et métropoles principales (Paris, Lyon, Marseille/Aix, Toulouse, Nantes, Bordeaux, Montpellier, Strasbourg, Rennes, Lille, Tours, Issy/GPSO).
  - 🔴 **Rouge** : Autres villes (Mulhouse...).
- **Clustering haute performance** avec [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) pour afficher de manière fluide plus de **15 000 bornes**.
- **Responsive Mobile (< 768px)** : En-tête mobile dédié avec menu hamburger, compteur et bouton « À propos » toujours visibles, et tiroir latéral glissant (drawer).
- **100% statique** : Un seul fichier `index.html` (HTML + CSS + JS inline, sans framework ni build).

---

## 📊 Données consolidées (15 241 PAV)

### 1. Les villes et métropoles principales (🟢 14 922 PAV)

| Ville / Métropole | Équipements retenus | Nombre de PAV | Source Open Data | Licence |
|---|---|---:|---|---|
| **Nantes** | Points de collecte déchets alimentaires (biodéchet) | 4 299 | [data.nantesmetropole.fr](https://data.nantesmetropole.fr) | Licence Ouverte |
| **Lyon** | Bornes à compost de la Métropole de Lyon | 2 662 | [data.grandlyon.com](https://data.grandlyon.com) | Licence Ouverte |
| **Strasbourg** | Bornes de déchets alimentaires (`dc_pav_borne_dalim`) | 1 561 | [data.strasbourg.eu](https://data.strasbourg.eu) | Licence Ouverte |
| **Bordeaux** | Emplacements PAV biodéchets (`en_empac_p`) | 1 465 | [datahub.bordeaux-metropole.fr](https://datahub.bordeaux-metropole.fr) | Licence Ouverte |
| **Marseille / Aix (AMP)** | PAV biodéchets (`ol-pav-harmonise`) | 1 210 | [data.ampmetropole.fr](https://data.ampmetropole.fr) | Licence Ouverte |
| **Montpellier** | PAV biodéchets (`MMM_MMM_Pav`) | 981 | [data.montpellier3m.fr](https://data.montpellier3m.fr) | ODbL |
| **Paris** | Abri-bacs (PAVDA) & Stations Trilib | 906 | [opendata.paris.fr](https://opendata.paris.fr) | Licence Ouverte |
| **Rennes** | Points d'apport volontaire (flux DA) | 717 | [data.rennesmetropole.fr](https://data.rennesmetropole.fr) | Licence Ouverte |
| **Toulouse** | PAV déchets alimentaires & abri-bacs | 618 | [data.toulouse-metropole.fr](https://data.toulouse-metropole.fr) | Licence Ouverte |
| **Lille** | PAV déchets alimentaires (carte officielle dataMEL) | 325 | [pav-dechets-alimentaires.lillemetropole.fr](https://pav-dechets-alimentaires.lillemetropole.fr/) | Licence Ouverte |
| **Tours** | Abri-bacs déchets alimentaires (`dechets_alimentaires`) | 148 | [data.tours-metropole.fr](https://data.tours-metropole.fr) | Licence Ouverte |
| **Issy / GPSO** | Abri-bacs Issy-les-Moulineaux, Meudon, Chaville (`abri-bac`) | 30 | [data.seineouest.fr](https://data.seineouest.fr) | Licence Ouverte |

### 2. Autres villes avec données ouvertes actives (🔴 319 PAV)

| Ville / Agglomération | Équipements retenus | Nombre de PAV | Source Open Data | Licence |
|---|---|---:|---|---|
| **Mulhouse (m2A)** | Bornes de biodéchets (`m2a_borne_biodechet-m2a`) | 319 | [data.mulhouse-alsace.fr](https://data.mulhouse-alsace.fr) | Licence Ouverte |
| **TOTAL ACTIF** | | **15 241** | | |

### 3. Autres villes du plan (en attente d'un flux biodéchets ouvert sur voirie — 0 PAV)

Conformément au principe de robustesse du plan, ces collectivités sont directement intégrées dans le sélecteur avec centrage cartographique automatique et statut explicite :
- **Nice (Métropole Nice Côte d'Azur)** : Le jeu open data actuel ne sépare pas de flux biodéchets spécifique.
- **Grenoble (Grenoble-Alpes-Métropole)** : Données ouvertes géolocalisées non publiées actuellement.
- **Montreuil** : Seuls les composteurs collectifs en parcs sont publiés (exclus du périmètre PAV sur voirie).
- **Rouen (Métropole Rouen Normandie)** : Dataset `donmetdec_pav` restreint au verre, emballages et ordures ménagères.
- **Dunkerque (CUD)** : Publication limitée aux bilans d'activité annuels sans coordonnées de conteneurs.
- **Orléans (Orléans Métropole)** : Dataset `dechets_pav` sans flux biodéchets pour le moment.
- **Metz (Eurométropole de Metz)** : Expérimentation en cours sans flux ouvert distinct dans les PAV.
- **Versailles (Versailles Grand Parc)** : Couches géographiques de collecte sans flux biodéchets ouvert.
- **Besançon (Grand Besançon Métropole)** : Données ouvertes non encore disponibles sur l'espace open data.
- **Le Mans (Le Mans Métropole)** : Viewer géographique sans API d'export ouverte.

---

## 📁 Structure du projet

```text
pavfinder/
├── index.html          # Page unique autonome (HTML + CSS + JS inline)
├── data/
│   ├── pav.geojson     # Données consolidées et normalisées (~5.5 Mo, servi par GitHub Pages)
│   └── raw/            # Exports bruts téléchargés depuis les API open data (ignoré par Git)
├── scripts/
│   ├── collect.py      # Télécharge les données brutes de chaque métropole et ville
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
Ce script télécharge les flux GeoJSON / JSON / WFS officiels de toutes les métropoles et villes cibles et les stocke dans `data/raw/`.

### 2. Transformer et fusionner

```bash
python scripts/transform.py
```
Ce script effectue :
1. La projection géographique en **WGS84** (EPSG:4326) si nécessaire (conversion Lambert-93).
2. Le filtrage strict pour ne conserver **que les PAV de biodéchets / déchets alimentaires** (exclusion systématique du verre, ordures résiduelles, emballages et composteurs collectifs).
3. L'attribution du champ `groupe` (`"principales"` pour les 8 métropoles, `"autres"` pour les autres villes).
4. La déduplication des points (arrondi des coordonnées à 5 décimales et contrôle d'adresse).
5. La normalisation vers le schéma commun :
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
       "source_url": "https://...",
       "groupe": "principales"
     }
   }
   ```
6. La génération du fichier compact `data/pav.geojson`.

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
   git commit -m "feat: ajout recherche adresse, autocompletion BAN et autres villes (Strasbourg, Mulhouse, Marseille)"
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
- **Géocodage** : API Base Adresse Nationale ([adresse.data.gouv.fr](https://adresse.data.gouv.fr/)).
