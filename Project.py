import face_recognition
import cv2
import os
import numpy as np
import pandas as pd
from datetime import datetime

# Load known faces
path = 'faces'  # Folder containing images of known people
known_face_encodings = []
known_face_names = []

for filename in os.listdir(path):
    image_path = os.path.join(path, filename)
    image = face_recognition.load_image_file(image_path)

    # Ensure face encoding is extracted correctly
    encodings = face_recognition.face_encodings(image)
    if encodings:  # Check if encoding is found
        encoding = encodings[0]
        known_face_encodings.append(encoding)
        known_face_names.append(os.path.splitext(filename)[0])  # Store name
    else:
        print(f"Warning: No face found in {filename}, skipping.")

print("Face Encoding Complete.")

# Initialize Webcam
try:
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        raise Exception("Error: Could not open webcam.")
except Exception as e:
    print(e)
    exit(1)

# Create an attendance log file
attendance_file = 'attendance.csv'
if not os.path.exists(attendance_file):
    pd.DataFrame(columns=["Name", "Time"]).to_csv(attendance_file, index=False)

# Track logged names to avoid duplicates
logged_names = set()

try:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to capture frame from webcam.")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # Optimize speed
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

        # Detect all faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=1)
        print("Face locations:", face_locations)

        if not face_locations:
            print("No faces detected in the frame.")
            continue

        # Extract encodings for all detected faces
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        print("Face encodings extracted:", len(face_encodings))

        # Process each face
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"

            # Find the best match
            if True in matches:
                match_index = matches.index(True)
                name = known_face_names[match_index]

                # Mark attendance
                if name not in logged_names:
                    new_entry = pd.DataFrame([[name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]], columns=["Name", "Time"])
                    df = pd.read_csv(attendance_file)
                    df = pd.concat([df, new_entry], ignore_index=True)
                    df.to_csv(attendance_file, index=False)
                    logged_names.add(name)

            # Display name on the webcam feed
            top, right, bottom, left = [i * 4 for i in face_location]  # Scale back
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Show webcam feed
        cv2.imshow('Face Recognition', frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting program...")
            break

finally:
    # Release resources
    video_capture.release()
    cv2.destroyAllWindows()

    # Export attendance data to Excel
    df = pd.read_csv(attendance_file)
    df.to_excel('attendance.xlsx', index=False)
    print("Attendance data exported to Excel.")