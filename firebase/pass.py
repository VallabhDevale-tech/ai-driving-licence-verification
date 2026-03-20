from firebase.firebase_init import db

# Update existing officer with password
db.collection("users").document("OFFICER_101").set({
    "name": "Traffic Officer Vallabh",
    "role": "officer",
    "is_active": True,
    "password": "password123"  # CHANGE THIS IN PRODUCTION!
})

print("✓ Officer OFFICER_101 updated with password")

# Update existing admin with password
db.collection("users").document("ADMIN_001").set({
    "name": "RTO Admin",
    "role": "admin",
    "is_active": True,
    "password": "admin123"  # CHANGE THIS IN PRODUCTION!
})

print("✓ Admin ADMIN_001 updated with password")

# Create another officer for testing
db.collection("users").document("OFFICER_102").set({
    "name": "Traffic Officer Sharma",
    "role": "officer",
    "is_active": True,
    "password": "officer123"
})

print("✓ Officer OFFICER_102 created")
print("\n=== Login Credentials ===")
print("Officer 1: OFFICER_101 / password123")
print("Officer 2: OFFICER_102 / officer123")
print("Admin: ADMIN_001 / admin123")