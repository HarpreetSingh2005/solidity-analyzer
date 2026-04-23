# =====================================================
# SESA - Final Report Graphics Generator (Real Data)
# =====================================================

!pip install pandas scikit-learn joblib xgboost lightgbm matplotlib seaborn -q

from google.colab import files
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Upload your latest features.csv
print("Upload features.csv (241 samples)")
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
from sklearn.metrics import accuracy_score, f1_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

results = []

# Train models
models = {
    "RandomForest": RandomForestClassifier(n_estimators=400, max_depth=12, class_weight='balanced', random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=400, max_depth=7, learning_rate=0.08, scale_pos_weight=143/98, random_state=42),
    "LightGBM": LGBMClassifier(n_estimators=400, max_depth=8, learning_rate=0.1, class_weight='balanced', random_state=42, verbose=-1),
    "LogisticRegression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
}

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    results.append([name, round(accuracy_score(y_test, pred), 4), round(f1_score(y_test, pred), 4)])

comparison = pd.DataFrame(results, columns=["Model", "Accuracy", "F1-Score"])
print("\nModel Comparison:\n", comparison.sort_values(by="F1-Score", ascending=False))

# ====================== GRAPHICS ======================

plt.style.use('seaborn-v0_8')

# 1. Model Comparison Bar Chart
plt.figure(figsize=(10,6))
sns.barplot(x='F1-Score', y='Model', data=comparison.sort_values(by="F1-Score", ascending=False), palette='viridis')
plt.title('Model Performance Comparison (F1-Score)', fontsize=16)
plt.xlabel('F1-Score')
plt.tight_layout()
plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. Dataset Distribution
plt.figure(figsize=(8,8))
sizes = [df['label'].sum(), len(df)-df['label'].sum()]
labels = ['Vulnerable (143)', 'Safe (98)']
plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#ff6666', '#66b3ff'], startangle=90, textprops={'fontsize': 14})
plt.title('Dataset Distribution (241 Contracts)', fontsize=16)
plt.savefig('dataset_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

# 3. Feature Importance (using best model - RandomForest)
rf = models["RandomForest"]
importances = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)

plt.figure(figsize=(10,8))
sns.barplot(x=importances.values, y=importances.index, palette='mako')
plt.title('Feature Importance (RandomForest)', fontsize=16)
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n✅ All graphics generated and saved!")
files.download('model_comparison.png')
files.download('dataset_distribution.png')
files.download('feature_importance.png')