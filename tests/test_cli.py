"""Testes da CLI."""

from click.testing import CliRunner

from src.cli import main


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
