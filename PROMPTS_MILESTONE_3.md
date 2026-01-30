# Prompts Milestone 3 - Execução e Tracking de Testes

Execute estes prompts na ordem. Cada prompt é autocontido.

---

## PROMPT 0: Atualizar documentação Milestone 2

```
Atualize a documentação para refletir a conclusão do Milestone 2.

1. Atualize CHANGELOG.md:
   - Adicionar seção [0.3.0] - Milestone 2
   - Listar features implementadas:
     - Geração automática de testes (`src/test_generator.py`)
     - Integração automática em `objective new`
     - Comando `vibe objective generate-tests <id>`
     - Validação de integridade em `project check`
     - Rollback se falha na geração
   - Listar testes criados:
     - `tests/test_test_generator.py`
     - Testes de integração CLI atualizados

2. Verifique pyproject.toml:
   - Confirmar versão 0.3.0

3. Verifique src/__init__.py:
   - Confirmar __version__ = "0.3.0"

Critério de aceitação:
- CHANGELOG completo e atualizado
- Versão 0.3.0 consistente em todos os arquivos
- Documentação reflete estado atual do projeto
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe --version  # deve mostrar 0.3.0
cat CHANGELOG.md | head -50
```

---

## PROMPT 1/7: Estender schema SQLite para tracking de testes

```
Leia scope.md seção "9. Persistência" e archeture.md.

Atualize src/database.py para adicionar tracking de testes:

1. Nova tabela test_runs:
   - id TEXT PRIMARY KEY (UUID)
   - objective_id TEXT NOT NULL (FK para objectives.id)
   - test_file TEXT NOT NULL (caminho relativo do arquivo de teste)
   - test_name TEXT NOT NULL (nome da função de teste)
   - status TEXT NOT NULL (PASSED, FAILED, SKIPPED, ERROR)
   - error_message TEXT (mensagem de erro se falhou)
   - duration REAL (duração em segundos)
   - run_at TEXT NOT NULL (timestamp ISO)
   - FOREIGN KEY (objective_id) REFERENCES objectives(id)

2. Nova tabela test_summary:
   - id TEXT PRIMARY KEY (UUID)
   - objective_id TEXT NOT NULL (FK)
   - total_tests INTEGER NOT NULL
   - passed INTEGER NOT NULL
   - failed INTEGER NOT NULL
   - skipped INTEGER NOT NULL
   - error INTEGER NOT NULL
   - last_run TEXT NOT NULL (timestamp ISO)
   - FOREIGN KEY (objective_id) REFERENCES objectives(id)

3. Adicionar métodos à classe Database:
   - save_test_run(test_run: TestRun) -> bool
   - get_test_runs(objective_id: str) -> List[TestRun]
   - get_latest_test_run(objective_id: str) -> Optional[TestRun]
   - save_test_summary(summary: TestSummary) -> bool
   - get_test_summary(objective_id: str) -> Optional[TestSummary]
   - update_test_summary(objective_id: str, summary: TestSummary) -> bool

4. Migração automática:
   - Detectar tabelas inexistentes
   - Criar novas tabelas se necessário
   - Preservar dados existentes

Critério de aceitação:
- Schema estendido com novas tabelas
- Métodos CRUD funcionais
- Migração automática sem perda de dados
- Foreign keys funcionando corretamente
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "
from src.database import Database
from pathlib import Path
db = Database(Path('test_migration.db'))
print('✓ Schema migrado com sucesso')
"
rm -f test_migration.db
```

---

## PROMPT 2/7: Criar modelos para test runs e summary

```
Atualize src/models.py para adicionar modelos de tracking.

1. Classe TestStatus (Enum):
   - PASSED
   - FAILED
   - SKIPPED
   - ERROR

2. Classe TestRun (dataclass):
   - id: str (UUID)
   - objective_id: str
   - test_file: str (Path relativo)
   - test_name: str
   - status: TestStatus
   - error_message: Optional[str]
   - duration: float (segundos)
   - run_at: datetime

3. Classe TestSummary (dataclass):
   - id: str (UUID)
   - objective_id: str
   - total_tests: int
   - passed: int
   - failed: int
   - skipped: int
   - error: int
   - last_run: datetime

4. Adicionar métodos:
   - to_dict() para ambas as classes
   - from_dict() para ambas as classes
   - Método TestSummary.is_passing() -> bool (True se todos passaram)
   - Método TestSummary.success_rate() -> float (% de testes passando)

Critério de aceitação:
- Modelos tipados com mypy
- Serialização/deserialização funcional
- Métodos auxiliares implementados
- Validação de campos obrigatórios
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "
from src.models import TestRun, TestSummary, TestStatus
from datetime import datetime
run = TestRun(
    id='test-id',
    objective_id='obj-id',
    test_file='test.py',
    test_name='test_foo',
    status=TestStatus.PASSED,
    error_message=None,
    duration=0.5,
    run_at=datetime.now()
)
print('✓ Models criados:', run.test_name)
"
```

