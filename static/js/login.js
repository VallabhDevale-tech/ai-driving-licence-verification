function togglePassword() {
    const pwd = document.getElementById("password");
    pwd.type = pwd.type === "password" ? "text" : "password";
}

const form = document.getElementById("loginForm");
const steps = document.getElementById("authSteps");
const btn = document.getElementById("loginBtn");

if (form) {
    form.addEventListener("submit", () => {
        btn.innerText = "Authenticating...";
        btn.disabled = true;

        steps.style.display = "block";

        const items = steps.children;
        for (let i = 0; i < items.length; i++) {
            items[i].style.opacity = "0";
            setTimeout(() => {
                items[i].style.opacity = "1";
            }, i * 400);
        }
    });
}
