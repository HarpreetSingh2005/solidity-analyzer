# scripts/extract_features_for_ml.py
import sys
from pathlib import Path
import pandas as pd
import csv

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from slither import Slither
from ml.feature_extractor import extract_features

def extract_all_features():
    dataset_dir = PROJECT_ROOT / "dataset"
    labels_path = dataset_dir / "labels.csv"
    features_path = dataset_dir / "features.csv"

    rows = []
    seen_paths = set()

    print("🚀 Starting full feature extraction...\n")

    # === ONLY use labels.csv (best source) ===
    if labels_path.exists():
        print("📌 Processing all contracts from labels.csv...")
        with open(labels_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contract_path = row["contract_path"]
                if contract_path in seen_paths:
                    continue
                seen_paths.add(contract_path)

                try:
                    label = int(row.get("label", 1))
                    slither = Slither(contract_path, disable_color=True)
                    features = extract_features(slither)
                    features["label"] = label
                    features["contract_path"] = contract_path
                    features["source"] = "custom"
                    rows.append(features)
                    
                    status = "Vulnerable" if label == 1 else "Safe"
                    print(f"   ✓ {status}: {Path(contract_path).name}")
                except Exception as e:
                    print(f"   ✗ Failed {Path(contract_path).name}: {e}")

    # Save
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(features_path, index=False)
        
        print("\n" + "="*70)
        print("✅ FEATURE EXTRACTION COMPLETED")
        print("="*70)
        print(f"Total samples     : {len(df)}")
        print(f"Vulnerable        : {df['label'].sum()}")
        print(f"Safe              : {len(df) - df['label'].sum()}")
        print(f"File saved at     : {features_path}")
        print("="*70)
    else:
        print("No contracts processed.")

if __name__ == "__main__":
    extract_all_features()