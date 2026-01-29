#!/bin/bash
set -e

echo "=== Setup de Desenvolvimento - Vibe Project ==="
echo "Sistema: Fedora 43"
echo ""

# Atualizar sistema
echo "[1/6] Atualizando sistema..."
sudo dnf update -y

# Instalar dependências base
echo "[2/6] Instalando dependências base..."
sudo dnf install -y \
    python3.13 \
    python3.13-pip \
    python3.13-devel \
    git \
    sqlite \
    sqlite-devel

# Criar ambiente virtual
echo "[3/6] Criando ambiente virtual Python..."
python3.13 -m venv .venv
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

# Configurar git hooks (será populado depois)
echo "[6/6] Preparando pre-commit (aguardando configuração)..."
# pre-commit install será executado após .pre-commit-config.yaml existir

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
