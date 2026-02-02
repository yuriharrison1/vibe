"""Validação de idempotência para comandos."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
import uuid

from src.database import Database


class OperationResult(str, Enum):
    """Resultado de uma operação."""
    SUCCESS = "SUCCESS"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"


class IdempotencyValidator:
    """Validador de idempotência para comandos."""

    def __init__(self, db: Database) -> None:
        """Inicializa o validador."""
        self.db = db
        self._create_schema()

    def _create_schema(self) -> None:
        """Cria a tabela command_history se não existir."""
        with self.db._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    arguments TEXT,
                    result TEXT NOT NULL,
                    executed_at TEXT NOT NULL,
                    user TEXT
                )
            """)

    def check_objective_new(self, name: str) -> tuple[bool, Optional[str]]:
        """Verifica se pode criar um novo objetivo com o nome dado.
        
        Args:
            name: Nome do objetivo.
            
        Returns:
            Tupla (pode_criar, id_existente).
        """
        objectives = self.db.list_objectives()
        for obj in objectives:
            if obj.nome == name:
                return False, obj.id
        return True, None

    def check_test_generation(self, objective_id: str) -> tuple[bool, Optional[datetime]]:
        """Verifica se pode gerar testes para um objetivo.
        
        Args:
            objective_id: ID do objetivo.
            
        Returns:
            Tupla (pode_gerar, ultima_geracao).
        """
        # Por enquanto, sempre permite
        return True, None

    def check_project_init(self, path: Path) -> tuple[bool, Optional[str]]:
        """Verifica se pode inicializar um projeto no caminho.
        
        Args:
            path: Caminho do projeto.
            
        Returns:
            Tupla (pode_inicializar, caminho_db_existente).
        """
        db_path = path / "state" / "vibe.db"
        if db_path.exists():
            return False, str(db_path)
        return True, None

    def record_command(
        self,
        command: str,
        arguments: Optional[Dict[str, Any]] = None,
        result: OperationResult = OperationResult.SUCCESS,
        user: Optional[str] = None,
    ) -> None:
        """Registra um comando executado no histórico.
        
        Args:
            command: Nome do comando.
            arguments: Argumentos do comando.
            result: Resultado da operação.
            user: Usuário que executou (opcional).
        """
        with self.db._connection() as conn:
            conn.execute("""
                INSERT INTO command_history (
                    id, command, arguments, result, executed_at, user
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                command,
                json.dumps(arguments) if arguments else None,
                result.value,
                datetime.now().isoformat(),
                user,
            ))


class CommandHistory:
    """Gerenciador do histórico de comandos."""

    def __init__(self, db: Database) -> None:
        """Inicializa o gerenciador."""
        self.db = db

    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retorna os comandos mais recentes.
        
        Args:
            limit: Número máximo de registros.
            
        Returns:
            Lista de registros.
        """
        with self.db._connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM command_history 
                ORDER BY executed_at DESC 
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_by_command(self, command: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retorna comandos filtrados por nome.
        
        Args:
            command: Nome do comando.
            limit: Número máximo de registros.
            
        Returns:
            Lista de registros.
        """
        with self.db._connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM command_history 
                WHERE command = ?
                ORDER BY executed_at DESC 
                LIMIT ?
            """, (command, limit))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_today(self) -> List[Dict[str, Any]]:
        """Retorna comandos executados hoje.
        
        Returns:
            Lista de registros.
        """
        today = datetime.now().date().isoformat()
        with self.db._connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM command_history 
                WHERE date(executed_at) = ?
                ORDER BY executed_at DESC
            """, (today,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Converte uma linha SQLite em dicionário."""
        data = dict(row)
        # Parse JSON de arguments
        if data.get("arguments"):
            data["arguments"] = json.loads(data["arguments"])
        else:
            data["arguments"] = {}
        # Converter executed_at para datetime
        data["executed_at"] = datetime.fromisoformat(data["executed_at"])
        return data
