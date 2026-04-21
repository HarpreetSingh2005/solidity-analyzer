# training_instructions.md

# Phase 2: Training the ML Model on Google Colab

Since training can be resource-intensive, we use Google Colab to train the model and then run inference locally on your laptop.

## 1. Prepare the Dataset
1. Download a small subset of the [SmartBugs Curated](https://github.com/smartbugs/smartbugs-curated) dataset.
2. For this research project, start with ~100-200 labeled contracts.
3. Organize your data into a CSV or JSON where each row represents a function and its features (use the `feature_extractor.py` to generate this).

## 2. Train on Google Colab
Copy the following code into a new cell in [Google Colab](https://colab.research.google.com/):

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load your extracted features
# Assuming you uploaded a 'features_dataset.csv'
df = pd.read_csv('features_dataset.csv')

# 2. Define Features and Labels
# 'is_vulnerable' should be your label (1 for bug, 0 for clean)
feature_cols = [
    "num_nodes", "num_lines", "num_parameters", "num_modifiers", 
    "is_payable", "is_constructor", "visibility_score", "num_external_calls", 
    "num_internal_calls", "num_state_reads", "num_state_writes", 
    "has_tx_origin", "has_msg_value", "can_send_eth", "has_assembly", 
    "calls_before_state_update"
]

X = df[feature_cols]
y = df['is_vulnerable']

# 3. Train the Lightweight Model
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X, y)

# 4. Save for Local Use
joblib.dump(model, 'model.pkl')
print("Training complete. Download 'model.pkl' and place it in the 'ml/' folder of your project.")
```

## 3. Local Setup
1. Download the `model.pkl` from Colab.
2. Place it inside your project at: `f:/Minor Project/solidity-analyzer/ml/model.pkl`.
3. Run the analyzer with the `--ml` flag:
   ```bash
   python main.py tests/Reentrancy.sol --ml
   ```

## 4. Why this works for your laptop
- **Training**: Done on Google's servers.
- **Inference**: Loading a `RandomForest` model and running prediction on ~20 features takes almost zero CPU/RAM, making it perfect for your hardware.
