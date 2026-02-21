import face_recognition
import cv2
import os
import pandas as pd
from datetime import datetime
import customtkinter as ctk
from PIL import Image, ImageTk
import time  # Import time module for adding delay

# CustomTkinter Setup
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

# Initialize the main window
root = ctk.CTk()
root.geometry('1900x1200')
root.title("Auto Attendance System (AAS)")

attendance_file = "attendance.csv"

def initialize_attendance_file():
    if not os.path.exists(attendance_file):
        pd.DataFrame(columns=["Name", "Date", "Time", "Teacher"]).to_csv(attendance_file, index=False)

# Create the login interface
def login():
    username = entry1.get()
    password = entry2.get()

    if username == 'a' and password == 'p':  # Example username/password check
        print('Login successful!')
        login_frame.pack_forget()  # Hide the login screen
        show_main_interface("John Doe", username)  # Pass teacher name and username
    else:
        print('Invalid credentials')

# Login screen (renamed to 'Login System')
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

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill='both', expand=True)

def show_main_interface(teacher_name, username):
    global video_frame, log_text, toggle_button
    for widget in root.winfo_children():
        widget.destroy()
    
    ctk.CTkLabel(root, text=f"Teacher: {teacher_name}", font=("Arial", 20, "bold"), text_color="white").pack(pady=10)
    ctk.CTkLabel(root, text=f"Username: {username}", font=("Arial", 14), text_color="white").pack(pady=5)
    video_frame = ctk.CTkLabel(root, text="Camera Feed", width=640, height=480, fg_color="#1e272e")
    video_frame.pack(pady=10)
    log_frame = ctk.CTkFrame(root, fg_color="#34495e", corner_radius=10)
    log_frame.pack(pady=10, padx=20, fill="both")
    ctk.CTkLabel(log_frame, text="Attendance Log:", font=("Arial", 14, "bold"), text_color="white").pack()
    log_text = ctk.CTkTextbox(log_frame, height=100, fg_color="#2c3e50", text_color="white")
    log_text.pack(padx=10, pady=5, fill="both")
    toggle_button = ctk.CTkButton(root, text="Start Camera", font=("Arial", 14, "bold"), command=toggle_camera)
    toggle_button.pack(pady=10)

def toggle_camera():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 60)
        toggle_button.configure(text="Stop Camera")
        update_camera()
    else:
        cap.release()
        cap = None
        toggle_button.configure(text="Next")
        show_final_screen()

def update_camera():
    if cap:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(Image.fromarray(frame))
            video_frame.configure(image=img_tk, text="")
            video_frame.image = img_tk
        root.after(10, update_camera)

def show_final_screen():
    for widget in root.winfo_children():
        widget.destroy()
    ctk.CTkLabel(root, text="Thanks for using AAS", font=("Times New Roman", 24, "bold"), text_color="white").pack(pady=10)
    ctk.CTkButton(root, text="Open Excel File", font=("Arial", 14, "bold"), command=lambda: os.system("start attendance.csv")).pack(pady=20)

initialize_attendance_file()
root.mainloop()
