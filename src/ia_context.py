"""Contexto e auditoria para integração com IA."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

from src.database import Database
from src.models import Objective


class IAActionType(str, Enum):
    """Tipo de ação realizada pela IA."""
    CODE_CHANGE = "CODE_CHANGE"
    TEST_UPDATE = "TEST_UPDATE"
    DOCUMENTATION = "DOCUMENTATION"
    CONFIGURATION = "CONFIGURATION"


class IAActionLog:
    """Registro de ações da IA para auditoria."""

    def __init__(self, db: Database) -> None:
        """Inicializa o logger de ações da IA."""
        self.db = db
        self._create_schema()

    def _create_schema(self) -> None:
        """Cria a tabela ia_action_log se não existir."""
        with self.db._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ia_action_log (
                    id TEXT PRIMARY KEY,
                    objective_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    files_changed TEXT NOT NULL,
                    tests_impacted TEXT,
                    decisions_made TEXT,
                    assumptions TEXT,
                    created_at TEXT NOT NULL,
                    ia_agent TEXT,
                    FOREIGN KEY (objective_id) REFERENCES objectives(id)
                )
            """)

    def log_action(
        self,
        objective_id: str,
        action_type: IAActionType,
        files_changed: List[Dict[str, str]],
        tests_impacted: Optional[List[Dict[str, str]]] = None,
        decisions_made: Optional[List[Dict[str, str]]] = None,
        assumptions: Optional[List[str]] = None,
        ia_agent: Optional[str] = None,
    ) -> None:
        """Registra uma ação da IA no log de auditoria.
        
        Args:
            objective_id: ID do objetivo associado.
            action_type: Tipo de ação realizada.
            files_changed: Lista de dicionários com 'file' e 'description'.
            tests_impacted: Lista de dicionários com 'test' e 'expected_result'.
            decisions_made: Lista de dicionários com 'decision' e 'justification'.
            assumptions: Lista de suposições feitas.
            ia_agent: Identificador do agente IA (opcional).
        """
        with self.db._connection() as conn:
            conn.execute("""
                INSERT INTO ia_action_log (
                    id, objective_id, action_type, files_changed,
                    tests_impacted, decisions_made, assumptions,
                    created_at, ia_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                objective_id,
                action_type.value,
                json.dumps(files_changed, ensure_ascii=False),
                json.dumps(tests_impacted or [], ensure_ascii=False),
                json.dumps(decisions_made or [], ensure_ascii=False),
                json.dumps(assumptions or [], ensure_ascii=False),
                datetime.now().isoformat(),
                ia_agent,
            ))

    def get_actions_for_objective(
        self,
        objective_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Recupera ações da IA para um objetivo específico.
        
        Args:
            objective_id: ID do objetivo.
            limit: Número máximo de registros.
            
        Returns:
            Lista de ações registradas.
        """
        with self.db._connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM ia_action_log 
                WHERE objective_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (objective_id, limit))
            rows = cursor.fetchall()
            
            actions = []
            for row in rows:
                data = dict(row)
                # Parse JSON strings
                for field in ["files_changed", "tests_impacted", "decisions_made", "assumptions"]:
                    if data.get(field):
                        data[field] = json.loads(data[field])
                    else:
                        data[field] = []
                # Converter created_at para datetime
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                actions.append(data)
            
            return actions


