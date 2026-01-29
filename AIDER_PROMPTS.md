# Prompts para Aider - Milestone 0

## Contexto

Este projeto implementa uma plataforma de orquestração para vibe coding.
Leia os seguintes arquivos antes de começar:
- `scope.md` - Escopo imutável
- `archeture.md` - Decisões arquiteturais
- `milestone.md` - Milestones do projeto

**Princípios fundamentais:**
- Sistema event-driven
- Objetivo como unidade fundamental
- SQLite como fonte de verdade
- Testes obrigatórios para tudo
- IA governada (não freestyle)

---

## Prompt 1: Configurar projeto Python com pyproject.toml

**Contexto:** Milestone 0 requer ambiente Python configurado.

**Tarefa:**
Crie o arquivo `pyproject.toml` com:
- Nome do projeto: "vibe"
- Versão: 0.1.0
- Python: >=3.13
- Dependências principais: click, pytest, ruff, black, mypy, pre-commit
- Dependências de dev: pytest-cov
- Entry point CLI: `vibe` → `src.cli:main`
- Configuração do ruff (line-length: 100, target-version: py313)
- Configuração do black (line-length: 100, target-version: py313)
- Configuração do mypy (strict mode)

**Critério de aceitação:**
- `pyproject.toml` válido e instalável
- Configuração de ferramentas incluída
- Entry point CLI definido

**Arquivos a criar:**
- `pyproject.toml`

---

## Prompt 2: Criar CLI mínima funcional

**Contexto:** Milestone 0 requer CLI executável com `vibe --help`.

**Tarefa:**
Crie a estrutura mínima da CLI:

1. Crie `src/__init__.py` (vazio)
2. Crie `src/cli.py` com:
   - Função `main()` usando Click
   - Comando `vibe` com opção `--help`
   - Versão exibida com `--version`
   - Descrição: "Plataforma de Orquestração para Vibe Coding"
   - Subcomandos preparados (sem implementação):
     - `project` - Gerenciamento de projeto
     - `objective` - Gerenciamento de objetivos
   - Cada subcomando deve exibir "Em desenvolvimento" quando executado

**Critério de aceitação:**
- `vibe --help` funciona e mostra descrição
- `vibe --version` mostra versão correta
- CLI instalável via pip
- Código limpo e tipado

**Arquivos a criar:**
- `src/__init__.py`
- `src/cli.py`

**Teste manual após implementar:**
```bash
pip install -e .
vibe --help
vibe --version
```

---

## Prompt 3: Criar validador de estrutura canônica

**Contexto:** Sistema deve garantir que estrutura não derive (Milestone 0).

**Tarefa:**
Implemente validador de estrutura:

1. Crie `src/validator.py` com:
   - Classe `StructureValidator`
   - Método `validate_canonical_structure()` que verifica:
     - Diretórios obrigatórios: docs, objectives, tests, scripts, ai, state, src
     - Arquivos obrigatórios na raiz: scope.md, archeture.md, milestone.md
     - Retorna lista de erros (vazia se válido)

2. Adicione comando `vibe project check` em `src/cli.py`:
   - Executa validação
   - Exibe resultado formatado
   - Exit code 0 se válido, 1 se inválido

**Critério de aceitação:**
- Validador detecta diretórios faltantes
- Validador detecta arquivos faltantes
- `vibe project check` funciona
- Código tipado com mypy

**Arquivos a criar:**
- `src/validator.py`

**Arquivos a modificar:**
- `src/cli.py`

**Teste manual:**
```bash
vibe project check  # deve passar
rm -rf docs
vibe project check  # deve falhar
mkdir docs
```

---

## Prompt 4: Configurar pre-commit hooks

**Contexto:** Milestone 0 requer qualidade automática via pre-commit.

**Tarefa:**
Configure pre-commit para bloquear código inválido:

1. Crie `.pre-commit-config.yaml` com hooks:
   - `trailing-whitespace` (remove espaços em branco)
   - `end-of-file-fixer` (garante newline no final)
   - `check-yaml` (valida YAML)
   - `check-added-large-files` (bloqueia arquivos grandes)
   - `ruff` (lint + auto-fix)
   - `black` (formatação)
   - `mypy` (type checking)
   - Hook local: executa `vibe project check` (validação de estrutura)

2. Atualize `install-dev.sh`:
   - Adicione execução de `pre-commit install` no final
   - Remova comentário sobre aguardar configuração

**Critério de aceitação:**
- `.pre-commit-config.yaml` válido
- Pre-commit bloqueia commit com código mal formatado
- Pre-commit bloqueia commit com estrutura inválida
- Hook local de validação funciona

**Arquivos a criar:**
- `.pre-commit-config.yaml`

**Arquivos a modificar:**
- `install-dev.sh`

**Teste manual:**
```bash
pre-commit install
echo "codigo_mal_formatado=1" > src/test.py
git add src/test.py
git commit -m "test"  # deve falhar
rm src/test.py
```

