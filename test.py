import face_recognition
import cv2
import os
import numpy as np
import pandas as pd
from datetime import datetime
import customtkinter as ctk
from PIL import Image, ImageTk

# Initialize GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FaceRecognitionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition Attendance System")
        self.geometry("900x600")

        self.known_face_encodings, self.known_face_names = self.load_known_faces()
        self.logged_names = set()
        self.video_capture = None
        self.running = False

        self.label_title = ctk.CTkLabel(self, text="Face Recognition Attendance", font=("Helvetica", 20, "bold"))
        self.label_title.pack(pady=10)

        self.video_label = ctk.CTkLabel(self)
        self.video_label.pack()

        self.btn_start = ctk.CTkButton(self, text="Start Recognition", command=self.start_recognition)
        self.btn_start.pack(pady=10)

        self.btn_stop = ctk.CTkButton(self, text="Stop Recognition", command=self.stop_recognition)
        self.btn_stop.pack()

        self.btn_export = ctk.CTkButton(self, text="Export to Excel", command=self.export_to_excel)
        self.btn_export.pack(pady=10)

    def load_known_faces(self, path="faces"):
        known_face_encodings = []
        known_face_names = []
        if not os.path.exists(path):
            print(f"Warning: '{path}' directory not found! Please create it and add images.")
            return known_face_encodings, known_face_names
        
        for filename in os.listdir(path):
            image_path = os.path.join(path, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(filename)[0])
            else:
                print(f"Warning: No face found in {filename}, skipping.")

        print(f"Loaded {len(known_face_names)} known faces.")
        return known_face_encodings, known_face_names

    def start_recognition(self):
        if self.running:
            return
        
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

        if not self.video_capture.isOpened():
            print("Error: Could not open webcam.")
            return

        self.running = True
        self.process_frame()

    def process_frame(self):
        if not self.running:
            return

        ret, frame = self.video_capture.read()
        if not ret:
            print("Error: Failed to capture frame.")
            self.stop_recognition()
            return

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            if True in matches:
                match_index = matches.index(True)
                name = self.known_face_names[match_index]
                self.mark_attendance(name)
            
            top, right, bottom, left = [i * 4 for i in face_location]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = ImageTk.PhotoImage(img)
        self.video_label.configure(image=img)
        self.video_label.image = img

        self.after(10, self.process_frame)

    def stop_recognition(self):
        if self.video_capture:
            self.running = False
            self.video_capture.release()
        self.video_label.configure(image="")

    def mark_attendance(self, name):
        attendance_file = "attendance.csv"
        if name not in self.logged_names:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(attendance_file, "a") as f:
                f.write(f"{name},{now}\n")
            self.logged_names.add(name)

    def export_to_excel(self):
        df = pd.read_csv("attendance.csv")
        df.to_excel("attendance.xlsx", index=False)
        print("Attendance exported to Excel.")

if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.mainloop()