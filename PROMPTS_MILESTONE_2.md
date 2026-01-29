# Prompts Milestone 2 - Geração Automática de Testes

Execute estes prompts na ordem. Cada prompt é autocontido.

---

## PROMPT 0: Correções do Milestone 1

```
Corrija os problemas pendentes do Milestone 1:

1. Atualize src/__init__.py:
   - Alterar __version__ = "0.1.0" para __version__ = "0.2.0"

2. Atualize README.md:
   - Mudar status de "🚧 Em desenvolvimento - Milestone 0" para "🚧 Em desenvolvimento - Milestone 1 ✅ concluído"
   - Adicionar badge: ![Milestone 1](https://img.shields.io/badge/milestone-1%20complete-green)
   - Remover "(Em desenvolvimento)" dos comandos objective new/list
   - Adicionar exemplos de uso:
     ```bash
     # Criar objetivo
     vibe objective new

     # Listar objetivos
     vibe objective list
     vibe objective list --status ATIVO
     vibe objective list --type filesystem --verbose
     ```

3. Fixar validação em src/cli.py (linha ~103):
   - A validação de nome vazio deve exibir mensagem antes de pedir novamente
   - Ajustar lógica do while para garantir que mensagem apareça

Critério de aceitação:
- vibe --version mostra 0.2.0
- README reflete Milestone 1 completo
- teste test_objective_new_validation passa
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe --version  # deve mostrar 0.2.0
pytest tests/test_cli.py::test_objective_new_validation -v
```

---

## PROMPT 1/6: Criar gerador de estrutura de testes

```
Leia scope.md seção "7. Geração automática de testes" e archeture.md.

Crie src/test_generator.py com:

1. Função map_objective_to_test_types(objective: Objective) -> List[str]:
   - Mapeia tipos de objetivo para tipos de teste
   - CLI_COMMAND → ["test_execution", "test_exit_code", "test_output"]
   - FILESYSTEM → ["test_file_creation", "test_structure", "test_idempotence"]
   - STATE → ["test_database_creation", "test_schema", "test_initial_state"]
   - PROJECT → ["test_structure_validation", "test_dependencies"]
   - INTEGRATION → ["test_command_sequence", "test_accumulated_effects"]

2. Função generate_test_directory(objective: Objective) -> Path:
   - Cria diretório tests/objectives/{objective_id}/
   - Retorna Path do diretório criado

3. Função generate_test_file(objective: Objective, test_type: str) -> str:
   - Gera conteúdo do arquivo de teste Python
   - Inclui:
     - Docstring explicando o teste
     - Imports necessários
     - Fixture setup/teardown
     - Função de teste com TODO explícito
     - Assert False no final (para falhar por padrão)

4. Função generate_tests_for_objective(objective: Objective) -> bool:
   - Orquestra geração completa
   - Cria diretório
   - Gera todos os arquivos de teste
   - Retorna True se sucesso

Critério de aceitação:
- Mapeamento correto de tipos
- Estrutura de diretórios criada
- Arquivos de teste válidos
- Testes gerados falham por padrão
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "from src.test_generator import generate_tests_for_objective; print('✓ Generator importado')"
```

---

## PROMPT 2/6: Integrar geração de testes no comando objective new

```
Integre geração automática de testes em src/cli.py.

Modifique a função objective_new():

1. Após persistir objetivo com sucesso (linha ~187):
   - Importar generate_tests_for_objective
   - Chamar generate_tests_for_objective(objective)
   - Capturar resultado

2. Atualizar mensagem de confirmação:
   - Se testes gerados com sucesso:
     ```
     ✅ Objetivo criado com sucesso!
        ID: {id}
        Nome: {nome}
        Status: {status}
        Tipos: {tipos}

     📋 Testes gerados automaticamente:
        - {lista de testes gerados}
        Localização: tests/objectives/{id}/

     ⚠️  Testes estão marcados como TODO e falham por padrão.
        Implemente-os antes de marcar o objetivo como concluído.
     ```
   - Se falhar:
     ```
     ⚠️  Objetivo criado, mas falha ao gerar testes automaticamente.
        Execute: vibe objective generate-tests {id}
     ```

3. Garantir que objetivo não é criado se geração de testes falhar
   - Regra: "Todo objetivo gera testes. Sem exceções."
   - Se gerar testes falhar, fazer rollback da criação do objetivo

Critério de aceitação:
- Testes gerados automaticamente
- Mensagem clara ao usuário
- Rollback se falhar
- Sem opção de desligar geração
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe objective new
# Preencher dados interativamente
# Verificar se diretório de testes foi criado
ls tests/objectives/
```

---

## PROMPT 3/6: Criar comando para regenerar testes

```
Crie comando vibe objective generate-tests em src/cli.py.

Implemente:

@objective.command(name="generate-tests")
@click.argument("objective_id")
def objective_generate_tests(objective_id: str) -> None:
    """Regenera testes para um objetivo existente."""

    1. Buscar objetivo no banco
    2. Validar que objetivo existe
    3. Verificar se já existem testes
    4. Se existirem, perguntar confirmação para sobrescrever
    5. Gerar testes usando test_generator
    6. Exibir resultado

Casos de erro:
- Objetivo não encontrado
- Falha na geração
- Usuário cancela sobrescrita

Critério de aceitação:
- Comando funcional
- Confirmação antes de sobrescrever
- Mensagens claras
- Tratamento de erros
```

**Teste após executar:**
```bash
source .venv/bin/activate
# Criar objetivo primeiro
vibe objective new
# Copiar ID do objetivo
vibe objective generate-tests <ID>
```

