from firebase.firebase_init import db

db.collection("users").document("OFFICER_101").set({
    "name": "Traffic Officer Vallabh",
    "role": "officer",
    "is_active": True
})

print(" Officer registered successfully")
