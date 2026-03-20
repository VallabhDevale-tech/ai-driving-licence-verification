from firebase.firebase_init import db

db.collection("users").document("ADMIN_001").set({
    "name": "RTO Admin",
    "role": "admin",
    "is_active": True
})

print(" Admin registered successfully")
