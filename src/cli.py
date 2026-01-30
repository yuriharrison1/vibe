"""CLI principal do Vibe."""

from pathlib import Path
from typing import Optional

import click

from src import __version__
from src.database import Database
from src.models import Objective, ObjectiveStatus, ObjectiveType, TestRun, TestStatus, TestSummary
from src.project import init_project
from src.validator import StructureValidator
from src.test_generator import generate_tests_for_objective, map_objective_to_test_types
from src.test_runner import TestRunner


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


@main.group()
def test() -> None:
    """Gerencia execução de testes."""
    pass


@project.command(name="check")
@click.argument("path", required=False, default=".")
def project_check(path: str) -> None:
    """Valida a estrutura canônica do projeto."""
    project_path = Path(path)
    validator = StructureValidator(project_path)
    errors = validator.validate_canonical_structure()
    
    # Validar integridade dos objetivos
    objective_errors = validator.validate_objectives_integrity()
    errors.extend(objective_errors)
    
    # Validar saúde dos testes
    click.echo("🧪 Validação de Testes")
    click.echo("")
    
    health_problems = validator.check_test_health()
    warnings = []
    critical_errors = []
    
    for problem in health_problems:
        if "marcado como CONCLUIDO" in problem:
            critical_errors.append(problem)
        else:
            warnings.append(problem)
    
    # Exibir status dos objetivos
    db_path = project_path / "state" / "vibe.db"
    if db_path.exists():
        db = Database(db_path)
        objectives = db.list_objectives()
        
        for obj in objectives:
            summary = db.get_test_summary(obj.id)
            if summary:
                if summary.is_passing():
                    click.secho(f"✅ Objetivo {obj.id[:8]}: {summary.passed}/{summary.total_tests} testes passando", fg="green")
                else:
                    rate = summary.success_rate() * 100
                    click.secho(f"⚠️  Objetivo {obj.id[:8]}: {summary.passed}/{summary.total_tests} testes passando ({rate:.1f}%)", fg="yellow")
            else:
                click.secho(f"⏸️  Objetivo {obj.id[:8]}: Testes não executados", fg="white")
    
    click.echo("")

    # Combinar todos os erros
    all_errors = errors + critical_errors
    
    if not all_errors and not warnings:
        click.secho("✓ Estrutura válida!", fg="green")
        click.secho("✓ Todos os objetivos têm testes.", fg="green")
        click.secho("✓ Saúde dos testes OK.", fg="green")
        raise SystemExit(0)
    else:
        if all_errors:
            click.secho("✗ Estrutura inválida!", fg="red")
            click.echo("\nErros encontrados:")
            for error in all_errors:
                click.echo(f"  • {error}")
        
        if warnings:
            click.echo("\nAvisos:")
            for warning in warnings:
                click.secho(f"  • {warning}", fg="yellow")
        
        if critical_errors:
            click.echo(f"\nResultado: ❌ FALHOU (Problemas críticos: {len(critical_errors)})")
        elif all_errors:
            click.echo(f"\nResultado: ❌ FALHOU (Problemas: {len(all_errors)})")
        else:
            click.echo(f"\nResultado: ⚠️  AVISOS ({len(warnings)} avisos)")
        
        if critical_errors or all_errors:
            raise SystemExit(1)
        else:
            # Apenas warnings, não falha
            raise SystemExit(0)


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

    # Gerar testes automaticamente
    click.echo("\n📋 Gerando testes automaticamente...")
    test_generated = generate_tests_for_objective(objective)
    
    if not test_generated:
        # Rollback: remover objetivo do banco
        db.delete_objective(objective.id)
        click.secho("❌ Falha ao gerar testes. Objetivo não foi criado.", fg="red")
        click.echo("   Execute 'vibe objective generate-tests' manualmente após corrigir o problema.")
        raise click.Abort()
    
    # Obter tipos de teste gerados
    test_types = map_objective_to_test_types(objective)
    
    # Confirmação
    click.secho(f"\n✅ Objetivo criado com sucesso!", fg="green")
    click.echo(f"   ID: {objective.id}")
    click.echo(f"   Nome: {objective.nome}")
    click.echo(f"   Status: {objective.status.value}")
    click.echo(f"   Tipos: {', '.join(t.value for t in objective.tipos)}")
    click.echo("\n📋 Testes gerados automaticamente:")
    for tt in test_types:
        click.echo(f"   - {tt}")
    click.echo(f"   Localização: tests/objectives/{objective.id}/")
    click.echo("\n⚠️  Testes estão marcados como TODO e falham por padrão.")
    click.echo("   Implemente-os antes de marcar o objetivo como concluído.")


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


