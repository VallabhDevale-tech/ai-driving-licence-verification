let faceSamples = [];
let videoStream = null;

window.onload = function() {

    // ✅ Fingerprint listeners
    try {
        if (typeof NEED_FP !== "undefined" && NEED_FP === true) {
            var fp1 = document.getElementById("fp_sample_1");
            var fp2 = document.getElementById("fp_sample_2");
            var fp3 = document.getElementById("fp_sample_3");

            if (fp1) fp1.addEventListener("input", checkSubmitReady);
            if (fp2) fp2.addEventListener("input", checkSubmitReady);
            if (fp3) fp3.addEventListener("input", checkSubmitReady);
        }
    } catch (e) {
        console.log("Fingerprint inputs error:", e);
    }

    checkSubmitReady();
};

// ✅ Start Camera ONLY on button click
function startCamera() {
    var video = document.getElementById("video");

    if (!video) {
        alert("Video element not found!");
        return;
    }

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            videoStream = stream;
            video.srcObject = stream;

            // ✅ Enable capture button once camera starts
            enableCaptureButton();
        })
        .catch(function(err) {
            alert("⚠ Camera access denied or camera not available!");
            console.log(err);
        });
}

// ✅ Enable Capture Button after camera start
function enableCaptureButton() {
    // ✅ Your HTML uses inline onclick, so we can't target button by ID
    // ✅ We'll enable by searching buttons in action row
    const actionButtons = document.querySelectorAll(".action-row button");
    actionButtons.forEach(btn => {
        if (btn.innerText.includes("Capture Face Sample")) {
            btn.disabled = false;
        }
    });
}

// ✅ Capture Face Sample
function captureFaceSample() {
    if (faceSamples.length >= 3) {
        alert("✅ Already captured 3 samples!");
        return;
    }

    var video = document.getElementById("video");
    var canvas = document.getElementById("canvas");

    if (!video || !canvas) {
        alert("Camera not ready!");
        return;
    }

    if (!video.srcObject) {
        alert("⚠ Please click Start Camera first!");
        return;
    }

    var ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth || 320;
    canvas.height = video.videoHeight || 240;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    var imgData = canvas.toDataURL("image/jpeg");

    faceSamples.push(imgData);

    // ✅ Store base64 into hidden fields
    var hiddenField = document.getElementById("face_sample_" + faceSamples.length);
    if (hiddenField) {
        hiddenField.value = imgData;
    }

    // ✅ Add thumbnail preview
    var preview = document.getElementById("facePreview");
    if (preview) {
        var img = document.createElement("img");
        img.src = imgData;
        preview.appendChild(img);
    }

    // ✅ Update counter
    var counter = document.getElementById("faceCounter");
    if (counter) {
        counter.innerText = "Face Samples: " + faceSamples.length + "/3";
    }

    checkSubmitReady();
}

// ✅ Enable submit only when required inputs complete
function checkSubmitReady() {
    var faceReady = true;
    var fpReady = true;

    // ✅ Face must be 3 samples if needed
    try {
        if (typeof NEED_FACE !== "undefined" && NEED_FACE === true) {
            faceReady = (faceSamples.length === 3);
        }
    } catch (e) {
        faceReady = true;
    }

    // ✅ Fingerprint must have 3 inputs if needed
    try {
        if (typeof NEED_FP !== "undefined" && NEED_FP === true) {
            var fp1 = document.getElementById("fp_sample_1");
            var fp2 = document.getElementById("fp_sample_2");
            var fp3 = document.getElementById("fp_sample_3");

            if (!fp1 || !fp2 || !fp3) {
                fpReady = false;
            } else {
                fpReady = (fp1.value.trim() !== "" && fp2.value.trim() !== "" && fp3.value.trim() !== "");
            }
        }
    } catch (e) {
        fpReady = true;
    }

    var submitBtn = document.getElementById("submitBtn");
    if (!submitBtn) return;

    if (faceReady && fpReady) {
        submitBtn.style.display = "inline-block";
    } else {
        submitBtn.style.display = "none";
    }
}