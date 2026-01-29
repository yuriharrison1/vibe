"""CLI principal do Vibe."""

from pathlib import Path

import click

from src import __version__
from src.project import init_project
from src.validator import StructureValidator


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Plataforma de Orquestração para Vibe Coding.

    Sistema de orquestração que organiza, governa e valida projetos
    feitos com vibe coding, garantindo previsibilidade, rastreabilidade
    e qualidade automática.
    """
    pass


@main.group()
def project() -> None:
    """Gerenciamento de projeto."""
    pass


@main.group()
def objective() -> None:
    """Gerenciamento de objetivos."""
    pass


@project.command(name="check")
@click.argument("path", required=False, default=".")
def project_check(path: str) -> None:
    """Valida a estrutura canônica do projeto."""
    project_path = Path(path)
    validator = StructureValidator(project_path)
    errors = validator.validate_canonical_structure()

    if not errors:
        click.secho("✓ Estrutura válida!", fg="green")
        raise SystemExit(0)
    else:
        click.secho("✗ Estrutura inválida!", fg="red")
        click.echo("\nErros encontrados:")
        for error in errors:
            click.echo(f"  • {error}")
        raise SystemExit(1)


@project.command(name="init")
@click.argument("path", required=False, default=".")
@click.option("--force", is_flag=True, help="Sobrescrever estrutura existente")
def project_init(path: str, force: bool) -> None:
    """Inicializa a estrutura canônica do projeto."""
    project_path = Path(path)

    if not force and project_path.exists():
        # Verificar se já é um projeto válido
        validator = StructureValidator(project_path)
        errors = validator.validate_canonical_structure()
        if len(errors) == 0:
            click.secho("✓ Projeto já existe e está válido!", fg="yellow")
            return

    success = init_project(project_path, force)

    if success:
        click.secho(f"✓ Projeto inicializado em: {project_path.absolute()}", fg="green")
        click.echo("\nEstrutura criada:")
        click.echo("  ├─ docs/")
        click.echo("  ├─ objectives/")
        click.echo("  ├─ tests/")
        click.echo("  ├─ scripts/")
        click.echo("  ├─ ai/")
        click.echo("  ├─ state/")
        click.echo("  └─ src/")
        click.echo("\nPróximo passo: edite os arquivos de documentação (scope.md, etc.)")
    else:
        click.secho("✗ Falha ao inicializar projeto", fg="red")
        raise SystemExit(1)


@objective.command(name="new")
def objective_new() -> None:
    """Cria um novo objetivo."""
    click.echo("🚧 Em desenvolvimento")


@objective.command(name="list")
def objective_list() -> None:
    """Lista todos os objetivos."""
    click.echo("🚧 Em desenvolvimento")


if __name__ == "__main__":
    main()
