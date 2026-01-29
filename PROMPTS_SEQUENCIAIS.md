# Prompts Sequenciais para Aider

Execute estes prompts na ordem. Cada prompt é autocontido e pode ser copiado direto para o Aider.

---

## PROMPT 1/8: Atualizar README com documentação completa

```
Atualize o README.md com instruções completas para desenvolvedores.

Adicione as seguintes seções:

1. **Instalação** (substituir seção atual):
   - Pré-requisitos: Python 3.13+, git, sqlite
   - Instruções para Fedora 43: ./install-dev.sh
   - Instruções genéricas: pip install, ativar venv
   - Como executar install-dev.sh

2. **Desenvolvimento**:
   - Como instalar em modo edição: pip install -e .
   - Como rodar testes: pytest -v
   - Como rodar cobertura: pytest --cov=src --cov-report=term-missing
   - Como rodar pre-commit manualmente: pre-commit run --all-files
   - Como validar estrutura: vibe project check

3. **Comandos disponíveis**:
   - vibe --version
   - vibe --help
   - vibe project check [PATH] - Valida estrutura canônica do projeto
   - vibe project init [PATH] - Inicializa novo projeto com estrutura canônica
   - vibe objective new - (Em desenvolvimento)
   - vibe objective list - (Em desenvolvimento)

4. Adicione badge:
   - ![Milestone 0](https://img.shields.io/badge/milestone-0%20complete-green)

Mantenha as seções existentes: Visão, Status, Documentação, Estrutura, Princípios.

Critério de aceitação:
- README claro, completo e bem formatado
- Todas as instruções testáveis
- Exemplos funcionais
```

**Teste após executar:**
```bash
# Validar markdown
cat README.md | head -100
```

---

## PROMPT 2/8: Criar modelo de dados para objetivos (SQLite)

```
Leia scope.md e archeture.md para entender o modelo de objetivos.

Crie src/models.py com:

1. Classe ObjectiveType (Enum):
   - CLI_COMMAND
   - FILESYSTEM
   - STATE
   - PROJECT
   - INTEGRATION

2. Classe ObjectiveStatus (Enum):
   - DEFINIDO
   - ATIVO
   - BLOQUEADO
   - CONCLUIDO
   - FALHOU

3. Classe Objective (dataclass):
   - id: str (UUID)
   - nome: str
   - descricao: str
   - tipos: List[ObjectiveType]
   - entradas: List[str]
   - saidas_esperadas: List[str]
   - efeitos_colaterais: List[str]
   - invariantes: List[str]
   - status: ObjectiveStatus
   - created_at: datetime
   - updated_at: datetime

4. Função to_dict() para serialização
5. Função from_dict() para deserialização

Critério de aceitação:
- Tipos bem definidos
- Validação de campos obrigatórios
- Código tipado com mypy
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "from src.models import Objective, ObjectiveType, ObjectiveStatus; print('✓ Models importados')"
```

---

## PROMPT 3/8: Criar camada de persistência SQLite

```
Crie src/database.py com gerenciamento de banco SQLite.

Implemente:

1. Classe Database:
   - __init__(db_path: Path)
   - Conexão com SQLite
   - Criação automática do schema

2. Schema (tabela objectives):
   - id TEXT PRIMARY KEY
   - nome TEXT NOT NULL
   - descricao TEXT NOT NULL
   - tipos TEXT NOT NULL (JSON array)
   - entradas TEXT (JSON array)
   - saidas_esperadas TEXT (JSON array)
   - efeitos_colaterais TEXT (JSON array)
   - invariantes TEXT (JSON array)
   - status TEXT NOT NULL
   - created_at TEXT NOT NULL
   - updated_at TEXT NOT NULL

3. Métodos:
   - create_objective(objective: Objective) -> bool
   - get_objective(id: str) -> Optional[Objective]
   - list_objectives() -> List[Objective]
   - update_objective(objective: Objective) -> bool
   - delete_objective(id: str) -> bool

4. Context manager para conexões

Critério de aceitação:
- Schema criado automaticamente
- CRUD completo
- Serialização JSON para arrays
- Tratamento de erros
```

**Teste após executar:**
```bash
source .venv/bin/activate
python -c "from src.database import Database; from pathlib import Path; db = Database(Path('test.db')); print('✓ Database criado')"
rm -f test.db
```

---

## PROMPT 4/8: Implementar comando 'vibe objective new'

```
Implemente o comando interativo para criar objetivos.

Atualize src/cli.py:

1. Remova "Em desenvolvimento" do comando objective new
2. Implemente com prompts interativos usando click.prompt():
   - Nome do objetivo (obrigatório)
   - Descrição (obrigatória)
   - Tipos (múltipla escolha: cli-command, filesystem, state, project, integration)
   - Entradas (lista separada por vírgula, opcional)
   - Saídas esperadas (lista separada por vírgula, opcional)
   - Efeitos colaterais (lista separada por vírgula, opcional)
   - Invariantes (lista separada por vírgula, opcional)

3. Após coletar dados:
   - Criar objeto Objective
   - Persistir no SQLite (state/vibe.db)
   - Exibir confirmação com ID gerado
   - Informar que testes serão gerados (placeholder por enquanto)

4. Validações:
   - Nome não vazio
   - Descrição não vazia
   - Pelo menos um tipo selecionado

Critério de aceitação:
- Comando interativo funcional
- Objetivo persistido no banco
- Validação de campos
- Mensagens claras ao usuário
```

