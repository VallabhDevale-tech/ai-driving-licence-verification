from firebase.firebase_init import db
from datetime import datetime

#  RBAC IMPORT
from utils.access_control import require_role


def get_today_cash_total(user_id, officer_id):
    """
    user_id    : Admin / Super Admin requesting the report
    officer_id : Officer whose cash collection is being calculated
    """

    #  ROLE CHECK — REPORTS ARE ADMIN ONLY
    require_role(user_id, ["admin", "super_admin"])

    today = datetime.utcnow().date()
    total = 0

    logs = (
        db.collection("enforcement_logs")
        .where("issued_by", "==", officer_id)   # matches audit field
        .where("payment_mode", "==", "CASH")
        .where("payment_status", "==", "PAID")
        .stream()
    )

    for log in logs:
        data = log.to_dict()

        # Defensive check
        if "issued_at" not in data:
            continue

        log_date = data["issued_at"].date()

        if log_date == today:
            total += data.get("fine", 0)

    return total


# --------------------------------------------------
# CLI ENTRY POINT
# --------------------------------------------------
if _name_ == "_main_":
    print("\n OFFICER CASH SUMMARY")
    print("----------------------------------")

    user_id = input("Enter Admin/User ID: ").strip()
    officer_id = input("Enter Officer ID: ").strip()

    if not user_id or not officer_id:
        print(" Admin ID and Officer ID are required")
        exit()

    try:
        cash = get_today_cash_total(user_id, officer_id)
    except PermissionError as e:
        print(e)
        exit()

    print("----------------------------------")
    print("Officer ID :", officer_id)
    print("Today's Cash Collected : ₹", cash)
    print("----------------------------------")