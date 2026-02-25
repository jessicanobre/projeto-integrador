#!/usr/bin/env bash
set -euo pipefail

# Script simples para rodar o backend FastAPI em desenvolvimento
# Executa dentro da pasta `backend` para que imports locais funcionem (models, schemas, ...)
cd "$(dirname "$0")/../backend"
source ../.venv/bin/activate 2>/dev/null || true
uvicorn main:app --host 127.0.0.1 --port 8003 --reload

# If AUTO_SEED is set, try to run the auto-seed helper in background
if [ "${AUTO_SEED:-""}" = "true" ]; then
	(cd "$(dirname "$0")/.." && ./scripts/auto_seed.sh) &
fi
