import qrcode
import os

UPI_ID = "rto@upi"
PAYEE_NAME = "RTO Department"
CURRENCY = "INR"


def generate_upi_qr(challan_no, amount):
    """
    Generates a UPI QR code for given challan and amount
    """

    upi_link = (
        f"upi://pay?"
        f"pa={UPI_ID}&"
        f"pn={PAYEE_NAME}&"
        f"am={amount}&"
        f"cu={CURRENCY}&"
        f"tn=Challan {challan_no}"
    )

    os.makedirs("payments/qr_codes", exist_ok=True)

    filename = f"payments/qr_codes/{challan_no}.png"

    qr = qrcode.make(upi_link)
    qr.save(filename)

    return upi_link, filename