"""Testes para o módulo de contexto de IA."""

from pathlib import Path

import pytest

from src.database import Database
from src.ia_context import IAContextManager, IAActionType, IAActionLog
from src.models import Objective, ObjectiveType, ObjectiveStatus


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Retorna um caminho temporário para o banco de dados."""
    return tmp_path / "test.db"


@pytest.fixture
def database(temp_db_path: Path) -> Database:
    """Retorna uma instância do Database com banco temporário."""
    return Database(temp_db_path)


@pytest.fixture
def sample_objective(database: Database) -> Objective:
    """Cria e retorna um objetivo de exemplo."""
    obj = Objective(
        nome="Teste IA",
        descricao="Objetivo para testar integração com IA",
        tipos=[ObjectiveType.CLI_COMMAND, ObjectiveType.FILESYSTEM],
        entradas=["input1"],
        saidas_esperadas=["output1"],
        status=ObjectiveStatus.DEFINIDO,
    )
    database.create_objective(obj)
    return obj


def test_ia_context_manager_activation(database: Database, sample_objective: Objective) -> None:
    """Testa ativação de objetivo no gerenciador de contexto."""
    context_mgr = IAContextManager(database)
    
    # Ativar objetivo
    activated = context_mgr.activate_objective(sample_objective.id)
    assert activated is not None
    assert activated.id == sample_objective.id
    assert activated.nome == "Teste IA"
    
    # Verificar que arquivos permitidos foram determinados
    assert len(context_mgr._allowed_files) > 0
    assert "src/cli.py" in context_mgr._allowed_files
    assert "src/validator.py" in context_mgr._allowed_files


def test_context_prompt_generation(database: Database, sample_objective: Objective) -> None:
    """Testa geração de prompt de contexto."""
    context_mgr = IAContextManager(database)
    context_mgr.activate_objective(sample_objective.id)
    
    prompt = context_mgr.get_context_prompt()
    
    assert "REGRAS ABSOLUTAS:" in prompt
    assert "Teste IA" in prompt
    assert "cli-command" in prompt
    assert "filesystem" in prompt
    assert "ARQUIVOS QUE VOCÊ PODE MODIFICAR:" in prompt


def test_ia_action_log(database: Database, sample_objective: Objective) -> None:
    """Testa registro de ações da IA."""
    action_log = IAActionLog(database)
    
    files_changed = [
        {"file": "src/cli.py", "description": "Adicionado novo comando"},
        {"file": "tests/test_cli.py", "description": "Adicionado teste para novo comando"},
    ]
    
    tests_impacted = [
        {"test": "test_new_command", "expected_result": "Deve passar"},
    ]
    
    decisions_made = [
        {"decision": "Usar Click para CLI", "justification": "Framework já estabelecido no projeto"},
    ]
    
    assumptions = [
        "Usuário tem Python 3.13+ instalado",
        "Projeto já está inicializado",
    ]
    
    # Registrar ação
    action_log.log_action(
        objective_id=sample_objective.id,
        action_type=IAActionType.CODE_CHANGE,
        files_changed=files_changed,
        tests_impacted=tests_impacted,
        decisions_made=decisions_made,
        assumptions=assumptions,
        ia_agent="claude-code",
    )
    
    # Recuperar ações
    actions = action_log.get_actions_for_objective(sample_objective.id)
    
    assert len(actions) == 1
    action = actions[0]
    
    assert action["objective_id"] == sample_objective.id
    assert action["action_type"] == "CODE_CHANGE"
    assert len(action["files_changed"]) == 2
    assert action["files_changed"][0]["file"] == "src/cli.py"
    assert len(action["tests_impacted"]) == 1
    assert action["tests_impacted"][0]["test"] == "test_new_command"
    assert len(action["decisions_made"]) == 1
    assert action["decisions_made"][0]["decision"] == "Usar Click para CLI"
    assert len(action["assumptions"]) == 2
    assert "Python 3.13+" in action["assumptions"][0]


def test_action_log_report_generation(database: Database, sample_objective: Objective) -> None:
    """Testa geração de relatório de ações da IA."""
    context_mgr = IAContextManager(database)
    context_mgr.activate_objective(sample_objective.id)
    
    files_changed = [
        {"file": "src/teste.py", "description": "Criado novo módulo"},
    ]
    
    report = context_mgr.generate_action_log_report(
        files_changed=files_changed,
        ia_agent="test-agent",
    )
    
    assert "IA_ACTION_LOG:" in report
    assert "Teste IA" in report
    assert "src/teste.py" in report
    assert "Criado novo módulo" in report
    
    # Verificar que foi registrado no banco
    actions = context_mgr.action_log.get_actions_for_objective(sample_objective.id)
    assert len(actions) == 1


def test_full_context_generation(database: Database, sample_objective: Objective) -> None:
    """Testa geração de contexto completo."""
    context_mgr = IAContextManager(database)
    context_mgr.activate_objective(sample_objective.id)
    
    # Modo default
    default_context = context_mgr.get_full_context("default")
    assert "REGRAS ABSOLUTAS:" in default_context
    assert "IMPLEMENTAÇÃO GUIADA POR TESTES" in default_context
    assert "RESTRIÇÃO DE FILESYSTEM" in default_context
    assert "BLOQUEIO EXPLÍCITO DE FREESTYLE" in default_context
    
    # Modo aider
    aider_context = context_mgr.get_full_context("aider")
    assert "INTEGRAÇÃO ESPECÍFICA: AIDER (CODER)" in aider_context
    
    # Modo claude-code
    claude_context = context_mgr.get_full_context("claude-code")
    assert "INTEGRAÇÃO ESPECÍFICA: CLAUDE CODE (ARQUITETO)" in claude_context


def test_ia_context_without_activation(database: Database) -> None:
    """Testa comportamento sem objetivo ativo."""
    context_mgr = IAContextManager(database)
    
    # Prompt sem objetivo ativo
    prompt = context_mgr.get_context_prompt()
    assert "ERRO: Nenhum objetivo ativo." in prompt
    
    # Full context sem objetivo
    full_context = context_mgr.get_full_context()
    assert "ERRO: Nenhum objetivo ativo." in full_context
