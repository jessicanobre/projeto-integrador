Arquivamento do backend Node
--------------------------------

Neste repositório existe um backend em Node/Express em `projeto/backend/src` que era um rascunho. A versão mantida e em uso pelo frontend neste projeto é a API em Python/FastAPI localizada em `projeto/backend` (arquivos `main.py`, `auth.py`, `models.py`, etc.).

Decisões tomadas:
- Mantive os arquivos Node no diretório `projeto/backend/src` como referência/arquivo, mas a API oficial para desenvolvimento e entrega é a implementada em FastAPI.
- Se quiser remover o Node do repositório, pode ser feito em uma etapa separada.

Como rodar a API FastAPI (resumo):
1. Crie um virtualenv em `projeto` e instale dependências: `pip install -r requirements.txt`.
2. Copie `.env.example` para `.env` e ajuste `SECRET_KEY` conforme necessário.
3. Na pasta `projeto/backend` rode: `uvicorn main:app --host 127.0.0.1 --port 8003 --reload`.
