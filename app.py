import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask, render_template, request, redirect, session, url_for
import os
import threading
import webbrowser
from datetime import datetime
import qrcode
import base64

from firebase.firebase_init import db

#  Licence Verify
from verify.web_verify import (
    licence_verify_step1,
    licence_verify_reconfirm,
    get_doc_by_licence
)

#  HSRP Verify
from verify.web_hsrp import hsrp_verify_step1

app = Flask(__name__)
app.secret_key = "mega_project_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

QR_FOLDER = os.path.join("static", "qr_codes")
os.makedirs(QR_FOLDER, exist_ok=True)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/login")


def safe_str(value):
    try:
        if value is None:
            return "N/A"
        if hasattr(value, "to_datetime"):
            dt = value.to_datetime()
            return dt.strftime("%Y-%m-%d")
        return str(value).split(" ")[0]
    except:
        return "N/A"


def safe_get(data, *keys, default="N/A"):
    try:
        cur = data
        for k in keys:
            if cur is None:
                return default
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return default
        return cur if cur is not None else default
    except:
        return default


#  OFFENCES LIST
OFFENCES = {
    "1": {
        "name": "Driving without Valid Driving Licence",
        "sub": {
            "1": {"title": "Driving without Driving Licence", "fine": 5000, "section": "MV Act 2019 - Section 3",
                  "severity": "High"},
            "2": {"title": "Driving with an expired licence", "fine": 5000, "section": "MV Act 2019 - Section 3",
                  "severity": "High"},
            "3": {"title": "Driving without Registration Certificate (RC)", "fine": 5000,
                  "section": "MV Act 2019 - Section 3", "severity": "High"},
            "4": {"title": "Driving an unregistered vehicle", "fine": 5000, "section": "MV Act 2019 - Section 3",
                  "severity": "High"},
            "5": {"title": "Using fake licence / fake RC", "fine": 10000, "section": "MV Act 2019 - Section 192",
                  "severity": "Critical"},
            "6": {"title": "Allowing unauthorized person to drive", "fine": 5000, "section": "MV Act 2019 - Section 3",
                  "severity": "High"},
        }
    },

    "2": {
        "name": "No High Security Registration Plate (HSRP)",
        "sub": {
            "1": {"title": "HSRP not installed", "fine": 5000, "section": "MV Act 2019 - Section 39",
                  "severity": "Medium"},
            "2": {"title": "Damaged or tampered HSRP", "fine": 5000, "section": "MV Act 2019 - Section 39",
                  "severity": "Medium"},
            "3": {"title": "HSRP number mismatch", "fine": 5000, "section": "MV Act 2019 - Section 39",
                  "severity": "High"},
        }
    },

    "3": {
        "name": "Driving without Valid Insurance",
        "sub": {
            "1": {"title": "Insurance expired", "fine": 2000, "section": "MV Act 2019 - Section 146",
                  "severity": "Medium"},
            "2": {"title": "No insurance found", "fine": 2000, "section": "MV Act 2019 - Section 146",
                  "severity": "High"},
        }
    },

    "4": {
        "name": "Suspected Drunk Driving",
        "sub": {
            "1": {"title": "Alcohol detected above permissible limit", "fine": 10000,
                  "section": "MV Act 2019 - Section 185", "severity": "Critical"},
            "2": {"title": "Refusal to undergo breath analyzer test", "fine": 10000,
                  "section": "MV Act 2019 - Section 185", "severity": "Critical"},
            "3": {"title": "Repeat offence drunk driving", "fine": 15000, "section": "MV Act 2019 - Section 185",
                  "severity": "Critical"},
        }
    },

    "5": {"name": "No Violation", "sub": {}}
}


def generate_challan_no():
    return "CH-" + datetime.now().strftime("%Y%m%d-%H%M%S")


def generate_qr(upi_link, challan_no):
    qr_img = qrcode.make(upi_link)
    filename = f"{challan_no}.png"
    save_path = os.path.join(QR_FOLDER, filename)
    qr_img.save(save_path)
    return f"qr_codes/{filename}"


#  ROOT
@app.route("/")
def root():
    return redirect(url_for("login"))


