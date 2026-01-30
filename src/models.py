"""Modelos de dados para objetivos."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
import uuid


class ObjectiveType(str, Enum):
    """Tipos de objetivo suportados pelo sistema."""

    CLI_COMMAND = "cli-command"
    FILESYSTEM = "filesystem"
    STATE = "state"
    PROJECT = "project"
    INTEGRATION = "integration"


class ObjectiveStatus(str, Enum):
    """Estados possíveis de um objetivo."""

    DEFINIDO = "DEFINIDO"
    ATIVO = "ATIVO"
    BLOQUEADO = "BLOQUEADO"
    CONCLUIDO = "CONCLUIDO"
    FALHOU = "FALHOU"


@dataclass
class Objective:
    """Objetivo formal do sistema.

    Representa uma unidade de trabalho que deve ser concluída
    seguindo as regras do sistema (eventos, testes, persistência).
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nome: str = ""
    descricao: str = ""
    tipos: List[ObjectiveType] = field(default_factory=list)
    entradas: List[str] = field(default_factory=list)
    saidas_esperadas: List[str] = field(default_factory=list)
    efeitos_colaterais: List[str] = field(default_factory=list)
    invariantes: List[str] = field(default_factory=list)
    status: ObjectiveStatus = ObjectiveStatus.DEFINIDO
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Converte o objetivo para um dicionário serializável."""
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "tipos": [t.value for t in self.tipos],
            "entradas": self.entradas,
            "saidas_esperadas": self.saidas_esperadas,
            "efeitos_colaterais": self.efeitos_colaterais,
            "invariantes": self.invariantes,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Objective":
        """Cria um objetivo a partir de um dicionário."""
        obj = cls()
        obj.id = data.get("id", str(uuid.uuid4()))
        obj.nome = data.get("nome", "")
        obj.descricao = data.get("descricao", "")
        # Converte strings de volta para ObjectiveType
        tipos_raw = data.get("tipos", [])
        obj.tipos = [ObjectiveType(t) for t in tipos_raw if t in [e.value for e in ObjectiveType]]
        obj.entradas = data.get("entradas", [])
        obj.saidas_esperadas = data.get("saidas_esperadas", [])
        obj.efeitos_colaterais = data.get("efeitos_colaterais", [])
        obj.invariantes = data.get("invariantes", [])
        # Status
        status_raw = data.get("status", ObjectiveStatus.DEFINIDO.value)
        try:
            obj.status = ObjectiveStatus(status_raw)
        except ValueError:
            obj.status = ObjectiveStatus.DEFINIDO
        # Datetimes
        created_at_raw = data.get("created_at")
        if created_at_raw:
            obj.created_at = datetime.fromisoformat(created_at_raw)
        updated_at_raw = data.get("updated_at")
        if updated_at_raw:
            obj.updated_at = datetime.fromisoformat(updated_at_raw)
        return obj

    def validate(self) -> List[str]:
        """Valida os campos obrigatórios do objetivo.

        Returns:
            Lista de mensagens de erro. Vazia se válido.
        """
        errors = []
        if not self.nome.strip():
            errors.append("Nome não pode ser vazio")
        if not self.descricao.strip():
            errors.append("Descrição não pode ser vazio")
        if not self.tipos:
            errors.append("Pelo menos um tipo deve ser selecionado")
        return errors


# Modelos para tracking de testes
class TestStatus(str, Enum):
    """Status de execução de um teste."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass
class TestRun:
    """Registro de execução de um teste individual."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective_id: str = ""
    test_file: str = ""
    test_name: str = ""
    status: TestStatus = TestStatus.FAILED
    error_message: Optional[str] = None
    duration: float = 0.0
    run_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Converte para dicionário serializável."""
        return {
            "id": self.id,
            "objective_id": self.objective_id,
            "test_file": self.test_file,
            "test_name": self.test_name,
            "status": self.status.value,
            "error_message": self.error_message,
            "duration": self.duration,
            "run_at": self.run_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TestRun":
        """Cria a partir de um dicionário."""
        obj = cls()
        obj.id = data.get("id", str(uuid.uuid4()))
        obj.objective_id = data.get("objective_id", "")
        obj.test_file = data.get("test_file", "")
        obj.test_name = data.get("test_name", "")
        status_raw = data.get("status", TestStatus.FAILED.value)
        try:
            obj.status = TestStatus(status_raw)
        except ValueError:
            obj.status = TestStatus.FAILED
        obj.error_message = data.get("error_message")
        obj.duration = data.get("duration", 0.0)
        run_at_raw = data.get("run_at")
        if run_at_raw:
            obj.run_at = datetime.fromisoformat(run_at_raw)
        return obj


@dataclass
class TestSummary:
    """Sumário de execução de testes para um objetivo."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective_id: str = ""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    error: int = 0
    last_run: datetime = field(default_factory=datetime.now)

    def is_passing(self) -> bool:
        """Retorna True se todos os testes passaram."""
        return self.failed == 0 and self.error == 0 and self.total_tests > 0

    def success_rate(self) -> float:
        """Retorna a taxa de sucesso (0.0 a 1.0)."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed + self.skipped) / self.total_tests

    def to_dict(self) -> dict:
        """Converte para dicionário serializável."""
        return {
            "id": self.id,
            "objective_id": self.objective_id,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "error": self.error,
            "last_run": self.last_run.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TestSummary":
        """Cria a partir de um dicionário."""
        obj = cls()
        obj.id = data.get("id", str(uuid.uuid4()))
        obj.objective_id = data.get("objective_id", "")
        obj.total_tests = data.get("total_tests", 0)
        obj.passed = data.get("passed", 0)
        obj.failed = data.get("failed", 0)
        obj.skipped = data.get("skipped", 0)
        obj.error = data.get("error", 0)
        last_run_raw = data.get("last_run")
        if last_run_raw:
            obj.last_run = datetime.fromisoformat(last_run_raw)
        return obj
