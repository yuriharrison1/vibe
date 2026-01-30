"""Testes para o test_runner."""

from pathlib import Path
from datetime import datetime

import pytest

from src.database import Database
from src.models import Objective, ObjectiveType, TestStatus, TestSummary
from src.test_generator import generate_tests_for_objective
from src.test_runner import TestRunner


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Retorna um caminho temporário para o banco de dados."""
    return tmp_path / "test.db"


@pytest.fixture
def database(temp_db_path: Path) -> Database:
    """Retorna uma instância do Database com banco temporário."""
    return Database(temp_db_path)


@pytest.fixture
def test_runner(database: Database) -> TestRunner:
    """Retorna uma instância do TestRunner."""
    return TestRunner(database)


def test_run_objective_tests(test_runner: TestRunner, database: Database, tmp_path: Path) -> None:
    """Testa execução de testes para um objetivo."""
    # Criar objetivo
    obj = Objective(
        nome="Test Runner Obj",
        descricao="For test runner",
        tipos=[ObjectiveType.CLI_COMMAND],
    )
    database.create_objective(obj)
    
    # Gerar testes em um diretório temporário
    test_dir = tmp_path / "tests" / "objectives" / obj.id
    test_dir.mkdir(parents=True)
    
    # Criar um arquivo de teste simples
    test_file = test_dir / "test_simple.py"
    test_file.write_text("""
def test_example():
    \"\"\"Teste exemplo.\"\"\"
    assert True

def test_another():
    \"\"\"Outro teste.\"\"\"
    assert 1 + 1 == 2
""")
    
    # Executar testes
    summary = test_runner.run_objective_tests(obj.id)
    
    # Verificar resultados
    assert summary is not None
    assert summary.objective_id == obj.id
    assert summary.total_tests == 2
    assert summary.passed == 2
    assert summary.failed == 0
    assert summary.error == 0


def test_run_objective_tests_with_failure(test_runner: TestRunner, database: Database, tmp_path: Path) -> None:
    """Testa execução de testes com falha."""
    obj = Objective(
        nome="Failing Test Obj",
        descricao="Has failing tests",
        tipos=[ObjectiveType.CLI_COMMAND],
    )
    database.create_objective(obj)
    
    # Criar diretório de testes
    test_dir = tmp_path / "tests" / "objectives" / obj.id
    test_dir.mkdir(parents=True)
    
    # Criar arquivo de teste com falha
    test_file = test_dir / "test_fail.py"
    test_file.write_text("""
def test_pass():
    assert True

def test_fail():
    assert False, "Falha intencional"
""")
    
    summary = test_runner.run_objective_tests(obj.id)
    
    assert summary is not None
    assert summary.total_tests == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert not summary.is_passing()


def test_test_results_persisted(test_runner: TestRunner, database: Database, tmp_path: Path) -> None:
    """Testa que resultados são persistidos no banco."""
    obj = Objective(
        nome="Persistence Test",
        descricao="Test persistence",
        tipos=[ObjectiveType.CLI_COMMAND],
    )
    database.create_objective(obj)
    
    test_dir = tmp_path / "tests" / "objectives" / obj.id
    test_dir.mkdir(parents=True)
    
    test_file = test_dir / "test_persist.py"
    test_file.write_text("""
def test_one():
    assert True
""")
    
    summary = test_runner.run_objective_tests(obj.id)
    
    # Verificar se summary foi salvo
    retrieved = database.get_test_summary(obj.id)
    assert retrieved is not None
    assert retrieved.total_tests == summary.total_tests
    assert retrieved.passed == summary.passed
    
    # Verificar se test runs foram salvos
    runs = database.get_test_runs(obj.id)
    assert len(runs) == 1
    assert runs[0].test_name == "test_one"


def test_summary_calculation() -> None:
    """Testa cálculos do TestSummary."""
    summary = TestSummary(
        objective_id="test",
        total_tests=10,
        passed=8,
        failed=1,
        skipped=1,
        error=0,
        last_run=datetime.now(),
    )
    
    assert summary.success_rate() == 0.9  # (8+1)/10
    assert not summary.is_passing()  # failed=1
    
    summary.failed = 0
    assert summary.is_passing()
