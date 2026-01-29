# Vibe - Plataforma de Orquestração para Vibe Coding

> "Vibe coding sem contrato é improviso. Este projeto transforma improviso em engenharia."

## Visão

Sistema de orquestração que organiza, governa e valida projetos feitos com vibe coding, garantindo previsibilidade, rastreabilidade e qualidade automática.

## Status

🚧 Em desenvolvimento - Milestone 0

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
