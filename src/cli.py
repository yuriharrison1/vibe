"""CLI principal do Vibe."""

from pathlib import Path

import click

from src import __version__
from src.database import Database
from src.models import Objective, ObjectiveStatus, ObjectiveType
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


def _get_database() -> Database:
    """Retorna instância do banco de dados padrão."""
    db_path = Path("state/vibe.db")
    db_path.parent.mkdir(exist_ok=True)
    return Database(db_path)


@objective.command(name="new")
def objective_new() -> None:
    """Cria um novo objetivo."""
    click.echo("📝 Criando novo objetivo")
    click.echo("")

    # Nome
    while True:
        nome = click.prompt("Nome do objetivo", type=str)
        if nome.strip():
            break
        click.echo("❌ Nome não pode ser vazio")

    # Descrição
    while True:
        descricao = click.prompt("Descrição", type=str)
        if descricao.strip():
            break
        click.echo("❌ Descrição não pode ser vazia")

    # Tipos
    click.echo("\nTipos disponíveis:")
    for i, tipo in enumerate(ObjectiveType, start=1):
        click.echo(f"  {i}. {tipo.value}")
    click.echo("  (separar múltiplos por vírgula, ex: 1,3,5)")

    tipos_input = click.prompt("Selecione os tipos", type=str)
    indices = []
    for part in tipos_input.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(ObjectiveType):
                indices.append(idx)
    if not indices:
        click.echo("⚠️  Nenhum tipo selecionado, usando CLI_COMMAND como padrão")
        indices = [0]  # CLI_COMMAND

    tipos = [list(ObjectiveType)[i] for i in indices]

    # Entradas
    entradas_str = click.prompt(
        "Entradas (lista separada por vírgula, opcional)",
        default="",
        show_default=False,
    )
    entradas = [e.strip() for e in entradas_str.split(",") if e.strip()]

    # Saídas esperadas
    saidas_str = click.prompt(
        "Saídas esperadas (lista separada por vírgula, opcional)",
        default="",
        show_default=False,
    )
    saidas_esperadas = [s.strip() for s in saidas_str.split(",") if s.strip()]

    # Efeitos colaterais
    efeitos_str = click.prompt(
        "Efeitos colaterais (lista separada por vírgula, opcional)",
        default="",
        show_default=False,
    )
    efeitos_colaterais = [ef.strip() for ef in efeitos_str.split(",") if ef.strip()]

    # Invariantes
    invariantes_str = click.prompt(
        "Invariantes (lista separada por vírgula, opcional)",
        default="",
        show_default=False,
    )
    invariantes = [inv.strip() for inv in invariantes_str.split(",") if inv.strip()]

    # Criar objeto
    objective = Objective(
        nome=nome,
        descricao=descricao,
        tipos=tipos,
        entradas=entradas,
        saidas_esperadas=saidas_esperadas,
        efeitos_colaterais=efeitos_colaterais,
        invariantes=invariantes,
        status=ObjectiveStatus.DEFINIDO,
    )

    # Validar
    errors = objective.validate()
    if errors:
        click.secho("❌ Erros de validação:", fg="red")
        for err in errors:
            click.echo(f"  - {err}")
        raise click.Abort()

    # Persistir
    db = _get_database()
    success = db.create_objective(objective)
    if not success:
        click.secho("❌ Falha ao persistir objetivo no banco de dados", fg="red")
        raise click.Abort()

    # Confirmação
    click.secho(f"\n✅ Objetivo criado com sucesso!", fg="green")
    click.echo(f"   ID: {objective.id}")
    click.echo(f"   Nome: {objective.nome}")
    click.echo(f"   Status: {objective.status.value}")
    click.echo(f"   Tipos: {', '.join(t.value for t in objective.tipos)}")
    click.echo("\n📋 Testes serão gerados automaticamente (Milestone 2 em andamento).")


@objective.command(name="list")
@click.option("--status", type=click.Choice([s.value for s in ObjectiveStatus]), help="Filtrar por status")
@click.option("--type", "type_filter", type=click.Choice([t.value for t in ObjectiveType]), help="Filtrar por tipo")
@click.option("--verbose", is_flag=True, help="Mostrar detalhes completos")
def objective_list(status: str | None, type_filter: str | None, verbose: bool) -> None:
    """Lista todos os objetivos."""
    db = _get_database()
    objectives = db.list_objectives()

    # Aplicar filtros
    filtered = []
    for obj in objectives:
        if status and obj.status.value != status:
            continue
        if type_filter and not any(t.value == type_filter for t in obj.tipos):
            continue
        filtered.append(obj)

    if not filtered:
        click.echo("📭 Nenhum objetivo encontrado.")
        click.echo("   Use 'vibe objective new' para criar um objetivo.")
        return

    # Cabeçalho
    click.echo(f"📋 Objetivos ({len(filtered)}):")
    click.echo("")

    if verbose:
        # Modo detalhado
        for i, obj in enumerate(filtered, start=1):
            click.echo(f"  {i}. {obj.nome}")
            click.echo(f"     ID: {obj.id}")
            click.echo(f"     Status: {_color_status(obj.status)}")
            click.echo(f"     Tipos: {', '.join(t.value for t in obj.tipos)}")
            click.echo(f"     Criado: {obj.created_at.strftime('%Y-%m-%d %H:%M')}")
            if obj.descricao:
                click.echo(f"     Descrição: {obj.descricao[:80]}{'...' if len(obj.descricao) > 80 else ''}")
            if obj.entradas:
                click.echo(f"     Entradas: {', '.join(obj.entradas)}")
            if obj.saidas_esperadas:
                click.echo(f"     Saídas esperadas: {', '.join(obj.saidas_esperadas)}")
            click.echo("")
    else:
        # Modo tabela compacta
        click.echo("  ID (curto)  Nome                          Status       Tipos")
        click.echo("  ──────────  ────────────────────────────  ───────────  ──────────────")
        for obj in filtered:
            short_id = obj.id[:8]
            nome_trunc = obj.nome[:30] + "..." if len(obj.nome) > 30 else obj.nome.ljust(30)
            status_colored = _color_status(obj.status)
            tipos_str = ", ".join(t.value for t in obj.tipos[:2])
            if len(obj.tipos) > 2:
                tipos_str += f" (+{len(obj.tipos)-2})"
            click.echo(f"  {short_id}  {nome_trunc}  {status_colored}  {tipos_str}")


def _color_status(status: ObjectiveStatus) -> str:
    """Retorna status colorido."""
    colors = {
        ObjectiveStatus.CONCLUIDO: "green",
        ObjectiveStatus.FALHOU: "red",
        ObjectiveStatus.ATIVO: "yellow",
        ObjectiveStatus.BLOQUEADO: "magenta",
        ObjectiveStatus.DEFINIDO: "white",
    }
    color = colors.get(status, "white")
    return click.style(status.value, fg=color)


if __name__ == "__main__":
    main()
