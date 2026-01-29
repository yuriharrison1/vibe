"""Testes para a camada de persistência SQLite."""

import json
from pathlib import Path

import pytest

from src.database import Database
from src.models import Objective, ObjectiveStatus, ObjectiveType


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Retorna um caminho temporário para o banco de dados."""
    return tmp_path / "test.db"


@pytest.fixture
def database(temp_db_path: Path) -> Database:
    """Retorna uma instância do Database com banco temporário."""
    return Database(temp_db_path)


def test_database_creation(temp_db_path: Path) -> None:
    """Testa criação do banco e schema."""
    db = Database(temp_db_path)
    # O schema deve ser criado automaticamente
    assert temp_db_path.exists()
    # Tentar criar um objetivo (deve funcionar)
    obj = Objective(
        nome="Teste",
        descricao="Desc",
        tipos=[ObjectiveType.CLI_COMMAND],
    )
    success = db.create_objective(obj)
    assert success is True


def test_create_objective(database: Database) -> None:
    """Testa inserção de objetivo."""
    obj = Objective(
        nome="Objetivo 1",
        descricao="Descrição 1",
        tipos=[ObjectiveType.FILESYSTEM, ObjectiveType.PROJECT],
        entradas=["ent1"],
        saidas_esperadas=["saida1"],
        efeitos_colaterais=["efeito1"],
        invariantes=["inv1"],
        status=ObjectiveStatus.ATIVO,
    )
    success = database.create_objective(obj)
    assert success is True
    # Recuperar e comparar
    retrieved = database.get_objective(obj.id)
    assert retrieved is not None
    assert retrieved.id == obj.id
    assert retrieved.nome == obj.nome
    assert retrieved.descricao == obj.descricao
    assert retrieved.tipos == obj.tipos
    assert retrieved.entradas == obj.entradas
    assert retrieved.saidas_esperadas == obj.saidas_esperadas
    assert retrieved.efeitos_colaterais == obj.efeitos_colaterais
    assert retrieved.invariantes == obj.invariantes
    assert retrieved.status == obj.status
    # Datetimes devem ser próximos
    assert abs((retrieved.created_at - obj.created_at).total_seconds()) < 1
    assert abs((retrieved.updated_at - obj.updated_at).total_seconds()) < 1


def test_get_objective_not_found(database: Database) -> None:
    """Testa busca por ID inexistente."""
    result = database.get_objective("inexistente")
    assert result is None


def test_list_objectives_empty(database: Database) -> None:
    """Testa listagem quando não há objetivos."""
    objectives = database.list_objectives()
    assert objectives == []


def test_list_objectives_with_data(database: Database) -> None:
    """Testa listagem com múltiplos objetivos."""
    obj1 = Objective(
        nome="Primeiro",
        descricao="Desc 1",
        tipos=[ObjectiveType.CLI_COMMAND],
        status=ObjectiveStatus.DEFINIDO,
    )
    obj2 = Objective(
        nome="Segundo",
        descricao="Desc 2",
        tipos=[ObjectiveType.FILESYSTEM],
        status=ObjectiveStatus.ATIVO,
    )
    database.create_objective(obj1)
    database.create_objective(obj2)

    objectives = database.list_objectives()
    assert len(objectives) == 2
    # Ordenados por created_at DESC (mais recente primeiro)
    assert objectives[0].nome == "Segundo"
    assert objectives[1].nome == "Primeiro"


def test_update_objective(database: Database) -> None:
    """Testa atualização de objetivo."""
    obj = Objective(
        nome="Original",
        descricao="Original desc",
        tipos=[ObjectiveType.CLI_COMMAND],
        status=ObjectiveStatus.DEFINIDO,
    )
    database.create_objective(obj)

    # Modificar
    obj.nome = "Atualizado"
    obj.descricao = "Nova desc"
    obj.tipos = [ObjectiveType.INTEGRATION]
    obj.status = ObjectiveStatus.CONCLUIDO
    success = database.update_objective(obj)
    assert success is True

    # Verificar
    retrieved = database.get_objective(obj.id)
    assert retrieved is not None
    assert retrieved.nome == "Atualizado"
    assert retrieved.descricao == "Nova desc"
    assert retrieved.tipos == [ObjectiveType.INTEGRATION]
    assert retrieved.status == ObjectiveStatus.CONCLUIDO
    # updated_at deve ter sido atualizado
    assert retrieved.updated_at > obj.created_at


def test_delete_objective(database: Database) -> None:
    """Testa remoção de objetivo."""
    obj = Objective(
        nome="Para deletar",
        descricao="Desc",
        tipos=[ObjectiveType.STATE],
    )
    database.create_objective(obj)
    # Verificar que existe
    assert database.get_objective(obj.id) is not None
    # Deletar
    success = database.delete_objective(obj.id)
    assert success is True
    # Verificar que não existe mais
    assert database.get_objective(obj.id) is None


def test_delete_objective_not_found(database: Database) -> None:
    """Testa remoção de ID inexistente (deve retornar True?)."""
    # Comportamento atual: retorna True mesmo se não existir
    success = database.delete_objective("inexistente")
    assert success is True


def test_persistence_across_connections(temp_db_path: Path) -> None:
    """Testa que dados persistem entre conexões."""
    # Primeira conexão
    db1 = Database(temp_db_path)
    obj = Objective(
        nome="Persistente",
        descricao="Teste",
        tipos=[ObjectiveType.PROJECT],
    )
    db1.create_objective(obj)
    # Segunda conexão
    db2 = Database(temp_db_path)
    retrieved = db2.get_objective(obj.id)
    assert retrieved is not None
    assert retrieved.nome == "Persistente"
    assert retrieved.tipos == [ObjectiveType.PROJECT]


def test_json_serialization_integrity(database: Database) -> None:
    """Testa que arrays são serializados/deserializados corretamente."""
    obj = Objective(
        nome="JSON",
        descricao="Test",
        tipos=[ObjectiveType.CLI_COMMAND, ObjectiveType.FILESYSTEM],
        entradas=["a", "b", "c"],
        saidas_esperadas=[],
        efeitos_colaterais=["side"],
        invariantes=["inv1", "inv2"],
    )
    database.create_objective(obj)
    retrieved = database.get_objective(obj.id)
    assert retrieved is not None
    assert retrieved.tipos == obj.tipos
    assert retrieved.entradas == obj.entradas
    assert retrieved.saidas_esperadas == obj.saidas_esperadas
    assert retrieved.efeitos_colaterais == obj.efeitos_colaterais
    assert retrieved.invariantes == obj.invariantes