---

## PROMPT 4/6: Validar que objetivo não existe sem testes

```
Crie validador para garantir que todo objetivo tem testes.

Em src/validator.py, adicione:

1. Função validate_objective_has_tests(objective_id: str) -> List[str]:
   - Verifica se diretório tests/objectives/{id}/ existe
   - Verifica se há pelo menos 1 arquivo de teste
   - Retorna lista de erros (vazia se válido)

2. Atualizar StructureValidator:
   - Adicionar método validate_objectives_integrity()
   - Para cada objetivo no banco:
     - Validar que tem testes
     - Validar que testes são executáveis
   - Retornar lista de erros

3. Integrar no comando vibe project check:
   - Executar validate_objectives_integrity()
   - Exibir erros se houver
   - Falhar se objetivos sem testes

Critério de aceitação:
- Detecta objetivos sem testes
- Integrado no project check
- Mensagens claras sobre qual objetivo está inválido
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe project check
# Deve passar se todos objetivos têm testes
# Criar objetivo sem testes manualmente para testar detecção
```

---

## PROMPT 5/6: Criar testes para test_generator

```
Crie tests/test_test_generator.py com testes completos.

Testes necessários:

1. test_map_objective_to_test_types():
   - Testar cada tipo de objetivo
   - Validar tipos de teste retornados
   - Testar objetivo com múltiplos tipos

2. test_generate_test_directory():
   - Criar diretório em tmp_path
   - Validar estrutura criada
   - Testar idempotência

3. test_generate_test_file():
   - Gerar arquivo para cada tipo de teste
   - Validar sintaxe Python (compile())
   - Verificar presença de TODO
   - Verificar assert False

4. test_generate_tests_for_objective():
   - Criar objetivo completo
   - Gerar testes
   - Validar todos os arquivos criados
   - Executar testes gerados (devem falhar)

5. test_generated_tests_fail_by_default():
   - Gerar testes
   - Executar com pytest
   - Validar que todos falham

Use tmp_path para isolamento.

Critério de aceitação:
- Todos os testes passam
- Cobertura > 90% em test_generator.py
- Testes isolados
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest tests/test_test_generator.py -v
pytest --cov=src.test_generator --cov-report=term-missing
```

---

## PROMPT 6/6: Atualizar CLI tests e documentação

```
Finalize o Milestone 2 com testes e documentação.

1. Atualize tests/test_cli.py:
   - test_objective_new_generates_tests(): validar geração automática
   - test_objective_new_rollback_on_test_failure(): simular falha e validar rollback
   - test_objective_generate_tests_command(): testar comando de regeneração

2. Atualize CHANGELOG.md:
   - Adicionar seção [0.3.0] - Milestone 2
   - Listar features:
     - Geração automática de testes por objetivo
     - Mapeamento tipo → testes
     - Comando generate-tests
     - Validação de integridade
   - Listar arquivos criados

3. Atualize pyproject.toml:
   - Versão 0.3.0

4. Atualize src/__init__.py:
   - __version__ = "0.3.0"

5. Atualize README.md:
   - Status: Milestone 2 ✅ concluído
   - Badge: ![Milestone 2](https://img.shields.io/badge/milestone-2%20complete-green)
   - Adicionar exemplo:
     ```bash
     # Objetivo gera testes automaticamente
     vibe objective new
     # Testes em: tests/objectives/{id}/

     # Regenerar testes
     vibe objective generate-tests <id>
     ```

Critério de aceitação:
- Todos os testes passam
- CHANGELOG atualizado
- Versão 0.3.0
- README reflete Milestone 2
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest -v
vibe --version  # deve mostrar 0.3.0
git diff README.md CHANGELOG.md
```

---

## Checklist Milestone 2

Após todos os prompts:

- [ ] test_generator.py criado e funcional
- [ ] Geração automática integrada em objective new
- [ ] Comando generate-tests implementado
- [ ] Validação de integridade implementada
- [ ] Testes do gerador passando
- [ ] Testes CLI atualizados
- [ ] Documentação atualizada
- [ ] Versão 0.3.0
- [ ] Rollback funcional se geração falhar

**Critérios de aceite do Milestone 2:**
✅ Criar objetivo gera testes
✅ Testes rodam e falham corretamente
✅ Nenhum objetivo existe sem testes

---

## Comandos úteis

```bash
# Ativar ambiente
source .venv/bin/activate

# Criar objetivo e verificar testes gerados
vibe objective new
ls -R tests/objectives/

# Executar testes gerados (devem falhar)
pytest tests/objectives/ -v

# Validar integridade
vibe project check

# Rodar suite completa
pytest -v --cov=src --cov-report=html

# Verificar cobertura do gerador
pytest --cov=src.test_generator --cov-report=term-missing

# Limpar testes de teste
rm -rf tests/objectives/*
```

---

## Notas importantes

1. **Lei imutável:** Todo objetivo DEVE gerar testes. Sem exceções. Sem opção de desligar.

2. **Testes falham por padrão:** Todos os testes gerados devem ter `assert False` ou equivalente para garantir que precisam ser implementados.

3. **Rollback obrigatório:** Se geração de testes falhar, objetivo NÃO deve ser criado no banco.

4. **Estrutura padrão:** tests/objectives/{objective_id}/test_{tipo}.py

5. **TODO explícito:** Cada teste gerado deve ter comentário claro: `# TODO: Implementar teste para {descrição}`

6. **Validação automática:** `vibe project check` deve detectar objetivos sem testes e falhar.
