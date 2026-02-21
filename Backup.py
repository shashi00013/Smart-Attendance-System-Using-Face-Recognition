import customtkinter as ctk
import face_recognition
import cv2
import os
import pandas as pd
from datetime import datetime
from PIL import Image, ImageTk

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

root = ctk.CTk()
root.geometry('800x600')

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill='both', expand=True)

def login():
    username = entry1.get()
    password = entry2.get()

    if username == 'admin' and password == 'password': 
        print('Login successful!')
        login_frame.pack_forget()  
        start_face_recognition() 
    else:
        print('Invalid credentials')


login_frame = ctk.CTkFrame(master=root)
login_frame.pack(pady=20, padx=60, fill='both', expand=True)

label = ctk.CTkLabel(master=login_frame, text='Login System', font=('Arial', 24))
label.pack(pady=20, padx=10)

entry1 = ctk.CTkEntry(master=login_frame, placeholder_text='Username')
entry1.pack(pady=12, padx=10)

entry2 = ctk.CTkEntry(master=login_frame, placeholder_text='Password', show='*')
entry2.pack(pady=12, padx=10)

button = ctk.CTkButton(master=login_frame, text='Login', command=login)
button.pack(pady=12, padx=10)

checkbox = ctk.CTkCheckBox(master=login_frame, text='Remember me')
checkbox.pack(pady=12, padx=10)


def start_face_recognition():
    path = 'faces' 
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(path):
        image_path = os.path.join(path, filename)
        image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)
        if encodings: 
            encoding = encodings[0]
            known_face_encodings.append(encoding)
            known_face_names.append(os.path.splitext(filename)[0])  
        else:
            print(f"Warning: No face found in {filename}, skipping.")

    print("Face Encoding Complete.")

    video_capture = cv2.VideoCapture(1)
    if not video_capture.isOpened():
        print("Error: Could not open webcam.")
        return

    attendance_file = 'attendance.csv'
    if not os.path.exists(attendance_file):
        pd.DataFrame(columns=["Name", "Time"]).to_csv(attendance_file, index=False)

    logged_names = set()

    def show_frame():
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to capture frame from webcam.")
            return

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  

        face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=1)
        print("Number of faces detected:", len(face_locations))

       

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        print("Number of face encodings generated:", len(face_encodings))

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"

            if True in matches:
                match_index = matches.index(True)
                name = known_face_names[match_index]

                if name not in logged_names:
                    new_entry = pd.DataFrame([[name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]], columns=["Name", "Time"])
                    df = pd.read_csv(attendance_file)
                    df = pd.concat([df, new_entry], ignore_index=True)
                    df.to_csv(attendance_file, index=False)
                    logged_names.add(name)

            top, right, bottom, left = [i * 4 for i in face_location]  # Scale back
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(img)

        canvas.create_image(0, 0, image=img_tk, anchor=ctk.NW)
        canvas.image = img_tk  
        canvas.after(10, show_frame)

    canvas = ctk.CTkCanvas(frame, width=640, height=480)
    canvas.pack()

    show_frame()  

    df = pd.read_csv(attendance_file)
    df.to_excel('attendance.xlsx', index=False)
    print("Attendance data exported to Excel.")
root.mainloop()