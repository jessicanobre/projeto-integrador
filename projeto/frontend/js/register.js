const registerForm = document.getElementById("registerForm");

registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const photoInput = document.getElementById("photo");
    const photoFile = photoInput.files && photoInput.files[0] ? photoInput.files[0] : null;

    try {
        // 1) Criar usuário
        const regResp = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const regData = await regResp.json().catch(()=>null);
        if (!regResp.ok) {
            showToast((regData && (regData.detail || regData.message)) || 'Erro ao criar conta', 'error');
            return;
        }

        showToast('Conta criada com sucesso!', 'success');

        // 2) Fazer login para obter token
        const loginResp = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const loginData = await loginResp.json().catch(()=>null);
        if (!loginResp.ok || !loginData || !loginData.access_token) {
            showToast('Conta criada, mas erro ao obter token. Faça login manualmente.', 'warn');
            window.location.href = 'login.html';
            return;
        }

        const token = loginData.access_token;
        localStorage.setItem('token', token);

        // 3) Se existir foto, enviar para /users/me/photo
        if (photoFile) {
            const form = new FormData();
            form.append('file', photoFile, photoFile.name);

            try {
                const upResp = await fetch(`${API_URL}/users/me/photo`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: form
                });
                if (!upResp.ok) {
                    const err = await upResp.json().catch(()=>null);
                    showToast((err && (err.detail || err.message)) || 'Foto não enviada', 'warn');
                } else {
                    showToast('Foto de perfil enviada', 'success');
                }
            } catch (e) {
                console.error(e);
                showToast('Erro ao enviar foto', 'warn');
            }
        }

        // Redirecionar para dashboard
        window.location.href = 'dashboard.html';

    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com o servidor', 'error');
    }
});
