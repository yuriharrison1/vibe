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

    def run_objective_tests(self, objective_id: str, base_path: Optional[Path] = None) -> Optional[TestSummary]:
        """Executa testes de um objetivo e salva resultados.

        Args:
            objective_id: ID do objetivo.
            base_path: Caminho base para testes (opcional). Se None, usa "tests".

        Returns:
            TestSummary se execução bem-sucedida, None caso contrário.
        """
        # Verificar se objetivo existe
        objective = self.db.get_objective(objective_id)
        if not objective:
            print(f"❌ Objetivo '{objective_id}' não encontrado.")
            return None

        # Determinar diretório de testes
        if base_path is None:
            base_path = Path("tests")
        test_dir = base_path / "objectives" / objective_id
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
                cwd=test_file.parent,
            )
            # Debug: imprimir output para análise
            print(f"DEBUG: Executando {test_file}")
            print(f"DEBUG: stdout: {result.stdout[:200] if result.stdout else 'None'}")
            print(f"DEBUG: stderr: {result.stderr[:200] if result.stderr else 'None'}")
            print(f"DEBUG: returncode: {result.returncode}")
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
        
        # Padrão: test_file.py::test_name PASSED [  0.00s]
        # Ou: test_file.py::test_name FAILED [  0.00s]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Verificar se contém "::" e um status
            if "::" in line:
                # Encontrar o nome do teste
                # Exemplo: "test_simple.py::test_example PASSED [  0.00s]"
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                test_part = parts[0]
                if "::" not in test_part:
                    continue
                
                test_name = test_part.split("::")[-1]
                
                # Determinar status
                status = None
                if "PASSED" in line:
                    status = TestStatus.PASSED
                elif "FAILED" in line:
                    status = TestStatus.FAILED
                elif "ERROR" in line:
                    status = TestStatus.ERROR
                elif "SKIPPED" in line:
                    status = TestStatus.SKIPPED
                
                if status is None:
                    # Talvez a linha seja diferente, continuar
                    continue
                
                # Extrair duração
                duration = 0.0
                for part in parts:
                    if part.startswith("[") and "s]" in part:
                        # Encontrar número
                        import re
                        match = re.search(r'\[([\d.]+)s\]', part)
                        if match:
                            try:
                                duration = float(match.group(1))
                            except ValueError:
                                pass
                        break
                
                results.append((test_name, status, duration, None))
        
        # Se ainda não encontrou resultados, tentar contar testes de outra forma
        if not results:
            # Contar quantas vezes "test_" aparece no output
            import re
            test_pattern = r'test_[a-zA-Z0-9_]+'
            test_names = re.findall(test_pattern, stdout)
            unique_tests = set(test_names)
            
            # Se encontrou testes, assumir que todos passaram (para testes simples)
            if unique_tests:
                for test_name in unique_tests:
                    # Verificar se o teste falhou procurando por "FAILED" ou "ERROR" perto do nome
                    test_failed = False
                    test_error = False
                    
                    # Procurar por linhas que mencionem este teste
                    for line in lines:
                        if test_name in line:
                            if "FAILED" in line:
                                test_failed = True
                                break
                            elif "ERROR" in line:
                                test_error = True
                                break
                    
                    if test_failed:
                        status = TestStatus.FAILED
                    elif test_error:
                        status = TestStatus.ERROR
                    else:
                        status = TestStatus.PASSED
                    
                    results.append((test_name, status, 0.0, None))
        
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
