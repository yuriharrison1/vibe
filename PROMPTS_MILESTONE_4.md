# Prompts Milestone 4 - Controle de Filesystem e Estrutura

Execute estes prompts na ordem. Cada prompt é autocontido.

---

## PROMPT 0: Corrigir testes falhando do Milestone 3

```
Corrija os 4 testes falhando identificados na revisão do Milestone 3.

1. Corrigir tests/test_test_runner.py:

   Problema: Os testes esperam que test_runner encontre testes em `tmp_path/objectives/{id}/`
   mas o código procura em `base_path/objectives/{id}/`.

   Solução: Ajustar os testes para criar a estrutura correta:
   - Em vez de: tmp_path / "tests" / "objectives" / obj.id
   - Usar: tmp_path / "objectives" / obj.id

   Ou ajustar o parâmetro base_path passado para o runner.

   Arquivos a corrigir:
   - test_run_objective_tests (linha ~32)
   - test_run_objective_tests_with_failure (linha ~70)
   - test_test_results_persisted (linha ~102)

2. Corrigir tests/test_test_generator.py:

   Problema: test_generate_tests_for_objective espera 6 arquivos mas são gerados 7
   (inclui __init__.py além dos 6 testes)

   Solução: Atualizar assertion de:
   ```python
   assert len(test_files) == 6
   ```
   Para:
   ```python
   assert len(test_files) == 7  # 6 testes + __init__.py
   ```

   Ou filtrar apenas arquivos test_*.py:
   ```python
   test_files = [f for f in test_dir.glob("test_*.py")]
   assert len(test_files) == 6
   ```

3. Executar testes para validar correção:
   ```bash
   pytest tests/test_test_runner.py -v
   pytest tests/test_test_generator.py::test_generate_tests_for_objective -v
   ```

Critério de aceitação:
- Todos os 46 testes passando
- pytest -v sem falhas
- test_runner.py funcional em testes
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest -v
# Deve mostrar 46 passed
```

---

## PROMPT 1/8: Expandir validador de estrutura canônica

```
Leia scope.md e archeture.md para entender a estrutura canônica.

Atualize src/validator.py para validações mais rigorosas:

1. Adicionar método validate_directory_structure() -> List[str]:
   - Verificar que APENAS os diretórios permitidos existem na raiz
   - Detectar diretórios não esperados (ex: build/, dist/, node_modules/, etc)
   - Validar que diretórios obrigatórios existem
   - Verificar permissões de leitura/escrita

   Diretórios permitidos na raiz:
   - docs/, objectives/, tests/, scripts/, ai/, state/, src/
   - .git/ (controle de versão)
   - .venv/, venv/ (ambientes virtuais)
   - .pytest_cache/, .mypy_cache/, __pycache__/ (caches de ferramentas)

   Diretórios NÃO permitidos (considerados "lixo"):
   - build/, dist/, *.egg-info/
   - node_modules/, bower_components/
   - .idea/, .vscode/ (exceto se configurado no .gitignore)
   - temp/, tmp/, cache/

2. Adicionar método validate_root_files() -> List[str]:
   - Verificar arquivos obrigatórios: scope.md, archeture.md, milestone.md
   - Detectar arquivos inesperados na raiz
   - Permitir: README.md, LICENSE, .gitignore, pyproject.toml, setup.py
   - Permitir: CHANGELOG.md, STATUS.md, PROMPTS_*.md
   - Avisar sobre: *.log, *.tmp, *.cache na raiz

3. Adicionar método validate_test_structure() -> List[str]:
   - Validar que tests/ contém apenas:
     - test_*.py (testes principais)
     - objectives/ (testes gerados)
     - conftest.py (configuração pytest)
     - __init__.py
   - Detectar arquivos órfãos em tests/
   - Verificar que tests/objectives/ contém apenas diretórios UUID válidos

4. Adicionar método validate_state_integrity() -> List[str]:
   - Verificar que state/ contém apenas:
     - vibe.db (banco principal)
     - backups/ (opcional)
   - Detectar arquivos .db-journal, .db-wal órfãos
   - Validar permissões de escrita

5. Adicionar método detect_junk_files() -> List[str]:
   - Procurar arquivos temporários: *.tmp, *.bak, *~
   - Procurar arquivos de log: *.log
   - Procurar arquivos de swap: .*.swp, .*.swo
   - Procurar diretórios de build: __pycache__ fora de src/
   - Retornar lista de "lixo" encontrado

6. Atualizar método validate_canonical_structure():
   - Chamar todos os novos métodos de validação
   - Consolidar erros
   - Separar erros críticos de avisos

Critério de aceitação:
- Validação completa da estrutura
- Detecção de arquivos/diretórios não esperados
- Separação entre erros e avisos
- Código tipado com mypy
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "
from src.validator import StructureValidator
from pathlib import Path
v = StructureValidator(Path('.'))
errors = v.validate_canonical_structure()
print('Erros encontrados:', len(errors))
for e in errors:
    print(' -', e)
"
```

