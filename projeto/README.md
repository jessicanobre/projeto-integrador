# PetCare+

Sistema de gerenciamento de pets com frontend dinâmico e backend em Python.

## Tecnologias
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python, FastAPI, SQLAlchemy
- **Banco de Dados**: SQLite

## Como Rodar o Projeto

### 1. Backend
Certifique-se de ter o Python instalado.

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Inicie o servidor:
   ```bash
   uvicorn backend.main:app --reload
   ```
   O backend estará rodando em `http://127.0.0.1:8000`.

### 2. Frontend
Basta abrir o arquivo `frontend/login.html` no seu navegador favorito.
(Recomendamos usar uma extensão como Live Server no VS Code para evitar problemas de CORS, embora o backend já esteja configurado para aceitar requisições de todas as origens).

## Funcionalidades Dinâmicas Implementadas
- [x] Cadastro e Login de Usuários (com JWT)
- [x] Gerenciamento de Pets (Adição, Listagem, Exclusão)
- [x] Controle de Vacinas vinculado aos pets
- [x] Agenda de Lembretes inteligente
- [x] Histórico Médico categorizado (Consultas, Exames, etc.)
