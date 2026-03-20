def decide(fp_ok, face_ok):
    if fp_ok and face_ok:
        return "VALID"

    if fp_ok or face_ok:
        return "RECONFIRM"

    return "INVALID"