#  LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        try:
            doc = db.collection("users").document(username).get()
        except Exception as e:
            return f"<h2>Firebase Error</h2><pre>{e}</pre>"

        if not doc.exists:
            error = "Invalid Officer ID or Password"
        else:
            user = doc.to_dict() or {}
            stored_password = (user.get("password") or user.get("password ") or "").strip()

            if stored_password != password:
                error = "Invalid Officer ID or Password"
            else:
                session.clear()
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("mode_select"))

    return render_template("login.html", error=error)


#  MODE SELECT
@app.route("/mode-select")
def mode_select():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("mode_select.html")


#  LICENCE MODE PAGE
@app.route("/licence_mode")
def licence_mode():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("licence_mode.html")


#  HSRP MODE PAGE
@app.route("/hsrp_mode")
def hsrp_mode():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("hsrp_mode.html")


# ==========================================================
#  COMBINED MODE (ONLY THIS PART UPDATED)
# ==========================================================
@app.route("/combined_mode")
def combined_mode():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("combined_mode.html")


@app.route("/combined_verify", methods=["POST"])
def combined_verify():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    fingerprint_id = request.form.get("fingerprint_id", "").strip()
    hsrp_no = request.form.get("hsrp_number", "").strip()
    face_b64 = request.form.get("face_sample", "").strip()

    #  validation
    if not fingerprint_id.isdigit():
        return render_template("combined_mode.html", error="Invalid Fingerprint ID (only numbers allowed)")

    if not hsrp_no:
        return render_template("combined_mode.html", error="Please enter HSRP Number Plate")

    if not face_b64:
        return render_template("combined_mode.html", error="Please capture face image")

    fingerprint_id = int(fingerprint_id)
    hsrp_clean = hsrp_no.upper().replace(" ", "").replace("-", "")

    #  save captured face into uploads/
    try:
        if "," in face_b64:
            face_b64 = face_b64.split(",")[1]

        img_bytes = base64.b64decode(face_b64)
        face_path = os.path.join(UPLOAD_FOLDER, "combined_face.jpg")

        with open(face_path, "wb") as f:
            f.write(img_bytes)
    except:
        return render_template("combined_mode.html", error="Face capture failed. Please try again")

    #  licence verify using same logic
    decision, matched_doc, fp_ok, face_ok = licence_verify_step1(fingerprint_id, face_path)

    licence_valid = (decision == "VALID" and matched_doc)
    licence_invalid = not licence_valid

    #  if reconfirm needed -> go reconfirm page
    if decision == "RECONFIRM" and matched_doc:
        licence_number = safe_get(matched_doc, "licence_info", "licence_number", default="")
        if licence_number and licence_number != "N/A":
            session["reconfirm_licence_no"] = licence_number
            session["need_fp"] = (not fp_ok)
            session["need_face"] = (not face_ok)

            #  store HSRP temporarily in session for later enforcement
            session["combined_hsrp_temp"] = hsrp_clean
            session["combined_mode_active"] = True

            return redirect(url_for("reconfirm_page"))

    #  HSRP verify
    hsrp_status, vehicle_data = hsrp_verify_step1(hsrp_clean)
    hsrp_valid = (hsrp_status == "VALID" and vehicle_data)

    #  Save combined result in session
    #  Status text like console output
    if licence_valid and hsrp_valid:
        final_status = "LICENCE + HSRP VALID"
    elif licence_invalid and hsrp_valid:
        final_status = "LICENCE INVALID"
    elif licence_valid and not hsrp_valid:
        final_status = "HSRP INVALID"
    else:
        final_status = "LICENCE + HSRP INVALID"

    session["last_result"] = {
        "mode": "COMBINED",
        "status": final_status,

        # licence data
        "name": safe_get(matched_doc, "licence_info", "full_name", default="UNKNOWN") if matched_doc else "UNKNOWN",
        "licence": safe_get(matched_doc, "licence_info", "licence_number", default="N/A") if matched_doc else "N/A",
        "expiry": safe_str(safe_get(matched_doc, "licence_info", "expiry_date", default="N/A")) if matched_doc else "N/A",
        "fp_ok": bool(fp_ok),
        "face_ok": bool(face_ok),

        # hsrp data
        "hsrp_no": hsrp_clean,
        "owner": vehicle_data.get("owner_name", "UNKNOWN") if vehicle_data else "UNKNOWN",
        "vehicle_type": vehicle_data.get("vehicle_type", "N/A") if vehicle_data else "N/A",
        "rto": vehicle_data.get("registration_rto", "N/A") if vehicle_data else "N/A",
        "plate_status": vehicle_data.get("plate_status", "INVALID") if vehicle_data else "INVALID",
    }

    #  offence suggestion
    if not licence_valid:
        session["suggest_offence"] = "1"
    elif not hsrp_valid:
        session["suggest_offence"] = "2"
    else:
        session.pop("suggest_offence", None)

    return redirect(url_for("enforcement_page"))


    #  FINAL STATUS TEXT
    licence_ok = (licence_status == "VALID")
    hsrp_ok = (hsrp_status == "VALID")

    if licence_ok and hsrp_ok:
        final_status_text = "LICENCE + HSRP VALID"
        session.pop("suggest_offence", None)
    elif (not licence_ok) and hsrp_ok:
        final_status_text = "LICENCE INVALID"
        session["suggest_offence"] = "1"
    elif licence_ok and (not hsrp_ok):
        final_status_text = "HSRP INVALID"
        session["suggest_offence"] = "2"
    else:
        final_status_text = "LICENCE + HSRP INVALID"
        session["suggest_offence"] = "1"

    #  STORE RESULT FOR ENFORCEMENT PAGE
    session["last_result"] = {
        "mode": "COMBINED",
        "status": final_status_text,

        # Licence info
        "name": licence_name,
        "licence": licence_no,
        "expiry": licence_expiry,

        # HSRP info
        "hsrp_no": hsrp_no_clean,
        "owner": (vehicle_data or {}).get("owner_name", "UNKNOWN"),
        "vehicle_type": (vehicle_data or {}).get("vehicle_type", "N/A"),
        "rto": (vehicle_data or {}).get("registration_rto", "N/A"),
        "plate_status": (vehicle_data or {}).get("plate_status", "INVALID")
    }

    #  clear combined flags if any
    session.pop("combined_active", None)
    session.pop("combined_hsrp_cache", None)

    return redirect(url_for("enforcement_page"))


