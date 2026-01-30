"""Validador de estrutura canônica do projeto."""

from pathlib import Path
from typing import List

from src.database import Database


class StructureValidator:
    """Valida se o projeto segue a estrutura canônica."""

    REQUIRED_DIRS = ["docs", "objectives", "tests", "scripts", "ai", "state", "src"]
    REQUIRED_FILES = ["scope.md", "archeture.md", "milestone.md"]

    def __init__(self, project_path: Path = Path(".")):
        """Inicializa o validador com o caminho do projeto."""
        self.project_path = project_path

    def validate_canonical_structure(self) -> List[str]:
        """Valida a estrutura canônica do projeto.

        Returns:
            Lista de erros encontrados. Vazia se estrutura válida.
        """
        errors: List[str] = []

        # Validar diretórios
        for dir_name in self.REQUIRED_DIRS:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                errors.append(f"Diretório faltante: {dir_name}/")
            elif not dir_path.is_dir():
                errors.append(f"Não é um diretório: {dir_name}/")

        # Validar arquivos
        for file_name in self.REQUIRED_FILES:
            file_path = self.project_path / file_name
            if not file_path.exists():
                errors.append(f"Arquivo faltante: {file_name}")
            elif not file_path.is_file():
                errors.append(f"Não é um arquivo: {file_name}")

        return errors

    def validate_objectives_integrity(self) -> List[str]:
        """Valida que todos os objetivos têm testes.

        Returns:
            Lista de erros encontrados.
        """
        errors: List[str] = []
        db_path = self.project_path / "state" / "vibe.db"
        if not db_path.exists():
            # Sem banco, sem objetivos
            return errors
        
        db = Database(db_path)
        objectives = db.list_objectives()
        
        for obj in objectives:
            test_dir = self.project_path / "tests" / "objectives" / obj.id
            if not test_dir.exists():
                errors.append(f"Objetivo '{obj.nome}' ({obj.id}) não tem diretório de testes")
                continue
            # Verificar se há pelo menos um arquivo .py
            test_files = list(test_dir.glob("*.py"))
            if not test_files:
                errors.append(f"Objetivo '{obj.nome}' ({obj.id}) não tem arquivos de teste")
                continue
            # Verificar se os testes são executáveis (pelo menos contêm 'def test_')
            has_test_func = False
            for tf in test_files:
                try:
                    content = tf.read_text(encoding="utf-8")
                    if "def test_" in content:
                        has_test_func = True
                        break
                except Exception:
                    pass
            if not has_test_func:
                errors.append(f"Objetivo '{obj.nome}' ({obj.id}) não tem funções de teste válidas")
        
        return errors
