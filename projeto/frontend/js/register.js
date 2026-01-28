const registerForm = document.getElementById("registerForm");

registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    // Foto de perfil seria implementada com FormData, mas vamos focar no básico primeiro

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showToast("Conta criada com sucesso!", 'success');
            window.location.href = "login.html";
        } else {
            showToast(data.detail || "Erro ao criar conta", 'error');
        }
    } catch (error) {
        console.error("Erro:", error);
        showToast("Erro ao conectar com o servidor", 'error');
    }
});
