#!/usr/bin/env bash
set -euo pipefail

# Auto seed helper for development.
# Usage: set AUTO_SEED=true when running run_backend.sh, or call this script manually.
# Environment variables (optional):
#  SEED_EMAIL (default teste@local)
#  SEED_PASSWORD (default senha123)
#  API_URL (default http://127.0.0.1:8003)

API_URL=${API_URL:-http://127.0.0.1:8003}
SEED_EMAIL=${SEED_EMAIL:-teste@local}
SEED_PASSWORD=${SEED_PASSWORD:-senha123}

echo "[auto_seed] waiting for backend at ${API_URL}..."
for i in {1..30}; do
  if curl -sSf "$API_URL/docs" >/dev/null 2>&1; then
    echo "[auto_seed] backend is up"
    break
  fi
  sleep 1
done

echo "[auto_seed] registering user ${SEED_EMAIL} (if not exists)"
reg_resp=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/register" -H "Content-Type: application/json" -d "{\"email\":\"${SEED_EMAIL}\",\"password\":\"${SEED_PASSWORD}\"}") || true
if [ "$reg_resp" = "201" ] || [ "$reg_resp" = "200" ]; then
  echo "[auto_seed] user created"
else
  echo "[auto_seed] register returned HTTP $reg_resp (may already exist)"
fi

echo "[auto_seed] logging in to get token"
token=$(curl -s -X POST "$API_URL/login" -H "Content-Type: application/json" -d "{\"email\":\"${SEED_EMAIL}\",\"password\":\"${SEED_PASSWORD}\"}" | jq -r '.access_token' 2>/dev/null || true)
if [ -z "$token" ] || [ "$token" = "null" ]; then
  echo "[auto_seed] login failed or token missing; skipping seed"
  exit 0
fi

echo "[auto_seed] calling /seed"
seed_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/seed" -H "Authorization: Bearer ${token}") || true
if [ "$seed_code" = "200" ] || [ "$seed_code" = "201" ]; then
  echo "[auto_seed] seed executed (HTTP $seed_code)"
else
  echo "[auto_seed] seed returned HTTP $seed_code"
fi

echo "[auto_seed] done"
