from firebase.firebase_init import db
from datetime import datetime


def log_enforcement(driver, vehicle, payload, user_id, record_type="ENFORCEMENT"):
    """
    driver      : Driver verification dictionary
    vehicle     : Vehicle verification dictionary
    payload     : Offence payload (empty dict for verification-only)
    user_id     : Officer ID (RBAC)
    record_type : "ENFORCEMENT" | "VERIFICATION"
    """

    # -------------------------------
    # COMMON DATA (FOR BOTH CASES)
    # -------------------------------
    data = {
        "record_type": record_type,        # 🔑 DIFFERENTIATOR
        "issued_by": user_id,
        "issued_at": datetime.utcnow(),

        "driver_name": driver.get("name"),
        "licence_no": driver.get("licence_no"),
        "vehicle_no": vehicle.get("number"),

        "verification_status": driver.get("status")
    }

    # -------------------------------
    # VERIFICATION ONLY (NO FINE)
    # -------------------------------
    if record_type == "VERIFICATION":
        data.update({
            "action_taken": "NO_FINE"
        })

    # -------------------------------
    # ENFORCEMENT (WITH FINE)
    # -------------------------------
    else:
        data.update({
            "challan_no": payload.get("challan_no"),

            "main_offence": payload.get("main_offence"),
            "sub_offence": payload.get("sub_offence"),
            "fine": payload.get("fine"),
            "legal_section": payload.get("section"),
            "severity": payload.get("severity"),

            "payment_mode": payload.get("payment_mode"),
            "payment_status": payload.get("payment_status"),

            # Optional online payment data
            "upi_link": payload.get("upi_link"),
            "qr_code_path": payload.get("qr_code_path")
        })

    # -------------------------------
    # FIRESTORE WRITE
    # -------------------------------
    db.collection("enforcement_logs").add(data)