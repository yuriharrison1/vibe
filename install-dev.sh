#!/bin/bash
set -e

echo "=== Setup de Desenvolvimento - Vibe Project ==="
echo "Sistema: Fedora 43"
echo ""


# Instalar dependências base
echo "[2/6] Instalando dependências base..."
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    git \
    sqlite \
    sqlite-devel

# Criar ambiente virtual
echo "[3/6] Criando ambiente virtual Python..."
python3 -m venv .venv
source .venv/bin/activate

# Atualizar pip
echo "[4/6] Atualizando pip..."
pip install --upgrade pip setuptools wheel

# Instalar ferramentas de desenvolvimento
echo "[5/6] Instalando ferramentas de desenvolvimento..."
pip install \
    click \
    pytest \
    pytest-cov \
    ruff \
    black \
    mypy \
    pre-commit

# Configurar git hooks
echo "[6/6] Instalando pre-commit hooks..."
if [ -f .pre-commit-config.yaml ]; then
    pre-commit install
    echo "Pre-commit hooks instalados!"
else
    echo "Aviso: .pre-commit-config.yaml não encontrado. Execute 'pre-commit install' após criá-lo."
fi

echo ""
echo "✓ Setup concluído!"
echo ""
echo "Para ativar o ambiente:"
echo "  source .venv/bin/activate"
echo ""
echo "Próximos passos:"
echo "  1. Execute os prompts do Aider na ordem"
echo "  2. Após criar .pre-commit-config.yaml, execute: pre-commit install"
echo ""
