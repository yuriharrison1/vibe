"""Testes da CLI."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import main
from src.database import Database
from src.models import ObjectiveStatus, ObjectiveType


def test_cli_executes_without_errors() -> None:
    """CLI executa sem erros."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0


def test_cli_help_shows_description() -> None:
    """--help exibe descrição correta."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "Plataforma de Orquestração para Vibe Coding" in result.output


def test_cli_version_shows_version() -> None:
    """--version exibe versão correta."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert "0.1.0" in result.output


def test_project_subcommand_exists() -> None:
    """Subcomando project existe."""
    runner = CliRunner()
    result = runner.invoke(main, ["project", "--help"])
    assert result.exit_code == 0
    assert "Gerenciamento de projeto" in result.output


def test_objective_subcommand_exists() -> None:
    """Subcomando objective existe."""
    runner = CliRunner()
    result = runner.invoke(main, ["objective", "--help"])
    assert result.exit_code == 0
    assert "Gerenciamento de objetivos" in result.output


# Fixtures para testes de objetivos
@pytest.fixture
def runner() -> CliRunner:
    """Retorna um CliRunner para testes."""
    return CliRunner()


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Retorna um caminho temporário para o banco de dados."""
    return tmp_path / "vibe.db"


@pytest.fixture
def setup_temp_db(temp_db_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Configura o banco de dados temporário e monkeypatch."""
    # Monkeypatch para usar o banco temporário
    original_get_database = None
    try:
        from src import cli
        original_get_database = cli._get_database
    except ImportError:
        pass

    def _temp_get_database():
        db_path = temp_db_path
        db_path.parent.mkdir(exist_ok=True)
        return Database(db_path)

    monkeypatch.setattr("src.cli._get_database", _temp_get_database)
    yield
    # Restaurar
    if original_get_database:
        monkeypatch.setattr("src.cli._get_database", original_get_database)


def test_objective_new_interactive(runner: CliRunner, setup_temp_db, temp_db_path: Path) -> None:
    """Testa criação interativa de objetivo."""
    input_data = (
        "Teste Objetivo\n"  # Nome
        "Descrição do objetivo\n"  # Descrição
        "1\n"  # Tipos: CLI_COMMAND (único)
        "\n"  # Entradas (vazio)
        "\n"  # Saídas esperadas (vazio)
        "\n"  # Efeitos colaterais (vazio)
        "\n"  # Invariantes (vazio)
    )
    result = runner.invoke(main, ["objective", "new"], input=input_data)
    assert result.exit_code == 0
    assert "✅ Objetivo criado com sucesso!" in result.output
    assert "ID:" in result.output
    assert "Teste Objetivo" in result.output
    assert "DEFINIDO" in result.output

    # Verificar se foi persistido
    db = Database(temp_db_path)
    objectives = db.list_objectives()
    assert len(objectives) == 1
    obj = objectives[0]
    assert obj.nome == "Teste Objetivo"
    assert obj.descricao == "Descrição do objetivo"
    assert obj.tipos == [ObjectiveType.CLI_COMMAND]
    assert obj.status == ObjectiveStatus.DEFINIDO


def test_objective_new_validation(runner: CliRunner, setup_temp_db) -> None:
    """Testa validação de campos obrigatórios."""
    # Nome vazio
    input_data = (
        "\n"  # Nome vazio (será rejeitado)
        "Nome válido\n"  # Segundo prompt
        "Descrição\n"
        "1\n"
        "\n" * 4
    )
    result = runner.invoke(main, ["objective", "new"], input=input_data)
    assert result.exit_code == 0  # O comando não aborta, mas pede novamente
    assert "❌ Nome não pode ser vazio" in result.output

    # Descrição vazia
    input_data = (
        "Nome\n"
        "\n"  # Descrição vazia (será rejeitado)
        "Descrição válida\n"
        "1\n"
        "\n" * 4
    )
    result = runner.invoke(main, ["objective", "new"], input=input_data)
    assert result.exit_code == 0
    assert "❌ Descrição não pode ser vazia" in result.output


