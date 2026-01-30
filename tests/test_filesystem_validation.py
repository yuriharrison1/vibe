"""Testes para validação de filesystem."""

import tempfile
from pathlib import Path

import pytest

from src.validator import StructureValidator


def test_canonical_structure_valid(tmp_path: Path) -> None:
    """Testa que estrutura canônica válida não gera erros."""
    # Criar estrutura canônica
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    assert len(errors) == 0, f"Erros encontrados: {errors}"


def test_missing_required_directory(tmp_path: Path) -> None:
    """Testa detecção de diretório obrigatório faltante."""
    # Criar estrutura sem 'docs'
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    assert any("docs" in err.lower() for err in errors), f"Erros: {errors}"


def test_missing_required_file(tmp_path: Path) -> None:
    """Testa detecção de arquivo obrigatório faltante."""
    # Criar estrutura sem 'scope.md'
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    assert any("scope.md" in err.lower() for err in errors), f"Erros: {errors}"


def test_detect_junk_directory(tmp_path: Path) -> None:
    """Testa detecção de diretório de lixo."""
    # Criar estrutura válida
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    # Adicionar diretório de lixo
    (tmp_path / "build").mkdir()
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    assert any("build" in err.lower() for err in errors), f"Erros: {errors}"


def test_detect_junk_files(tmp_path: Path) -> None:
    """Testa detecção de arquivos de lixo."""
    # Criar estrutura válida
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    # Adicionar arquivos de lixo
    (tmp_path / "test.log").write_text("log")
    (tmp_path / "temp.tmp").write_text("temp")
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    assert any("test.log" in err or "temp.tmp" in err for err in errors), f"Erros: {errors}"


def test_unauthorized_root_directory(tmp_path: Path) -> None:
    """Testa detecção de diretório não autorizado na raiz."""
    # Criar estrutura válida
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    # Adicionar diretório não autorizado
    (tmp_path / "node_modules").mkdir()
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    assert any("node_modules" in err.lower() for err in errors), f"Erros: {errors}"


def test_test_directory_structure(tmp_path: Path) -> None:
    """Testa validação da estrutura de testes."""
    # Criar estrutura válida
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    # Criar estrutura de testes válida
    tests_dir = tmp_path / "tests"
    (tests_dir / "test_example.py").write_text("def test(): pass")
    (tests_dir / "__init__.py").write_text("")
    
    # Adicionar arquivo órfão
    (tests_dir / "test_orphan.txt").write_text("orphan")
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    # Deve detectar o arquivo .txt não permitido
    assert any("test_orphan.txt" in err for err in errors), f"Erros: {errors}"


def test_state_integrity(tmp_path: Path) -> None:
    """Testa validação de integridade do state."""
    # Criar estrutura válida
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    # Criar state/ com vibe.db
    state_dir = tmp_path / "state"
    (state_dir / "vibe.db").write_text("sqlite")
    
    # Adicionar arquivo de journal órfão
    (state_dir / "vibe.db-journal").write_text("journal")
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    # Deve detectar o arquivo .db-journal
    assert any("db-journal" in err for err in errors), f"Erros: {errors}"


def test_objectives_directory_invalid_names(tmp_path: Path) -> None:
    """Testa validação de nomes inválidos em tests/objectives/."""
    # Criar estrutura válida
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    # Criar tests/objectives/ com diretório inválido
    objectives_dir = tmp_path / "tests" / "objectives"
    objectives_dir.mkdir(parents=True)
    (objectives_dir / "invalid-name").mkdir()  # Não é UUID
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    # Deve detectar nome não-UUID
    assert any("invalid-name" in err.lower() for err in errors), f"Erros: {errors}"


def test_allowed_exceptions(tmp_path: Path) -> None:
    """Testa que diretórios permitidos não geram erros."""
    # Criar estrutura válida
    (tmp_path / "docs").mkdir()
    (tmp_path / "objectives").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "ai").mkdir()
    (tmp_path / "state").mkdir()
    (tmp_path / "src").mkdir()
    
    (tmp_path / "scope.md").write_text("# Scope")
    (tmp_path / "archeture.md").write_text("# Architecture")
    (tmp_path / "milestone.md").write_text("# Milestone")
    
    # Adicionar diretórios permitidos
    (tmp_path / ".git").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "__pycache__").mkdir()
    
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    
    # Não deve gerar erros para diretórios permitidos
    assert not any(".git" in err or ".venv" in err or "__pycache__" in err for err in errors), \
        f"Erros inesperados: {errors}"