---

## PROMPT 2/8: Implementar validação de idempotência

```
Crie src/idempotency.py para garantir que comandos são idempotentes.

Implemente:

1. Classe IdempotencyValidator:
   - __init__(db: Database)
   - Registro de operações executadas

2. Método check_objective_new(name: str) -> bool:
   - Verificar se já existe objetivo com mesmo nome
   - Retornar True se pode criar, False se duplicado

3. Método check_test_generation(objective_id: str) -> bool:
   - Verificar se diretório de testes já existe
   - Verificar timestamp de última geração
   - Retornar True se pode gerar, False se já existe recente

4. Método check_project_init(path: Path) -> bool:
   - Verificar se path já é um projeto vibe
   - Verificar se tem state/vibe.db
   - Retornar True se pode inicializar, False se já existe

5. Enum OperationResult:
   - SUCCESS (operação executada)
   - ALREADY_EXISTS (idempotente, sem ação)
   - CONFLICT (erro, não pode executar)

6. Classe CommandHistory:
   - Registrar histórico de comandos executados
   - Timestamp de cada operação
   - Resultado da operação
   - Salvar no SQLite (nova tabela command_history)

7. Schema da tabela command_history:
   - id TEXT PRIMARY KEY (UUID)
   - command TEXT NOT NULL (nome do comando)
   - arguments TEXT (JSON com argumentos)
   - result TEXT NOT NULL (SUCCESS/ALREADY_EXISTS/CONFLICT)
   - executed_at TEXT NOT NULL (timestamp ISO)
   - user TEXT (opcional, para auditoria)

Critério de aceitação:
- Validadores de idempotência implementados
- Histórico de comandos registrado
- Operações duplicadas detectadas
- Código tipado com mypy
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "
from src.idempotency import IdempotencyValidator
from src.database import Database
from pathlib import Path
db = Database(Path('state/vibe.db'))
iv = IdempotencyValidator(db)
print('✓ IdempotencyValidator criado')
"
```

---

## PROMPT 3/8: Integrar idempotência nos comandos CLI

