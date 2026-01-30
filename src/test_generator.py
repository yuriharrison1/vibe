"""Gerador automático de testes para objetivos."""

import json
from pathlib import Path
from typing import List

from src.models import Objective, ObjectiveType


def map_objective_to_test_types(objective: Objective) -> List[str]:
    """Mapeia tipos de objetivo para tipos de teste.

    Args:
        objective: Objetivo a ser mapeado.

    Returns:
        Lista de tipos de teste correspondentes.
    """
    test_types = []
    for tipo in objective.tipos:
        if tipo == ObjectiveType.CLI_COMMAND:
            test_types.extend(["test_execution", "test_exit_code", "test_output"])
        elif tipo == ObjectiveType.FILESYSTEM:
            test_types.extend(["test_file_creation", "test_structure", "test_idempotence"])
        elif tipo == ObjectiveType.STATE:
            test_types.extend(["test_database_creation", "test_schema", "test_initial_state"])
        elif tipo == ObjectiveType.PROJECT:
            test_types.extend(["test_structure_validation", "test_dependencies"])
        elif tipo == ObjectiveType.INTEGRATION:
            test_types.extend(["test_command_sequence", "test_accumulated_effects"])
    # Remover duplicatas mantendo ordem
    unique_types = []
    for t in test_types:
        if t not in unique_types:
            unique_types.append(t)
    return unique_types


def generate_test_directory(objective: Objective) -> Path:
    """Cria diretório de testes para o objetivo.

    Args:
        objective: Objetivo para o qual gerar testes.

    Returns:
        Caminho do diretório criado.
    """
    base_dir = Path("tests") / "objectives"
    objective_dir = base_dir / objective.id
    objective_dir.mkdir(parents=True, exist_ok=True)
    return objective_dir


def generate_test_file(objective: Objective, test_type: str) -> str:
    """Gera conteúdo do arquivo de teste.

    Args:
        objective: Objetivo sendo testado.
        test_type: Tipo de teste a ser gerado.

    Returns:
        Conteúdo do arquivo de teste Python.
    """
    # Mapear tipo de teste para descrição
    descriptions = {
        "test_execution": "Testa execução básica do comando CLI",
        "test_exit_code": "Testa códigos de saída do comando",
        "test_output": "Testa saída padrão e de erro",
        "test_file_creation": "Testa criação de arquivos e diretórios",
        "test_structure": "Testa estrutura de diretórios",
        "test_idempotence": "Testa idempotência de operações",
        "test_database_creation": "Testa criação do banco de dados",
        "test_schema": "Testa schema do banco de dados",
        "test_initial_state": "Testa estado inicial do banco",
        "test_structure_validation": "Testa validação de estrutura do projeto",
        "test_dependencies": "Testa dependências do projeto",
        "test_command_sequence": "Testa sequência de comandos",
        "test_accumulated_effects": "Testa efeitos acumulados de operações",
    }
    
    description = descriptions.get(test_type, f"Teste para {test_type}")
    
    # Nome do arquivo
    test_name = test_type.replace("_", " ").title().replace(" ", "")
    
    content = f'''"""Teste gerado automaticamente para objetivo: {objective.nome}"""

import pytest

# TODO: Implementar teste para {description}
# Objetivo ID: {objective.id}
# Tipo de teste: {test_type}


def test_{test_type}():
    """{description}"""
    # TODO: Implementar teste
    # Este teste falha intencionalmente até ser implementado
    assert False, "Teste gerado automaticamente - precisa ser implementado"
'''
    return content


def generate_tests_for_objective(objective: Objective) -> bool:
    """Gera todos os testes para um objetivo.

    Args:
        objective: Objetivo para o qual gerar testes.

    Returns:
        True se todos os testes foram gerados com sucesso, False caso contrário.
    """
    try:
        # Obter tipos de teste
        test_types = map_objective_to_test_types(objective)
        if not test_types:
            return False
        
        # Criar diretório
        test_dir = generate_test_directory(objective)
        
        # Gerar arquivos de teste
        for test_type in test_types:
            content = generate_test_file(objective, test_type)
            test_file = test_dir / f"test_{test_type}.py"
            test_file.write_text(content, encoding="utf-8")
        
        # Criar arquivo __init__.py no diretório
        init_file = test_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Pacote de testes gerados automaticamente\n")
        
        return True
    except Exception as e:
        print(f"Erro ao gerar testes: {e}")
        return False
