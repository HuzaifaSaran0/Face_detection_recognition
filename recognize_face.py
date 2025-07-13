import face_recognition
import cv2
import pickle
import numpy as np

# Load all known faces
with open("known_faces.pkl", "rb") as f:
    known_faces = pickle.load(f)

known_names = list(known_faces.keys())
known_encodings = list(known_faces.values())

# Start webcam
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

print("🎥 Running face recognition... Press 'q' to quit.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        continue

    frame = frame.copy()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame = np.ascontiguousarray(rgb_frame)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(distances)
        best_distance = distances[best_match_index]

        if best_distance < 0.5:  # Threshold
            name = known_names[best_match_index]
            label = f"✅ {name} ({best_distance:.2f})"
            color = (0, 255, 0)
        else:
            label = "❌ Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
