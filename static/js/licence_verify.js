let currentStep = 1;

function verifyFingerprint() {
    document.getElementById("fp-success").style.display = "block";
    setTimeout(nextStep, 800);
}

function verifyFace() {
    document.getElementById("face-success").style.display = "block";
    setTimeout(nextStep, 800);
}

function nextStep() {
    document.getElementById(`step-${currentStep}`).classList.remove("active");
    document.querySelectorAll(".step")[currentStep - 1].classList.remove("active");

    currentStep++;

    document.getElementById(`step-${currentStep}`).classList.add("active");
    document.querySelectorAll(".step")[currentStep - 1].classList.add("active");
}

function complete(offence) {
    document.getElementById("done").style.display = "block";
    console.log("Offence Selected:", offence);
}