def test_objective_list_empty(runner: CliRunner, setup_temp_db) -> None:
    """Testa listagem quando não há objetivos."""
    result = runner.invoke(main, ["objective", "list"])
    assert result.exit_code == 0
    assert "📭 Nenhum objetivo encontrado." in result.output
    assert "Use 'vibe objective new' para criar um objetivo." in result.output


def test_objective_list_with_data(runner: CliRunner, setup_temp_db, temp_db_path: Path) -> None:
    """Testa listagem com objetivos existentes."""
    # Criar objetivo diretamente no banco
    db = Database(temp_db_path)
    from src.models import Objective
    obj = Objective(
        nome="Objetivo de Teste",
        descricao="Descrição",
        tipos=[ObjectiveType.FILESYSTEM],
        status=ObjectiveStatus.ATIVO,
    )
    db.create_objective(obj)

    result = runner.invoke(main, ["objective", "list"])
    assert result.exit_code == 0
    assert "📋 Objetivos (1):" in result.output
    assert "Objetivo de Teste" in result.output
    assert "ATIVO" in result.output
    assert "filesystem" in result.output


def test_objective_list_filters(runner: CliRunner, setup_temp_db, temp_db_path: Path) -> None:
    """Testa filtros --status e --type."""
    db = Database(temp_db_path)
    from src.models import Objective
    # Objetivo 1: DEFINIDO, CLI_COMMAND
    obj1 = Objective(
        nome="Obj1",
        descricao="Desc1",
        tipos=[ObjectiveType.CLI_COMMAND],
        status=ObjectiveStatus.DEFINIDO,
    )
    # Objetivo 2: ATIVO, FILESYSTEM
    obj2 = Objective(
        nome="Obj2",
        descricao="Desc2",
        tipos=[ObjectiveType.FILESYSTEM],
        status=ObjectiveStatus.ATIVO,
    )
    db.create_objective(obj1)
    db.create_objective(obj2)

    # Filtrar por status DEFINIDO
    result = runner.invoke(main, ["objective", "list", "--status", "DEFINIDO"])
    assert result.exit_code == 0
    assert "Obj1" in result.output
    assert "Obj2" not in result.output

    # Filtrar por tipo filesystem
    result = runner.invoke(main, ["objective", "list", "--type", "filesystem"])
    assert result.exit_code == 0
    assert "Obj2" in result.output
    assert "Obj1" not in result.output

    # Filtrar por status ATIVO e tipo filesystem (deve retornar Obj2)
    result = runner.invoke(main, ["objective", "list", "--status", "ATIVO", "--type", "filesystem"])
    assert result.exit_code == 0
    assert "Obj2" in result.output
    assert "Obj1" not in result.output

    # Filtrar por status DEFINIDO e tipo filesystem (nenhum)
    result = runner.invoke(main, ["objective", "list", "--status", "DEFINIDO", "--type", "filesystem"])
    assert result.exit_code == 0
    assert "📭 Nenhum objetivo encontrado." in result.output


def test_objective_list_verbose(runner: CliRunner, setup_temp_db, temp_db_path: Path) -> None:
    """Testa modo verbose."""
    db = Database(temp_db_path)
    from src.models import Objective
    obj = Objective(
        nome="Verbose Obj",
        descricao="Uma descrição longa para testar truncamento",
        tipos=[ObjectiveType.CLI_COMMAND, ObjectiveType.PROJECT],
        entradas=["entrada1"],
        saidas_esperadas=["saida1"],
        status=ObjectiveStatus.CONCLUIDO,
    )
    db.create_objective(obj)

    result = runner.invoke(main, ["objective", "list", "--verbose"])
    assert result.exit_code == 0
    assert "Verbose Obj" in result.output
    assert "ID:" in result.output
    assert "CONCLUIDO" in result.output
    assert "cli-command" in result.output
    assert "project" in result.output
    assert "Criado:" in result.output
    assert "Descrição:" in result.output
    assert "Entradas:" in result.output
    assert "Saídas esperadas:" in result.output
