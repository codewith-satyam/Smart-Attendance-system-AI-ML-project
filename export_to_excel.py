import pandas as pd
import os

CSV_FILE = "attendance.csv"
EXCEL_FILE = "attendance.xlsx"

if not os.path.exists(CSV_FILE):
    print("❌ attendance.csv not found")
    exit()

df = pd.read_csv(CSV_FILE)
df.to_excel(EXCEL_FILE, index=False)

print("✅ Excel file created: attendance.xlsx")