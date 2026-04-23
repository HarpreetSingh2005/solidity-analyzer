# SESA - Final Training on 241 Samples

!pip install pandas scikit-learn joblib xgboost lightgbm matplotlib seaborn -q

from google.colab import files
import pandas as pd
import io

print("Upload latest features.csv (241 rows)")
uploaded = files.upload()
df = pd.read_csv(io.BytesIO(uploaded[list(uploaded.keys())[0]]))

print(f"✅ Loaded {len(df)} samples | Vulnerable: {df['label'].sum()} | Safe: {len(df)-df['label'].sum()}")

feature_cols = [
    "num_functions", "num_external_calls", "calls_before_state_update",
    "num_state_vars", "has_tx_origin", "has_selfdestruct", "avg_function_size",
    "num_payable_functions", "num_modifiers", "num_state_writes",
    "has_delegatecall", "has_assembly", "uses_tx_origin_in_condition",
    "external_call_before_any_state_update", "has_unchecked_external_call",
    "has_balance_check_before_send", "max_call_depth",
    "has_reentrancy_guard_pattern", "num_user_controlled_inputs_to_state"
]

X = df[feature_cols].fillna(0)
y = df["label"]

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

results = []

print("\n=== Training Multiple Models ===")

# Random Forest
rf = RandomForestClassifier(n_estimators=500, max_depth=12, class_weight='balanced', random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
pred = rf.predict(X_test)
results.append(["RandomForest", round(accuracy_score(y_test, pred), 4), round(f1_score(y_test, pred), 4)])

# XGBoost
xgb = XGBClassifier(n_estimators=400, max_depth=7, learning_rate=0.08, scale_pos_weight=143/98, random_state=42)
xgb.fit(X_train, y_train)
pred = xgb.predict(X_test)
results.append(["XGBoost", round(accuracy_score(y_test, pred), 4), round(f1_score(y_test, pred), 4)])

# LightGBM
lgb = LGBMClassifier(n_estimators=400, max_depth=8, learning_rate=0.1, class_weight='balanced', random_state=42, verbose=-1)
lgb.fit(X_train, y_train)
pred = lgb.predict(X_test)
results.append(["LightGBM", round(accuracy_score(y_test, pred), 4), round(f1_score(y_test, pred), 4)])

# Comparison
comparison = pd.DataFrame(results, columns=["Model", "Accuracy", "F1-Score"])
print(comparison.sort_values(by="F1-Score", ascending=False))

# Save Best Model (usually RandomForest)
joblib.dump(rf, 'model.pkl')
files.download('model.pkl')

print("\n✅ Best model downloaded as model.pkl")