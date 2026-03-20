import cv2
from utils.face_utils import generate_face_encoding, match_face

# -----------------------------
# FACE RE-CONFIRMATION (MANUAL)
# -----------------------------
def face_reconfirm(stored_encoding):
    success = 0
    attempts = 3

    cap = cv2.VideoCapture(0)
    print("🔁 FACE RE-CONFIRMATION MODE")
    print("Press 'S' to capture each face sample")

    captured = 0

    while captured < attempts:
        ret, frame = cap.read()
        cv2.imshow("Re-Confirm Face", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            img_name = f"re_face_{captured+1}.jpg"
            cv2.imwrite(img_name, frame)
            print(f"[SYSTEM] Captured face sample {captured+1}/3")

            current_encoding = generate_face_encoding(img_name)

            if current_encoding is not None:
                if match_face(stored_encoding, current_encoding):
                    success += 1

            captured += 1

            if success >= 2:
                cap.release()
                cv2.destroyAllWindows()
                return True

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False


# -----------------------------
# FINGERPRINT RE-CONFIRMATION
# -----------------------------
def fingerprint_reconfirm(expected_fp):
    success = 0
    attempts = 3

    print("🔁 FINGERPRINT RE-CONFIRMATION MODE")

    for i in range(attempts):
        fp = int(input(f"[SYSTEM] Fingerprint re-scan {i+1}/3: "))
        if fp == expected_fp:
            success += 1

        if success >= 2:
            return True

    return False