#  LICENCE VERIFY (UNCHANGED)
@app.route("/licence_verify", methods=["POST"])
def licence_verify():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    fingerprint_id = request.form.get("fingerprint_id", "").strip()
    face_image = request.files.get("face_image")

    if not fingerprint_id.isdigit():
        return render_template("licence_mode.html", error="Invalid Fingerprint ID (only numbers allowed)")

    if face_image is None:
        return render_template("licence_mode.html", error="Please capture face image")

    fingerprint_id = int(fingerprint_id)

    image_path = os.path.join(UPLOAD_FOLDER, "scan.jpg")
    face_image.save(image_path)

    decision, matched_doc, fp_ok, face_ok = licence_verify_step1(fingerprint_id, image_path)

    if decision == "VALID" and matched_doc:
        expiry_date = safe_str(safe_get(matched_doc, "licence_info", "expiry_date", default="N/A"))
        session["last_result"] = {
            "mode": "LICENCE",
            "status": "LICENCE VALID",
            "name": safe_get(matched_doc, "licence_info", "full_name", default="UNKNOWN"),
            "licence": safe_get(matched_doc, "licence_info", "licence_number", default="N/A"),
            "expiry": expiry_date,
            "fp_ok": bool(fp_ok),
            "face_ok": bool(face_ok)
        }
        return redirect(url_for("enforcement_page"))

    if decision == "RECONFIRM" and matched_doc:
        licence_number = safe_get(matched_doc, "licence_info", "licence_number", default="")

        if not licence_number or licence_number == "N/A":
            session["last_result"] = {
                "mode": "LICENCE",
                "status": "LICENCE INVALID",
                "name": "UNKNOWN",
                "licence": "N/A",
                "expiry": "N/A",
                "fp_ok": bool(fp_ok),
                "face_ok": bool(face_ok)
            }
            return redirect(url_for("enforcement_page"))

        session["reconfirm_licence_no"] = licence_number
        session["need_fp"] = (not fp_ok)
        session["need_face"] = (not face_ok)
        return redirect(url_for("reconfirm_page"))

    session["last_result"] = {
        "mode": "LICENCE",
        "status": "LICENCE INVALID",
        "name": "UNKNOWN",
        "licence": "N/A",
        "expiry": "N/A",
        "fp_ok": bool(fp_ok),
        "face_ok": bool(face_ok)
    }
    return redirect(url_for("enforcement_page"))


