# 🎯 Smart Attendance System Using Face Recognition

An AI-powered real-time attendance management system that uses Face Recognition technology to automatically mark attendance through a live camera feed.

This system eliminates manual attendance, reduces proxy attendance, and generates structured reports in CSV/Excel format for easy monitoring and record keeping.

---

## 🚀 Project Overview

The Smart Attendance System leverages computer vision and machine learning techniques to:

- Detect faces in real-time using a webcam
- Recognize registered individuals
- Automatically mark attendance
- Store attendance data securely
- Export reports in CSV and Excel format

This project demonstrates practical implementation of AI in real-world classroom and organizational scenarios.

---

## ✨ Key Features

✅ Real-time Face Detection  
✅ Face Recognition using encodings  
✅ Automatic Attendance Marking  
✅ CSV & Excel Report Generation  
✅ Proxy Attendance Prevention  
✅ Simple and Interactive GUI  
✅ Lightweight and Easy to Deploy  

---

## 🛠️ Tech Stack

| Technology        | Purpose |
|------------------|---------|
| Python            | Core Programming Language |
| OpenCV            | Face Detection & Camera Handling |
| face_recognition  | Face Recognition & Encoding |
| CustomTkinter     | GUI Development |
| Pandas            | Attendance Data Handling |
| OpenPyXL          | Excel File Generation |

---

## 📂 Project Structure


Smart-Attendance-System-Using-Face-Recognition/
│
├── Main.py
├── main_final.py
├── Project.py
├── Backup.py
├── Faces/ # Registered face images
├── attendance.csv # Attendance record
├── attendance.xlsx # Excel report
├── .gitignore
└── README.md


---

## 💻 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/shashi00013/Smart-Attendance-System-Using-Face-Recognition.git
cd Smart-Attendance-System-Using-Face-Recognition
2️⃣ Install Dependencies

Make sure Python 3.9 or 3.10 is installed.

pip install customtkinter
pip install opencv-python
pip install face-recognition
pip install pandas
pip install openpyxl
pip install pillow
3️⃣ Run the Application
python Main.py
📊 How It Works

The system captures video from the webcam.

Faces are detected using OpenCV.

Face encodings are generated.

Encodings are compared with stored images.

If matched:

Name is identified

Attendance is marked

Time & Date are recorded

Report is saved in CSV & Excel format.

🔒 Security & Accuracy

Uses face encoding comparison to reduce false positives

Prevents proxy attendance

Stores structured attendance logs

Ensures one-time marking per session

📈 Future Enhancements

Flask Web-Based Dashboard

Admin Login System

Attendance Analytics & Charts

Database Integration (SQLite/MySQL)

Cloud Deployment

Face Confidence Score Display

🎓 Learning Outcomes

Through this project, I gained hands-on experience in:

Computer Vision

Face Recognition Algorithms

GUI Development

Data Handling & Reporting

Git & GitHub Version Control

👨‍💻 Author

Shashi Kumar
B.Tech Computer Science Engineering
📧 sk5251476@gmail.com

🔗 GitHub: https://github.com/shashi00013

⭐ If You Like This Project

Give it a ⭐ on GitHub and feel free to contribute or suggest improvements!


---
