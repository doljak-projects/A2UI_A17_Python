#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BE="$ROOT/apps/backend"
FE="$ROOT/apps/frontend"

# --- dependências do backend ---
if [ ! -f "$BE/.venv/bin/activate" ]; then
  echo "[BE] venv não encontrado — criando e instalando dependências..."
  python3 -m venv "$BE/.venv"
  "$BE/.venv/bin/pip" install --quiet -r "$BE/requirements-dev.txt"
  echo "[BE] Dependências instaladas."
fi

if [ ! -f "$BE/.env" ]; then
  if [ -f "$BE/.env.example" ]; then
    cp "$BE/.env.example" "$BE/.env"
    echo "[WARN] apps/backend/.env criado a partir do .env.example."
    echo "[WARN] Preencha as chaves (LLM_API_KEY, WEATHER_API_KEY, etc.) antes de usar o chat."
  else
    echo "[ERROR] apps/backend/.env não encontrado e .env.example também ausente."
    exit 1
  fi
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
