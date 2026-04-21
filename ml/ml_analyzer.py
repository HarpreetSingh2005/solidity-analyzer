# ml/ml_analyzer.py
from .feature_extractor import extract_features_from_slither, prepare_for_prediction, get_feature_names
from .model import load_model, predict_vulnerability, get_explanations

def analyze_with_ml(slither):
    """
    Main entry point for ML analysis. Executes prediction and converts results
    into standard finding format.
    """
    print("[ML] Starting ML-based Semantic Analysis...")
    
    # 1. Feature Extraction
    features_list = extract_features_from_slither(slither)
    if not features_list:
        print("[ML] No functions found for ML analysis.")
        return []
        
    X_features, metadata_df = prepare_for_prediction(features_list)
    if X_features is None or len(X_features) == 0:
        return []

    # 2. Prediction
    model = load_model()
    labels, probs = predict_vulnerability(model, X_features)
    
    # 3. Explainability (SHAP) - Only for detections
    # To keep it lightweight, we only explain if probability is high (> 0.5)
    vulnerable_indices = [i for i, label in enumerate(labels) if label == 1]
    
    if not vulnerable_indices:
        print("[ML] No AI-flagged vulnerabilities found.")
        return []

    X_to_explain = X_features[vulnerable_indices]
    feature_names = get_feature_names()
    explanations = get_explanations(model, X_to_explain, feature_names)

    # 4. Format findings
    ml_findings = []
    for i, idx in enumerate(vulnerable_indices):
        info = metadata_df.iloc[idx]
        confidence = float(probs[idx])
        
        # Decide severity based on confidence (Research logic)
        severity = "High" if confidence > 0.8 else "Medium"
        
        finding = {
            "vulnerability": "AI Flagged Semantic Risk",
            "contract": info["contract_name"],
            "function": info["function_name"],
            "line": int(info["line_number"]),
            "severity": severity,
            "explanation": (
                f"The ML model identified a semantic risk pattern in this function with "
                f"{confidence:.1%} confidence. {explanations[i]} "
                "This may indicate a complex logical flaw or business logic vulnerability."
            ),
            "suggested_fix": (
                "Review the business logic of this function. Check for unexpected state transitions "
                "or sensitive operations performed without proper validation or guardrails."
            ),
            "is_ml_finding": True,
            "confidence": round(confidence, 2)
        }
        ml_findings.append(finding)

    print(f"[ML] AI analysis complete: {len(ml_findings)} potential risks identified.")
    return ml_findings
