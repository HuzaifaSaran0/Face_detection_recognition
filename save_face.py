import cv2
import dlib
import numpy as np
import pickle
import os

# Load models
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

# File to store all face encodings
FACE_DB = "known_faces.pkl"

# Load existing faces if any
if os.path.exists(FACE_DB):
    with open(FACE_DB, "rb") as f:
        known_faces = pickle.load(f)
else:
    known_faces = {}

video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

print("Press 's' to save new face, or 'q' to quit.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        continue

    frame = frame.copy()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame = np.ascontiguousarray(rgb_frame)

    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)

    if key == ord('s'):
        faces = detector(rgb_frame, 1)
        if faces:
            name = input("Enter the name of the person: ").strip()
            shape = predictor(rgb_frame, faces[0])
            face_descriptor = face_rec_model.compute_face_descriptor(rgb_frame, shape)
            face_encoding = np.array(face_descriptor)

            known_faces[name] = face_encoding
            with open(FACE_DB, "wb") as f:
                pickle.dump(known_faces, f)

            print(f"✅ Saved face for '{name}'")
        else:
            print("❌ No face detected!")

    elif key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
