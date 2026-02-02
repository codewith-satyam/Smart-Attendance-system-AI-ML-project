import cv2
import os
import numpy as np
import csv
from datetime import datetime, date
import tkinter as tk
from tkinter import messagebox

# ===================== CONFIG =====================
DATASET_DIR = "dataset"
ATTENDANCE_FILE = "attendance.csv"
CONFIDENCE_THRESHOLD = 70

# ===================== FACE CASCADE =====================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ===================== LOAD & TRAIN =====================
def train_model():
    faces = []
    labels = []
    label_map = {}
    label_id = 0

    for person in os.listdir(DATASET_DIR):
        person_path = os.path.join(DATASET_DIR, person)
        if not os.path.isdir(person_path):
            continue

        label_map[label_id] = person

        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            detected = face_cascade.detectMultiScale(img, 1.3, 5)
            for (x, y, w, h) in detected:
                faces.append(img[y:y+h, x:x+w])
                labels.append(label_id)

        label_id += 1

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    return recognizer, label_map

recognizer, label_map = train_model()

# ===================== ATTENDANCE =====================
def already_marked(name):
    today = date.today().isoformat()
    if not os.path.exists(ATTENDANCE_FILE):
        return False

    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == name and row[1] == today:
                return True
    return False


def mark_attendance(name, status):
    if already_marked(name):
        return

    file_exists = os.path.exists(ATTENDANCE_FILE)
    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Date", "Time", "Status"])
        now = datetime.now()
        writer.writerow([name, now.date(), now.strftime("%H:%M:%S"), status])


# ===================== CAMERA =====================
cap = None
running = False

def start_camera():
    global cap, running
    cap = cv2.VideoCapture(0)
    running = True

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(face)

            if confidence < CONFIDENCE_THRESHOLD:
                name = label_map[label]
                mark_attendance(name, "P")
                text = f"{name} - Present"
                color = (0, 255, 0)
            else:
                text = "Unknown"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
            cv2.putText(frame, text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Attendance System", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    stop_camera()


def stop_camera():
    global running
    running = False
    if cap:
        cap.release()
    cv2.destroyAllWindows()


def mark_absent():
    today = date.today().isoformat()
    present_students = set()

    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[1] == today and row[3] == "P":
                    present_students.add(row[0])

    for person in os.listdir(DATASET_DIR):
        if person not in present_students:
            mark_attendance(person, "A")

    messagebox.showinfo("Done", "Absent marked successfully")

# ===================== GUI =====================
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("400x300")

tk.Label(root, text="Attendance System", font=("Arial", 18, "bold")).pack(pady=10)

tk.Button(root, text="Start Camera", width=20, command=start_camera).pack(pady=5)
tk.Button(root, text="Stop Camera", width=20, command=stop_camera).pack(pady=5)
tk.Button(root, text="Mark Absent", width=20, command=mark_absent).pack(pady=5)

tk.Label(root, text="Press 'Q' to close camera", fg="gray").pack(pady=10)

root.mainloop()