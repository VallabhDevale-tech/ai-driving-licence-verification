let stream = null;
let faceCaptured = false;

window.onload = function() {
    const startBtn = document.getElementById("startCamBtn");
    const captureBtn = document.getElementById("captureBtn");
    const verifyBtn = document.getElementById("verifyBtn");

    const fpInput = document.getElementById("fingerprint_id");
    const hsrpInput = document.getElementById("hsrp_number");

    if (startBtn) startBtn.addEventListener("click", startCamera);
    if (captureBtn) captureBtn.addEventListener("click", captureFace);

    if (fpInput) fpInput.addEventListener("input", checkReady);
    if (hsrpInput) hsrpInput.addEventListener("input", checkReady);

    checkReady();
};

async function startCamera() {
    const video = document.getElementById("video");
    const captureBtn = document.getElementById("captureBtn");

    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;

        captureBtn.disabled = false;
    } catch (err) {
        alert("⚠ Camera access denied or not available!");
        console.log(err);
    }
}

function captureFace() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");

    if (!stream || !video.srcObject) {
        alert("⚠ Please start camera first!");
        return;
    }

    canvas.width = video.videoWidth || 320;
    canvas.height = video.videoHeight || 240;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imgData = canvas.toDataURL("image/jpeg");

    // ✅ Save base64 in hidden input
    document.getElementById("face_sample").value = imgData;

    // ✅ Show preview
    const preview = document.getElementById("facePreview");
    preview.innerHTML = "";
    const img = document.createElement("img");
    img.src = imgData;
    preview.appendChild(img);

    // ✅ Update counter
    document.getElementById("faceCounter").innerText = "Face Captured: ✅ YES";

    faceCaptured = true;
    checkReady();
}

function checkReady() {
    const fp = document.getElementById("fingerprint_id").value.trim();
    const hsrp = document.getElementById("hsrp_number").value.trim();

    const verifyBtn = document.getElementById("verifyBtn");

    if (fp !== "" && hsrp !== "" && faceCaptured === true) {
        verifyBtn.disabled = false;
    } else {
        verifyBtn.disabled = true;
    }
}