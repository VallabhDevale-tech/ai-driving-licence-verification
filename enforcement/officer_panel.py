from datetime import datetime

from enforcement.rto_fines import RTO_FINES
from enforcement.firebase_logger import log_enforcement
from enforcement.fine_history import save_fine_report
from payments.upi_qr import generate_upi_qr

# 🔐 RBAC
from utils.access_control import require_role

# --------------------------------------------------
# FIXED INVALID DOCUMENT FINES
# --------------------------------------------------
FIXED_INVALID_LICENCE_FINE = 5000
FIXED_INVALID_HSRP_FINE = 5000


# --------------------------------------------------
# INTERNAL HELPERS
# --------------------------------------------------
def _detect_context(status: str):
    if "LICENCE + HSRP" in status:
        return "COMBINED"
    if "LICENCE" in status:
        return "LICENCE"
    if "HSRP" in status:
        return "HSRP"
    return "UNKNOWN"


def _suggest_offence(status: str):
    if "LICENCE INVALID" in status:
        return 1
    if "HSRP INVALID" in status:
        return 2
    return 5


# --------------------------------------------------
# CHALLAN NUMBER GENERATOR
# --------------------------------------------------
def generate_challan_number():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"CH-{timestamp}"


# --------------------------------------------------
# PAYMENT SELECTION
# --------------------------------------------------
def select_payment_mode():
    print("\nSelect Payment Mode:")
    print("1. Online Payment")
    print("2. Cash Payment")

    while True:
        choice = input("Enter choice: ")
        if choice == "1":
            return "ONLINE", "PENDING"
        elif choice == "2":
            return "CASH", "PAID"
        else:
            print("❌ Invalid choice. Try again.")


