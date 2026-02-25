# PetCare+ — Como rodar localmente

Este documento descreve como preparar o ambiente e executar a aplicação (backend FastAPI + frontend estático) para desenvolvimento local.

Requisitos
- Python 3.10+ (ou 3.11)
- Git
- Navegador moderno

Estrutura relevante
- `projeto/backend` — aplicação FastAPI (server)
- `projeto/frontend` — páginas HTML/JS (cliente)
- `projeto/requirements.txt` — dependências Python

1) Criar ambiente Python e instalar dependências

Windows PowerShell:
```powershell
cd projeto
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

WSL / Linux / macOS:
```bash
cd projeto
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2) Rodar o backend (FastAPI / Uvicorn)

Antes de rodar, copie `.env.example` para `.env` e ajuste `SECRET_KEY` se desejar.

No diretório `projeto/backend` execute:
```bash
cd projeto/backend
uvicorn main:app --host 127.0.0.1 --port 8003 --reload
```

Opção: seed automático para desenvolvimento

Você pode habilitar um seed automático ao iniciar o backend definindo a variável de ambiente `AUTO_SEED=true` antes de executar `./scripts/run_backend.sh`. O script auxiliar `./scripts/auto_seed.sh` irá esperar o backend subir, registrar um usuário de teste, logar e executar `POST /seed`.

Exemplo:
```bash
cd projeto
AUTO_SEED=true ./scripts/run_backend.sh
```

Observação: `auto_seed.sh` usa `jq` para parsear o token — se não tiver `jq` instalado, o script ainda tentará executar, mas pode falhar ao extrair o token; você pode instalar `jq` ou ajustar as variáveis `SEED_EMAIL`/`SEED_PASSWORD` e rodar manualmente.



Observações:
- O servidor cria as tabelas no SQLite automaticamente. Existe uma rotina de compatibilidade que adiciona colunas quando necessário.
- Endpoints principais:
  - `POST /register` — criar usuário
  - `POST /login` — obter token JWT
  - `POST /seed` — popular dados de exemplo (protegido por token)
  - `GET /stats` — estatísticas agregadas
  - `GET /calendar` — eventos (ex.: `/calendar?start=YYYY-MM-DD&end=YYYY-MM-DD`)

Configuração recomendada:
- Defina `SECRET_KEY` via variável de ambiente ou um arquivo `.env` (veja `.env.example`).
- A frontend espera que a API esteja em `http://127.0.0.1:8003` (ver `projeto/frontend/js/global.js`).

3) Servir o frontend (estático)

No diretório `projeto/frontend` rode um servidor estático simples (ex.: Python http.server):
```bash
cd projeto/frontend
python -m http.server 5500
```

Abra o navegador em `http://127.0.0.1:5500/dashboard.html` (faça login primeiro).

4) Uso básico (registro, login e seed)

- Registrar um usuário (exemplo curl):
```bash
curl -X POST "http://127.0.0.1:8003/register" -H "Content-Type: application/json" -d '{"email":"meu@exemplo.com","password":"senha"}'
```
- Obter token:
```bash
curl -X POST "http://127.0.0.1:8003/login" -H "Content-Type: application/json" -d '{"email":"meu@exemplo.com","password":"senha"}'
```
Resposta: `{ "access_token": "<TOKEN>", "token_type": "bearer" }`

- Popular dados de teste (use o token retornado):
```bash
curl -X POST "http://127.0.0.1:8003/seed" -H "Authorization: Bearer <TOKEN>"
```

5) Configurações rápidas
- A frontend espera que a API esteja em `http://127.0.0.1:8003` (ver `projeto/frontend/js/global.js`). Ajuste se necessário.
- Se mudar portas, atualize o CORS em `projeto/backend/main.py` ou adicione a origem do frontend.

6) Problemas comuns
- Se o SQLite já existia e você adicionou campos, o backend tem uma rotina de startup que tenta aplicar `ALTER TABLE` para colunas simples; reinicie o servidor.
- Evite commitar a virtualenv (`projeto/.venv`) ou o arquivo `petcare.db` — já estão adicionados ao `.gitignore`.

--
Se quiser, eu posso:
- Gerar um `requirements-lock.txt` com as versões exatas.
- Transformar o frontend em PWA e preparar um pacote para Android (veja opções abaixo).