---

## PROMPT 3/7: Criar executor de testes (test runner)

```
Crie src/test_runner.py para executar testes e coletar resultados.

Implemente:

1. Classe TestRunner:
   - __init__(db: Database)
   - Configuração do pytest programaticamente

2. Método run_objective_tests(objective_id: str) -> TestSummary:
   - Localizar diretório de testes: tests/objectives/{objective_id}/
   - Validar que diretório existe
   - Executar pytest programaticamente usando pytest.main() ou subprocess
   - Capturar resultados de cada teste
   - Parsear output do pytest (usar --json-report se disponível, ou --verbose)
   - Criar TestRun para cada teste executado
   - Salvar TestRuns no banco
   - Calcular TestSummary
   - Salvar TestSummary no banco
   - Retornar TestSummary

3. Método run_all_tests() -> Dict[str, TestSummary]:
   - Buscar todos os objetivos no banco
   - Para cada objetivo, executar run_objective_tests()
   - Retornar dict {objective_id: TestSummary}

4. Tratamento de erros:
   - Objetivo sem diretório de testes
   - Testes com erro de sintaxe
   - Testes que não executam
   - Timeout de execução

5. Output formatado:
   - Exibir progresso durante execução
   - Mostrar cada teste executado
   - Resumo final com estatísticas

Critério de aceitação:
- Execução programática de pytest funcional
- Resultados capturados corretamente
- Persistência automática de resultados
- Tratamento robusto de erros
- Output claro e informativo
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "
from src.test_runner import TestRunner
from src.database import Database
from pathlib import Path
db = Database(Path('state/vibe.db'))
runner = TestRunner(db)
print('✓ TestRunner criado')
"
```

---

## PROMPT 4/7: Implementar comando 'vibe test run'

```
Crie grupo de comandos 'test' em src/cli.py.

Implemente:

@cli.group()
def test():
    """Gerencia execução de testes."""
    pass

@test.command(name="run")
@click.argument("objective_id", required=False)
@click.option("--all", is_flag=True, help="Executar testes de todos os objetivos")
@click.option("--verbose", "-v", is_flag=True, help="Mostrar output detalhado")
def test_run(objective_id: Optional[str], all: bool, verbose: bool) -> None:
    """Executa testes de um objetivo específico ou todos."""

    1. Validações:
       - Se não passar --all nem objective_id: erro com mensagem
       - Se passar ambos: erro com mensagem
       - Se objetivo não existir: erro
       - Se objetivo não tiver testes: aviso

    2. Execução:
       - Criar TestRunner
       - Se objective_id: executar run_objective_tests()
       - Se --all: executar run_all_tests()
       - Exibir progresso em tempo real

    3. Output:
       - Modo normal: resumo compacto
         ```
         🧪 Executando testes para objetivo: {nome}

         ✅ test_foo.py::test_basic ... PASSED (0.5s)
         ❌ test_bar.py::test_edge ... FAILED (0.2s)

         📊 Resultado:
            Total: 2
            ✅ Passou: 1
            ❌ Falhou: 1
            Taxa de sucesso: 50%
         ```

       - Modo verbose: mostrar detalhes de erros
         ```
         ❌ test_bar.py::test_edge
            AssertionError: expected True, got False
            > assert result == expected
         ```

    4. Exit code:
       - 0 se todos passaram
       - 1 se algum falhou
       - 2 se erro de execução

Critério de aceitação:
- Comando funcional com validações
- Output claro e formatado
- Modo verbose detalhado
- Exit code correto
- Integração com TestRunner
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe test --help
# Criar objetivo com testes primeiro
vibe objective new
# Copiar ID e executar
vibe test run <ID>
vibe test run --all
```

---

## PROMPT 5/7: Implementar comando 'vibe objective status'

