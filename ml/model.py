# ml/model.py
import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Attempt to import SHAP for explainability, handle gracefully if missing
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

def train_and_save_model(X, y):
    """
    Simple training function designed for Google Colab/local small datasets.
    """
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    print(f"[ML] Model trained and saved to {MODEL_PATH}")
    return model

def load_model():
    """
    Loads the pre-trained model from disk.
    If not found, creates a dummy model for initial development/testing.
    """
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"[ML Warning] Failed to load model: {e}")
    
    # Generate a dummy model if none exists so the code doesn't crash on first run
    print("[ML] No model.pkl found. Initializing dummy model for testing...")
    dummy_model = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=42)
    # Train on 16 zero-features (matching num_features in extractor)
    X_dummy = np.zeros((2, 16))
    y_dummy = np.array([0, 1])
    dummy_model.fit(X_dummy, y_dummy)
    return dummy_model

def predict_vulnerability(model, X_features):
    """
    Predicts vulnerability probability for a set of features.
    """
    probs = model.predict_proba(X_features)[:, 1]
    labels = (probs > 0.5).astype(int)
    return labels, probs

def get_explanations(model, X_features, feature_names):
    """
    Uses SHAP to explain why the ML model made its decisions.
    Returns a list of top contributing features for each prediction.
    """
    if not SHAP_AVAILABLE:
        return ["SHAP library not installed for AI reasoning."] * len(X_features)

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_features)
        
        # shap_values[1] contains values for the 'Vulnerable' class
        explanations = []
        for i in range(len(X_features)):
            # Get indices of top 3 features with highest SHAP values
            top_indices = np.argsort(np.abs(shap_values[1][i]))[-3:][::-1]
            reasons = [feature_names[idx] for idx in top_indices if np.abs(shap_values[1][i][idx]) > 0.01]
            
            if reasons:
                explanations.append(f"Strongly influenced by: {', '.join(reasons)}")
            else:
                explanations.append("Decision based on multiple low-impact features.")
        return explanations
    except Exception as e:
        return [f"Reasoning unavailable: {str(e)}"] * len(X_features)
