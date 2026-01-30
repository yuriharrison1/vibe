"""Testes do validador de estrutura."""

import tempfile
from pathlib import Path

import pytest

from src.validator import StructureValidator


def test_valid_structure_passes(tmp_path: Path) -> None:
    """Estrutura válida passa na validação."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    assert len(errors) == 0


def test_missing_directory_is_detected(tmp_path: Path) -> None:
    """Diretório faltante é detectado."""
    # Criar estrutura parcial (faltando 'docs')
    for dir_name in StructureValidator.REQUIRED_DIRS:
        if dir_name != "docs":
            (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    assert len(errors) == 1
    assert "docs/" in errors[0]


def test_missing_file_is_detected(tmp_path: Path) -> None:
    """Arquivo faltante é detectado."""
    # Criar estrutura parcial (faltando 'scope.md')
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        if file_name != "scope.md":
            (tmp_path / file_name).touch()

    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    assert len(errors) == 1
    assert "scope.md" in errors[0]


def test_multiple_errors_are_reported(tmp_path: Path) -> None:
    """Múltiplos erros são reportados."""
    # Criar estrutura vazia
    validator = StructureValidator(tmp_path)
    errors = validator.validate_canonical_structure()
    expected_count = len(StructureValidator.REQUIRED_DIRS) + len(
        StructureValidator.REQUIRED_FILES
    )
    assert len(errors) == expected_count


def test_validate_directory_structure(tmp_path: Path) -> None:
    """Testa validação de estrutura de diretórios."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    # Adicionar diretório não autorizado
    (tmp_path / "build").mkdir()

    validator = StructureValidator(tmp_path)
    errors = validator.validate_directory_structure()
    
    # Deve detectar o diretório 'build' como lixo
    assert any("build" in err.lower() for err in errors), f"Erros: {errors}"


def test_validate_root_files(tmp_path: Path) -> None:
    """Testa validação de arquivos na raiz."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    # Adicionar arquivo de lixo
    (tmp_path / "temp.tmp").write_text("temporary")

    validator = StructureValidator(tmp_path)
    errors = validator.validate_root_files()
    
    # Deve detectar o arquivo .tmp
    assert any("temp.tmp" in err for err in errors), f"Erros: {errors}"


def test_detect_junk_files(tmp_path: Path) -> None:
    """Testa detecção de arquivos de lixo."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    # Adicionar vários tipos de lixo
    (tmp_path / "test.log").write_text("log")
    (tmp_path / "temp.tmp").write_text("temp")
    (tmp_path / "backup.bak").write_text("backup")
    (tmp_path / "build").mkdir()

    validator = StructureValidator(tmp_path)
    junk_items = validator.detect_junk_files()
    
    # Deve detectar pelo menos alguns itens de lixo
    assert len(junk_items) >= 3, f"Itens de lixo: {junk_items}"
    
    # Verificar tipos específicos
    junk_paths = [str(Path(item).name) for item in junk_items]
    assert any("test.log" in item or "test.log" == item for item in junk_paths)
    assert any("temp.tmp" in item or "temp.tmp" == item for item in junk_paths)
    assert any("build" in item for item in junk_paths)


def test_validate_test_structure(tmp_path: Path) -> None:
    """Testa validação da estrutura de testes."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    # Criar estrutura de testes válida
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_example.py").write_text("def test(): pass")
    
    # Adicionar arquivo não permitido
    (tests_dir / "README.txt").write_text("readme")

    validator = StructureValidator(tmp_path)
    errors = validator.validate_test_structure()
    
    # Deve detectar o arquivo .txt não permitido
    assert any("README.txt" in err for err in errors), f"Erros: {errors}"


def test_validate_state_integrity(tmp_path: Path) -> None:
    """Testa validação de integridade do state."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    # Criar state/ com vibe.db
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / "vibe.db").write_text("sqlite")
    
    # Adicionar arquivo de journal órfão
    (state_dir / "vibe.db-journal").write_text("journal")

    validator = StructureValidator(tmp_path)
    errors = validator.validate_state_integrity()
    
    # Deve detectar o arquivo .db-journal
    assert any("db-journal" in err.lower() for err in errors), f"Erros: {errors}"


def test_allowed_exceptions_not_errors(tmp_path: Path) -> None:
    """Testa que diretórios permitidos não geram erros."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    # Adicionar diretórios permitidos
    (tmp_path / ".git").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "__pycache__").mkdir()

    validator = StructureValidator(tmp_path)
    errors = validator.validate_directory_structure()
    
    # Não deve gerar erros para diretórios permitidos
    assert not any(".git" in err or ".venv" in err or "__pycache__" in err for err in errors), \
        f"Erros inesperados: {errors}"


def test_validate_objectives_test_structure(tmp_path: Path) -> None:
    """Testa validação da estrutura de tests/objectives/."""
    # Criar estrutura válida
    for dir_name in StructureValidator.REQUIRED_DIRS:
        (tmp_path / dir_name).mkdir()

    for file_name in StructureValidator.REQUIRED_FILES:
        (tmp_path / file_name).touch()

    # Criar tests/objectives/ com estrutura válida
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    objectives_dir = tests_dir / "objectives"
    objectives_dir.mkdir()
    
    # Diretório com nome UUID válido
    import uuid
    valid_uuid = str(uuid.uuid4())
    obj_dir = objectives_dir / valid_uuid
    obj_dir.mkdir()
    (obj_dir / "test_example.py").write_text("def test(): pass")
    
    # Diretório com nome inválido
    invalid_dir = objectives_dir / "invalid-name"
    invalid_dir.mkdir()

    validator = StructureValidator(tmp_path)
    errors = validator.validate_test_structure()
    
    # Deve detectar nome não-UUID
    assert any("invalid-name" in err.lower() for err in errors), f"Erros: {errors}"
