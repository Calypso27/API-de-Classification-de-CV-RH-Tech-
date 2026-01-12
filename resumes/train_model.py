import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import pickle
import os

print("Chargement du dataset...")


current_dir = os.getcwd()
if current_dir.endswith('resumes'):
    csv_path = '../resume_dataset/Resume/Resume.csv'
    ml_models_path = '../ml_models'
else:
    csv_path = 'resume_dataset/Resume/Resume.csv'
    ml_models_path = 'ml_models'

try:
    df = pd.read_csv(csv_path)
    print(f"Dataset charge: {len(df)} lignes")
    print(f"Colonnes: {list(df.columns)}")
except FileNotFoundError:
    print(f"Erreur: Fichier non trouve - {csv_path}")
    exit(1)
except Exception as e:
    print(f"Erreur lors du chargement: {e}")
    exit(1)


print("\nApercu des donnees:")
print(df.head(2))


X = df['Resume_str']
y = df['Category']

# Nettons les valeurs manquantes
print("\nNettoyage des donnees...")
mask = X.notna() & y.notna()
X = X[mask]
y = y[mask]
print(f"Donnees nettoyees: {len(X)} CV")

# Afficher les catégories
print(f"\nCategories trouvees: {y.nunique()}")
print("\nDistribution des categories:")
print(y.value_counts())

# Split train/test
print("\nSeparation train/test...")
try:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
except ValueError:
    print("Stratification impossible, split simple...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

print(f"Train: {len(X_train)} echantillons")
print(f"Test: {len(X_test)} echantillons")

# Vectorisation
print("\nVectorisation du texte...")
vectorizer = TfidfVectorizer(
    max_features=1500,
    stop_words='english',
    min_df=2,
    max_df=0.8,
    strip_accents='unicode',
    lowercase=True
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)
print(f"Vocabulaire: {len(vectorizer.vocabulary_)} mots")

# Entraînons le modèle
print("\nEntrainement du modele...")
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Évaluons la précisions du modèle
accuracy = model.score(X_test_vec, y_test)
print(f"\nPrecision du modele: {accuracy:.2%}")

# Test sur quelques exemples
print("\nTests sur 5 exemples:")
for i in range(min(5, len(X_test))):
    sample_text = X_test.iloc[i]
    true_label = y_test.iloc[i]
    pred_label = model.predict(vectorizer.transform([sample_text]))[0]
    proba = model.predict_proba(vectorizer.transform([sample_text]))[0]
    confidence = max(proba)

    print(f"\nExemple {i + 1}:")
    print(f"  Texte: {sample_text[:100]}...")
    print(f"  Predit: {pred_label} (confiance: {confidence:.2%})")
    print(f"  Reel: {true_label}")
    print(f"  Resultat: {'CORRECT' if pred_label == true_label else 'INCORRECT'}")

# Sauvegarde du modèle
print("\nSauvegarde du modele...")
os.makedirs(ml_models_path, exist_ok=True)

with open(f'{ml_models_path}/resume_classifier.pkl', 'wb') as f:
    pickle.dump(model, f)

with open(f'{ml_models_path}/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

# Sauvegarde des catégories
categories = list(model.classes_)
with open(f'{ml_models_path}/categories.pkl', 'wb') as f:
    pickle.dump(categories, f)

print(f"\nModele sauvegarde dans {ml_models_path}/")

print("RESUME FINAL")
print("=" * 50)
print(f"Dataset: {len(df)} CV")
print(f"Precision: {accuracy:.2%}")
print(f"Categories: {len(categories)}")
print(f"Vocabulaire: {len(vectorizer.vocabulary_)} mots")
print("\nCategories disponibles:")
for cat in sorted(categories):
    count = sum(y == cat)
    print(f"  - {cat}: {count} CV")
print("\nFichiers crees:")
print(f"  - {ml_models_path}/resume_classifier.pkl")
print(f"  - {ml_models_path}/vectorizer.pkl")
print(f"  - {ml_models_path}/categories.pkl")
print("\n" + "=" * 50)
print("Entrainement termine avec succes!")
