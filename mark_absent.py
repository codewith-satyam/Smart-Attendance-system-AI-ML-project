import os
import csv
from datetime import datetime

DATASET_PATH = "dataset"
ATTENDANCE_FILE = "attendance.csv"

today = datetime.now().strftime("%Y-%m-%d")

students = [
    s for s in os.listdir(DATASET_PATH)
    if os.path.isdir(os.path.join(DATASET_PATH, s))
]

present_students = []

if os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header

        for row in reader:
            # ✅ skip empty or broken rows
            if not row or len(row) < 4:
                continue

            if row[1] == today and row[3] == "P":
                present_students.append(row[0])

with open(ATTENDANCE_FILE, "a", newline="") as f:
    writer = csv.writer(f)

    for student in students:
        if student not in present_students:
            writer.writerow([student, today, "NA", "A"])
            print(f"❌ Absent marked: {student}")
