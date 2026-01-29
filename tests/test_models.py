"""Testes para os modelos de dados."""

import json
from datetime import datetime

import pytest

from src.models import Objective, ObjectiveStatus, ObjectiveType


def test_objective_creation() -> None:
    """Testa criação básica de um objetivo."""
    obj = Objective(
        nome="Teste",
        descricao="Descrição de teste",
        tipos=[ObjectiveType.CLI_COMMAND],
        entradas=["input1"],
        saidas_esperadas=["output1"],
        efeitos_colaterais=["side1"],
        invariantes=["inv1"],
        status=ObjectiveStatus.DEFINIDO,
    )
    assert obj.nome == "Teste"
    assert obj.descricao == "Descrição de teste"
    assert obj.tipos == [ObjectiveType.CLI_COMMAND]
    assert obj.entradas == ["input1"]
    assert obj.saidas_esperadas == ["output1"]
    assert obj.efeitos_colaterais == ["side1"]
    assert obj.invariantes == ["inv1"]
    assert obj.status == ObjectiveStatus.DEFINIDO
    assert isinstance(obj.id, str)
    assert len(obj.id) == 36  # UUID
    assert isinstance(obj.created_at, datetime)
    assert isinstance(obj.updated_at, datetime)


def test_objective_defaults() -> None:
    """Testa valores padrão."""
    obj = Objective()
    assert obj.nome == ""
    assert obj.descricao == ""
    assert obj.tipos == []
    assert obj.entradas == []
    assert obj.saidas_esperadas == []
    assert obj.efeitos_colaterais == []
    assert obj.invariantes == []
    assert obj.status == ObjectiveStatus.DEFINIDO
    assert obj.id is not None
    assert obj.created_at is not None
    assert obj.updated_at is not None


def test_objective_to_dict() -> None:
    """Testa serialização para dicionário."""
    obj = Objective(
        nome="Serial",
        descricao="Teste serialização",
        tipos=[ObjectiveType.FILESYSTEM, ObjectiveType.PROJECT],
        entradas=["a", "b"],
        saidas_esperadas=["c"],
        efeitos_colaterais=[],
        invariantes=["x"],
        status=ObjectiveStatus.ATIVO,
    )
    data = obj.to_dict()
    assert data["nome"] == "Serial"
    assert data["descricao"] == "Teste serialização"
    assert data["tipos"] == ["filesystem", "project"]
    assert data["entradas"] == ["a", "b"]
    assert data["saidas_esperadas"] == ["c"]
    assert data["efeitos_colaterais"] == []
    assert data["invariantes"] == ["x"]
    assert data["status"] == "ATIVO"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    # Datetimes devem ser strings ISO
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)


def test_objective_from_dict() -> None:
    """Testa deserialização a partir de dicionário."""
    original = Objective(
        nome="Original",
        descricao="Desc",
        tipos=[ObjectiveType.INTEGRATION],
        entradas=["e"],
        saidas_esperadas=["s"],
        efeitos_colaterais=["ec"],
        invariantes=["i"],
        status=ObjectiveStatus.BLOQUEADO,
    )
    data = original.to_dict()
    restored = Objective.from_dict(data)
    assert restored.id == original.id
    assert restored.nome == original.nome
    assert restored.descricao == original.descricao
    assert restored.tipos == original.tipos
    assert restored.entradas == original.entradas
    assert restored.saidas_esperadas == original.saidas_esperadas
    assert restored.efeitos_colaterais == original.efeitos_colaterais
    assert restored.invariantes == original.invariantes
    assert restored.status == original.status
    # Datetimes devem ser iguais (dentro de um segundo)
    assert abs(restored.created_at - original.created_at).total_seconds() < 1
    assert abs(restored.updated_at - original.updated_at).total_seconds() < 1


def test_objective_from_dict_minimal() -> None:
    """Testa deserialização com dados mínimos."""
    data = {
        "nome": "Minimal",
        "descricao": "Desc",
        "tipos": ["cli-command"],
        "status": "DEFINIDO",
    }
    obj = Objective.from_dict(data)
    assert obj.nome == "Minimal"
    assert obj.descricao == "Desc"
    assert obj.tipos == [ObjectiveType.CLI_COMMAND]
    assert obj.status == ObjectiveStatus.DEFINIDO
    assert obj.entradas == []
    assert obj.saidas_esperadas == []
    assert obj.efeitos_colaterais == []
    assert obj.invariantes == []
    # ID deve ser gerado automaticamente
    assert obj.id is not None


def test_objective_validate() -> None:
    """Testa validação de campos obrigatórios."""
    # Objetivo válido
    obj = Objective(
        nome="Nome",
        descricao="Descrição",
        tipos=[ObjectiveType.STATE],
    )
    errors = obj.validate()
    assert errors == []

    # Nome vazio
    obj.nome = ""
    errors = obj.validate()
    assert "Nome não pode ser vazio" in errors

    # Descrição vazia
    obj.nome = "Nome"
    obj.descricao = ""
    errors = obj.validate()
    assert "Descrição não pode ser vazia" in errors

    # Tipos vazio
    obj.descricao = "Desc"
    obj.tipos = []
    errors = obj.validate()
    assert "Pelo menos um tipo deve ser selecionado" in errors


def test_objective_type_enum() -> None:
    """Testa valores do enum ObjectiveType."""
    assert ObjectiveType.CLI_COMMAND.value == "cli-command"
    assert ObjectiveType.FILESYSTEM.value == "filesystem"
    assert ObjectiveType.STATE.value == "state"
    assert ObjectiveType.PROJECT.value == "project"
    assert ObjectiveType.INTEGRATION.value == "integration"
    # Verificar que todos os valores são strings
    for t in ObjectiveType:
        assert isinstance(t.value, str)


def test_objective_status_enum() -> None:
    """Testa valores do enum ObjectiveStatus."""
    assert ObjectiveStatus.DEFINIDO.value == "DEFINIDO"
    assert ObjectiveStatus.ATIVO.value == "ATIVO"
    assert ObjectiveStatus.BLOQUEADO.value == "BLOQUEADO"
    assert ObjectiveStatus.CONCLUIDO.value == "CONCLUIDO"
    assert ObjectiveStatus.FALHOU.value == "FALHOU"
    for s in ObjectiveStatus:
        assert isinstance(s.value, str)
