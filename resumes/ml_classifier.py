import pickle
import os
from django.conf import settings


class CVClassifier:

    def __init__(self):

        base_path = os.path.join(settings.BASE_DIR, 'ml_models')
        model_path = os.path.join(base_path, 'resume_classifier.pkl')
        vectorizer_path = os.path.join(base_path, 'vectorizer.pkl')

        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            self.is_loaded = True
        else:
            self.model = None
            self.vectorizer = None
            self.is_loaded = False

    def predict(self, text):

        if not self.is_loaded:
            raise Exception("Modèle non chargé. Téléchargez-le depuis Kaggle.")

        X = self.vectorizer.transform([text])

        # Prédire la catégorie
        predicted_category = self.model.predict(X)[0]

        # Score de confiance
        probabilities = self.model.predict_proba(X)[0]
        confidence = max(probabilities)

        return predicted_category, confidence

    def get_all_categories(self):
        if self.is_loaded:
            return list(self.model.classes_)
        return []