```
Atualize src/cli.py para usar IdempotencyValidator.

Modificar comandos:

1. objective_new():
   - Antes de criar, verificar se nome já existe
   - Se existe: exibir mensagem e ID do existente
   - Perguntar se quer criar mesmo assim ou cancelar
   - Registrar operação no command_history

2. objective_generate_tests():
   - Verificar se testes já existem
   - Se existem e são recentes (< 1 hora): avisar
   - Perguntar confirmação para sobrescrever
   - Registrar operação no command_history

3. project_init():
   - Verificar se diretório já é projeto vibe
   - Se é: exibir mensagem clara
   - Oferecer: [A]bortar, [F]orçar reinicialização
   - Registrar operação no command_history

4. test_run():
   - Verificar se testes foram executados recentemente (< 5 min)
   - Se sim: avisar e perguntar se quer reexecutar
   - Permitir flag --force para pular verificação
   - Registrar operação no command_history

5. Adicionar comando 'vibe history':
   ```bash
   vibe history                  # Últimas 20 operações
   vibe history --all            # Todas as operações
   vibe history --command test   # Filtrar por comando
   vibe history --today          # Operações de hoje
   ```

6. Formato do output de history:
   ```
   📜 Histórico de Comandos

   2026-01-30 14:32:15 | objective new       | SUCCESS        | "Criar API REST"
   2026-01-30 14:35:20 | test run            | SUCCESS        | objective_id=abc123
   2026-01-30 14:40:10 | objective new       | ALREADY_EXISTS | "Criar API REST"
   2026-01-30 14:45:00 | test run --all      | SUCCESS        |
   ```

Critério de aceitação:
- Todos os comandos verificam idempotência
- Mensagens claras sobre operações duplicadas
- Comando history funcional
- Histórico persistido no SQLite
- Opção --force para bypass quando necessário
```

**Teste após executar:**
```bash
source .venv/bin/activate
# Criar objetivo
vibe objective new
# Tentar criar novamente com mesmo nome
vibe objective new
# Ver histórico
vibe history
```

---

## PROMPT 4/8: Criar testes de filesystem

```
Crie tests/test_filesystem_validation.py com testes de estrutura.

Implemente testes:

1. test_canonical_structure_valid():
   - Criar estrutura canônica em tmp_path
   - Validar que não há erros
   - Verificar todos os diretórios obrigatórios

2. test_missing_required_directory():
   - Criar estrutura sem diretório 'docs'
   - Validar que erro é detectado
   - Verificar mensagem de erro

3. test_missing_required_file():
   - Criar estrutura sem 'scope.md'
   - Validar que erro é detectado

4. test_detect_junk_directory():
   - Criar estrutura com diretório 'build/'
   - Validar que é detectado como lixo
   - Verificar lista de junk retornada

5. test_detect_junk_files():
   - Criar arquivos .tmp, .log na raiz
   - Validar detecção de lixo
   - Verificar lista completa

6. test_unauthorized_root_directory():
   - Criar diretório 'node_modules/'
   - Validar que é detectado como não autorizado

7. test_test_directory_structure():
   - Criar tests/ com estrutura válida
   - Adicionar arquivo órfão test_orphan.txt
   - Validar que órfão é detectado

8. test_state_integrity():
   - Criar state/ com vibe.db
   - Adicionar arquivo .db-journal órfão
   - Validar detecção de problema

9. test_objectives_directory_invalid_names():
   - Criar tests/objectives/ com diretório "invalid-name"
   - Validar que não-UUID é detectado

10. test_allowed_exceptions():
    - Criar .git/, .venv/, __pycache__/
    - Validar que são permitidos
    - Verificar que não geram erros

Usar tmp_path e fixtures para isolamento.

Critério de aceitação:
- 10+ testes de filesystem
- Todos os casos cobertos
- Testes isolados
- Cobertura > 90% do validator.py
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest tests/test_filesystem_validation.py -v
pytest --cov=src.validator --cov-report=term-missing
```

---

## PROMPT 5/8: Expandir comando 'vibe project check'

