from firebase.firebase_init import db
from datetime import datetime

#  RBAC IMPORT
from utils.access_control import require_role


def update_payment_status(user_id, challan_no):
    """
    user_id    : Admin / Super Admin ID
    challan_no : Challan number whose payment is to be confirmed
    """

    #  ROLE CHECK
    require_role(user_id, ["admin", "super_admin"])

    # Find challan in Firestore
    docs = (
        db.collection("enforcement_logs")
        .where("challan_no", "==", challan_no)
        .where("payment_mode", "==", "ONLINE")
        .where("payment_status", "==", "PENDING")
        .stream()
    )

    updated = False

    for doc in docs:
        doc.reference.update({
            "payment_status": "PAID",
            "payment_confirmed_at": datetime.utcnow(),
            "payment_confirmed_by": user_id   #  AUDIT FIELD
        })
        updated = True

    return updated


# --------------------------------------------------
# CLI ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
    print("\n ONLINE PAYMENT CONFIRMATION")
    print("----------------------------------")

    user_id = input("Enter Admin/User ID: ").strip()
    challan_no = input("Enter Challan Number: ").strip()

    if not user_id or not challan_no:
        print(" User ID and Challan number are required")
        exit()

    try:
        success = update_payment_status(user_id, challan_no)
    except PermissionError as e:
        print(e)
        exit()

    if success:
        print(" Payment status updated to PAID")
    else:
        print(" No pending online payment found for this challan")