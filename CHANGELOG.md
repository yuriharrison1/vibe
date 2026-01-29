# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-29

### Added
- Modelo de dados para objetivos (`src/models.py`)
  - Enums `ObjectiveType` e `ObjectiveStatus`
  - Classe `Objective` com serialização/deserialização
- Camada de persistência SQLite (`src/database.py`)
  - CRUD completo para objetivos
  - Schema automático com JSON para arrays
- Comandos CLI interativos:
  - `vibe objective new` – criação interativa de objetivos
  - `vibe objective list` – listagem com filtros (--status, --type, --verbose)
- Testes automatizados:
  - `tests/test_models.py` – testes de modelo de dados
  - `tests/test_database.py` – testes de persistência
  - `tests/test_cli.py` – testes de integração CLI
- Documentação atualizada:
  - README com instruções completas de instalação e uso
  - Badge de Milestone 1

### Changed
- Atualizada versão do projeto para 0.2.0
- README.md reformatado com seções detalhadas
- Comandos `objective new` e `objective list` agora funcionais (removido "Em desenvolvimento")

### Fixed
- Nenhum

### Removed
- Nenhum

## [0.1.0] - 2026-01-28

### Added
- Estrutura inicial do projeto
- CLI básica com `vibe --help`, `vibe --version`
- Subcomandos `project check` e `project init`
- Validador de estrutura canônica
- Script de instalação `install-dev.sh`
- Configuração de pre‑commit (lint, format, testes)
- Arquivos de documentação congelados (scope.md, archeture.md, milestone.md)
