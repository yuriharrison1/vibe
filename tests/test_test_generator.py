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
    obj = Objective(id="test-uuid-123")
    test_dir = generate_test_directory(obj, base_path=tmp_path)
    assert test_dir.exists()
    assert test_dir.name == "test-uuid-123"
    assert test_dir.parent.name == "objectives"
    assert test_dir.parent.parent == tmp_path
    
    # Idempotência
    test_dir2 = generate_test_directory(obj, base_path=tmp_path)
    assert test_dir2 == test_dir


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
    obj = Objective(
        nome="Objeto Teste",
        descricao="Descrição",
        tipos=[ObjectiveType.CLI_COMMAND, ObjectiveType.FILESYSTEM],
        status=ObjectiveStatus.DEFINIDO,
    )
    
    success = generate_tests_for_objective(obj, base_path=tmp_path)
    assert success is True
    
    test_dir = tmp_path / "objectives" / obj.id
    assert test_dir.exists()
    
    # Verificar arquivos gerados
    # O gerador cria arquivos com prefixo "test_" + test_type
    # map_objective_to_test_types retorna ["test_execution", "test_exit_code", ...]
    # Então test_type = "test_execution", e o arquivo será "test_test_execution.py"
    # Vamos verificar os arquivos reais
    actual_files = [f.name for f in test_dir.iterdir() if f.is_file() and f.name.endswith('.py')]
    print(f"Arquivos gerados: {actual_files}")
    
    # Esperamos 6 arquivos (CLI_COMMAND + FILESYSTEM)
    assert len(actual_files) == 6
    
    # Verificar se contém os tipos esperados
    expected_suffixes = [
        "test_execution",
        "test_exit_code", 
        "test_output",
        "test_file_creation",
        "test_structure",
        "test_idempotence",
    ]
    for suffix in expected_suffixes:
        # O arquivo deve ser test_{suffix}.py
        expected_file = f"test_{suffix}.py"
        assert any(f == expected_file for f in actual_files), f"Arquivo {expected_file} não encontrado"
    
    # Verificar __init__.py
    assert (test_dir / "__init__.py").exists()
    
    # Conteúdo dos arquivos
    for fname in expected_files:
        content = (test_dir / fname).read_text(encoding="utf-8")
        assert "def test_" in content
        assert "assert False" in content


def test_generated_tests_fail_by_default(tmp_path: Path) -> None:
    """Testa que testes gerados falham por padrão."""
    obj = Objective(
        nome="Falha Test",
        tipos=[ObjectiveType.CLI_COMMAND],
    )
    
    success = generate_tests_for_objective(obj, base_path=tmp_path)
    assert success is True
    
    test_file = tmp_path / "objectives" / obj.id / "test_execution.py"
    # Executar o teste gerado com pytest (deve falhar)
    import subprocess
    result = subprocess.run(
        ["pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
    )
    # O teste deve falhar (assert False)
    assert result.returncode != 0
    # Verificar se o teste falhou (pode ser FAILED ou ERROR)
    output = result.stdout + result.stderr
    assert "FAILED" in output or "ERROR" in output or "assert False" in output


# Necessário para os testes
import os
