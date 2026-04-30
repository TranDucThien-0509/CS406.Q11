import os
import json
import pandas as pd

CSV_PATH = "data/annotations.csv"
OUT_DIR = "data/output_json"

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

REQUIRED_LABELS = ["SELLER", "ADDRESS", "TIMESTAMP", "TOTAL_COST"]

# Nếu có cột file_name thì group theo file
group_key = "file_name" if "file_name" in df.columns else None

groups = df.groupby(group_key) if group_key else [(None, df)]

for file_id, g in groups:
    result = {k: "" for k in REQUIRED_LABELS}

    for _, row in g.iterrows():
        label = str(row["anno_labels"]).strip()
        text = str(row["anno_text"]).strip()

        if label in result:
            # nếu 1 label xuất hiện nhiều lần → nối lại
            if result[label]:
                result[label] += " " + text
            else:
                result[label] = text

    # tên output file
    out_name = file_id if file_id else "output"
    out_name = os.path.splitext(str(out_name))[0]

    out_path = os.path.join(OUT_DIR, f"{out_name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_path}")
