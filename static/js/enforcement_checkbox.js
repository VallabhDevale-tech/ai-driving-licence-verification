function resetGenerateButton() {
    const generateBtn = document.getElementById("generateBtn");
    generateBtn.disabled = true;
    generateBtn.style.display = "none";
}

function showSubOffences(offenceId) {

    const subSection = document.getElementById("subOffenceSection");
    const subGrid = document.getElementById("subOffenceGrid");
    const paymentSection = document.getElementById("paymentSection");
    const noViolationMsg = document.getElementById("noViolationMsg");
    const generateBtn = document.getElementById("generateBtn");

    // Reset everything
    subGrid.innerHTML = "";
    subSection.style.display = "none";
    paymentSection.style.display = "none";
    noViolationMsg.style.display = "none";
    resetGenerateButton();

    // Clear payment selections
    const payInputs = document.querySelectorAll("input[name='payment_mode']");
    payInputs.forEach((x) => x.checked = false);

    // NO VIOLATION CASE
    if (offenceId === "5") {

        noViolationMsg.style.display = "block";

        // check verification status from page
        const statusBox = document.querySelector(".status");
        const statusText = statusBox ? statusBox.innerText : "";

        // only show payment if NOT VERIFIED
        if (statusText.includes("NOT VERIFIED")) {

            paymentSection.style.display = "block";

            generateBtn.style.display = "block";
            generateBtn.disabled = true;
        }

        return;
    }

    // Show sub offences
    subSection.style.display = "block";

    const subs = OFFENCES[offenceId]["sub"];

    Object.keys(subs).forEach((key) => {

        const data = subs[key];

        const label = document.createElement("label");
        label.className = "select-card";

        label.innerHTML = `
            <input type="radio" name="sub_id" value="${key}" required onchange="showPaymentSection()">
            <div class="card-body">
                <h4>${key}. ${data.title}</h4>
                <p>Fine: ₹${data.fine} | ${data.section}</p>
            </div>
        `;

        subGrid.appendChild(label);
    });
}

function showPaymentSection() {

    const paymentSection = document.getElementById("paymentSection");

    // reset generate button
    resetGenerateButton();

    // clear payment selection
    const payInputs = document.querySelectorAll("input[name='payment_mode']");
    payInputs.forEach((x) => x.checked = false);

    // show payment options
    paymentSection.style.display = "block";
}

function enableGenerate() {

    const generateBtn = document.getElementById("generateBtn");

    // enable generate button after payment selection
    generateBtn.style.display = "block";
    generateBtn.disabled = false;
}