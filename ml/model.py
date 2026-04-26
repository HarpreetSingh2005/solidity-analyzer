# ml/model.py
import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# We must ensure the features are ordered exactly as they were during training
FEATURE_COLS = [
    "num_functions", "num_external_calls", "calls_before_state_update",
    "num_state_vars", "has_tx_origin", "has_selfdestruct", "avg_function_size",
    "num_payable_functions", "num_modifiers", "num_state_writes",
    "has_delegatecall", "has_assembly", "uses_tx_origin_in_condition",
    "external_call_before_any_state_update", "has_unchecked_external_call",
    "has_balance_check_before_send", "max_call_depth",
    "has_reentrancy_guard_pattern", "num_user_controlled_inputs_to_state"
]

_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)
    return _model

def predict(features_dict):
    """
    Predicts vulnerability for a given dictionary of features.
    Returns: (prediction_label, confidence)
    """
    model = load_model()
    
    # Build dataframe for prediction in correct order
    row = {}
    for col in FEATURE_COLS:
        row[col] = features_dict.get(col, 0)
        
    df = pd.DataFrame([row], columns=FEATURE_COLS)
    
    # Get probability of class 1 (Vulnerable)
    probs = model.predict_proba(df)[0]
    
    # If the model only has one class or something weird happens
    if len(probs) > 1:
        confidence = probs[1]
    else:
        confidence = float(model.predict(df)[0])
    
    # Prediction label
    prediction = 1 if confidence > 0.5 else 0
    
    return prediction, confidence