```
Adicione comando status ao grupo objective em src/cli.py.

Implemente:

@objective.command(name="status")
@click.argument("objective_id", required=False)
@click.option("--all", is_flag=True, help="Status de todos os objetivos")
@click.option("--verbose", "-v", is_flag=True, help="Mostrar detalhes dos testes")
def objective_status(objective_id: Optional[str], all: bool, verbose: bool) -> None:
    """Exibe status de testes de um ou todos os objetivos."""

    1. Se objective_id fornecido:
       - Buscar objetivo no banco
       - Buscar último TestSummary
       - Exibir status do objetivo:
         ```
         📋 Objetivo: {nome}
         ID: {id}
         Status: {status}
         Tipo(s): {tipos}

         🧪 Testes:
            Última execução: {timestamp}
            Total: {total}
            ✅ Passou: {passed}
            ❌ Falhou: {failed}
            ⏭️  Pulado: {skipped}
            ⚠️  Erro: {error}
            Taxa de sucesso: {rate}%

         Estado: {"✅ APROVADO" se todos passaram else "❌ FALHOU"}
         ```

    2. Se --all:
       - Listar todos os objetivos
       - Para cada um, mostrar resumo compacto:
         ```
         abc123de | Criar CLI | ✅ 5/5 (100%) | Última execução: 2h atrás
         def456gh | Validador | ❌ 3/5 (60%)  | Última execução: 1h atrás
         ```

    3. Se --verbose:
       - Mostrar lista de testes individuais
       - Incluir nomes dos arquivos de teste
       - Mostrar duração de cada teste

    4. Casos especiais:
       - Objetivo sem testes ainda executados: "⏸️  Testes não executados"
       - Objetivo sem diretório de testes: "⚠️  Testes não gerados"

Critério de aceitação:
- Status preciso refletindo realidade
- Formatação clara e informativa
- Modo all com visão geral
- Modo verbose com detalhes
- Timestamp humanizado (ex: "2h atrás")
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe objective status <ID>
vibe objective status --all
vibe objective status <ID> --verbose
```

---

## PROMPT 6/7: Implementar health check no 'vibe project check'

```
Atualize src/validator.py para incluir validação de testes.

Adicione ao StructureValidator:

1. Método check_test_health() -> List[str]:
   - Para cada objetivo no banco:
     - Verificar se tem testes gerados
     - Verificar se testes foram executados
     - Verificar se testes estão passando
   - Retornar lista de problemas encontrados:
     - "Objetivo {id} não tem testes gerados"
     - "Objetivo {id} nunca teve testes executados"
     - "Objetivo {id} tem testes falhando ({failed}/{total})"
     - "Objetivo {id} marcado como CONCLUIDO mas testes falhando"

2. Atualizar método validate() em src/cli.py:
   - Adicionar seção "🧪 Validação de Testes"
   - Chamar check_test_health()
   - Exibir problemas encontrados
   - Falhar se:
     - Objetivo marcado como CONCLUIDO com testes falhando
     - Objetivo ATIVO sem testes executados há mais de 24h

3. Adicionar warnings (não bloqueia):
   - Testes nunca executados
   - Taxa de sucesso < 100%

4. Output esperado:
   ```
   🧪 Validação de Testes

   ✅ Objetivo abc123: 5/5 testes passando
   ⚠️  Objetivo def456: 3/5 testes passando (60%)
   ❌ Objetivo ghi789: Marcado como CONCLUIDO mas 2 testes falhando

   Resultado: ❌ FALHOU
   Problemas encontrados: 1
   Avisos: 1
   ```

Critério de aceitação:
- Validação de saúde dos testes implementada
- Bloqueio de objetivos concluídos com testes falhando
- Warnings informativos
- Integração com vibe project check
- Mensagens claras
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe project check
# Deve validar testes além da estrutura
```

---

## PROMPT 7/7: Criar testes e atualizar documentação

