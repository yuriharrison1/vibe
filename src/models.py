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
            errors.append("Descrição não pode ser vazia")
        if not self.tipos:
            errors.append("Pelo menos um tipo deve ser selecionado")
        return errors
