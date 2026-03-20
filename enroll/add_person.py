import cv2
from datetime import datetime
from firebase.firebase_init import db
from utils.face_utils import generate_face_encoding
from firebase_admin import firestore


# Capture face
cap = cv2.VideoCapture(0)
print("Press S to capture face")

while True:
    ret, frame = cap.read()
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("person.jpg", frame)
        break

cap.release()
cv2.destroyAllWindows()

# Face encoding
face_encoding = generate_face_encoding("person.jpg")
if face_encoding is None:
    print("❌ Face not detected")
    exit()

# Inputs
full_name = input("Full Name: ")
licence_number = input("Licence Number: ")
dob = input("DOB (YYYY-MM-DD): ")
address = input("Address: ")
issue_date = input("Issue Date (YYYY-MM-DD): ")
expiry_date = input("Expiry Date (YYYY-MM-DD): ")
vehicle_class = input("Vehicle Class: ")
fingerprint_id = int(input("Fingerprint ID: "))

# Firebase document (YOUR STRUCTURE)
doc_data = {
    "biometric": {
        "face_encoding": face_encoding,
        "fingerprint_id": fingerprint_id
    },
    "licence_info": {
        "full_name": full_name,
        "licence_number": licence_number,
        "dob": datetime.strptime(dob, "%Y-%m-%d"),
        "address": address,
        "issue_date": datetime.strptime(issue_date, "%Y-%m-%d"),
        "expiry_date": datetime.strptime(expiry_date, "%Y-%m-%d"),
        "vehicle_class": vehicle_class
    },
    "is_active": True,
    "created_at": firestore.SERVER_TIMESTAMP
}


db.collection("licence_holders").add(doc_data)
print("✅ Licence holder enrolled")

