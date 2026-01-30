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
        """Cria as tabelas se não existirem."""
        with self._connection() as conn:
            # Tabela objectives
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
            # Tabela test_runs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id TEXT PRIMARY KEY,
                    objective_id TEXT NOT NULL,
                    test_file TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    duration REAL,
                    run_at TEXT NOT NULL,
                    FOREIGN KEY (objective_id) REFERENCES objectives(id)
                )
            """)
            # Tabela test_summary
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_summary (
                    id TEXT PRIMARY KEY,
                    objective_id TEXT NOT NULL,
                    total_tests INTEGER NOT NULL,
                    passed INTEGER NOT NULL,
                    failed INTEGER NOT NULL,
                    skipped INTEGER NOT NULL,
                    error INTEGER NOT NULL,
                    last_run TEXT NOT NULL,
                    FOREIGN KEY (objective_id) REFERENCES objectives(id)
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

    # Métodos para test_runs
    def save_test_run(self, test_run: "TestRun") -> bool:
        """Salva uma execução de teste no banco."""
        try:
            with self._connection() as conn:
                conn.execute("""
                    INSERT INTO test_runs (
                        id, objective_id, test_file, test_name,
                        status, error_message, duration, run_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_run.id,
                    test_run.objective_id,
                    test_run.test_file,
                    test_run.test_name,
                    test_run.status.value,
                    test_run.error_message,
                    test_run.duration,
                    test_run.run_at.isoformat(),
                ))
            return True
        except sqlite3.Error:
            return False

    def get_test_runs(self, objective_id: str) -> List["TestRun"]:
        """Recupera todas as execuções de teste de um objetivo."""
        from src.models import TestRun, TestStatus
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM test_runs WHERE objective_id = ? ORDER BY run_at DESC",
                (objective_id,)
            )
            rows = cursor.fetchall()
            runs = []
            for row in rows:
                data = dict(row)
                runs.append(TestRun(
                    id=data["id"],
                    objective_id=data["objective_id"],
                    test_file=data["test_file"],
                    test_name=data["test_name"],
                    status=TestStatus(data["status"]),
                    error_message=data["error_message"],
                    duration=data["duration"],
                    run_at=datetime.fromisoformat(data["run_at"]),
                ))
            return runs

    def get_latest_test_run(self, objective_id: str) -> Optional["TestRun"]:
        """Recupera a execução mais recente de um objetivo."""
        runs = self.get_test_runs(objective_id)
        return runs[0] if runs else None

    # Métodos para test_summary
    def save_test_summary(self, summary: "TestSummary") -> bool:
        """Salva um sumário de testes no banco."""
        try:
            with self._connection() as conn:
                conn.execute("""
                    INSERT INTO test_summary (
                        id, objective_id, total_tests, passed,
                        failed, skipped, error, last_run
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    summary.id,
                    summary.objective_id,
                    summary.total_tests,
                    summary.passed,
                    summary.failed,
                    summary.skipped,
                    summary.error,
                    summary.last_run.isoformat(),
                ))
            return True
        except sqlite3.Error:
            return False

    def get_test_summary(self, objective_id: str) -> Optional["TestSummary"]:
        """Recupera o sumário de testes de um objetivo."""
        from src.models import TestSummary
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM test_summary WHERE objective_id = ? ORDER BY last_run DESC LIMIT 1",
                (objective_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            data = dict(row)
            return TestSummary(
                id=data["id"],
                objective_id=data["objective_id"],
                total_tests=data["total_tests"],
                passed=data["passed"],
                failed=data["failed"],
                skipped=data["skipped"],
                error=data["error"],
                last_run=datetime.fromisoformat(data["last_run"]),
            )

    def update_test_summary(self, objective_id: str, summary: "TestSummary") -> bool:
        """Atualiza um sumário existente."""
        try:
            with self._connection() as conn:
                conn.execute("""
                    UPDATE test_summary SET
                        total_tests = ?,
                        passed = ?,
                        failed = ?,
                        skipped = ?,
                        error = ?,
                        last_run = ?
                    WHERE objective_id = ?
                """, (
                    summary.total_tests,
                    summary.passed,
                    summary.failed,
                    summary.skipped,
                    summary.error,
                    summary.last_run.isoformat(),
                    objective_id,
                ))
            return True
        except sqlite3.Error:
            return False
