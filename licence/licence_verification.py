# licence/licence_verification.py

import cv2
from datetime import datetime, timezone
from firebase.firebase_init import db
from utils.face_utils import generate_face_encoding, match_face
from utils.decision_engine import decide
from utils.reconfirmation import face_reconfirm, fingerprint_reconfirm


def is_licence_expired(licence_doc):
    expiry = licence_doc["licence_info"]["expiry_date"]

    if hasattr(expiry, "replace"):
        expiry_dt = expiry.replace(tzinfo=timezone.utc)
    else:
        expiry_dt = expiry

    return datetime.utcnow().replace(tzinfo=timezone.utc) > expiry_dt


def licence_verification():
    print("\nLICENCE VERIFICATION MODE\n")

    print("Please place your finger on the sensor to scan:")
    fp_input = int(input("Enter Fingerprint ID: "))

    matched_doc = None
    fp_ok = False

    docs = db.collection("licence_holders") \
        .where("biometric.fingerprint_id", "==", fp_input) \
        .where("is_active", "==", True) \
        .stream()

    for doc in docs:
        matched_doc = doc.to_dict()
        fp_ok = True
        break

    print("✅ Fingerprint is matched\n" if fp_ok else "❌ Fingerprint is not matched\n")

    print("Please Scan the Face of Driver")
    print("Press 'S' button to capture face")

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow("Face Scan", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite("scan.jpg", frame)
            break

    cap.release()
    cv2.destroyAllWindows()

    current_encoding = generate_face_encoding("scan.jpg")
    face_ok = False

    if current_encoding is not None and fp_ok:
        face_ok = match_face(
            matched_doc["biometric"]["face_encoding"],
            current_encoding
        )

    print("✅ Face matched\n" if face_ok else "❌ Face not matched\n")

    decision = decide(fp_ok, face_ok)

    if decision in ["VALID", "RECONFIRM"] and matched_doc:

        if decision == "RECONFIRM":
            print("\n⚠ RE-CONFIRMATION MODE IS ON")

            if not face_ok:
                if not face_reconfirm(matched_doc["biometric"]["face_encoding"]):
                    print("\n❌ ACCESS DENIED")
                    return False, matched_doc

            if not fp_ok:
                if not fingerprint_reconfirm(matched_doc["biometric"]["fingerprint_id"]):
                    print("\n❌ ACCESS DENIED")
                    return False, matched_doc

        # 🔴 EXPIRY CHECK ADDED
        if is_licence_expired(matched_doc):
            print("\n⚠ LICENCE EXPIRED")
            print("Licence Expiry Date:", matched_doc["licence_info"]["expiry_date"])
            return False, matched_doc

        print("==============================================")
        print("✅ DRIVER VERIFIED")
        print("==============================================")
        print("Licence Holder Name :", matched_doc["licence_info"]["full_name"])
        print("Licence Number     :", matched_doc["licence_info"]["licence_number"])
        print("Licence Expiry Date:", matched_doc["licence_info"]["expiry_date"])
        return True, matched_doc

    print("\n❌ ACCESS DENIED")
    return False, None