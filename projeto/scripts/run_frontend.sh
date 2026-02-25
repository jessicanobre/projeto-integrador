#!/usr/bin/env bash
set -euo pipefail

# Script para servir frontend estático na porta 5500
cd "$(dirname "$0")/../frontend"
python3 -m http.server 5500
