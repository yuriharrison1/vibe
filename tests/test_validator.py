"""Testes do validador de estrutura."""

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
