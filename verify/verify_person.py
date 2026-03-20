import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# --------------------------------------------------
# OFFICER IDENTIFICATION (RBAC USER)
# --------------------------------------------------
USER_ID = "OFFICER_101"   # Must exist in Firebase users collection

import cv2
from firebase.firebase_init import db
from utils.face_utils import generate_face_encoding, match_face
from utils.decision_engine import decide
from utils.reconfirmation import face_reconfirm, fingerprint_reconfirm
from enforcement.officer_panel import officer_enforcement

# -----------------------------
# VERIFICATION MODES
# -----------------------------
MODE_LICENCE = 1
MODE_HSRP = 2
MODE_COMBINED = 3


print("\n==============================================")
print("  WELCOME IN AUTHENTICATION SYSTEM OF")
print("           DRIVING LICENSE")
print("==============================================\n")

print("Select Verification Mode:")
print("1. Licence Verification Mode")
print("2. HSRP Vehicle Verification Mode")
print("3. Combined Mode")

try:
    mode = int(input("Enter choice: "))
except ValueError:
    print("Invalid input")
    mode = -1


# =====================================================
# LICENCE VERIFICATION
# =====================================================
def licence_verification():
    print("\nLICENCE VERIFICATION MODE\n")

    fp_input = int(input("Enter Fingerprint ID: "))
    matched_doc = None
    fp_ok = False

    docs = (
        db.collection("licence_holders")
        .where("biometric.fingerprint_id", "==", fp_input)
        .where("is_active", "==", True)
        .stream()
    )

    for doc in docs:
        matched_doc = doc.to_dict()
        fp_ok = True
        break

    print(" Fingerprint matched\n" if fp_ok else " Fingerprint not matched\n")

    # -----------------------------
    # FACE SCAN
    # -----------------------------
    print("Scan Face (Press 'S')")
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        cv2.imshow("Face Scan", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite("scan.jpg", frame)
            break

    cap.release()
    cv2.destroyAllWindows()

    current_encoding = generate_face_encoding("scan.jpg")
    face_ok = False

    if current_encoding is not None:
        if fp_ok and matched_doc:
            face_ok = match_face(
                matched_doc["biometric"]["face_encoding"],
                current_encoding
            )
        else:
            docs = db.collection("licence_holders") \
                .where("is_active", "==", True) \
                .stream()

            for doc in docs:
                data = doc.to_dict()
                if match_face(data["biometric"]["face_encoding"], current_encoding):
                    matched_doc = data
                    face_ok = True
                    break

    print(" Face matched\n" if face_ok else " Face not matched\n")

    decision = decide(fp_ok, face_ok)

    # -----------------------------
    # RECONFIRMATION
    # -----------------------------
    if decision in ["VALID", "RECONFIRM"] and matched_doc:

        if decision == "RECONFIRM":
            print(" RE-CONFIRMATION REQUIRED")

            if not face_ok:
                if not face_reconfirm(matched_doc["biometric"]["face_encoding"]):
                    return False, matched_doc

            if not fp_ok:
                if not fingerprint_reconfirm(
                        matched_doc["biometric"]["fingerprint_id"]):
                    return False, matched_doc

        print("==============================================")
        print(" DRIVER VERIFIED")
        print("==============================================")
        print("Licence Holder Name :", matched_doc["licence_info"]["full_name"])
        print("Licence Number     :", matched_doc["licence_info"]["licence_number"])
        print("Licence Expiry Date:", matched_doc["licence_info"]["expiry_date"])
        print("==============================================")

        return True, matched_doc

    print("\n ACCESS DENIED")
    return False, matched_doc


# =====================================================
# HSRP VERIFICATION
# =====================================================
def hsrp_verification(expected_licence_number=None):
    print("\nHSRP VEHICLE VERIFICATION MODE\n")

    hsrp_number = input("Enter HSRP Number Plate: ").upper()
    hsrp_doc = db.collection("hsrp_vehicles").document(hsrp_number).get()

    if not hsrp_doc.exists:
        print(" HSRP INVALID")
        return False, None

    hsrp_data = hsrp_doc.to_dict()
    hsrp_data["hsrp_number"] = hsrp_number

    if hsrp_data.get("is_blacklisted", False):
        print(" HSRP BLACKLISTED")
        return False, hsrp_data

    if expected_licence_number and \
        hsrp_data["linked_licence_number"] != expected_licence_number:
        print(" Vehicle does not belong to licence holder")
        return False, hsrp_data

    print("==============================================")
    print("HSRP Status : VALID")
    print("Owner Name  :", hsrp_data["owner_name"])
    print("Vehicle Type:", hsrp_data["vehicle_type"])
    print("RTO         :", hsrp_data["registration_rto"])
    print("Plate Status:", hsrp_data["plate_status"])
    print("==============================================")

    return True, hsrp_data


# =====================================================
# MAIN FLOW
# =====================================================
doc = None
vehicle_data = None
verification_status = "UNKNOWN"

if mode == MODE_LICENCE:
    ok, doc = licence_verification()
    verification_status = "LICENCE VALID" if ok else "LICENCE INVALID"

elif mode == MODE_HSRP:
    ok, vehicle_data = hsrp_verification()
    verification_status = "HSRP VALID" if ok else "HSRP INVALID"

    # --------------------------------------------------
    # FETCH DRIVER DATA FROM LINKED LICENCE
    # --------------------------------------------------
    if ok and vehicle_data:
        linked_licence = vehicle_data.get("linked_licence_number")

        if linked_licence:
            docs = db.collection("licence_holders") \
                .where("licence_info.licence_number", "==", linked_licence) \
                .where("is_active", "==", True) \
                .stream()

            for d in docs:
                doc = d.to_dict()
                break

elif mode == MODE_COMBINED:

    ok_lic, doc = licence_verification()
    ok_hsrp = False
    vehicle_data = None

    if doc:
        ok_hsrp, vehicle_data = hsrp_verification(
            expected_licence_number=doc["licence_info"]["licence_number"]
        )

    licence_status = "VALID" if ok_lic else "INVALID"
    hsrp_status = "VALID" if ok_hsrp else "INVALID"

    verification_status = f"LICENCE {licence_status} | HSRP {hsrp_status}"

else:
    print(" Invalid Mode Selected")
    verification_status = "INVALID MODE"


# =====================================================
# ENFORCEMENT (RBAC SAFE)
# =====================================================
driver_data = {
    "name": doc["licence_info"]["full_name"] if doc else "UNKNOWN",
    "licence_no": doc["licence_info"]["licence_number"] if doc else "N/A",
    "status": verification_status
}

vehicle_info = {
    "number": vehicle_data["hsrp_number"] if vehicle_data else "N/A",
    "status": verification_status
}

#  PASS USER_ID EXPLICITLY
officer_enforcement(USER_ID, driver_data, vehicle_info)