#  RECONFIRM PAGE (UNCHANGED)
@app.route("/reconfirm")
def reconfirm_page():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    licence_no = session.get("reconfirm_licence_no")
    if not licence_no:
        return redirect(url_for("licence_mode"))

    return render_template(
        "reconfirm.html",
        need_fp=session.get("need_fp", False),
        need_face=session.get("need_face", False),
        error=None
    )


#  RECONFIRM SUBMIT (UNCHANGED LOGIC + ONLY ADD SMALL COMBINED SUPPORT)
@app.route("/reconfirm_submit", methods=["POST"])
def reconfirm_submit():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    licence_no = session.get("reconfirm_licence_no")
    if not licence_no:
        return redirect(url_for("licence_mode"))

    matched_doc = get_doc_by_licence(licence_no)

    if not matched_doc:
        session["last_result"] = {
            "mode": "LICENCE",
            "status": "LICENCE INVALID",
            "name": "UNKNOWN",
            "licence": "N/A",
            "expiry": "N/A",
            "fp_ok": False,
            "face_ok": False
        }
        return redirect(url_for("enforcement_page"))

    need_fp = session.get("need_fp", False)
    need_face = session.get("need_face", False)

    fp_list = []
    if need_fp:
        fp1 = request.form.get("fp_sample_1", "").strip()
        fp2 = request.form.get("fp_sample_2", "").strip()
        fp3 = request.form.get("fp_sample_3", "").strip()

        if not (fp1.isdigit() and fp2.isdigit() and fp3.isdigit()):
            return render_template("reconfirm.html", need_fp=need_fp, need_face=need_face,
                                   error="Please enter 3 fingerprint samples")

        fp_list = [int(fp1), int(fp2), int(fp3)]

    face_sample_paths = []
    if need_face:
        b1 = request.form.get("face_sample_1", "").strip()
        b2 = request.form.get("face_sample_2", "").strip()
        b3 = request.form.get("face_sample_3", "").strip()

        if not (b1 and b2 and b3):
            return render_template("reconfirm.html", need_fp=need_fp, need_face=need_face,
                                   error="Please capture 3 face samples")

        base64_list = [b1, b2, b3]

        for i, b64img in enumerate(base64_list, start=1):
            try:
                if "," in b64img:
                    b64img = b64img.split(",")[1]

                img_bytes = base64.b64decode(b64img)

                img_path = os.path.join(UPLOAD_FOLDER, f"reconfirm_face_{i}.jpg")
                with open(img_path, "wb") as f:
                    f.write(img_bytes)

                face_sample_paths.append(img_path)

            except Exception as e:
                print("[ERROR] Face decode:", e)
                return render_template("reconfirm.html", need_fp=need_fp, need_face=need_face,
                                       error="Face capture failed. Please try again")

    final_status, fp_ok_final, face_ok_final = licence_verify_reconfirm(
        matched_doc,
        fp_list,
        face_sample_paths,
        need_fp,
        need_face
    )

    #  RESULT AFTER RECONFIRM
    expiry_date = safe_str(safe_get(matched_doc, "licence_info", "expiry_date", default="N/A"))

    licence_result = {
        "licence_status": "VALID" if final_status == "VALID" else "INVALID",
        "name": safe_get(matched_doc, "licence_info", "full_name", default="UNKNOWN"),
        "licence": safe_get(matched_doc, "licence_info", "licence_number", default="N/A"),
        "expiry": expiry_date,
        "fp_ok": bool(fp_ok_final),
        "face_ok": bool(face_ok_final),
    }

    #  IF THIS RECONFIRM CAME FROM COMBINED MODE
    if session.get("combined_active") is True:
        hsrp_cache = session.get("combined_hsrp_cache", {})
        hsrp_status = hsrp_cache.get("hsrp_status", "INVALID")
        hsrp_no = hsrp_cache.get("hsrp_no", "N/A")
        vehicle_data = hsrp_cache.get("vehicle_data", {})

        licence_ok = (licence_result["licence_status"] == "VALID")
        hsrp_ok = (hsrp_status == "VALID")

        if licence_ok and hsrp_ok:
            final_text = "LICENCE + HSRP VALID"
            session.pop("suggest_offence", None)
        elif (not licence_ok) and hsrp_ok:
            final_text = "LICENCE INVALID"
            session["suggest_offence"] = "1"
        elif licence_ok and (not hsrp_ok):
            final_text = "HSRP INVALID"
            session["suggest_offence"] = "2"
        else:
            final_text = "LICENCE + HSRP INVALID"
            session["suggest_offence"] = "1"

        session["last_result"] = {
            "mode": "COMBINED",
            "status": final_text,
            "name": licence_result["name"],
            "licence": licence_result["licence"],
            "expiry": licence_result["expiry"],

            "hsrp_no": hsrp_no,
            "owner": vehicle_data.get("owner_name", "UNKNOWN"),
            "vehicle_type": vehicle_data.get("vehicle_type", "N/A"),
            "rto": vehicle_data.get("registration_rto", "N/A"),
            "plate_status": vehicle_data.get("plate_status", "INVALID"),
        }

        #  clear combined cache
        session.pop("combined_active", None)
        session.pop("combined_hsrp_cache", None)

    else:
        #  NORMAL LICENCE MODE RECONFIRM RESULT
        if final_status == "VALID":
            session["last_result"] = {
                "mode": "LICENCE",
                "status": "LICENCE VALID",
                "name": licence_result["name"],
                "licence": licence_result["licence"],
                "expiry": licence_result["expiry"],
                "fp_ok": bool(fp_ok_final),
                "face_ok": bool(face_ok_final)
            }
        else:
            session["last_result"] = {
                "mode": "LICENCE",
                "status": "LICENCE INVALID",
                "name": "UNKNOWN",
                "licence": "N/A",
                "expiry": "N/A",
                "fp_ok": bool(fp_ok_final),
                "face_ok": bool(face_ok_final)
            }

    #  Clear reconfirm session
    session.pop("reconfirm_licence_no", None)
    session.pop("need_fp", None)
    session.pop("need_face", None)

    return redirect(url_for("enforcement_page"))