```
Atualize src/cli.py para expandir o comando project check.

Modificar validate() (comando project check):

1. Adicionar seções de validação:
   ```
   🏗️  Estrutura Canônica
   📁 Filesystem
   🗄️  Estado (SQLite)
   🧪 Testes
   📊 Relatório Final
   ```

2. Seção Estrutura Canônica:
   - Validar diretórios obrigatórios
   - Validar arquivos obrigatórios
   - Exibir ✅ ou ❌ para cada item

3. Seção Filesystem:
   - Detectar diretórios não autorizados
   - Detectar lixo (arquivos temporários)
   - Validar estrutura de tests/
   - Validar estrutura de state/
   - Exibir avisos em amarelo, erros em vermelho

4. Seção Estado:
   - Validar que vibe.db existe
   - Validar schema do banco
   - Contar objetivos por status
   - Verificar integridade referencial

5. Seção Testes:
   - Validar que objetivos têm testes
   - Verificar health dos testes
   - Exibir estatísticas de cobertura

6. Relatório Final:
   ```
   📊 Relatório Final

   ✅ Estrutura: OK (7/7 diretórios, 3/3 arquivos)
   ⚠️  Filesystem: 2 avisos (arquivos temporários detectados)
   ✅ Estado: OK (5 objetivos, banco íntegro)
   ❌ Testes: FALHOU (2 objetivos sem testes)

   Resultado: ❌ VALIDAÇÃO FALHOU
   - 1 erro crítico
   - 2 avisos

   Execute 'vibe project clean' para remover lixo.
   ```

7. Adicionar flags:
   - --strict: Tratar avisos como erros
   - --fix: Tentar corrigir problemas automaticamente
   - --verbose: Mostrar detalhes de cada validação
   - --json: Output em formato JSON para CI

8. Exit codes:
   - 0: Tudo OK
   - 1: Avisos encontrados
   - 2: Erros críticos encontrados

Critério de aceitação:
- Validação completa e detalhada
- Output claro e estruturado
- Flags funcionais
- Exit codes corretos
- Relatório final informativo
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe project check
vibe project check --verbose
vibe project check --strict
echo "Exit code: $?"
```

---

## PROMPT 6/8: Implementar comando 'vibe project clean'

```
Crie comando 'vibe project clean' para remover arquivos de lixo.

Adicionar a src/cli.py:

@project.command(name="clean")
@click.option("--dry-run", is_flag=True, help="Mostrar o que seria removido sem remover")
@click.option("--force", is_flag=True, help="Remover sem confirmação")
@click.option("--all", is_flag=True, help="Remover inclusive caches de ferramentas")
def project_clean(dry_run: bool, force: bool, all: bool) -> None:
    """Remove arquivos e diretórios temporários do projeto."""

1. Itens a remover (padrão):
   - Arquivos: *.tmp, *.bak, *~, *.log
   - Diretórios: build/, dist/, *.egg-info/
   - Diretórios não autorizados: node_modules/, temp/, tmp/

2. Itens a remover (com --all):
   - Todos os acima
   - Caches: __pycache__/, .pytest_cache/, .mypy_cache/
   - Build artifacts: .eggs/, htmlcov/

3. Itens NUNCA removidos:
   - .git/ (controle de versão)
   - .venv/, venv/ (ambientes virtuais)
   - state/vibe.db (banco de dados)
   - src/, tests/, docs/ (código e documentação)

4. Fluxo de execução:
   - Escanear projeto buscando lixo
   - Se --dry-run: apenas listar
   - Se não --force: pedir confirmação
   - Remover itens confirmados
   - Exibir relatório final

5. Output:
   ```
   🧹 Limpeza do Projeto

   Arquivos a remover:
   - ./test.log (512 KB)
   - ./debug.tmp (1.2 MB)

   Diretórios a remover:
   - ./build/ (15 MB)
   - ./__pycache__/ (2 MB)

   Total: 18.7 MB em 4 itens

   Confirma remoção? [s/N]: s

   ✅ Removido: 18.7 MB
   ✅ Projeto limpo!
   ```

6. Integração com IdempotencyValidator:
   - Registrar operação no command_history
   - Listar itens removidos

7. Segurança:
   - Nunca remover arquivos rastreados pelo git
   - Backup automático de arquivos > 10 MB antes de remover
   - Confirmar remoção de diretórios grandes

Critério de aceitação:
- Comando funcional
- Dry-run mostra o que seria feito
- Confirmação obrigatória (exceto com --force)
- Proteção contra remoção acidental
- Relatório claro de operações
```

**Teste após executar:**
```bash
source .venv/bin/activate
# Criar lixo para testar
touch test.log debug.tmp
mkdir -p build
# Testar dry-run
vibe project clean --dry-run
# Limpar
vibe project clean --force
```

---

