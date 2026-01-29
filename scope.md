# ESCOPO DO PROJETO
Plataforma de Orquestração para Vibe Coding

## 1. Propósito (imutável)
Criar uma ferramenta que organiza, governa e valida projetos feitos com vibe coding, garantindo previsibilidade, rastreabilidade, qualidade mínima automática e controle da atuação de IAs.

## 2. Problema resolvido
- IA escreve rápido, mas não mantém coerência.
- Vibe coding sem método gera código instável, refactors destrutivos e projetos não auditáveis.
- Ferramentas atuais focam em escrever código, não em governança.

## 3. O que o sistema É
### 3.1 CLI
- Executável local
- Independente de IDE
- Scriptável
- Integrável com CI

### 3.2 Gerenciador de projetos
- Cria projetos com estrutura canônica
- Mantém consistência
- Evita deriva arquitetural

### 3.3 Sistema orientado a objetivos (core)
- Tudo gira em torno de objetivos
- Objetivos geram contratos e testes automaticamente
- Objetivo só conclui quando testes passam

## 4. Estrutura canônica (v1)
/
├─ docs        → visão, decisões, regras para IA
├─ objectives  → definição formal dos objetivos
├─ tests       → testes gerados + implementados
├─ scripts     → automações
├─ ai          → prompts e limites da IA
├─ state       → SQLite e metadados
└─ src         → código

## 5. Objetivos (contrato)
Um objetivo contém:
- nome
- descrição
- tipo(s)
- entradas
- saídas esperadas
- efeitos colaterais permitidos
- invariantes

## 6. Tipos de objetivo (v1)
- cli-command
- filesystem
- state
- project
- integration
(Objetivos podem ter múltiplos tipos)

## 7. Geração automática de testes (núcleo)
Regra: Todo objetivo gera automaticamente esqueleto de testes.
Sem exceções. Sem desligar.

O sistema gera:
- diretório de testes
- setup/teardown
- execução do comportamento
- asserções marcadas como pendentes (TODO explícito)

## 8. Testes suportados (v1)
### CLI
- execução
- exit code
- stdout/stderr
- help/flags inválidas

### Filesystem
- criação de arquivos
- estrutura esperada
- ausência de lixo
- idempotência

### Estado
- SQLite criado
- schema mínimo
- estado inicial
- migrações simples

### Integração
- sequência de comandos
- efeitos acumulados
- regressão básica

## 9. Persistência
SQLite como fonte de verdade:
- projetos
- objetivos
- estado dos testes
- histórico de execuções
- versões

## 10. Integração com IA
- Define contexto enviado à IA
- Limita arquivos alteráveis
- Associa IA a objetivo ativo
- Bloqueia alterações fora do escopo

IA decide COMO implementar, não O QUÊ.

## 11. Qualidade obrigatória
- pre-commit hooks
- lint
- formatação
- testes obrigatórios
- falha bloqueia avanço

## 12. Fora do escopo (v1)
- UI gráfica
- IDE próprio
- LLM próprio
- Geração de código sem objetivo
- Testes de performance avançados
- Cloud

## 13. Critério de sucesso da v1
- Criar projeto
- Definir objetivos
- Gerar testes automaticamente
- Implementar com IA
- Garantir qualidade mínima

Frase-chave:
“Vibe coding sem contrato é improviso. Este projeto transforma improviso em engenharia.”
