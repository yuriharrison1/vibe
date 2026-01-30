"""Testes para o gerador automático de testes."""

import tempfile
from pathlib import Path

import pytest

from src.models import Objective, ObjectiveStatus, ObjectiveType
from src.test_generator import (
    generate_test_directory,
    generate_test_file,
    generate_tests_for_objective,
    map_objective_to_test_types,
)


def test_map_objective_to_test_types() -> None:
    """Testa mapeamento de tipos de objetivo para tipos de teste."""
    # CLI_COMMAND
    obj = Objective(tipos=[ObjectiveType.CLI_COMMAND])
    result = map_objective_to_test_types(obj)
    assert "test_execution" in result
    assert "test_exit_code" in result
    assert "test_output" in result
    
    # FILESYSTEM
    obj = Objective(tipos=[ObjectiveType.FILESYSTEM])
    result = map_objective_to_test_types(obj)
    assert "test_file_creation" in result
    assert "test_structure" in result
    assert "test_idempotence" in result
    
    # STATE
    obj = Objective(tipos=[ObjectiveType.STATE])
    result = map_objective_to_test_types(obj)
    assert "test_database_creation" in result
    assert "test_schema" in result
    assert "test_initial_state" in result
    
    # PROJECT
    obj = Objective(tipos=[ObjectiveType.PROJECT])
    result = map_objective_to_test_types(obj)
    assert "test_structure_validation" in result
    assert "test_dependencies" in result
    
    # INTEGRATION
    obj = Objective(tipos=[ObjectiveType.INTEGRATION])
    result = map_objective_to_test_types(obj)
    assert "test_command_sequence" in result
    assert "test_accumulated_effects" in result
    
    # Múltiplos tipos
    obj = Objective(tipos=[ObjectiveType.CLI_COMMAND, ObjectiveType.FILESYSTEM])
    result = map_objective_to_test_types(obj)
    assert "test_execution" in result
    assert "test_file_creation" in result
    # Remover duplicatas
    assert result.count("test_execution") == 1


def test_generate_test_directory(tmp_path: Path) -> None:
    """Testa criação de diretório de testes."""
    # Mudar diretório de trabalho temporário
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        obj = Objective(id="test-uuid-123")
        test_dir = generate_test_directory(obj)
        assert test_dir.exists()
        assert test_dir.name == "test-uuid-123"
        assert test_dir.parent.name == "objectives"
        assert test_dir.parent.parent.name == "tests"
        
        # Idempotência
        test_dir2 = generate_test_directory(obj)
        assert test_dir2 == test_dir
    finally:
        os.chdir(original_cwd)


def test_generate_test_file() -> None:
    """Testa geração de conteúdo de arquivo de teste."""
    obj = Objective(nome="Teste Objetivo", id="abc123")
    content = generate_test_file(obj, "test_execution")
    assert "Teste gerado automaticamente para objetivo: Teste Objetivo" in content
    assert "def test_test_execution():" in content
    assert "assert False" in content
    assert "# TODO:" in content
    
    # Verificar sintaxe Python
    compile(content, "<string>", "exec")


def test_generate_tests_for_objective(tmp_path: Path) -> None:
    """Testa geração completa de testes para um objetivo."""
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        # Criar estrutura de diretórios necessária
        (tmp_path / "tests").mkdir()
        
        obj = Objective(
            nome="Objeto Teste",
            descricao="Descrição",
            tipos=[ObjectiveType.CLI_COMMAND, ObjectiveType.FILESYSTEM],
            status=ObjectiveStatus.DEFINIDO,
        )
        
        success = generate_tests_for_objective(obj)
        assert success is True
        
        test_dir = tmp_path / "tests" / "objectives" / obj.id
        assert test_dir.exists()
        
        # Verificar arquivos gerados
        expected_files = [
            "test_execution.py",
            "test_exit_code.py",
            "test_output.py",
            "test_file_creation.py",
            "test_structure.py",
            "test_idempotence.py",
        ]
        for fname in expected_files:
            assert (test_dir / fname).exists()
        
        # Verificar __init__.py
        assert (test_dir / "__init__.py").exists()
        
        # Conteúdo dos arquivos
        for fname in expected_files:
            content = (test_dir / fname).read_text(encoding="utf-8")
            assert "def test_" in content
            assert "assert False" in content
    finally:
        os.chdir(original_cwd)


def test_generated_tests_fail_by_default(tmp_path: Path) -> None:
    """Testa que testes gerados falham por padrão."""
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        (tmp_path / "tests").mkdir()
        
        obj = Objective(
            nome="Falha Test",
            tipos=[ObjectiveType.CLI_COMMAND],
        )
        
        success = generate_tests_for_objective(obj)
        assert success is True
        
        test_file = tmp_path / "tests" / "objectives" / obj.id / "test_execution.py"
        # Executar o teste gerado com pytest (deve falhar)
        import subprocess
        result = subprocess.run(
            ["pytest", str(test_file), "-v"],
            capture_output=True,
            text=True,
        )
        # O teste deve falhar (assert False)
        assert result.returncode != 0
        assert "FAILED" in result.stdout or "FAILED" in result.stderr
    finally:
        os.chdir(original_cwd)


# Necessário para os testes
import os
