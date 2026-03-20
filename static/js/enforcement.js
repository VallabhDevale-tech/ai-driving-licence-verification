async function loadSubOffences() {
    const offenceId = document.getElementById("offenceSelect").value;
    const subSelect = document.getElementById("subOffenceSelect");

    subSelect.innerHTML = `<option value="">-- Select Sub Offence --</option>`;

    if (!offenceId || offenceId === "5") return;

    const res = await fetch(`/get_sub_offences/${offenceId}`);
    const data = await res.json();

    Object.keys(data).forEach(key => {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = `${key}. ${data[key].title} | ₹${data[key].fine}`;
        subSelect.appendChild(option);
    });
}