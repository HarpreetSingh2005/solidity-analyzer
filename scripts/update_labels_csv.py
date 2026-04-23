import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
LABELS_FILE = os.path.join(DATASET_DIR, 'labels.csv')

# Category to label mapping
CATEGORY_MAPPING = {
    'safe': 0,
    'business_logic': 1,
    'price_oracle': 1,
    'flash_loan': 1
}

# Read existing labels to preserve descriptions
existing_entries = {}
headers = ["contract_path", "label", "category", "description"]

if os.path.exists(LABELS_FILE):
    with open(LABELS_FILE, "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            path = row.get("contract_path")
            if path:
                # Normalize path for comparison
                norm_path = os.path.abspath(path).lower()
                existing_entries[norm_path] = row

new_entries = []
count_new = 0

for category, label in CATEGORY_MAPPING.items():
    cat_dir = os.path.join(DATASET_DIR, category)
    if not os.path.exists(cat_dir):
        continue
    
    for filename in os.listdir(cat_dir):
        if filename.endswith(".sol"):
            filepath = os.path.join(cat_dir, filename)
            abs_path = os.path.abspath(filepath)
            norm_path = abs_path.lower()
            
            if norm_path in existing_entries:
                # Use existing row
                new_entries.append(existing_entries[norm_path])
            else:
                # Create new row
                desc = f"Legacy or missing contract: {filename}"
                new_entries.append({
                    "contract_path": abs_path,
                    "label": str(label),
                    "category": category,
                    "description": desc
                })
                count_new += 1

# Write the updated rows back to labels.csv
with open(LABELS_FILE, "w", newline="", encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for row in new_entries:
        writer.writerow({h: row.get(h, "") for h in headers})

print("="*40)
print("CSV Update Summary")
print("="*40)
print(f"Total contracts discovered and logged: {len(new_entries)}")
print(f"New entries added to CSV: {count_new}")
print(f"Successfully updated {LABELS_FILE}")
print("="*40)