@test.command(name="run")
@click.argument("objective_id", required=False)
@click.option("--all", is_flag=True, help="Executar testes de todos os objetivos")
@click.option("--verbose", "-v", is_flag=True, help="Mostrar output detalhado")
def test_run(objective_id: Optional[str], all: bool, verbose: bool) -> None:
    """Executa testes de um objetivo específico ou todos."""
    # Validações
    if not objective_id and not all:
        click.secho("❌ É necessário fornecer um ID de objetivo ou usar --all", fg="red")
        click.echo("   Exemplo: vibe test run <ID>")
        click.echo("   Exemplo: vibe test run --all")
        raise SystemExit(1)
    
    if objective_id and all:
        click.secho("❌ Use apenas um: ID de objetivo OU --all, não ambos", fg="red")
        raise SystemExit(1)
    
    db = _get_database()
    runner = TestRunner(db)
    
    if objective_id:
        # Verificar se objetivo existe
        objective = db.get_objective(objective_id)
        if not objective:
            click.secho(f"❌ Objetivo '{objective_id}' não encontrado", fg="red")
            raise SystemExit(1)
        
        # Verificar se tem testes
        test_dir = Path("tests") / "objectives" / objective_id
        if not test_dir.exists():
            click.secho(f"⚠️  Objetivo '{objective.nome}' não tem diretório de testes", fg="yellow")
            click.echo(f"   Execute: vibe objective generate-tests {objective_id}")
            raise SystemExit(1)
        
        click.echo(f"🧪 Executando testes para objetivo: {objective.nome}")
        click.echo("")
        
        summary = runner.run_objective_tests(objective_id)
        if not summary:
            click.secho("❌ Falha ao executar testes", fg="red")
            raise SystemExit(2)
        
        # Exibir resultados
        _display_test_results(summary, verbose)
        
        # Exit code baseado no resultado
        if summary.is_passing():
            raise SystemExit(0)
        else:
            raise SystemExit(1)
    
    else:  # --all
        click.echo("🧪 Executando testes para todos os objetivos")
        click.echo("")
        
        summaries = runner.run_all_tests()
        
        if not summaries:
            click.echo("📭 Nenhum objetivo com testes encontrado")
            raise SystemExit(0)
        
        # Exibir resumo geral
        total_passed = 0
        total_failed = 0
        total_tests = 0
        
        for obj_id, summary in summaries.items():
            objective = db.get_objective(obj_id)
            if not objective:
                continue
            
            status = "✅" if summary.is_passing() else "❌"
            click.echo(f"  {status} {objective.nome}: {summary.passed}/{summary.total_tests} testes passando")
            
            total_passed += summary.passed
            total_failed += summary.failed + summary.error
            total_tests += summary.total_tests
        
        click.echo("")
        click.echo("📊 Resumo geral:")
        click.echo(f"   Total de objetivos: {len(summaries)}")
        click.echo(f"   Total de testes: {total_tests}")
        click.echo(f"   ✅ Passou: {total_passed}")
        click.echo(f"   ❌ Falhou: {total_failed}")
        
        if total_failed == 0:
            click.secho("🎉 Todos os testes passaram!", fg="green")
            raise SystemExit(0)
        else:
            click.secho(f"⚠️  {total_failed} teste(s) falharam", fg="red")
            raise SystemExit(1)


def _display_test_results(summary: TestSummary, verbose: bool) -> None:
    """Exibe resultados de testes de forma formatada."""
    db = _get_database()
    test_runs = db.get_test_runs(summary.objective_id)
    
    if not test_runs:
        click.echo("📭 Nenhum teste executado")
        return
    
    # Agrupar por arquivo
    by_file = {}
    for run in test_runs:
        if run.test_file not in by_file:
            by_file[run.test_file] = []
        by_file[run.test_file].append(run)
    
    for test_file, runs in by_file.items():
        click.echo(f"  📄 {test_file}")
        for run in runs:
            if run.status == TestStatus.PASSED:
                icon = "✅"
                color = "green"
            elif run.status == TestStatus.FAILED:
                icon = "❌"
                color = "red"
            elif run.status == TestStatus.SKIPPED:
                icon = "⏭️"
                color = "yellow"
            else:  # ERROR
                icon = "⚠️"
                color = "red"
            
            status_text = click.style(f"{run.status.value}", fg=color)
            click.echo(f"    {icon} {run.test_name} ... {status_text} ({run.duration:.2f}s)")
            
            if verbose and run.status in [TestStatus.FAILED, TestStatus.ERROR] and run.error_message:
                # Mostrar detalhes do erro no modo verbose
                click.echo("      " + "-" * 40)
                for line in run.error_message.split('\n'):
                    if line.strip():
                        click.echo(f"      {line}")
                click.echo("      " + "-" * 40)
    
    click.echo("")
    click.echo("📊 Resultado:")
    click.echo(f"   Total: {summary.total_tests}")
    click.echo(f"   ✅ Passou: {summary.passed}")
    click.echo(f"   ❌ Falhou: {summary.failed}")
    click.echo(f"   ⏭️  Pulado: {summary.skipped}")
    click.echo(f"   ⚠️  Erro: {summary.error}")
    
    success_rate = summary.success_rate() * 100
    if success_rate == 100:
        click.secho(f"   Taxa de sucesso: {success_rate:.1f}% 🎉", fg="green")
    elif success_rate >= 80:
        click.secho(f"   Taxa de sucesso: {success_rate:.1f}%", fg="yellow")
    else:
        click.secho(f"   Taxa de sucesso: {success_rate:.1f}%", fg="red")
    
    if summary.is_passing():
        click.secho("   Estado: ✅ APROVADO", fg="green")
    else:
        click.secho("   Estado: ❌ FALHOU", fg="red")


