# enforcement/fine_history.py

import os
import re
from datetime import datetime

REPORT_DIR = "reports/enforcement_reports"


# --------------------------------------------------
# SAFE FILE NAME CLEANER
# --------------------------------------------------
def _sanitize_filename(name: str):
    # Remove invalid filename characters
    return re.sub(r'[\\/*?:"<>|]', "_", str(name))


# --------------------------------------------------
# SAVE FINE REPORT
# --------------------------------------------------
def save_fine_report(driver, vehicle, offence):

    # --------------------------------------------------
    # Ensure report directory exists
    # --------------------------------------------------
    os.makedirs(REPORT_DIR, exist_ok=True)

    # --------------------------------------------------
    # SAFE DATA EXTRACTION
    # --------------------------------------------------
    licence_no = driver.get("licence_no", "N/A")
    driver_name = driver.get("name", "UNKNOWN")
    vehicle_no = vehicle.get("number", "N/A")

    challan_no = offence.get("challan_no", "N/A")

    main_offence = offence.get("main_offence", "N/A")
    sub_offence = offence.get("sub_offence", "N/A")
    fine_amount = offence.get("fine", 0)
    legal_section = offence.get("section", "N/A")
    severity = offence.get("severity", "N/A")
    payment_mode = offence.get("payment_mode", "N/A")
    payment_status = offence.get("payment_status", "N/A")

    # --------------------------------------------------
    # SMART FILE NAMING
    # --------------------------------------------------
    if licence_no != "N/A":
        base_name = licence_no
    elif vehicle_no != "N/A":
        base_name = vehicle_no
    else:
        base_name = challan_no

    base_name = _sanitize_filename(base_name)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.txt"
    filepath = os.path.join(REPORT_DIR, filename)

    # --------------------------------------------------
    # WRITE REPORT
    # --------------------------------------------------
    with open(filepath, "w", encoding="utf-8") as file:

        file.write("RTO ENFORCEMENT REPORT\n")
        file.write("=" * 50 + "\n")

        file.write(f"Date & Time      : {datetime.now()}\n")
        file.write(f"Challan Number   : {challan_no}\n")
        file.write(f"Driver Name      : {driver_name}\n")
        file.write(f"Licence Number   : {licence_no}\n")
        file.write(f"Vehicle Number   : {vehicle_no}\n\n")

        file.write("OFFENCE DETAILS\n")
        file.write("-" * 50 + "\n")
        file.write(f"Main Offence     : {main_offence}\n")
        file.write(f"Sub Offence      : {sub_offence}\n")
        file.write(f"Total Fine       : ₹{fine_amount}\n")
        file.write(f"Legal Section    : {legal_section}\n")
        file.write(f"Severity         : {severity}\n\n")

        file.write("PAYMENT DETAILS\n")
        file.write("-" * 50 + "\n")
        file.write(f"Payment Mode     : {payment_mode}\n")
        file.write(f"Payment Status   : {payment_status}\n")

        file.write("=" * 50 + "\n")

    print(f"\n✔ Fine report saved successfully: {filepath}")

    return filepath