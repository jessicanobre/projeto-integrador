#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv..."
  python3 -m venv "$VENV_DIR"
fi

echo "Activating venv and installing requirements..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
"$VENV_DIR/bin/pip" install -r requirements.txt >/dev/null

chmod +x scripts/*.sh || true

echo "Starting backend (with AUTO_SEED=true)... logs: /tmp/petcare_backend.log"
AUTO_SEED=true ./scripts/run_backend.sh > /tmp/petcare_backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting frontend (logs: /tmp/petcare_frontend.log)..."
./scripts/run_frontend.sh > /tmp/petcare_frontend.log 2>&1 &
FRONTEND_PID=$!

API_URL=${API_URL:-http://127.0.0.1:8003}

echo "Waiting for backend to be ready at ${API_URL}..."
for i in {1..30}; do
  if curl -sSf "$API_URL/docs" >/dev/null 2>&1; then
    echo "Backend is up"
    break
  fi
  sleep 1
done

echo "Running basic API tests..."
TEST_EMAIL="dev+teste@local"
TEST_PASS="senhaDev123"

echo "1) Register user"
reg_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/register" -H "Content-Type: application/json" -d "{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASS}\"}") || true
echo "  HTTP $reg_code"

echo "2) Login"
login_resp=$(curl -s -X POST "$API_URL/login" -H "Content-Type: application/json" -d "{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASS}\"}") || true
token=$(echo "$login_resp" | python3 -c "import sys, json; d=json.load(sys.stdin) if sys.stdin.readable() else {}; print(d.get('access_token',''))" 2>/dev/null || true)
if [ -z "$token" ]; then
  token=$(echo "$login_resp" | jq -r '.access_token' 2>/dev/null || true)
fi
if [ -z "$token" ] || [ "$token" = "null" ]; then
  echo "  Login failed, aborting tests. Response: $login_resp"
  exit 1
fi
echo "  Got token"

echo "3) Call /seed"
seed_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/seed" -H "Authorization: Bearer ${token}") || true
echo "  HTTP $seed_code"

echo "4) Create pet"
pet_payload='{ "name": "Bolt", "age": "2", "breed": "SRD" }'
create_resp=$(curl -s -X POST "$API_URL/pets" -H "Content-Type: application/json" -H "Authorization: Bearer ${token}" -d "$pet_payload") || true
echo "  create response: $create_resp"

echo "5) List pets"
pets=$(curl -s -X GET "$API_URL/pets" -H "Authorization: Bearer ${token}") || true
echo "  pets: $pets"

echo "6) Cleanup: if created pet exists, try to delete it"
pet_id=$(echo "$create_resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || true)
if [ -z "$pet_id" ] || [ "$pet_id" = "None" ]; then
  pet_id=$(echo "$pets" | python3 -c "import sys,json; l=json.load(sys.stdin) if sys.stdin.readable() else []; print(l[0].get('id','') if l else '')" 2>/dev/null || true)
fi
if [ -n "$pet_id" ]; then
  del_code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/pets/${pet_id}" -H "Authorization: Bearer ${token}") || true
  echo "  deleted pet ${pet_id}, HTTP $del_code"
else
  echo "  no pet id to delete"
fi

echo "Basic tests completed. Backend PID: $BACKEND_PID, Frontend PID: $FRONTEND_PID"
echo "Backend log tail:"
tail -n 40 /tmp/petcare_backend.log || true

echo "Frontend log tail:"
tail -n 20 /tmp/petcare_frontend.log || true

echo "Dev setup finished"
