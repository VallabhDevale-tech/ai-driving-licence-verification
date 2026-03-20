import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from firebase.firebase_init import db


def hsrp_verify_step1(hsrp_no: str):
    """
    Returns:
        ("VALID", vehicle_data)      -> If plate exists and not blacklisted
        ("BLACKLISTED", vehicle_data)-> If plate exists but blacklisted
        ("INVALID", None)           -> If plate not found
    """

    try:
        #  Normalize again (extra safe)
        hsrp_no_clean = str(hsrp_no).strip().upper().replace(" ", "").replace("-", "")

        #  IMPORTANT: Firestore doc id is plate number
        doc_ref = db.collection("hsrp_vehicles").document(hsrp_no_clean)
        doc = doc_ref.get()

        #  Plate not found
        if not doc.exists:
            return "INVALID", None

        vehicle_data = doc.to_dict() or {}

        #  Add plate number in response (for UI display)
        vehicle_data["hsrp_number"] = hsrp_no_clean

        #  Blacklisted check
        if vehicle_data.get("is_blacklisted", False) is True:
            return "BLACKLISTED", vehicle_data

        return "VALID", vehicle_data

    except Exception as e:
        print(" ERROR inside hsrp_verify_step1:", e)
        return "INVALID", None