---

## Prompt 5: Criar testes básicos da CLI

**Contexto:** Sistema exige testes obrigatórios (princípio fundamental).

**Tarefa:**
Implemente testes básicos para Milestone 0:

1. Crie `tests/__init__.py` (vazio)

2. Crie `tests/test_cli.py`:
   - Teste: CLI executa sem erros
   - Teste: `--help` exibe descrição correta
   - Teste: `--version` exibe versão correta
   - Teste: subcomandos existem (project, objective)

3. Crie `tests/test_validator.py`:
   - Teste: estrutura válida passa
   - Teste: diretório faltante é detectado
   - Teste: arquivo faltante é detectado
   - Use fixtures com `tmp_path` para criar estruturas temporárias

4. Crie `pytest.ini` na raiz:
   - Configurar testpaths = tests
   - Configurar markers se necessário
   - Configurar output verboso

**Critério de aceitação:**
- Todos os testes passam
- Cobertura > 80% (verificar com pytest-cov)
- Testes são isolados (usam tmp_path)
- Testes são determinísticos

**Arquivos a criar:**
- `tests/__init__.py`
- `tests/test_cli.py`
- `tests/test_validator.py`
- `pytest.ini`

**Teste manual:**
```bash
pytest -v
pytest --cov=src --cov-report=term-missing
```

---

## Prompt 6: Adicionar comando de inicialização de projeto

**Contexto:** CLI precisa criar estrutura canônica em novos projetos.

**Tarefa:**
Implemente comando para criar estrutura:

1. Crie `src/project.py` com:
   - Função `init_project(path: Path) -> bool`
   - Cria todos os diretórios canônicos
   - Cria arquivos .gitkeep nos diretórios
   - Valida se já existe projeto no path
   - Retorna True se sucesso, False se falhar

2. Adicione em `src/cli.py`:
   - Subcomando `vibe project init [PATH]`
   - PATH opcional (default: diretório atual)
   - Opção `--force` para sobrescrever
   - Exibe mensagem de sucesso/erro

**Critério de aceitação:**
- `vibe project init` cria estrutura válida
- Comando é idempotente (não quebra se executado 2x)
- Validação integrada executa após criação
- Testes cobrem casos de sucesso e erro

**Arquivos a criar:**
- `src/project.py`

**Arquivos a modificar:**
- `src/cli.py`
- `tests/test_cli.py` (adicionar testes para init)

**Teste manual:**
```bash
mkdir /tmp/test-vibe
cd /tmp/test-vibe
vibe project init
vibe project check  # deve passar
ls -la  # verificar estrutura
```

---

## Prompt 7: Documentar instalação e uso no README

**Contexto:** Milestone 0 requer documentação clara para desenvolvedores.

**Tarefa:**
Atualize o README.md com instruções completas:

1. Adicione seção "Instalação":
   - Pré-requisitos (Python 3.13+, git, sqlite)
   - Instruções para Fedora 43
   - Instruções genéricas para outras distros
   - Como executar install-dev.sh
   - Como ativar venv

2. Adicione seção "Desenvolvimento":
   - Como instalar em modo edição (`pip install -e .`)
   - Como rodar testes (`pytest`)
   - Como rodar pre-commit manualmente
   - Como validar estrutura

3. Adicione seção "Comandos disponíveis":
   - Listar comandos da CLI com exemplos
   - Breve descrição de cada comando

4. Adicione badge de status do Milestone 0

**Critério de aceitação:**
- README claro e completo
- Instruções testáveis
- Exemplos funcionais
- Markdown bem formatado

**Arquivos a modificar:**
- `README.md`

---

## Checklist de conclusão do Milestone 0

Após executar todos os prompts, valide:

- [ ] `vibe --help` funciona
- [ ] `vibe --version` mostra versão correta
- [ ] `vibe project check` valida estrutura
- [ ] `vibe project init` cria estrutura válida
- [ ] `pytest` passa todos os testes
- [ ] `pre-commit run --all-files` passa
- [ ] Estrutura canônica está completa
- [ ] README documentado
- [ ] Código está no GitHub
- [ ] CLI instalável via pip

**Critério de aceite final:**
- CLI executa ✓
- Estrutura validada automaticamente ✓
- Pre-commit bloqueia código inválido ✓

---

## Notas importantes

1. **Ordem de execução**: Seguir numeração dos prompts
2. **Testes primeiro**: Sempre criar testes junto com implementação
3. **Validação contínua**: Rodar `pytest` e `pre-commit` após cada prompt
4. **Commits atômicos**: Fazer commit após cada prompt concluído
5. **Referência aos documentos**: Sempre consultar scope.md e archeture.md em caso de dúvida

## Próximos passos após Milestone 0

Após concluir, seguir para Milestone 1 (Modelo de objetivos).