class IAContextManager:
    """Gerenciador de contexto para IA."""
    
    def __init__(self, db: Database) -> None:
        """Inicializa o gerenciador de contexto."""
        self.db = db
        self.action_log = IAActionLog(db)
        self._current_objective: Optional[Objective] = None
        self._allowed_files: List[str] = []
    
    def activate_objective(self, objective_id: str) -> Optional[Objective]:
        """Ativa um objetivo para trabalho da IA.
        
        Args:
            objective_id: ID do objetivo a ser ativado.
            
        Returns:
            Objetivo ativado ou None se não encontrado.
        """
        objective = self.db.get_objective(objective_id)
        if objective:
            self._current_objective = objective
            # Determinar arquivos permitidos baseado no tipo de objetivo
            self._determine_allowed_files(objective)
        return objective
    
    def _determine_allowed_files(self, objective: Objective) -> None:
        """Determina arquivos permitidos para modificação baseado no objetivo.
        
        Args:
            objective: Objetivo ativo.
        """
        allowed = []
        
        # Arquivos base sempre permitidos
        base_files = [
            "src/__init__.py",
            "pyproject.toml",
        ]
        allowed.extend(base_files)
        
        # Baseado nos tipos de objetivo
        for tipo in objective.tipos:
            if tipo.value == "cli-command":
                allowed.append("src/cli.py")
                allowed.append("tests/test_cli.py")
            elif tipo.value == "filesystem":
                allowed.append("src/validator.py")
                allowed.append("tests/test_filesystem_validation.py")
            elif tipo.value == "state":
                allowed.append("src/database.py")
                allowed.append("src/models.py")
                allowed.append("tests/test_database.py")
                allowed.append("tests/test_models.py")
            elif tipo.value == "project":
                allowed.append("src/project.py")
                allowed.append("src/validator.py")
            elif tipo.value == "integration":
                allowed.append("src/cli.py")
                allowed.append("src/database.py")
                allowed.append("src/models.py")
        
        # Adicionar arquivos de teste específicos do objetivo
        test_dir = f"tests/objectives/{objective.id}/"
        allowed.append(test_dir + "*.py")
        
        self._allowed_files = list(set(allowed))  # Remover duplicatas
    
    def get_context_prompt(self) -> str:
        """Gera o prompt de contexto base para IA.
        
        Returns:
            String com o prompt formatado.
        """
        if not self._current_objective:
            return "ERRO: Nenhum objetivo ativo."
        
        obj = self._current_objective
        
        # PROMPT 1 - Contexto base
        prompt = """Você está atuando como IA integrada ao projeto "Plataforma de Orquestração para Vibe Coding".

REGRAS ABSOLUTAS:
- Você só pode trabalhar dentro do objetivo atualmente ativo.
- Você NÃO pode alterar arquivos fora da lista explicitamente permitida.
- Testes são a fonte de verdade.
- Não reestruture o projeto.
- Não refatore código fora do escopo solicitado.
- Não crie novos objetivos.
- Se algo não estiver claro, PARE e peça esclarecimento.

PAPEL:
Você decide COMO implementar.
O sistema decide O QUÊ.

Violação dessas regras é falha grave.

"""
        
        # PROMPT 2 - Ativação de objetivo
        prompt += f"""
OBJETIVO ATIVO: {obj.nome}

DESCRIÇÃO:
{obj.descricao}

TIPOS:
{', '.join(t.value for t in obj.tipos)}

ENTRADAS ESPERADAS:
{', '.join(obj.entradas) if obj.entradas else 'Nenhuma'}

SAÍDAS ESPERADAS:
{', '.join(obj.saidas_esperadas) if obj.saidas_esperadas else 'Nenhuma'}

EFEITOS COLATERAIS PERMITIDOS:
{', '.join(obj.efeitos_colaterais) if obj.efeitos_colaterais else 'Nenhum'}

INVARIANTES:
{', '.join(obj.invariantes) if obj.invariantes else 'Nenhum'}

ARQUIVOS QUE VOCÊ PODE MODIFICAR:
"""
        
        for file in self._allowed_files:
            prompt += f"- {file}\n"
        
        prompt += """
ARQUIVOS FORA DO ESCOPO SÃO PROIBIDOS.
Confirme que entendeu o contrato antes de escrever qualquer código.
"""
        
        return prompt
    
    def get_test_guidance_prompt(self) -> str:
        """Gera o prompt de implementação guiada por testes (PROMPT 3).
        
        Returns:
            String com o prompt formatado.
        """
        if not self._current_objective:
            return ""
        
        prompt = """
IMPLEMENTAÇÃO GUIADA POR TESTES

Antes de escrever código:
1. Leia os testes associados ao objetivo.
2. Explique, em poucas linhas, o comportamento esperado.
3. Aponte quais testes devem passar ao final.

Somente depois disso, implemente o código mínimo necessário
para fazer os testes passarem.

Não implemente funcionalidades extras.
"""
        return prompt
    
    def get_filesystem_restriction_prompt(self) -> str:
        """Gera o prompt de restrição de filesystem (PROMPT 4).
        
        Returns:
            String com o prompt formatado.
        """
        prompt = """
RESTRIÇÃO DE FILESYSTEM (ANTI-DERIVA)
Você está proibido de:
- Criar novos diretórios
- Alterar estrutura canônica
- Apagar arquivos existentes
- Mover arquivos

Se a implementação exigir algo fora disso,
explique o motivo e aguarde autorização explícita.
"""
        return prompt
    
    def generate_action_log_report(
        self,
        files_changed: List[Dict[str, str]],
        tests_impacted: Optional[List[Dict[str, str]]] = None,
        decisions_made: Optional[List[Dict[str, str]]] = None,
        assumptions: Optional[List[str]] = None,
        ia_agent: str = "claude-code"
    ) -> str:
        """Gera relatório de ações da IA no formato especificado (PROMPT 5).
        
        Args:
            files_changed: Lista de dicionários com 'file' e 'description'.
            tests_impacted: Lista de dicionários com 'test' e 'expected_result'.
            decisions_made: Lista de dicionários com 'decision' e 'justification'.
            assumptions: Lista de suposições feitas.
            ia_agent: Identificador do agente IA.
            
        Returns:
            String com relatório formatado.
        """
        if not self._current_objective:
            return "ERRO: Nenhum objetivo ativo."
        
        report = f"""IA_ACTION_LOG:
- Objetivo: {self._current_objective.nome}
- Arquivos alterados:
"""
        
        for file_change in files_changed:
            report += f"  - {file_change['file']}: {file_change['description']}\n"
        
        report += "- Testes impactados:\n"
        if tests_impacted:
            for test in tests_impacted:
                report += f"  - {test['test']}: {test['expected_result']}\n"
        else:
            report += "  - Nenhum teste impactado diretamente\n"
        
        report += "- Decisões tomadas:\n"
        if decisions_made:
            for decision in decisions_made:
                report += f"  - {decision['decision']} → {decision['justification']}\n"
        else:
            report += "  - Nenhuma decisão documentada\n"
        
        report += "- Assunções feitas:\n"
        if assumptions:
            for assumption in assumptions:
                report += f"  - {assumption}\n"
        else:
            report += "  - Nenhuma assunção documentada\n"
        
        # Registrar no banco de dados
        self.action_log.log_action(
            objective_id=self._current_objective.id,
            action_type=IAActionType.CODE_CHANGE,
            files_changed=files_changed,
            tests_impacted=tests_impacted,
            decisions_made=decisions_made,
            assumptions=assumptions,
            ia_agent=ia_agent,
        )
        
        return report
    
    def get_freestyle_block_prompt(self) -> str:
        """Gera o prompt de bloqueio de freestyle (PROMPT 6).
        
        Returns:
            String com o prompt formatado.
        """
        prompt = """
BLOQUEIO EXPLÍCITO DE FREESTYLE
Você NÃO deve:
- "Melhorar" código existente
- Refatorar por estética
- Aplicar padrões não solicitados
- Otimizar performance
- Simplificar arquitetura

Faça exatamente o necessário.
Nada além.
"""
        return prompt
    
    def get_aider_integration_prompt(self) -> str:
        """Gera o prompt de integração com Aider (PROMPT 7).
        
        Returns:
            String com o prompt formatado.
        """
        prompt = """
INTEGRAÇÃO ESPECÍFICA: AIDER (CODER)
Você está operando via Aider.

Modo:
- Implementador
- Código mínimo
- Seguir testes existentes

Não discuta arquitetura.
Não proponha mudanças estruturais.
Implemente e pare.
"""
        return prompt
    
    def get_claude_code_integration_prompt(self) -> str:
        """Gera o prompt de integração com Claude Code (PROMPT 8).
        
        Returns:
            String com o prompt formatado.
        """
        prompt = """
INTEGRAÇÃO ESPECÍFICA: CLAUDE CODE (ARQUITETO)
Você está operando como arquiteto.
"""
        return prompt
    
    def get_full_context(self, mode: str = "default") -> str:
        """Retorna o contexto completo para IA baseado no modo.
        
        Args:
            mode: Modo de operação ("default", "aider", "claude-code").
            
        Returns:
            Contexto completo formatado.
        """
        context = self.get_context_prompt() + "\n"
        
        if mode == "aider":
            context += self.get_aider_integration_prompt() + "\n"
        elif mode == "claude-code":
            context += self.get_claude_code_integration_prompt() + "\n"
        
        context += self.get_test_guidance_prompt() + "\n"
        context += self.get_filesystem_restriction_prompt() + "\n"
        context += self.get_freestyle_block_prompt() + "\n"
        
        return context
