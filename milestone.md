# MILESTONES – Projeto de Orquestração para Vibe Coding

Este arquivo define os marcos de execução do projeto.
Cada milestone só é considerada concluída quando seus objetivos
e testes associados estiverem completos.

**Progresso atual:** Milestone 6 concluído ✅
**Data da conclusão:** 2026-02-02

---

## Milestone 0 – Fundamentos do projeto
**Objetivo:** Ter um projeto executável, versionado e controlado.

✅ **CONCLUÍDO**

- Inicializar repositório
- Definir estrutura canônica de diretórios
- Criar CLI mínima (`vibe --help`)
- Configurar ambiente Python
- Configurar pre-commit (lint, format, testes)
- Definir arquivo de escopo (congelado)

Critério de aceite:
- CLI executa
- Estrutura validada automaticamente
- Pre-commit bloqueia código inválido

---

## Milestone 1 – Modelo de objetivos (core conceitual)
**Objetivo:** Formalizar o conceito de “objetivo” no sistema.

✅ **CONCLUÍDO**

- Definir formato de contrato de objetivo
- Definir tipos de objetivo (catálogo v1)
- Persistir objetivos no SQLite
- Criar comando `objective new`
- Criar comando `objective list`

Critério de aceite:
- Objetivo criado via CLI
- Objetivo persistido
- Tipos validados

---

## Milestone 2 – Geração automática de esqueleto de testes
**Objetivo:** Todo objetivo gera testes automaticamente.

✅ **CONCLUÍDO**

- Mapear tipo de objetivo → tipos de teste
- Gerar diretório de testes por objetivo
- Gerar setup/teardown padrão
- Gerar testes com TODO explícito
- Garantir que testes falhem por padrão

Critério de aceite:
- Criar objetivo gera testes
- Testes rodam e falham corretamente
- Nenhum objetivo existe sem testes

---

## Milestone 3 – Execução e tracking de testes
**Objetivo:** O sistema sabe o estado real do projeto.

✅ **CONCLUÍDO**

- Executar testes via CLI
- Registrar resultado no SQLite
- Associar testes a objetivos
- Comando `objective status`
- Health check geral do projeto

Critério de aceite:
- Status reflete realidade
- Falha bloqueia progresso
- Estado persistente correto

---

## Milestone 4 – Controle de filesystem e estrutura
**Objetivo:** Garantir que o projeto não derive.

✅ **CONCLUÍDO**

- Validador de estrutura canônica
- Testes de filesystem (criação, ausência de lixo)
- Idempotência de comandos
- Comando `project check`

Critério de aceite:
- Estrutura inválida é detectada
- Comandos são idempotentes
- Projeto pode ser validado a qualquer momento

---

## Milestone 5 – Integração com IA (governada)
**Objetivo:** IA trabalha sob contrato, não em freestyle.

✅ **CONCLUÍDO**

- Definir contexto padrão para IA
- Limitar arquivos alteráveis por objetivo
- Registrar ações da IA
- Bloquear alterações fora do escopo
- Integrar com Aider / Claude Code

Critério de aceite:
- IA só altera o permitido
- Alterações rastreadas
- Testes continuam sendo a fonte de verdade

---

## Milestone 6 – Qualidade obrigatória com exceção explícita
**Objetivo:** Qualidade mínima automática, com exceção rastreada e controlada.

✅ **CONCLUÍDO** – Implementado em 2026-02-02

### Implementações

1. **Objetivos baseados em arquivos (fonte primária)**
   - Cada objetivo existe como arquivo JSON em `/objectives`
   - Arquivo contém contrato completo (nome, descrição, tipos, entradas, etc.)
   - Banco de dados SQLite é estado derivado, sempre regenerável
   - Validação automática de integridade arquivo↔banco

2. **CLI como executor, não como fonte de verdade**
   - Comandos `objective new` criam arquivo automaticamente
   - Comando `objective sync-files` sincroniza banco com arquivos
   - Comando `objective validate-file` valida arquivo JSON individual
   - Comando `objective update-status` com validações de estado

