from firebase.firebase_init import db
from datetime import datetime

# =====================================================
# HSRP VEHICLE REGISTRATION (ADD NEW VEHICLE)
# =====================================================
print("\n==============================================")
print("   HSRP VEHICLE REGISTRATION SYSTEM")
print("==============================================\n")

# -----------------------------
# INPUT VEHICLE DETAILS
# -----------------------------
hsrp_number = input("Enter HSRP Number Plate (e.g. MH12AB1234): ").upper()
owner_name = input("Enter Vehicle Owner Name: ")
linked_licence_number = input("Enter Linked Licence Number: ")
vehicle_type = input("Enter Vehicle Type (LMV / MCWG): ")
registration_rto = input("Enter Registration RTO (e.g. RTO PUNE): ")
fuel_type = input("Enter Fuel Type (PETROL / DIESEL / ELECTRIC): ")

# -----------------------------
# BASIC VALIDATION
# -----------------------------
existing_doc = db.collection("hsrp_vehicles").document(hsrp_number).get()
if existing_doc.exists:
    print("\n❌ ERROR: This HSRP number already exists.")
    exit()

# -----------------------------
# CREATE VEHICLE DOCUMENT
# -----------------------------
vehicle_data = {
    "hsrp_number": hsrp_number,
    "owner_name": owner_name,
    "linked_licence_number": linked_licence_number,
    "vehicle_type": vehicle_type,
    "registration_rto": registration_rto,
    "fuel_type": fuel_type,
    "plate_status": "GENUINE",
    "is_blacklisted": False,
    "created_at": datetime.now()
}

# -----------------------------
# SAVE TO FIRESTORE
# -----------------------------
db.collection("hsrp_vehicles").document(hsrp_number).set(vehicle_data)

print("\n✅ HSRP Vehicle Registered Successfully")
print("----------------------------------------------")
print("HSRP Number Plate :", hsrp_number)
print("Owner Name        :", owner_name)
print("Linked Licence No :", linked_licence_number)
print("Vehicle Type      :", vehicle_type)
print("Registration RTO  :", registration_rto)
print("Plate Status      : GENUINE")
print("----------------------------------------------")