import pandas as pd
import mysql.connector
from datetime import datetime
import os
import glob

# ==== TỰ ĐỘNG LẤY FILE CSV MỚI NHẤT ====
folder_path = r"G:\crawl"
csv_files = glob.glob(os.path.join(folder_path, "bds_*.csv"))

if not csv_files:
    raise FileNotFoundError(f"Không tìm thấy file CSV nào trong thư mục {folder_path}")

csv_path = max(csv_files, key=os.path.getctime)
print(f"👉 Đang đọc file mới nhất: {csv_path}")

# ==== CẤU HÌNH DATABASE ====
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "staging"
}
table_name = "batdongsan"

df = pd.read_csv(csv_path)
df["crawl_date"] = datetime.now().strftime("%Y-%m-%d")

# === XỬ LÝ DỮ LIỆU TRỐNG ===
for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col].fillna(-1)
    else:
        df[col] = df[col].where(pd.notnull(df[col]), None)

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# === TẠO BẢNG NẾU CHƯA CÓ ===
column_defs = []
for col in df.columns:
    if col == "crawl_date":
        column_defs.append(f"`{col}` DATE")
    elif pd.api.types.is_numeric_dtype(df[col]):
        column_defs.append(f"`{col}` FLOAT")
    else:
        column_defs.append(f"`{col}` TEXT")

columns_sql = ", ".join(column_defs)

create_sql = f"""
CREATE TABLE IF NOT EXISTS `{table_name}` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    {columns_sql}
);
"""
cursor.execute(create_sql)

insert_sql = f"""
INSERT INTO `{table_name}` ({', '.join([f'`{c}`' for c in df.columns])})
VALUES ({', '.join(['%s'] * len(df.columns))})
"""

for _, row in df.iterrows():
    cursor.execute(insert_sql, tuple(row))

conn.commit()
cursor.close()
conn.close()

print(f"Đã import {len(df)} dòng dữ liệu từ {os.path.basename(csv_path)} vào bảng `{table_name}` trong database staging.")
