"""Camada de persistência SQLite para objetivos."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.models import Objective, ObjectiveStatus, ObjectiveType


class Database:
    """Gerenciamento de banco de dados SQLite para objetivos."""

    def __init__(self, db_path: Path) -> None:
        """Inicializa a conexão com o banco e cria o schema se necessário.

        Args:
            db_path: Caminho para o arquivo SQLite.
        """
        self.db_path = db_path
        self._create_schema()

    @contextmanager
    def _connection(self):
        """Context manager para conexões com o banco."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _create_schema(self) -> None:
        """Cria a tabela objectives se não existir."""
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS objectives (
                    id TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    tipos TEXT NOT NULL,
                    entradas TEXT,
                    saidas_esperadas TEXT,
                    efeitos_colaterais TEXT,
                    invariantes TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def create_objective(self, objective: Objective) -> bool:
        """Insere um novo objetivo no banco.

        Args:
            objective: Objetivo a ser persistido.

        Returns:
            True se sucesso, False se falhar.
        """
        try:
            with self._connection() as conn:
                conn.execute("""
                    INSERT INTO objectives (
                        id, nome, descricao, tipos,
                        entradas, saidas_esperadas,
                        efeitos_colaterais, invariantes,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    objective.id,
                    objective.nome,
                    objective.descricao,
                    json.dumps([t.value for t in objective.tipos]),
                    json.dumps(objective.entradas),
                    json.dumps(objective.saidas_esperadas),
                    json.dumps(objective.efeitos_colaterais),
                    json.dumps(objective.invariantes),
                    objective.status.value,
                    objective.created_at.isoformat(),
                    objective.updated_at.isoformat(),
                ))
            return True
        except sqlite3.Error:
            return False

    def get_objective(self, objective_id: str) -> Optional[Objective]:
        """Recupera um objetivo pelo ID.

        Args:
            objective_id: ID do objetivo.

        Returns:
            Objetivo se encontrado, None caso contrário.
        """
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM objectives WHERE id = ?",
                (objective_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_objective(row)

    def list_objectives(self) -> List[Objective]:
        """Lista todos os objetivos armazenados.

        Returns:
            Lista de objetivos ordenados por created_at (mais recente primeiro).
        """
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM objectives ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            return [self._row_to_objective(row) for row in rows]

    def update_objective(self, objective: Objective) -> bool:
        """Atualiza um objetivo existente.

        Args:
            objective: Objetivo com dados atualizados.

        Returns:
            True se sucesso, False se falhar.
        """
        try:
            with self._connection() as conn:
                conn.execute("""
                    UPDATE objectives SET
                        nome = ?,
                        descricao = ?,
                        tipos = ?,
                        entradas = ?,
                        saidas_esperadas = ?,
                        efeitos_colaterais = ?,
                        invariantes = ?,
                        status = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    objective.nome,
                    objective.descricao,
                    json.dumps([t.value for t in objective.tipos]),
                    json.dumps(objective.entradas),
                    json.dumps(objective.saidas_esperadas),
                    json.dumps(objective.efeitos_colaterais),
                    json.dumps(objective.invariantes),
                    objective.status.value,
                    objective.updated_at.isoformat(),
                    objective.id,
                ))
            return True
        except sqlite3.Error:
            return False

    def delete_objective(self, objective_id: str) -> bool:
        """Remove um objetivo do banco.

        Args:
            objective_id: ID do objetivo a ser removido.

        Returns:
            True se sucesso, False se falhar.
        """
        try:
            with self._connection() as conn:
                conn.execute(
                    "DELETE FROM objectives WHERE id = ?",
                    (objective_id,)
                )
            return True
        except sqlite3.Error:
            return False

    def _row_to_objective(self, row: sqlite3.Row) -> Objective:
        """Converte uma linha SQLite em um objeto Objective."""
        data = dict(row)
        # Converte JSON strings de volta para listas
        tipos_raw = json.loads(data["tipos"])
        tipos = [ObjectiveType(t) for t in tipos_raw]
        entradas = json.loads(data["entradas"] or "[]")
        saidas_esperadas = json.loads(data["saidas_esperadas"] or "[]")
        efeitos_colaterais = json.loads(data["efeitos_colaterais"] or "[]")
        invariantes = json.loads(data["invariantes"] or "[]")
        status = ObjectiveStatus(data["status"])
        # Cria o objeto
        obj = Objective(
            id=data["id"],
            nome=data["nome"],
            descricao=data["descricao"],
            tipos=tipos,
            entradas=entradas,
            saidas_esperadas=saidas_esperadas,
            efeitos_colaterais=efeitos_colaterais,
            invariantes=invariantes,
            status=status,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
        return obj
