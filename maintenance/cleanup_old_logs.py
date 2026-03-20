from firebase.firebase_init import db
from datetime import datetime, timedelta


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
RETENTION_DAYS = 7


def cleanup_old_enforcement_logs():
    cutoff_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS)

    print(" Log Cleanup Started")
    print("Deleting logs older than:", cutoff_date)

    logs = db.collection("enforcement_logs") \
        .where("issued_at", "<", cutoff_date) \
        .stream()

    deleted_count = 0

    for log in logs:
        log.reference.delete()
        deleted_count += 1

    print(f" Cleanup completed. Deleted {deleted_count} old logs.")
    return deleted_count


# --------------------------------------------------
# MANUAL RUN SUPPORT
# --------------------------------------------------
if _name_ == "_main_":
    cleanup_old_enforcement_logs()