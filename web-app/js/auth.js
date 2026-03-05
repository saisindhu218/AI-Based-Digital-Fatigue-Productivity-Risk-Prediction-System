const API_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {

    const token = localStorage.getItem("token");

    // If already logged in and user opens login page → redirect to dashboard
    if (window.location.pathname.includes("login.html") && token) {
        window.location.href = "index.html";
        return;
    }

    if (document.getElementById("login-form")) setupLogin();
    if (document.getElementById("register-form")) setupRegister();

    showUserName();
});

function checkAuth(page) {

    const token = localStorage.getItem("token");

    if (page === "index.html" && !token) {
        location.href = "login.html";
    }

    if ((page === "login.html" || page === "register.html") && token) {
        location.href = "index.html";
    }
}


// ================= REGISTER =================

function setupRegister() {

    const form = document.getElementById("register-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {

        e.preventDefault();

        const name = document.getElementById("full-name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirm = document.getElementById("confirm-password")?.value;

        if (!name || !email || !password) {
            alert("All fields are required");
            return;
        }

        if (password.length < 6) {
            alert("Password must be at least 6 characters");
            return;
        }

        if (confirm && password !== confirm) {
            alert("Passwords do not match");
            return;
        }

        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = "Registering...";

        try {

            const res = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: email,
                    full_name: name,
                    password: password
                })
            });

            const data = await res.json();

            if (!res.ok) {
                alert(data.detail || "Registration failed");
                btn.disabled = false;
                btn.textContent = "Register";
                return;
            }

            alert("Registration successful! Please login.");
            location.href = "login.html";

        } catch (error) {

            alert("Network error. Is backend running?");
            btn.disabled = false;
            btn.textContent = "Register";

        }

    });

}


// ================= LOGIN =================

function setupLogin() {

    const form = document.getElementById("login-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {

        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if (!email || !password) {
            alert("Email and password required");
            return;
        }

        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = "Logging in...";

        try {

            const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (!res.ok) {
                alert(data.detail || "Login failed");
                btn.disabled = false;
                btn.textContent = "Login";
                return;
            }

            console.log("Login success", data);

            // Extract username from email
            const username = email.split("@")[0];

            // Store login info
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("studentName", username);
            localStorage.setItem("userId", username);

            // Notify backend about active user (optional)
            try {

                await fetch(`${API_BASE_URL}/api/v1/pairing/save-user`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        user_id: username
                    })
                });

            } catch (err) {

                console.warn("Could not save active user");

            }

            location.href = "index.html";

        } catch (error) {

            alert("Network error. Is backend running?");
            btn.disabled = false;
            btn.textContent = "Login";

        }

    });

}

// ================= USER NAME DISPLAY =================

function showUserName() {

    const box = document.getElementById("userEmail");

    if (box) {
        box.textContent = localStorage.getItem("studentName") || "User";
    }

}


// ================= LOGOUT =================

document.addEventListener("click", (e) => {

    if (e.target.id === "logoutBtn" || e.target.closest("#logoutBtn")) {

        localStorage.clear();
        location.href = "login.html";

    }

});