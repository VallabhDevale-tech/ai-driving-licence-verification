# hsrp/hsrp_verification.py

from firebase.firebase_init import db


def hsrp_verification(expected_licence_number=None):
    print("\nHSRP VEHICLE VERIFICATION MODE\n")

    hsrp_number = input("Enter HSRP Number Plate: ").upper()
    doc = db.collection("hsrp_vehicles").document(hsrp_number).get()

    if not doc.exists:
        print("\n❌ HSRP Status: INVALID (Not Found)")
        return False, None

    data = doc.to_dict()
    data["hsrp_number"] = hsrp_number

    if data.get("is_blacklisted", False):
        print("\n❌ HSRP Status: BLACKLISTED")
        return False, data

    # 🔴 Plate status validation added
    if data.get("plate_status") != "GENUINE":
        print("\n❌ HSRP Status: INVALID (Plate Tampered or Fake)")
        return False, data

    if expected_licence_number:
        if data["linked_licence_number"] != expected_licence_number:
            print("\n❌ Vehicle does NOT belong to this Licence Holder")
            return False, data

    print("\nHSRP Plate Verification in Progress...\n")
    print("HSRP Status        : VALID")
    print("OWNER of Vehicle   :", data["owner_name"])
    print("Vehicle Type       :", data["vehicle_type"])
    print("Registration RTO   :", data["registration_rto"])
    print("Plate Issue Status :", data["plate_status"])

    return True, data