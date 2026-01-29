RESUMO — ARQUITETURA & DECISÕES (CONGELADO)
1. Natureza do sistema

O sistema é um ORQUESTRADOR DE FLUXO

Não é IDE, não é framework, não é gerador de código

Coordena estados, eventos e bloqueios

Decide se pode avançar ou não

2. Unidade fundamental

A unidade fundamental é o OBJETIVO

Objetivos:

nascem independentes por padrão

podem ter dependências explícitas

nunca avançam parcialmente

possuem estado discreto

Estados típicos:

definido

ativo

bloqueado

concluído

falhou

3. Fonte de verdade

A única fonte de verdade é o ESTADO PERSISTENTE (SQLite)

Projeto só existe após inicialização do estado

Filesystem e testes não mandam, apenas evidenciam

Nada é válido se não estiver registrado no estado

4. Modelo de fluxo

O sistema é EVENT-DRIVEN

Estado evolui apenas quando eventos são aceitos

Eventos são fatos registrados, não intenções

Ordem e causalidade importam

Execução é síncrona e determinística

5. Papel da IA

A IA é um agente que pode gerar eventos

IA não tem privilégios especiais

Todo evento da IA:

passa pelo mesmo validador que eventos humanos

está associado a um objetivo

deixa rastro completo

IA nunca altera estado diretamente

6. Definição de progresso

Progresso é uma combinação obrigatória de:

Evidência técnica (testes)

Decisão formal (evento)

Registro persistente (estado)

Regra:

Testes provam

Eventos decidem

Estado registra

Objetivo só é concluído se evento válido + testes exigidos passando.

7. Leis imutáveis do sistema
🔒 Lei 1 — Reconhecimento por evento

Mudanças podem ocorrer fora do sistema,
mas só são reconhecidas quando viram eventos válidos.

🔒 Lei 2 — Teste não decide

Testes são evidência, não autoridade.
Teste passando não fecha objetivo sozinho.

🔒 Lei 3 — Passado é imutável

Objetivo concluído não reabre.
Mudança exige novo objetivo e novo histórico.

8. Princípios implícitos

Sem estado registrado, nada existe

Sem evento, nada é reconhecido

Sem teste válido, não há decisão

Auditoria acima de conveniência

Disciplina acima de “experiência mágica”

📌 Status:
Chat encerrado. Decisões congeladas.
Este resumo guia todos os próximos chats de execução.
