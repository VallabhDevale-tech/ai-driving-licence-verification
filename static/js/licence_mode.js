let videoStream = null;

window.onload = async function() {
    await loadCameraDevices();
};

async function loadCameraDevices() {
    const cameraSelect = document.getElementById("cameraSelect");
    if (!cameraSelect) return;

    cameraSelect.innerHTML = "";

    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const cameras = devices.filter(device => device.kind === "videoinput");

        if (cameras.length === 0) {
            cameraSelect.innerHTML = `<option>No Camera Found</option>`;
            return;
        }

        cameras.forEach((camera, index) => {
            const option = document.createElement("option");
            option.value = camera.deviceId;
            option.text = camera.label ? camera.label : `Camera ${index + 1}`;
            cameraSelect.appendChild(option);
        });

    } catch (err) {
        console.error("Device List Error:", err);
    }
}

async function startCamera() {
    const video = document.getElementById("video");
    const errorBox = document.getElementById("cameraError");
    const cameraSelect = document.getElementById("cameraSelect");

    if (errorBox) errorBox.innerText = "";

    try {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
        }

        let selectedDeviceId = null;
        if (cameraSelect) selectedDeviceId = cameraSelect.value;

        videoStream = await navigator.mediaDevices.getUserMedia({
            video: {
                deviceId: selectedDeviceId ? { exact: selectedDeviceId } : undefined
            }
        });

        video.srcObject = videoStream;
        await video.play();

    } catch (err) {
        console.error("Camera Error:", err);
        if (errorBox) errorBox.innerText = "❌ Camera error! Please check permissions.";
    }
}

function capturePhoto() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const fileInput = document.getElementById("face_image");
    const errorBox = document.getElementById("cameraError");

    if (errorBox) errorBox.innerText = "";

    if (!videoStream) {
        if (errorBox) errorBox.innerText = "❌ Start Camera first!";
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        const file = new File([blob], "scan.jpg", { type: "image/jpeg" });

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;

        alert("✅ Face Captured Successfully!");
    }, "image/jpeg", 0.95);
}