```
Finalize o Milestone 3 com testes e documentação.

1. Crie tests/test_test_runner.py:
   - test_run_objective_tests(): criar objetivo, gerar testes, executar
   - test_run_all_tests(): múltiplos objetivos
   - test_test_results_persisted(): verificar persistência no banco
   - test_summary_calculation(): validar cálculos de summary
   - test_error_handling(): testar casos de erro
   - Usar tmp_path e mock do pytest

2. Atualize tests/test_cli.py:
   - test_test_run_command(): testar comando test run
   - test_test_run_all(): testar --all flag
   - test_objective_status(): testar comando status
   - test_objective_status_all(): testar status --all
   - test_health_check_integration(): validar integração com project check

3. Atualize tests/test_database.py:
   - test_test_runs_crud(): testar métodos de TestRun
   - test_test_summary_crud(): testar métodos de TestSummary
   - test_foreign_key_constraint(): validar constraints

4. Atualize CHANGELOG.md:
   - Adicionar seção [0.4.0] - Milestone 3
   - Listar features:
     - Execução de testes via CLI (`vibe test run`)
     - Tracking de resultados no SQLite
     - Comando `vibe objective status`
     - Health check integrado em `vibe project check`
     - TestRunner com execução programática
   - Listar arquivos criados:
     - src/test_runner.py
     - Novos modelos: TestRun, TestSummary, TestStatus
     - Novas tabelas: test_runs, test_summary
     - tests/test_test_runner.py

5. Atualize pyproject.toml:
   - Versão: 0.4.0

6. Atualize src/__init__.py:
   - __version__ = "0.4.0"

7. Atualize README.md:
   - Status: Milestone 3 ✅ concluído
   - Badge: ![Milestone 3](https://img.shields.io/badge/milestone-3%20complete-green)
   - Adicionar exemplos:
     ```bash
     # Executar testes de um objetivo
     vibe test run <ID>

     # Executar todos os testes
     vibe test run --all

     # Ver status dos testes
     vibe objective status <ID>
     vibe objective status --all

     # Health check do projeto
     vibe project check
     ```

Critério de aceitação:
- Todos os testes passam
- Cobertura > 80% nos novos arquivos
- CHANGELOG atualizado
- Versão 0.4.0
- README reflete Milestone 3
- Documentação clara e completa
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest -v
pytest --cov=src --cov-report=html
vibe --version  # deve mostrar 0.4.0
git diff README.md CHANGELOG.md
```

---

## Checklist Milestone 3

Após todos os prompts:

- [ ] Schema SQLite estendido (test_runs, test_summary)
- [ ] Modelos TestRun e TestSummary criados
- [ ] TestRunner implementado
- [ ] Comando `vibe test run` funcional
- [ ] Comando `vibe objective status` funcional
- [ ] Health check integrado em `project check`
- [ ] Testes do test_runner passando
- [ ] Testes de CLI atualizados
- [ ] Testes de database atualizados
- [ ] Documentação atualizada
- [ ] Versão 0.4.0

**Critérios de aceite do Milestone 3:**
✅ Status reflete realidade
✅ Falha bloqueia progresso
✅ Estado persistente correto

---

## Comandos úteis

```bash
# Ativar ambiente
source .venv/bin/activate

# Criar objetivo e gerar testes
vibe objective new

# Executar testes de um objetivo
vibe test run <ID>

# Executar todos os testes
vibe test run --all --verbose

# Ver status
vibe objective status <ID>
vibe objective status --all

# Health check completo
vibe project check

# Rodar suite completa de testes
pytest -v --cov=src --cov-report=html

# Verificar cobertura do test_runner
pytest --cov=src.test_runner --cov-report=term-missing

# Limpar database de teste
rm -f state/vibe.db
rm -rf tests/objectives/*
```

---

## Notas importantes

1. **Estado é verdade:** O banco SQLite sempre reflete o estado real dos testes. Nada é assumido.

2. **Execução obrigatória:** Antes de marcar objetivo como CONCLUIDO, testes devem ser executados e passar.

3. **Bloqueio automático:** `project check` falha se objetivo concluído tem testes falhando.

4. **Rastreabilidade completa:** Cada execução de teste é registrada com timestamp, duração e resultado.

5. **Health check contínuo:** Validação de saúde dos testes é parte integral do `project check`.

6. **Exit codes corretos:** Comandos retornam códigos apropriados para integração com CI/CD.

7. **Output informativo:** Sempre mostrar progresso, estatísticas e estado atual de forma clara.

---

## Dependências adicionais

Caso precise instalar plugin do pytest para JSON report:

```bash
pip install pytest-json-report
```

Ou use parsing do output verbose do pytest diretamente (preferível para manter dependências mínimas).

---

## Integração futura (Milestone 4+)

Este milestone prepara o terreno para:
- Bloqueio automático de avanço se testes falharem
- Integração com pre-commit hooks
- Validação antes de permitir IA modificar código
- Dashboards de qualidade
- Histórico de execuções para detecção de regressão