## PROMPT 7/8: Criar testes de idempotência

```
Crie tests/test_idempotency.py com testes de idempotência.

Implemente testes:

1. test_objective_new_duplicate_name():
   - Criar objetivo com nome "Test"
   - Tentar criar outro com mesmo nome
   - Validar que idempotência é detectada

2. test_generate_tests_already_exists():
   - Criar objetivo e gerar testes
   - Tentar gerar testes novamente
   - Validar que detecta testes existentes

3. test_project_init_already_initialized():
   - Inicializar projeto em tmp_path
   - Tentar inicializar novamente
   - Validar que detecta projeto existente

4. test_command_history_recorded():
   - Executar várias operações
   - Verificar que todas foram registradas
   - Validar timestamps e resultados

5. test_idempotency_success():
   - Executar comando idempotente 2x
   - Verificar que segunda vez retorna ALREADY_EXISTS
   - Validar que histórico tem ambas as execuções

6. test_idempotency_force_bypass():
   - Executar comando com --force
   - Validar que idempotência é ignorada
   - Verificar que operação é executada

7. test_history_command():
   - Criar histórico de 10 comandos
   - Testar filtros (--command, --today)
   - Validar output

8. test_operation_result_enum():
   - Testar todos os valores de OperationResult
   - Validar serialização/deserialização

Use tmp_path e mock do pytest.

Critério de aceitação:
- 8+ testes de idempotência
- Cobertura > 90% de idempotency.py
- Testes isolados
- Todos passando
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest tests/test_idempotency.py -v
pytest --cov=src.idempotency --cov-report=term-missing
```

---

## PROMPT 8/8: Atualizar testes CLI e documentação

```
Finalize o Milestone 4 com testes e documentação.

1. Atualize tests/test_cli.py:
   - test_project_check_expanded(): testar novo formato detalhado
   - test_project_check_strict(): testar flag --strict
   - test_project_check_verbose(): testar flag --verbose
   - test_project_check_json(): testar output JSON
   - test_project_clean_dry_run(): testar dry-run
   - test_project_clean_force(): testar remoção com --force
   - test_history_command(): testar comando history
   - test_idempotency_in_commands(): testar idempotência nos comandos

2. Atualize tests/test_validator.py:
   - test_validate_directory_structure()
   - test_validate_root_files()
   - test_detect_junk_files()
   - test_validate_test_structure()
   - test_validate_state_integrity()

3. Atualize CHANGELOG.md:
   - Adicionar seção [0.5.0] - Milestone 4
   - Listar features:
     - Validação expandida de estrutura canônica
     - Detecção de arquivos/diretórios não autorizados
     - Sistema de idempotência para comandos
     - Histórico de comandos (command_history)
     - Comando `vibe project clean`
     - Comando `vibe history`
     - Validação rigorosa em `project check`
     - Flags --strict, --fix, --verbose, --json
   - Listar arquivos criados:
     - src/idempotency.py
     - tests/test_filesystem_validation.py
     - tests/test_idempotency.py
   - Listar arquivos modificados:
     - src/validator.py (validações expandidas)
     - src/cli.py (novos comandos e flags)
     - src/database.py (tabela command_history)

4. Atualize pyproject.toml:
   - Versão: 0.5.0

5. Atualize src/__init__.py:
   - __version__ = "0.5.0"

6. Atualize README.md:
   - Status: Milestone 4 ✅ concluído
   - Badge: ![Milestone 4](https://img.shields.io/badge/milestone-4%20complete-green)
   - Adicionar exemplos:
     ```bash
     # Validação completa do projeto
     vibe project check
     vibe project check --verbose
     vibe project check --strict

     # Limpeza de arquivos temporários
     vibe project clean --dry-run
     vibe project clean --force

     # Histórico de comandos
     vibe history
     vibe history --today
     ```

7. Atualize STATUS.md:
   - Marcar Milestone 4 como concluído
   - Atualizar seção "Próximo Milestone" para Milestone 5

Critério de aceitação:
- Todos os testes passam
- Cobertura > 80% nos novos arquivos
- CHANGELOG atualizado
- Versão 0.5.0
- README reflete Milestone 4
- Documentação clara e completa
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest -v
pytest --cov=src --cov-report=html
vibe --version  # deve mostrar 0.5.0
vibe project check --verbose
git diff README.md CHANGELOG.md
```

