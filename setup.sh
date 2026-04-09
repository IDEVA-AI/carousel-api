#!/bin/bash
# setup.sh — Instalação e inicialização do Gerador de Carrosseis
# Executar uma única vez: bash setup.sh

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Gerador de Carrosseis — Julio Carvalho ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Verificar Python 3.10+ ──────────────────────────────────────────────
PYTHON=$(which python3 || which python)
PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "✓ Python: $PY_VERSION"

# ── 2. Criar ambiente virtual ──────────────────────────────────────────────
if [ ! -d ".venv" ]; then
  echo "→ Criando ambiente virtual..."
  $PYTHON -m venv .venv
fi
source .venv/bin/activate
echo "✓ Ambiente virtual ativado"

# ── 3. Instalar dependências ──────────────────────────────────────────────
echo "→ Instalando dependências Python..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependências instaladas"

# ── 4. Instalar Playwright Chromium ───────────────────────────────────────
echo "→ Instalando Playwright Chromium (necessário para renderizar slides)..."
playwright install chromium
echo "✓ Chromium instalado"

# ── 5. Configurar variáveis de ambiente ──────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "╔══════════════════════════════════════════╗"
  echo "║  AÇÃO NECESSÁRIA: Configure suas chaves  ║"
  echo "╚══════════════════════════════════════════╝"
  echo ""
  echo "Edite o arquivo .env e preencha:"
  echo ""
  echo "  ANTHROPIC_API_KEY=sk-ant-..."
  echo "  (Obrigatório — obtenha em https://console.anthropic.com/keys)"
  echo ""
  echo "  UNSPLASH_ACCESS_KEY=..."
  echo "  (Opcional — obtenha em https://unsplash.com/developers)"
  echo ""
  echo "Depois de preencher, execute: bash start.sh"
else
  echo "✓ Arquivo .env encontrado"
  echo ""
  echo "→ Iniciando servidor..."
  bash start.sh
fi
