import customtkinter as ctk
import time
import cv2
import pandas as pd
import face_recognition
import os
from PIL import Image, ImageTk
from datetime import datetime
import subprocess
import threading

# Load known faces
known_faces = []
known_names = []
recognized_students = set()
face_dir = "faces"

if os.path.exists(face_dir):
    for filename in os.listdir(face_dir):
        image_path = os.path.join(face_dir, filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_faces.append(encoding[0])
            known_names.append(os.path.splitext(filename)[0])

# Initialize main window
root = ctk.CTk()
root.geometry("1000x700")
root.title("Advance Attendance System (AAS)")
root.configure(bg="#2c3e50")

# Title Label Outside Login Frame
ctk.CTkLabel(root, text="Advance Attendance System (AAS)", font=("Times New Roman", 32, "bold"), text_color="white").pack(pady=(20, 10))

cap = None
attendance_log = []
last_face_recognition_time = time.time()
is_camera_running = False

def login():
    entered_username = username_entry.get()
    entered_password = password_entry.get()
    if entered_username == "admin" and entered_password == "1234":
        login_frame.destroy()
        show_main_interface(entered_username)
    else:
        error_label.configure(text="Invalid Username or Password!", text_color="red")

def show_login_form():
    global username_entry, password_entry, login_frame, error_label
    
    login_frame = ctk.CTkFrame(root, fg_color="#34495e", corner_radius=10)
    login_frame.pack(pady=20, padx=200, fill="both")
    
    ctk.CTkLabel(login_frame, text="Username:", font=("Arial", 14), text_color="white").pack(pady=(20, 5))
    username_entry = ctk.CTkEntry(login_frame, width=250)
    username_entry.pack(pady=5)
    
    ctk.CTkLabel(login_frame, text="Password:", font=("Arial", 14), text_color="white").pack(pady=(20, 5))
    password_entry = ctk.CTkEntry(login_frame, width=250, show="*")
    password_entry.pack(pady=5)
    
    error_label = ctk.CTkLabel(login_frame, text="", font=("Arial", 12))
    error_label.pack(pady=5)
    
    login_button = ctk.CTkButton(login_frame, text="Login", font=("Arial", 14, "bold"), corner_radius=8, command=login)
    login_button.pack(pady=20)

def splash_screen():
    splash_frame = ctk.CTkFrame(root, fg_color="#2c3e50")
    splash_frame.place(relwidth=1, relheight=1)
    
    try:
        img = Image.open("face_icon.png").resize((100, 100))
        img = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(splash_frame, image=img, text="")
        img_label.image = img
        img_label.place(relx=0.5, rely=0.4, anchor="center")
    except:
        pass
    
    splash_label = ctk.CTkLabel(splash_frame, text="Advance Attendance System", font=("Arial", 18, "bold"), text_color="white")
    splash_label.place(relx=0.5, rely=0.6, anchor="center")
    
    # Use root.after to delay the transition to the login form
    root.after(1500, lambda: transition_to_login(splash_frame))

def transition_to_login(splash_frame):
    splash_frame.destroy()
    show_login_form()

def recognize_faces(frame):
    global last_face_recognition_time
    
    if time.time() - last_face_recognition_time < 1.0:  # Run recognition every 1 second
        return []

    last_face_recognition_time = time.time()
    
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame, model="hog")  # Faster detection
    if not face_locations:  # Skip encoding if no faces detected
        return []

    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    recognized_names = []
    for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        if len(known_faces) == 0:
            continue  # Skip matching if no known faces loaded

        distances = face_recognition.face_distance(known_faces, encoding)
        best_match_index = distances.argmin() if len(distances) > 0 else None
        
        if best_match_index is not None and distances[best_match_index] < 0.6:  # Threshold for match
            name = known_names[best_match_index]
        else:
            name = "Unknown"

        # Only add recognized faces (not "Unknown") to the attendance log
        if name != "Unknown" and name not in recognized_students:
            recognized_students.add(name)
            recognized_names.append(name)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            attendance_log.append([name, timestamp])

        # Scale face locations back to original frame size
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw green rectangle and name on the frame
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return recognized_names

def show_main_interface(username):
    global cap, video_frame, log_text, toggle_button, is_camera_running
    
    for widget in root.winfo_children():
        widget.destroy()
    
    ctk.CTkLabel(root, text=f"Teacher: {username}", font=("Arial", 22, "bold"), text_color="white").pack(pady=(10, 5))
    ctk.CTkLabel(root, text="Face Recognition Attendance System", font=("Arial", 20, "bold"), text_color="white").pack(pady=10)
    
    video_frame = ctk.CTkLabel(root, text="Camera Feed", width=640, height=360, fg_color="#1e272e")
    video_frame.pack(pady=10)
    
    log_text = ctk.CTkTextbox(root, height=100, fg_color="#34495e", text_color="white")
    log_text.pack(pady=10, padx=150, fill="both")
    log_text.insert("end", "Attendance Log:\n")

    def toggle_camera():
        global cap, is_camera_running
        if not is_camera_running:
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    raise Exception("Camera not available")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                cap.set(cv2.CAP_PROP_FPS, 30)  # Set to 30 FPS for smoother feed
                is_camera_running = True
                toggle_button.configure(text="Stop Camera")
                update_camera()
            except Exception as e:
                log_text.insert("end", f"Error: {e}\n")
                cap = None
        else:
            is_camera_running = False
            cap.release()
            cap = None
            video_frame.configure(image="", text="Camera Feed")
            toggle_button.configure(text="Start Camera")
            show_summary_screen(username)

    def update_camera():
        if is_camera_running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                recognized_names = recognize_faces(frame)
                for name in recognized_names:
                    log_text.insert("end", f"{name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(img)
                video_frame.configure(image=img_tk, text="")
                video_frame.image = img_tk
            
            # Schedule the next frame update
            root.after(10, update_camera)  # Update every 10ms for smoother feed

    toggle_button = ctk.CTkButton(root, text="Start Camera", font=("Arial", 14, "bold"), command=toggle_camera)
    toggle_button.pack()

def show_summary_screen(teacher_name):
    for widget in root.winfo_children():
        widget.destroy()
    
    ctk.CTkLabel(root, text="✨ Thanks for using AAS ✨", font=("Times New Roman", 26, "bold"), text_color="gold").pack(pady=20)
    ctk.CTkLabel(root, text="Your attendance is successfully recorded!", font=("Arial", 18), text_color="white").pack(pady=10)
    
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_students = len(attendance_log)
    
    ctk.CTkLabel(root, text=f"👨‍🏫 Teacher: {teacher_name}", font=("Arial", 16), text_color="white").pack(pady=5)
    ctk.CTkLabel(root, text=f"📅 Date & Time: {date_time}", font=("Arial", 16), text_color="white").pack(pady=5)
    ctk.CTkLabel(root, text=f"👨‍🎓 Students Present: {total_students}", font=("Arial", 16), text_color="white").pack(pady=5)
    
    def export_to_excel():
        df = pd.DataFrame(attendance_log, columns=["Student Name", "Timestamp"])
        df.to_excel("attendance.xlsx", index=False)
        subprocess.run(["start", "excel", "attendance.xlsx"], shell=True)
    ctk.CTkButton(root, text="📂 Open Excel File", font=("Arial", 14, "bold"), command=export_to_excel).pack(pady=20)

# Show splash screen first
splash_screen()

# Ensure resources are released on exit
def on_closing():
    global cap, is_camera_running
    if cap is not None:
        is_camera_running = False
        cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()