// backend base URL (ajuste a porta se necessário)
const API_URL = "http://127.0.0.1:8003";

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
        throw new Error('Unauthorized');
    }

    // No content
    if (response.status === 204) return null;

    const text = await response.text();
    try {
        const data = text ? JSON.parse(text) : null;
        if (!response.ok) {
            const detail = (data && (data.detail || data.message)) || `Erro ${response.status}`;
            throw new Error(detail);
        }
        return data;
    } catch (err) {
        // JSON parse failed or explicit error
        if (!response.ok) throw err;
        return null;
    }
}

// Toast helper
;(function createToastContainer(){
    if (document.getElementById('toast-container')) return;
    const style = document.createElement('style');
    style.innerHTML = `
    #toast-container{position:fixed;right:20px;bottom:20px;z-index:9999;display:flex;flex-direction:column;gap:10px}
    .toast{min-width:200px;padding:12px 16px;border-radius:10px;color:#fff;box-shadow:0 6px 18px rgba(0,0,0,0.12);font-family:Inter,Arial,sans-serif}
    .toast.info{background:#0f172a}
    .toast.success{background:#16a34a}
    .toast.error{background:#ef4444}
    .toast.warn{background:#f59e0b;color:#000}
    `;
    document.head.appendChild(style);
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
})();

function showToast(message, type = 'info', duration = 3500){
    try{
        const container = document.getElementById('toast-container');
        if(!container){ console.warn('Toast container missing'); return; }

        const icons = {
            info: 'ℹ️',
            success: '✅',
            error: '❌',
            warn: '⚠️'
        };

        const el = document.createElement('div');
        el.className = `toast ${type}`;

        const icon = document.createElement('span');
        icon.style.marginRight = '8px';
        icon.textContent = icons[type] || icons.info;

        const text = document.createElement('span');
        text.style.flex = '1';
        text.textContent = message;

        const close = document.createElement('button');
        close.textContent = '✕';
        close.style.marginLeft = '12px';
        close.style.border = 'none';
        close.style.background = 'transparent';
        close.style.color = 'inherit';
        close.style.cursor = 'pointer';

        el.style.display = 'flex';
        el.style.alignItems = 'center';

        el.appendChild(icon);
        el.appendChild(text);
        el.appendChild(close);

        container.appendChild(el);

        // entry animation
        el.style.opacity = '0';
        el.style.transform = 'translateY(8px)';
        requestAnimationFrame(()=>{ el.style.transition = 'opacity 220ms, transform 220ms'; el.style.opacity = '1'; el.style.transform = 'translateY(0)'; });

        const remover = () => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(8px)';
            setTimeout(()=> el.remove(), 250);
        };

        const timeoutId = setTimeout(remover, duration);
        close.addEventListener('click', ()=>{ clearTimeout(timeoutId); remover(); });
    }catch(e){ console.error(e); }
}
