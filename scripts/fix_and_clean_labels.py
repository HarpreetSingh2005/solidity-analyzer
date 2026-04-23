from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path("F:/Minor Project/solidity-analyzer")
labels_path = PROJECT_ROOT / "dataset" / "labels.csv"

if not labels_path.exists():
    print("labels.csv not found!")
    exit()

df = pd.read_csv(labels_path)

print(f"Original entries: {len(df)}")

# Clean and fix labels based on path
def get_clean_label(row):
    path_str = str(row['contract_path']).lower()
    filename = Path(path_str).name.lower()
    
    if any(x in filename for x in ['safe', 'safe_']) or '/safe/' in path_str:
        return 0
    else:
        return 1

df['label'] = df.apply(get_clean_label, axis=1)

# Remove any obvious duplicates based on contract_path
df = df.drop_duplicates(subset=['contract_path'], keep='first')

# Save cleaned version
df.to_csv(labels_path, index=False)

print("✅ labels.csv cleaned and fixed!")
print(f"Total entries now: {len(df)}")
print(f"Vulnerable: {df['label'].sum()}")
print(f"Safe: {len(df) - df['label'].sum()}")

# Show summary
print("\nLabel Distribution:")
print(df['label'].value_counts())
print("\nFirst 8 rows:")
print(df[['contract_path', 'label']].head(8))