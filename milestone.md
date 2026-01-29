# MILESTONES – Projeto de Orquestração para Vibe Coding

Este arquivo define os marcos de execução do projeto.
Cada milestone só é considerada concluída quando seus objetivos
e testes associados estiverem completos.

---

## Milestone 0 – Fundamentos do projeto
**Objetivo:** Ter um projeto executável, versionado e controlado.

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

## Milestone 6 – Qualidade obrigatória e automação
**Objetivo:** Qualidade mínima automática e inescapável.

- Testes obrigatórios antes de avançar objetivo
- Integração com pre-commit
- Scripts de automação padrão
- Execução completa via CLI única

Critério de aceite:
- Não existe “pular teste”
- Falha interrompe fluxo
- Qualidade reproduzível

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
