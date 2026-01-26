const API_URL = "http://127.0.0.1:8000";

function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token && !window.location.pathname.includes("login.html") && !window.location.pathname.includes("register.html")) {
        window.location.href = "login.html";
    }
    return token;
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

async function apiFetch(endpoint, method = "GET", body = null) {
    const token = localStorage.getItem("token");
    const headers = {
        "Content-Type": "application/json"
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_URL}${endpoint}`, config);

    if (response.status === 401) {
        logout();
        return;
    }

    return response.json();
}
