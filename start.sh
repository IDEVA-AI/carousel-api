#!/bin/bash
# start.sh — Iniciar o servidor após o setup

set -e

# Ativa o ambiente virtual
source .venv/bin/activate

# Carrega variáveis de ambiente
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Verifica API key
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-..." ]; then
  echo ""
  echo "⚠️  ANTHROPIC_API_KEY não configurada!"
  echo "   Edite o arquivo .env e adicione sua chave."
  echo "   Obtenha em: https://console.anthropic.com/keys"
  echo ""
  exit 1
fi

PORT=${PORT:-8000}

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Gerador de Carrosseis — INICIADO       ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Abra no navegador: http://localhost:$PORT"
echo ""
echo "  Pressione Ctrl+C para parar."
echo ""

uvicorn server:app --host 0.0.0.0 --port $PORT --reload
