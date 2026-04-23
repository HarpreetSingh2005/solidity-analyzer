# scripts/train_ml.py
import sys
from pathlib import Path

# === CRITICAL FIX: Add project root to Python path ===
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.model import train_model

if __name__ == "__main__":
    print("=" * 60)
    print("SESA Phase 2 — ML Model Training")
    print("=" * 60)
    print(f"Project root: {PROJECT_ROOT}")
    print("Starting training using dataset/features.csv...\n")

    try:
        model = train_model()
        print("\n🎉 Training completed successfully!")
        print("Model saved to ml/model.pkl")
    except Exception as e:
        print(f"\n❌ Training failed: {e}")