---

## Checklist Milestone 4

Após todos os prompts:

- [ ] Testes do Milestone 3 corrigidos
- [ ] Validador expandido (detect_junk, validate_root_files, etc)
- [ ] Sistema de idempotência implementado
- [ ] Histórico de comandos (command_history)
- [ ] Comando `vibe history` funcional
- [ ] Comando `vibe project clean` funcional
- [ ] `project check` expandido com relatório detalhado
- [ ] Flags --strict, --verbose, --json, --fix
- [ ] Testes de filesystem passando
- [ ] Testes de idempotência passando
- [ ] Testes de CLI atualizados
- [ ] Documentação atualizada
- [ ] Versão 0.5.0

**Critérios de aceite do Milestone 4:**
✅ Estrutura inválida é detectada
✅ Comandos são idempotentes
✅ Projeto pode ser validado a qualquer momento

---

## Comandos úteis

```bash
# Ativar ambiente
source .venv/bin/activate

# Validação completa
vibe project check
vibe project check --verbose
vibe project check --strict

# Limpeza
vibe project clean --dry-run
vibe project clean --force
vibe project clean --all

# Histórico
vibe history
vibe history --command test
vibe history --today

# Rodar testes
pytest -v
pytest tests/test_filesystem_validation.py -v
pytest tests/test_idempotency.py -v

# Verificar cobertura
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Criar lixo para testar
touch test.log debug.tmp
mkdir -p build dist

# Testar idempotência
vibe objective new  # Criar
vibe objective new  # Tentar duplicar (deve detectar)
```

---

## Notas importantes

1. **Estrutura canônica é lei:** Apenas diretórios e arquivos permitidos podem existir. Resto é lixo.

2. **Idempotência é obrigatória:** Comandos executados múltiplas vezes devem produzir o mesmo resultado sem efeitos colaterais.

3. **Auditoria completa:** Todo comando é registrado no command_history para rastreabilidade.

4. **Limpeza segura:** `project clean` nunca remove código, apenas lixo. Sempre confirma antes de remover.

5. **Validação rigorosa:** `project check` detecta qualquer deriva da estrutura canônica.

6. **Exit codes corretos:** Comandos retornam códigos apropriados para integração com CI/CD.

7. **Proteção contra perda:** Backups automáticos antes de operações destrutivas.

---

## Integração com Milestones anteriores

Este milestone fortalece:
- **Milestone 0:** Estrutura canônica agora é validada rigorosamente
- **Milestone 1:** Objetivos agora têm proteção contra duplicação
- **Milestone 2:** Geração de testes agora verifica idempotência
- **Milestone 3:** Execução de testes integrada com validação de estrutura

---

## Preparação para Milestone 5

O Milestone 4 estabelece a base para o Milestone 5 (Integração com IA):
- Estrutura validada e controlada
- Histórico de comandos para auditoria
- Sistema pronto para limitar arquivos alteráveis pela IA
- Validação rigorosa para detectar mudanças não autorizadas

---

## Dependências

Nenhuma dependência adicional necessária. Tudo usa biblioteca padrão do Python.

---

## Troubleshooting

**Problema:** `vibe project check` falha com erro de permissão
**Solução:** Verificar permissões de leitura em todos os diretórios

**Problema:** `vibe project clean` remove arquivos importantes
**Solução:** NUNCA acontece - há proteção múltipla contra isso. Se acontecer, é bug crítico.

**Problema:** Testes de filesystem falham em Windows
**Solução:** Ajustar paths usando pathlib.Path para compatibilidade

**Problema:** Command history não registra
**Solução:** Verificar que tabela command_history foi criada no banco