@objective.command(name="status")
@click.argument("objective_id", required=False)
@click.option("--all", is_flag=True, help="Status de todos os objetivos")
@click.option("--verbose", "-v", is_flag=True, help="Mostrar detalhes dos testes")
def objective_status(objective_id: Optional[str], all: bool, verbose: bool) -> None:
    """Exibe status de testes de um ou todos os objetivos."""
    # Validações
    if not objective_id and not all:
        click.secho("❌ É necessário fornecer um ID de objetivo ou usar --all", fg="red")
        click.echo("   Exemplo: vibe objective status <ID>")
        click.echo("   Exemplo: vibe objective status --all")
        raise SystemExit(1)
    
    if objective_id and all:
        click.secho("❌ Use apenas um: ID de objetivo OU --all, não ambos", fg="red")
        raise SystemExit(1)
    
    db = _get_database()
    
    if objective_id:
        # Status de um objetivo específico
        objective = db.get_objective(objective_id)
        if not objective:
            click.secho(f"❌ Objetivo '{objective_id}' não encontrado", fg="red")
            raise SystemExit(1)
        
        summary = db.get_test_summary(objective_id)
        
        click.echo(f"📋 Objetivo: {objective.nome}")
        click.echo(f"   ID: {objective.id}")
        click.echo(f"   Status: {_color_status(objective.status)}")
        click.echo(f"   Tipo(s): {', '.join(t.value for t in objective.tipos)}")
        click.echo("")
        
        if not summary:
            click.echo("🧪 Testes: ⏸️  Testes não executados")
            return
        
        # Calcular tempo desde a última execução
        from datetime import datetime
        now = datetime.now()
        last_run = summary.last_run
        delta = now - last_run
        hours = delta.total_seconds() / 3600
        
        if hours < 1:
            time_ago = f"{int(delta.total_seconds() / 60)} minutos atrás"
        elif hours < 24:
            time_ago = f"{int(hours)} horas atrás"
        else:
            time_ago = f"{int(hours / 24)} dias atrás"
        
        click.echo("🧪 Testes:")
        click.echo(f"   Última execução: {last_run.strftime('%Y-%m-%d %H:%M')} ({time_ago})")
        click.echo(f"   Total: {summary.total_tests}")
        click.echo(f"   ✅ Passou: {summary.passed}")
        click.echo(f"   ❌ Falhou: {summary.failed}")
        click.echo(f"   ⏭️  Pulado: {summary.skipped}")
        click.echo(f"   ⚠️  Erro: {summary.error}")
        
        success_rate = summary.success_rate() * 100
        click.echo(f"   Taxa de sucesso: {success_rate:.1f}%")
        click.echo("")
        
        if summary.is_passing():
            click.secho("   Estado: ✅ APROVADO", fg="green")
        else:
            click.secho("   Estado: ❌ FALHOU", fg="red")
        
        if verbose:
            click.echo("")
            click.echo("📄 Testes individuais:")
            test_runs = db.get_test_runs(objective_id)
            for run in test_runs[:10]:  # Limitar a 10 para não poluir
                if run.status == TestStatus.PASSED:
                    icon = "✅"
                elif run.status == TestStatus.FAILED:
                    icon = "❌"
                elif run.status == TestStatus.SKIPPED:
                    icon = "⏭️"
                else:
                    icon = "⚠️"
                click.echo(f"   {icon} {run.test_file}::{run.test_name} ({run.duration:.2f}s)")
    
    else:  # --all
        objectives = db.list_objectives()
        if not objectives:
            click.echo("📭 Nenhum objetivo encontrado")
            return
        
        click.echo("📋 Status de todos os objetivos:")
        click.echo("")
        
        for obj in objectives:
            summary = db.get_test_summary(obj.id)
            
            if not summary:
                status_str = "⏸️  Não executado"
                color = "white"
            elif summary.is_passing():
                status_str = f"✅ {summary.passed}/{summary.total_tests}"
                color = "green"
            else:
                status_str = f"❌ {summary.passed}/{summary.total_tests}"
                color = "red"
            
            # Formatar nome truncado
            nome_trunc = obj.nome[:25] + "..." if len(obj.nome) > 25 else obj.nome.ljust(28)
            
            # Tempo desde última execução
            time_info = ""
            if summary:
                from datetime import datetime
                now = datetime.now()
                delta = now - summary.last_run
                hours = delta.total_seconds() / 3600
                if hours < 1:
                    time_info = f"{int(delta.total_seconds() / 60)}min"
                elif hours < 24:
                    time_info = f"{int(hours)}h"
                else:
                    time_info = f"{int(hours / 24)}d"
                time_info = f" | {time_info} atrás"
            
            click.echo(f"  {obj.id[:8]} | {nome_trunc} | {click.style(status_str, fg=color)}{time_info}")


if __name__ == "__main__":
    main()
