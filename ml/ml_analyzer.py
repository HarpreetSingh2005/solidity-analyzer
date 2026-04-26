# ml/ml_analyzer.py
from ml.feature_extractor import extract_features
from ml.model import predict

def analyze_with_ml(slither):
    try:
        features = extract_features(slither)
        prediction, confidence = predict(features)
        
        print(f"[ML] Prediction: {prediction} | Confidence: {confidence:.1%}")

        if confidence > 0.65:          # ← Increased threshold
            return [{
                "vulnerability": "Potential Semantic / Business Logic Vulnerability (ML)",
                "contract": slither.contracts[0].name,
                "function": "Multiple Functions",
                "line": "N/A (Semantic)",
                "severity": "Medium",
                "explanation": f"RandomForest ML model detected possible complex vulnerability with {confidence:.1%} confidence.",
                "suggested_fix": "Manually review business logic, reward calculations, price oracles, flash loan protections, and economic invariants.",
                "ml_confidence": round(confidence, 4),
                "is_ml_finding": True
            }]
        else:
            print(f"[ML] Skipped (confidence too low)")
            return []
    except Exception as e:
        print(f"[ML] Error: {e}")
        return []