3. **Qualidade obrigatória com exceção explícita (`--skip-tests`)**
   - Testes são obrigatórios para conclusão de objetivo
   - Flag `--skip-tests` permite pular execução temporariamente
   - Quando usada:
     - Status do objetivo muda para `TESTS_SKIPPED`
     - Objetivo **NÃO PODE** ser marcado como `CONCLUIDO`
     - Fluxo **NÃO PODE** ser concluído
     - Registro explícito no histórico (data, comando, usuário)
   - Frase-guia: *“Pular teste é permitido. Fingir que passou, não.”*

4. **Integração com validação de estrutura (pre‑commit ajustada)**
   - Comando `project check` valida:
     - Estrutura canônica
     - Integridade arquivo↔banco
     - Estados proibidos
     - Saúde dos testes
   - Estados proibidos detectados automaticamente:
     - Objetivo no banco sem arquivo
     - Arquivo sem testes gerados
     - `CONCLUIDO` com `TESTS_SKIPPED`
     - Milestone com objetivo em `TESTS_SKIPPED`

5. **Automação orientada a arquivos**
   - Scripts obrigatórios varrem `/objectives`
   - Detectam objetivos em estado `TESTS_SKIPPED` ou `INCOMPLETO`
   - Esses estados **não bloqueiam desenvolvimento**, mas **bloqueiam conclusão**

6. **Estados proibidos (lista negra atualizada)**
   - Objetivo no SQLite sem arquivo correspondente → **erro fatal**
   - Arquivo de objetivo sem testes gerados → **aviso crítico**
   - Objetivo marcado como `DONE` com testes pulados → **erro fatal**
   - Milestone concluído com qualquer objetivo em `TESTS_SKIPPED` → **erro fatal**
   - Código alterado sem objetivo ativo → **aviso**

7. **Fluxo único de execução (revisado)**
   - **Fluxo normal**: criar arquivo → validar → gerar testes → implementar → executar testes → concluir
   - **Fluxo com exceção**: criar arquivo → validar → gerar testes → implementar → executar com `--skip-tests` → estado `TESTS_SKIPPED` → **fluxo não pode ser concluído**

### Critério de aceite (atendido)

- [x] **Objetivos existem primariamente como arquivos** – `objective new` cria arquivo JSON; `sync-files` sincroniza
- [x] **Estado persistido é sempre derivável** – Banco pode ser reconstruído a partir de `/objectives`
- [x] **`--skip-tests` existe, mas é explícito e rastreável** – Flag registra ação e muda status para `TESTS_SKIPPED`
- [x] **`--skip-tests` não fecha objetivo nem milestone** – Validações bloqueiam conclusão
- [x] **Qualidade continua sendo o caminho padrão** – Testes obrigatórios para `CONCLUIDO`

### Comandos novos/atualizados

```bash
# Criar objetivo (já cria arquivo JSON)
vibe objective new

# Sincronizar banco com arquivos
vibe objective sync-files [--dry-run]

# Validar arquivo de objetivo
vibe objective validate-file objectives/<id>.json

# Atualizar status com validações
vibe objective update-status <id> <status>

# Executar testes com exceção temporária
vibe test run <id> --skip-tests

# Validar projeto completo (inclui estados proibidos)
vibe project check
```

### Próximos passos naturais

- Expandir validações de pre‑commit para exigir `--allow-skip-tests` explícito
- Implementar mensagem de commit padronizada para operações com `--skip-tests`
- Adicionar dashboard de saúde do projeto (objetivos em `TESTS_SKIPPED`, `INCOMPLETO`)
- Integrar com hooks de CI/CD para bloquear merge de objetivos em estado inválido

---

## Milestone 7 – Projeto exemplo (dogfooding)
**Objetivo:** Validar a ferramenta usando ela mesma.

- Criar projeto exemplo com a ferramenta
- Definir objetivos reais
- Gerar testes automaticamente
- Implementar usando IA
- Validar fluxo completo

Critério de aceite:
- Ferramenta usada para se desenvolver
- Fluxo completo validado
- Nenhuma etapa manual escondida

**Status:** Próximo após conclusão do Milestone 6

---

## Fora de escopo (confirmado)
- Interface gráfica
- IDE próprio
- LLM próprio
- Execução em nuvem
- Testes de performance avançados

---

Frase-guia:
“Cada milestone reduz o caos. Nenhuma adiciona magia.”
