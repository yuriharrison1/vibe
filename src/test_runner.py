"""Executor de testes para objetivos."""

import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.database import Database
from src.models import TestRun, TestStatus, TestSummary


class TestRunner:
    """Executa testes e registra resultados."""

    def __init__(self, db: Database) -> None:
        """Inicializa o runner com conexão ao banco."""
        self.db = db

    def run_objective_tests(self, objective_id: str) -> Optional[TestSummary]:
        """Executa testes de um objetivo e salva resultados.

        Args:
            objective_id: ID do objetivo.

        Returns:
            TestSummary se execução bem-sucedida, None caso contrário.
        """
        # Verificar se objetivo existe
        objective = self.db.get_objective(objective_id)
        if not objective:
            print(f"❌ Objetivo '{objective_id}' não encontrado.")
            return None

        # Verificar diretório de testes
        test_dir = Path("tests") / "objectives" / objective_id
        if not test_dir.exists():
            print(f"❌ Diretório de testes não encontrado: {test_dir}")
            return None

        # Encontrar arquivos de teste
        test_files = list(test_dir.glob("*.py"))
        if not test_files:
            print(f"⚠️  Nenhum arquivo de teste encontrado em {test_dir}")
            return None

        # Executar pytest para cada arquivo
        summary = TestSummary(objective_id=objective_id)
        test_runs: List[TestRun] = []

        for test_file in test_files:
            result = self._run_pytest(test_file)
            if result is None:
                continue

            # Processar resultados
            for test_name, status, duration, error_msg in result:
                test_run = TestRun(
                    objective_id=objective_id,
                    test_file=str(test_file.relative_to(Path.cwd())),
                    test_name=test_name,
                    status=status,
                    error_message=error_msg,
                    duration=duration,
                )
                test_runs.append(test_run)

                # Atualizar contagens
                summary.total_tests += 1
                if status == TestStatus.PASSED:
                    summary.passed += 1
                elif status == TestStatus.FAILED:
                    summary.failed += 1
                elif status == TestStatus.SKIPPED:
                    summary.skipped += 1
                elif status == TestStatus.ERROR:
                    summary.error += 1

        # Salvar resultados
        summary.last_run = datetime.now()
        for run in test_runs:
            self.db.save_test_run(run)

        # Salvar ou atualizar sumário
        existing = self.db.get_test_summary(objective_id)
        if existing:
            self.db.update_test_summary(objective_id, summary)
        else:
            self.db.save_test_summary(summary)

        return summary

    def _run_pytest(self, test_file: Path) -> Optional[List[tuple]]:
        """Executa pytest em um arquivo e retorna resultados.

        Args:
            test_file: Caminho para o arquivo de teste.

        Returns:
            Lista de tuplas (test_name, status, duration, error_message)
            ou None se execução falhar.
        """
        try:
            # Usar subprocess para capturar output
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    str(test_file),
                    "-v",
                    "--tb=short",
                    "--disable-warnings",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return self._parse_pytest_output(result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout ao executar {test_file}")
            return None
        except Exception as e:
            print(f"❌ Erro ao executar pytest: {e}")
            return None

    def _parse_pytest_output(self, stdout: str, stderr: str) -> List[Tuple[str, TestStatus, float, Optional[str]]]:
        """Parseia output do pytest para extrair resultados.

        Args:
            stdout: Saída padrão do pytest.
            stderr: Saída de erro do pytest.

        Returns:
            Lista de (test_name, status, duration, error_message).
        """
        results: List[Tuple[str, TestStatus, float, Optional[str]]] = []
        lines = stdout.split("\n")

        current_test: Optional[str] = None
        current_status: Optional[TestStatus] = None
        current_duration: float = 0.0
        error_lines: List[str] = []
        in_error = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detectar início de uma seção de erros
            if line.startswith("FAILURES") or line.startswith("ERRORS") or line.startswith("===="):
                in_error = True
                continue
            
            if in_error:
                # Coletar linhas de erro
                if line and not line.startswith("===="):
                    error_lines.append(line)
                continue

            # Detectar resultado de teste (formato comum do pytest)
            # Exemplo: "test_file.py::test_name PASSED [ 99%]"
            # Ou: "test_file.py::test_name FAILED [ 99%]"
            if "::" in line and ("PASSED" in line or "FAILED" in line or "SKIPPED" in line or "ERROR" in line):
                # Extrair nome do teste
                parts = line.split()
                if len(parts) < 2:
                    continue
                    
                # O nome do teste está antes do primeiro espaço após "::"
                test_part = parts[0]
                if "::" in test_part:
                    test_name = test_part.split("::")[-1]
                else:
                    test_name = test_part
                
                # Determinar status
                if "PASSED" in line:
                    status = TestStatus.PASSED
                elif "FAILED" in line:
                    status = TestStatus.FAILED
                elif "SKIPPED" in line:
                    status = TestStatus.SKIPPED
                else:
                    status = TestStatus.ERROR
                
                # Extrair duração
                duration = 0.0
                for part in parts:
                    if part.startswith("[") and "s]" in part:
                        # Encontrar o número antes de 's'
                        match = re.search(r'\[([\d.]+)s\]', part)
                        if match:
                            try:
                                duration = float(match.group(1))
                            except ValueError:
                                pass
                        break
                
                # Salvar teste anterior se houver
                if current_test and current_status:
                    error_msg = "\n".join(error_lines) if error_lines else None
                    results.append((current_test, current_status, current_duration, error_msg))
                    error_lines = []
                
                # Iniciar novo teste
                current_test = test_name
                current_status = status
                current_duration = duration
            
            # Coletar linhas de erro para o teste atual
            elif current_test and current_status in [TestStatus.FAILED, TestStatus.ERROR]:
                if line and not line.startswith("---"):
                    error_lines.append(line)

        # Adicionar último teste
        if current_test and current_status:
            error_msg = "\n".join(error_lines) if error_lines else None
            results.append((current_test, current_status, current_duration, error_msg))

        return results

    def run_all_tests(self) -> Dict[str, TestSummary]:
        """Executa testes de todos os objetivos.

        Returns:
            Dicionário {objective_id: TestSummary}.
        """
        objectives = self.db.list_objectives()
        summaries = {}

        for obj in objectives:
            print(f"🧪 Executando testes para: {obj.nome}")
            summary = self.run_objective_tests(obj.id)
            if summary:
                summaries[obj.id] = summary
                status = "✅" if summary.is_passing() else "❌"
                print(f"   {status} {summary.passed}/{summary.total_tests} testes passando")

        return summaries
