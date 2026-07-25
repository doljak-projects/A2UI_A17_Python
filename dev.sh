#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BE="$ROOT/apps/backend"
FE="$ROOT/apps/frontend"

# --- validações rápidas ---
if [ ! -f "$BE/.venv/bin/activate" ]; then
  echo "[ERROR] venv não encontrado. Rode primeiro:"
  echo "  cd apps/backend && python -m venv .venv && pip install -r requirements-dev.txt"
  exit 1
fi

if [ ! -f "$BE/.env" ]; then
  echo "[ERROR] apps/backend/.env não encontrado. Rode:"
  echo "  cp apps/backend/.env.example apps/backend/.env  # e preencha as chaves"
  exit 1
fi

if [ ! -d "$FE/node_modules" ]; then
  echo "[INFO] node_modules ausente — rodando npm install..."
  npm install --prefix "$FE"
fi

cleanup() {
  echo ""
  echo "[DEV] Encerrando processos..."
  kill "$BE_PID" "$FE_PID" 2>/dev/null
  wait "$BE_PID" "$FE_PID" 2>/dev/null
  echo "[DEV] Encerrado."
}
trap cleanup INT TERM

# --- backend ---
echo "[BE] Iniciando FastAPI em http://localhost:8000 ..."
source "$BE/.venv/bin/activate"
cd "$BE"
uvicorn app.main:app --reload --port 8000 &
BE_PID=$!
deactivate 2>/dev/null || true

# --- frontend ---
echo "[FE] Iniciando Angular em http://localhost:4200 ..."
cd "$FE"
npx ng serve &
FE_PID=$!

echo ""
echo "  Backend  → http://localhost:8000/docs"
echo "  Frontend → http://localhost:4200"
echo "  MCP      → http://localhost:8000/mcp"
echo ""
echo "  Ctrl+C para encerrar ambos."
echo ""

wait "$BE_PID" "$FE_PID"
