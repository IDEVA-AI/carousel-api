#!/bin/bash
# start.sh — Iniciar o servidor do Gerador de Carrosseis

set -e

# Ativa o ambiente virtual
source .venv/bin/activate

# Carrega variáveis de ambiente
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

PORT=${PORT:-8765}

# Verifica se Claude CLI ou API key está disponível
if ! command -v claude &>/dev/null && { [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-..." ]; }; then
  echo ""
  echo "  Claude Code CLI nao encontrado e ANTHROPIC_API_KEY nao configurada."
  echo "  Instale o Claude Code (plano Max) ou adicione a chave no .env"
  echo ""
  exit 1
fi

echo ""
echo "  Gerador de Carrosseis — INICIADO"
echo "  http://localhost:$PORT"
echo ""

uvicorn server:app --host 0.0.0.0 --port $PORT --reload