#  HSRP VERIFY (UNCHANGED)
@app.route("/hsrp_verify", methods=["POST"])
def hsrp_verify():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    hsrp_no = request.form.get("hsrp_number", "").strip()
    hsrp_no_clean = hsrp_no.upper().replace(" ", "").replace("-", "")

    if len(hsrp_no_clean) < 6:
        return render_template("hsrp_mode.html", error="Invalid HSRP Number Plate")

    status, vehicle_data = hsrp_verify_step1(hsrp_no_clean)

    if status == "VALID" and vehicle_data:
        session["last_result"] = {
            "mode": "HSRP",
            "status": "HSRP VALID",
            "hsrp_no": hsrp_no_clean,
            "owner": vehicle_data.get("owner_name", "UNKNOWN"),
            "vehicle_type": vehicle_data.get("vehicle_type", "N/A"),
            "rto": vehicle_data.get("registration_rto", "N/A"),
            "plate_status": vehicle_data.get("plate_status", "N/A"),
        }
        return redirect(url_for("enforcement_page"))

    session["last_result"] = {
        "mode": "HSRP",
        "status": "HSRP INVALID",
        "hsrp_no": hsrp_no_clean,
        "owner": "UNKNOWN",
        "vehicle_type": "N/A",
        "rto": "N/A",
        "plate_status": "INVALID"
    }

    session["suggest_offence"] = "2"
    return redirect(url_for("enforcement_page"))