# --------------------------------------------------
# OFFICER ENFORCEMENT PANEL
# --------------------------------------------------
def officer_enforcement(user_id, driver, vehicle):

    require_role(user_id, ["officer"])

    print("\n--------------------------------------")
    print("RTO OFFICER ENFORCEMENT MODE")
    print("--------------------------------------")
    print("Officer ID          :", user_id)
    print("Verification Status :", driver.get("status"))

    status = driver.get("status", "")
    context = _detect_context(status)
    suggestion = _suggest_offence(status)

    # --------------------------------------------------
    # BASE INVALID FINE CALCULATION
    # --------------------------------------------------
    base_invalid_fine = 0

    if "LICENCE INVALID" in status:
        base_invalid_fine += FIXED_INVALID_LICENCE_FINE

    if "HSRP INVALID" in status:
        base_invalid_fine += FIXED_INVALID_HSRP_FINE

    if base_invalid_fine > 0:
        print("\n⚠ AUTOMATIC INVALID DOCUMENT FINE APPLIED")
        print("Base Invalid Fine : ₹", base_invalid_fine)

    if suggestion != 5:
        print("\n🔍 SYSTEM SUGGESTION:")
        print("Suggested Offence :", RTO_FINES[suggestion]["offence"])

    # --------------------------------------------------
    # SMART OFFENCE FILTERING
    # --------------------------------------------------
    lic_invalid = "LICENCE INVALID" in status
    hsrp_invalid = "HSRP INVALID" in status

    filtered = {}

    for k, v in RTO_FINES.items():

        if k == 5:  # No Violation
            filtered[k] = v
            continue

        if k == 4:  # Drunk driving
            filtered[k] = v
            continue

        if k == 3:  # Insurance (vehicle required)
            if context in ["HSRP", "COMBINED"]:
                filtered[k] = v
            continue

        if k == 1 and lic_invalid:
            filtered[k] = v
            continue

        if k == 2 and hsrp_invalid:
            filtered[k] = v
            continue

    # --------------------------------------------------
    # SERIAL DISPLAY
    # --------------------------------------------------
    print("\nSelect Offence (If Any):")

    serial_map = {}
    serial = 1

    for real_key, offence in filtered.items():
        serial_map[serial] = real_key
        print(f"{serial}. {offence['offence']}")
        serial += 1

    try:
        choice_serial = int(input("Enter choice: "))
    except ValueError:
        print("❌ Invalid input")
        return

    if choice_serial not in serial_map:
        print("❌ Invalid selection")
        return

    choice = serial_map[choice_serial]
    offence = RTO_FINES[choice]

    # --------------------------------------------------
    # NO VIOLATION
    # --------------------------------------------------
    if choice == 5:

        # If base invalid fine exists → still generate challan
        if base_invalid_fine > 0:

            challan_no = generate_challan_number()

            offence_payload = {
                "challan_no": challan_no,
                "main_offence": "Invalid Document",
                "sub_offence": "Licence Verification Failed",
                "fine": base_invalid_fine,
                "base_invalid_fine": base_invalid_fine,
                "offence_fine": 0,
                "section": "MV Act 2019 - Section 3",
                "severity": "High",
                "issued_by": user_id,
                "issued_at": datetime.utcnow()
            }

            print("\n⚠ DOCUMENT INVALID FINE APPLIED")
            print("--------------------------------------")
            print("Invalid Fine : ₹", base_invalid_fine)
            print("Total Fine   : ₹", base_invalid_fine)
            print("Challan No   :", challan_no)
            print("--------------------------------------")

            payment_mode, payment_status = select_payment_mode()

            offence_payload["payment_mode"] = payment_mode
            offence_payload["payment_status"] = payment_status

            print("\n💳 PAYMENT DETAILS")
            print("--------------------------------------")
            print("Payment Mode   :", payment_mode)
            print("--------------------------------------")

            if payment_mode == "ONLINE":
                upi_link, qr_path = generate_upi_qr(
                    challan_no,
                    base_invalid_fine
                )

                offence_payload["upi_link"] = upi_link
                offence_payload["qr_code_path"] = qr_path

                print("\n📲 ONLINE PAYMENT INITIATED")
                print("--------------------------------------")
                print("UPI Link :", upi_link)
                print("QR Code  :", qr_path)
                print("--------------------------------------")

            log_enforcement(
                driver=driver,
                vehicle=vehicle,
                payload=offence_payload,
                user_id=user_id
            )

            save_fine_report(driver, vehicle, offence_payload)

            print("✔ Enforcement logged & report generated successfully")
            return

        # If no base fine → normal verification
        print("✔ No offence recorded")

        log_enforcement(
            driver=driver,
            vehicle=vehicle,
            payload={},
            user_id=user_id,
            record_type="VERIFICATION"
        )

        print("✔ Verification stored in enforcement logs (No Fine)")
        return

    # --------------------------------------------------
    # SUB-OFFENCE SELECTION
    # --------------------------------------------------
    print("\nSelect Specific Violation:")
    subs = offence["sub_offences"]

    sub_serial_map = {}
    sub_serial = 1

    for real_sub_key, sub_data in subs.items():
        sub_serial_map[sub_serial] = real_sub_key
        print(f"{sub_serial}. {sub_data['title']} | ₹{sub_data['fine']}")
        sub_serial += 1

    try:
        sub_choice_serial = int(input("Enter sub-offence choice: "))
    except ValueError:
        print("❌ Invalid input")
        return

    if sub_choice_serial not in sub_serial_map:
        print("❌ Invalid sub-offence selected")
        return

    selected = subs[sub_serial_map[sub_choice_serial]]

    # --------------------------------------------------
    # TOTAL FINE CALCULATION
    # --------------------------------------------------
    offence_fine = selected["fine"]
    total_fine = base_invalid_fine + offence_fine

    challan_no = generate_challan_number()

    offence_payload = {
        "challan_no": challan_no,
        "main_offence": offence["offence"],
        "sub_offence": selected["title"],
        "fine": total_fine,
        "base_invalid_fine": base_invalid_fine,
        "offence_fine": offence_fine,
        "section": selected["section"],
        "severity": selected["severity"],
        "issued_by": user_id,
        "issued_at": datetime.utcnow()
    }

    print("\n⚠ OFFENCE CONFIRMED")
    print("--------------------------------------")
    print("Main Offence :", offence_payload["main_offence"])
    print("Sub Offence  :", offence_payload["sub_offence"])
    print("Invalid Fine : ₹", base_invalid_fine)
    print("Offence Fine : ₹", offence_fine)
    print("Total Fine   : ₹", total_fine)
    print("Legal Sec.   :", offence_payload["section"])
    print("Severity     :", offence_payload["severity"])
    print("Challan No   :", challan_no)
    print("--------------------------------------")

    # --------------------------------------------------
    # PAYMENT
    # --------------------------------------------------
    payment_mode, payment_status = select_payment_mode()

    offence_payload["payment_mode"] = payment_mode
    offence_payload["payment_status"] = payment_status

    print("\n💳 PAYMENT DETAILS")
    print("--------------------------------------")
    print("Payment Mode   :", payment_mode)
    print("--------------------------------------")

    if payment_mode == "ONLINE":
        upi_link, qr_path = generate_upi_qr(
            challan_no,
            total_fine
        )

        offence_payload["upi_link"] = upi_link
        offence_payload["qr_code_path"] = qr_path

        print("\n📲 ONLINE PAYMENT INITIATED")
        print("--------------------------------------")
        print("UPI Link :", upi_link)
        print("QR Code  :", qr_path)
        print("--------------------------------------")

    # --------------------------------------------------
    # LOGGING
    # --------------------------------------------------
    log_enforcement(
        driver=driver,
        vehicle=vehicle,
        payload=offence_payload,
        user_id=user_id
    )

    save_fine_report(driver, vehicle, offence_payload)

    print("✔ Enforcement logged & report generated successfully")