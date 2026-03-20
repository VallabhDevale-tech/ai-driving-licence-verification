import base64
import os
from firebase.firebase_init import db
from utils.face_utils import generate_face_encoding, match_face
from utils.decision_engine import decide


#  Get licence holder document using licence number
def get_doc_by_licence(licence_no):
    try:
        docs = (
            db.collection("licence_holders")
            .where("licence_info.licence_number", "==", licence_no)
            .where("is_active", "==", True)
            .stream()
        )
        for doc in docs:
            return doc.to_dict()
    except Exception as e:
        print("[ERROR] get_doc_by_licence:", e)

    return None


#  Step-1 Verification (Fingerprint + Face)
def licence_verify_step1(fingerprint_id, scan_image_path):
    matched_doc = None
    fp_ok = False
    face_ok = False

    try:
        # First check fingerprint
        docs = (
            db.collection("licence_holders")
            .where("biometric.fingerprint_id", "==", fingerprint_id)
            .where("is_active", "==", True)
            .stream()
        )

        for doc in docs:
            matched_doc = doc.to_dict()
            fp_ok = True
            break

        # Now check face
        current_encoding = generate_face_encoding(scan_image_path)

        if current_encoding is not None:
            if fp_ok and matched_doc:
                stored_enc = matched_doc.get("biometric", {}).get("face_encoding", None)

                if stored_enc is not None:
                    face_ok = match_face(stored_enc, current_encoding)
                else:
                    face_ok = False

            else:
                #  Face-only matching (search all active users)
                docs = db.collection("licence_holders").where("is_active", "==", True).stream()
                for doc in docs:
                    data = doc.to_dict()
                    stored_enc = data.get("biometric", {}).get("face_encoding", None)

                    if stored_enc is not None:
                        if match_face(stored_enc, current_encoding):
                            matched_doc = data
                            face_ok = True
                            break

        #  Decision engine
        decision = decide(fp_ok, face_ok)
        return decision, matched_doc, fp_ok, face_ok

    except Exception as e:
        print("[ERROR] licence_verify_step1:", e)
        return "INVALID", None, False, False


# Save base64 image to JPG file
def save_base64_image(base64_str, filepath):
    try:
        # remove header "data:image/jpeg;base64,"
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]

        img_bytes = base64.b64decode(base64_str)
        with open(filepath, "wb") as f:
            f.write(img_bytes)

        return True
    except Exception as e:
        print("[ERROR] save_base64_image:", e)
        return False


#  FACE reconfirm logic (2/3 match)
def face_reconfirm_web(stored_encoding, image_paths):
    match_count = 0

    for img_path in image_paths:
        enc = generate_face_encoding(img_path)

        if enc is not None:
            if match_face(stored_encoding, enc):
                match_count += 1

    return match_count >= 2  #  2 out of 3 must match


# Fingerprint reconfirm logic (2/3 match)
def fingerprint_reconfirm_web(stored_fp_id, scans_list):
    match_count = 0

    for fp in scans_list:
        try:
            if int(fp) == int(stored_fp_id):
                match_count += 1
        except:
            pass

    return match_count >= 2  # 2 out of 3 must match


#  MAIN RECONFIRMATION VERIFY FUNCTION
def licence_verify_reconfirm(matched_doc, fp_list, face_sample_paths, need_fp, need_face):
    """
    fp_list -> [fp1, fp2, fp3]
    face_sample_paths -> ["uploads/f1.jpg", "uploads/f2.jpg", "uploads/f3.jpg"]
    """

    fp_ok = True
    face_ok = True

    # Face Reconfirm Check
    if need_face:
        stored_encoding = matched_doc.get("biometric", {}).get("face_encoding", None)

        if stored_encoding is None:
            face_ok = False
        else:
            face_ok = face_reconfirm_web(stored_encoding, face_sample_paths)

    #  Fingerprint Reconfirm Check
    if need_fp:
        stored_fp = matched_doc.get("biometric", {}).get("fingerprint_id", None)

        if stored_fp is None:
            fp_ok = False
        else:
            fp_ok = fingerprint_reconfirm_web(stored_fp, fp_list)

    #  Final Decision
    decision = decide(fp_ok, face_ok)

    if decision == "VALID":
        return "VALID", fp_ok, face_ok

    return "INVALID", fp_ok, face_ok
