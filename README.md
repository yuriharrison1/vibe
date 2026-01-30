# Vibe - Plataforma de Orquestração para Vibe Coding

> "Vibe coding sem contrato é improviso. Este projeto transforma improviso em engenharia."

## Visão

Sistema de orquestração que organiza, governa e valida projetos feitos com vibe coding, garantindo previsibilidade, rastreabilidade e qualidade automática.

## Status

🚧 Em desenvolvimento - Milestone 3 ✅ concluído

![Milestone 3](https://img.shields.io/badge/milestone-3%20complete-green)

## Documentação

- [SCOPE.md](./scope.md) - Escopo imutável do projeto
- [ARCHITECTURE.md](./archeture.md) - Decisões arquiteturais
- [MILESTONES](./milestone.md) - Marcos de execução

## Instalação (Desenvolvimento)

```bash
# Fedora 43
./install-dev.sh
source .venv/bin/activate
```

## Uso

```bash
vibe --help
```

### Comandos principais

```bash
# Criar objetivo (gera testes automaticamente)
vibe objective new

# Listar objetivos
vibe objective list
vibe objective list --status ATIVO
vibe objective list --type filesystem --verbose

# Executar testes
vibe test run <ID_OBJETIVO>
vibe test run --all
vibe test run --all --verbose

# Ver status dos testes
vibe objective status <ID_OBJETIVO>
vibe objective status --all
vibe objective status --all --verbose

# Validar projeto
vibe project check
vibe project init
```

## Estrutura

```
/
├─ docs        # Visão, decisões, regras para IA
├─ objectives  # Definição formal dos objetivos
├─ tests       # Testes gerados + implementados
├─ scripts     # Automações
├─ ai          # Prompts e limites da IA
├─ state       # SQLite e metadados
└─ src         # Código fonte
```

## Princípios

- **Event-driven**: Estado evolui apenas por eventos válidos
- **Objetivo como unidade**: Tudo gira em torno de objetivos
- **SQLite como fonte de verdade**: Persistência antes de tudo
- **Testes obrigatórios**: Todo objetivo gera testes automaticamente
- **IA governada**: IA trabalha sob contrato, não em freestyle
