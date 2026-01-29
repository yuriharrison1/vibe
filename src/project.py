"""Gerenciamento de projetos."""

from pathlib import Path
from typing import List

from src.validator import StructureValidator


def init_project(path: Path, force: bool = False) -> bool:
    """Inicializa a estrutura canônica do projeto.

    Args:
        path: Caminho onde criar o projeto
        force: Se True, sobrescreve estrutura existente

    Returns:
        True se sucesso, False se falhar
    """
    # Verificar se já existe projeto
    if not force:
        validator = StructureValidator(path)
        errors = validator.validate_canonical_structure()
        if len(errors) == 0:
            return False  # Projeto já existe e está válido

    # Criar diretórios
    for dir_name in StructureValidator.REQUIRED_DIRS:
        dir_path = path / dir_name
        dir_path.mkdir(exist_ok=True, parents=True)
        gitkeep = dir_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text(f"# Diretório: {dir_name}\n")

    # Criar arquivos mínimos (se não existirem)
    for file_name in StructureValidator.REQUIRED_FILES:
        file_path = path / file_name
        if not file_path.exists():
            content = _get_file_template(file_name)
            file_path.write_text(content)

    return True


def _get_file_template(file_name: str) -> str:
    """Retorna template para arquivo de documentação.

    Args:
        file_name: Nome do arquivo

    Returns:
        Conteúdo template
    """
    if file_name == "scope.md":
        return """# ESCOPO DO PROJETO

## 1. Propósito
[Descrever o propósito do projeto]

## 2. O que o sistema É
[Descrever a natureza do sistema]

## 3. Fora do escopo
[Listar o que NÃO faz parte do projeto]
"""
    elif file_name == "archeture.md":
        return """# ARQUITETURA DO PROJETO

## 1. Decisões arquiteturais
[Documentar decisões e princípios]

## 2. Tecnologias
[Listar tecnologias utilizadas]

## 3. Padrões
[Descrever padrões adotados]
"""
    elif file_name == "milestone.md":
        return """# MILESTONES

## Milestone 0 - Setup inicial
[Descrever objetivos do milestone]

Critérios de aceite:
- [ ] Item 1
- [ ] Item 2
"""
    return ""
