"""Validador de estrutura canônica do projeto."""

from pathlib import Path
from typing import List


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
