import face_recognition
import pickle
import numpy as np
from PIL import Image

def generate_face_encoding(image_path):
    try:
        # Load image using PIL (Python 3.12 safe)
        image = Image.open(image_path).convert("RGB")
        image = np.array(image, dtype=np.uint8)

        encodings = face_recognition.face_encodings(image, model="hog")

        if len(encodings) == 0:
            return None

        return pickle.dumps(encodings[0])

    except Exception as e:
        print("Face encoding error:", e)
        return None


def match_face(stored_blob, current_blob):
    try:
        # Firestore stores bytes as list
        if isinstance(stored_blob, list):
            stored_blob = bytes(stored_blob)

        # Safety check
        if not stored_blob:
            return False

        stored = pickle.loads(stored_blob)
        current = pickle.loads(current_blob)

        result = face_recognition.compare_faces(
            [stored], current, tolerance=0.5
        )

        return result[0]

    except Exception as e:
        print("Face match error:", e)
        return False

