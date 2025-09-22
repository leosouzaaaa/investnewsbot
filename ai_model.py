import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
class InvestmentAI:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.model = LogisticRegression()
    def train(self, news_texts, labels, out_path='app/ai_model.pkl'):
        X = self.vectorizer.fit_transform(news_texts)
        self.model.fit(X, labels)
        joblib.dump((self.vectorizer, self.model), out_path)
    def predict(self, news_texts, model_path='app/ai_model.pkl'):
        try:
            vec, mdl = joblib.load(model_path)
            X = vec.transform(news_texts)
            return mdl.predict_proba(X)[:,1]
        except Exception:
            # fallback neutral probabilities
            return [0.5 for _ in news_texts]