**Teste após executar:**
```bash
source .venv/bin/activate
# Teste interativo (você precisará preencher)
vibe objective new
# Verificar se foi criado
ls -la state/
```

---

## PROMPT 5/8: Implementar comando 'vibe objective list'

```
Implemente comando para listar objetivos.

Atualize src/cli.py:

1. Remova "Em desenvolvimento" do comando objective list
2. Implemente:
   - Carregar todos os objetivos do banco
   - Exibir em formato tabular ou lista
   - Mostrar: ID (primeiros 8 chars), Nome, Status, Tipos

3. Opções:
   - --status <status>: filtrar por status
   - --type <type>: filtrar por tipo
   - --verbose: mostrar detalhes completos

4. Casos especiais:
   - Se não houver objetivos: "Nenhum objetivo encontrado. Use 'vibe objective new' para criar."
   - Colorir status: CONCLUIDO=verde, FALHOU=vermelho, ATIVO=amarelo, outros=branco

Critério de aceitação:
- Lista formatada e legível
- Filtros funcionais
- Modo verbose completo
- Mensagens para lista vazia
```

**Teste após executar:**
```bash
source .venv/bin/activate
vibe objective list
vibe objective list --verbose
vibe objective list --status DEFINIDO
```

---

## PROMPT 6/8: Criar testes para models e database

```
Crie testes completos para as novas funcionalidades.

Crie tests/test_models.py:
- Teste criação de Objective
- Teste serialização to_dict()
- Teste deserialização from_dict()
- Teste validação de campos
- Teste Enums

Crie tests/test_database.py:
- Teste criação de database (usar tmp_path)
- Teste CRUD completo
- Teste get de objetivo inexistente
- Teste list vazio
- Teste persistência entre conexões

Use fixtures do pytest para criar database temporário.

Critério de aceitação:
- Todos os testes passam
- Cobertura > 80% nos novos arquivos
- Testes isolados (tmp_path)
- Não deixar arquivos .db no projeto
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest tests/test_models.py -v
pytest tests/test_database.py -v
pytest --cov=src --cov-report=term-missing
```

---

## PROMPT 7/8: Criar testes de integração CLI para objetivos

```
Crie testes de integração para os comandos de objetivos.

Atualize tests/test_cli.py:

Adicione testes:
- test_objective_new_interactive(): simular entrada do usuário com CliRunner.invoke(input=...)
- test_objective_list_empty(): listar quando não há objetivos
- test_objective_list_with_data(): criar objetivo e listar
- test_objective_list_filters(): testar filtros --status e --type
- test_objective_new_validation(): testar validações de campos

Use fixtures para:
- Database temporário
- Limpeza após testes

Critério de aceitação:
- Testes end-to-end funcionais
- Simulação de input do usuário
- Validação de output
- Database isolado por teste
```

**Teste após executar:**
```bash
source .venv/bin/activate
pytest tests/test_cli.py -v -k objective
pytest -v
```

---

## PROMPT 8/8: Atualizar documentação do Milestone 1

```
Atualize a documentação para refletir conclusão do Milestone 1.

1. Atualize README.md:
   - Mudar badge para: ![Milestone 1](https://img.shields.io/badge/milestone-1%20complete-green)
   - Atualizar Status: "🚧 Em desenvolvimento - Milestone 1 ✅ concluído"
   - Atualizar seção "Comandos disponíveis" removendo "(Em desenvolvimento)" de objective new/list
   - Adicionar exemplos de uso de objective new/list

2. Crie CHANGELOG.md:
   - Seção [0.2.0] - Milestone 1
   - Listar features implementadas
   - Listar arquivos criados

3. Atualize pyproject.toml:
   - Versão: 0.2.0

Critério de aceitação:
- Documentação atualizada e precisa
- CHANGELOG seguindo padrão keepachangelog.com
- Versão bumped corretamente
```

**Teste após executar:**
```bash
source .venv/bin/activate
cat CHANGELOG.md
vibe --version  # deve mostrar 0.2.0
git diff README.md
```

---

## Checklist Milestone 1

Após todos os prompts:

- [ ] Modelo de dados criado (models.py)
- [ ] Persistência SQLite funcional (database.py)
- [ ] `vibe objective new` funcional e interativo
- [ ] `vibe objective list` com filtros
- [ ] Testes de models passando
- [ ] Testes de database passando
- [ ] Testes de CLI passando
- [ ] Documentação atualizada
- [ ] Versão 0.2.0

**Critérios de aceite do Milestone 1:**
✅ Objetivo criado via CLI
✅ Objetivo persistido
✅ Tipos validados

---

## Comandos úteis durante execução

```bash
# Ativar ambiente
source .venv/bin/activate

# Rodar testes específicos
pytest tests/test_models.py -v
pytest tests/test_database.py -v
pytest tests/test_cli.py -v -k objective

# Verificar cobertura
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Limpar database de teste
rm -f state/vibe.db

# Validar estrutura
vibe project check

# Commit após cada prompt
git add -A
git commit -m "feat: [descrição do prompt]"
```
