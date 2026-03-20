# utils/access_control.py

from firebase.firebase_init import db

def get_user_role(user_id):
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return None
    return doc.to_dict().get("role")


def require_role(user_id, allowed_roles):
    role = get_user_role(user_id)

    if role is None:
        raise PermissionError(" User not registered in system")

    if role not in allowed_roles:
        raise PermissionError(f" Access denied for role: {role}")

    return True