#  ENFORCEMENT PAGE (UNCHANGED)
@app.route("/enforcement")
def enforcement_page():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    result = session.get("last_result")
    if not result:
        return redirect(url_for("mode_select"))

    suggestion = session.get("suggest_offence", None)
    return render_template("enforcement.html", result=result, offences=OFFENCES, suggestion=suggestion)


#  SUBMIT ENFORCEMENT (UNCHANGED)
@app.route("/submit_enforcement", methods=["POST"])
def submit_enforcement():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    officer_id = session.get("username", "OFFICER_101")
    result = session.get("last_result", {})

    offence_id = request.form.get("offence_id", "").strip()
    sub_id = request.form.get("sub_id", "").strip()
    payment_mode = request.form.get("payment_mode", "").strip()

    challan_no = generate_challan_no()

    if not offence_id:
        return "<h2>Error: Offence not selected</h2>"

    if offence_id == "5":

        status = result.get("status", "")

        base_invalid_fine = 0
        sub_offence_text = ""

        #  Combined Invalid
        if "LICENCE + HSRP INVALID" in status:
            base_invalid_fine = 10000
            sub_offence_text = "Licence + HSRP Verification Failed"

        #  Licence Invalid
        elif "LICENCE INVALID" in status:
            base_invalid_fine = 5000
            sub_offence_text = "Licence Verification Failed"

        #  HSRP Invalid
        elif "HSRP INVALID" in status:
            base_invalid_fine = 5000
            sub_offence_text = "HSRP Verification Failed"

        #  Fully verified
        else:
            base_invalid_fine = 0
            sub_offence_text = "No Violation"

        payment_mode = request.form.get("payment_mode", "").strip()

        qr_url = None
        upi_link = None

        if payment_mode == "ONLINE" and base_invalid_fine > 0:
            upi_link = f"upi://pay?pa=rto@upi&pn=RTO Department&am={base_invalid_fine}&cu=INR&tn=Challan {challan_no}"
            qr_url = generate_qr(upi_link, challan_no)

        session.pop("suggest_offence", None)

        return render_template(
            "challan_result.html",
            challan_no=challan_no,
            officer_id=officer_id,
            main_offence="Invalid Document",
            sub_offence=sub_offence_text,
            fine_amount=base_invalid_fine,
            section="MV Act 2019 - Section 3",
            severity="High",
            payment_mode=payment_mode,
            upi_link=upi_link,
            qr_url=qr_url,
            result=result
        )

    if not sub_id:
        return "<h2>Error: Sub-Offence not selected</h2>"

    if not payment_mode:
        return "<h2>Error: Payment mode not selected</h2>"

    if offence_id not in OFFENCES:
        return "<h2>Error: Invalid offence ID</h2>"
    if sub_id not in OFFENCES[offence_id]["sub"]:
        return "<h2>Error: Invalid sub offence ID</h2>"

    main_offence = OFFENCES[offence_id]["name"]
    sub_data = OFFENCES[offence_id]["sub"][sub_id]

    sub_offence = sub_data["title"]
    section = sub_data["section"]
    severity = sub_data["severity"]

    sub_fine = sub_data["fine"]

    # Detect base invalid fine
    status = result.get("status", "")
    base_invalid_fine = 0

    if "LICENCE INVALID" in status:
        base_invalid_fine += 5000

    if "HSRP INVALID" in status:
        base_invalid_fine += 5000

    # Total fine
    fine_amount = base_invalid_fine + sub_fine

    qr_url = None
    upi_link = None

    if payment_mode == "ONLINE":
        upi_link = f"upi://pay?pa=rto@upi&pn=RTO Department&am={fine_amount}&cu=INR&tn=Challan {challan_no}"
        qr_url = generate_qr(upi_link, challan_no)

    session.pop("suggest_offence", None)

    return render_template(
        "challan_result.html",
        challan_no=challan_no,
        officer_id=officer_id,
        main_offence=main_offence,
        sub_offence=sub_offence,
        fine_amount=fine_amount,
        base_fine=base_invalid_fine,
        sub_fine=sub_fine,
        section=section,
        severity=severity,
        payment_mode=payment_mode,
        upi_link=upi_link,
        qr_url=qr_url,
        result=result
    )


#  LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()

    app.run(debug=True)
