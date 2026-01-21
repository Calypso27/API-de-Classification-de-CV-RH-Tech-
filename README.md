# API de Classification de CV (RH-Tech)

API REST pour classifier automatiquement des CV par secteur d'activité (Python Developer, Java Developer, Data Science, etc.) en utilisant le Machine Learning.

## Technologies

- Django 4.2
- Django REST Framework
- JWT (djangorestframework-simplejwt)
- scikit-learn (Naive Bayes + TF-IDF)
- Swagger (drf-yasg)
- SQLite

## Installation

```bash
# Cloner le projet
git clone https://github.com/votre-username/API-de-Classification-de-CV-RH-Tech-.git
cd API-de-Classification-de-CV-RH-Tech

# Créer l'environnement virtuel
uv venv
.venv\Scripts\activate

# Installer les dépendances
uv sync

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Entraîner le modèle ML

```bash
# Télécharger le dataset depuis Kaggle
# https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset

# Placer le fichier Resume.csv dans resume_dataset/Resume/

# Lancer l'entraînement
python resumes/train_model.py
```

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/resumes/` | POST | Uploader un CV (PDF/DOCX) |
| `/api/resumes/{id}/classify/` | POST | Classifier un CV |
| `/api/resumes/by-category/?category=Python` | GET | Filtrer par catégorie |
| `/api/resumes/{id}/extract-skills/` | GET | Extraire les compétences |
| `/api/categories/` | GET | Lister les catégories |
| `/api/classifications/` | GET | Lister les classifications |
| `/api/classifications/stats/` | GET | Statistiques |
| `/api/jobpostings/` | GET | Lister les offres d'emploi |
| `/api/token/` | POST | Obtenir un token JWT |
| `/api/token/refresh/` | POST | Rafraîchir le token |

## Documentation Swagger

- Swagger UI : http://localhost:8000/swagger/

## Exemples d'utilisation

### Obtenir un token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### Uploader un CV

```bash
curl -X POST http://localhost:8000/api/resumes/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@mon_cv.pdf"
```

### Classifier un CV

```bash
curl -X POST http://localhost:8000/api/resumes/1/classify/ \
  -H "Authorization: Bearer <token>"
```

### Rechercher par catégorie

```bash
curl -X GET "http://localhost:8000/api/resumes/by-category/?category=Python" \
  -H "Authorization: Bearer <token>"
```

## Tests

```bash
python manage.py test resumes
```

## Structure du projet

```
├── cvclassifier/          # Configuration Django
├── resumes/               # Application principale
│   ├── models.py          # Modèles (Resume, Category, Classification, JobPosting)
│   ├── views.py           # ViewSets API
│   ├── serializers.py     # Serializers DRF
│   ├── ml_classifier.py   # Classe de classification ML
│   ├── train_model.py     # Script d'entraînement
│   └── utils.py           # Utilitaires (extraction texte)
├── ml_models/             # Modèles ML sauvegardés (.pkl)
└── manage.py
```

## Auteur

MBENGMO CALYPSO  Projet Master 2 Datascience - Institut Saint Jean
