---
name: haos-quality-gates
description: >-
  Escada progressiva de gates de qualidade (lint, tipos, testes, build, varredura
  de segredo e teste de comportamento) com baseline numerica, owner unico por
  arquivo, stop-loss e rollback testado, sem instalar ferramenta nova por cima da
  que o projeto ja tem. Use SEMPRE que a tarefa for criar, migrar ou endurecer
  validacao de um projeto: definir o que trava um merge, montar ou apertar CI,
  estabelecer baseline de erro antes de mexer, promover warning para erro, limpar
  lote de lint ou de tipo sem quebrar comportamento, decidir se um check entra como
  bloqueante, ou auditar por que um projeto passa no CI e continua quebrado.
  Gatilhos tipicos do usuario: "cria um gate pra isso", "nao deixa passar warning",
  "quero baseline antes", "isso tinha que travar o merge", "poe no CI", "limpa
  esses erros de lint", "zera os warnings", "trava isso pra nao regredir", "roda os
  testes antes de subir", "por que passou se ta quebrado". NAO use para revisar o
  codigo em si nem para consolidar achado de varios revisores: para isso veja
  haos-multi-agent-review e /code-review. NAO use para deploy, container ou infra:
  isso e @devops.
metadata:
  version: 1.0.0
  autor: Gian Marco Menegussi Scaglianti
  portado_de: <toolkit-codex-interno>/.agents/skills/haos-quality-gates (26/08/2026)
  portado_em: 2026-09-04
---

# HAOS Quality Gates

Use ao criar, migrar ou endurecer as validacoes de um projeto.

## Quem executa (le isto antes de qualquer coisa)

No Claude Code o main e **fisicamente bloqueado** pelo hook `main_guard.py`
(ENFORCE) de rodar `python`, `node`, `pwsh`, `npm`, `pytest` e de editar arquivo de
projeto. Logo:

- **O main ORQUESTRA:** le manifest e CI (Read/Grep/Glob passam), define a escada,
  escreve o contrato do lote, recebe o resultado e decide promover ou nao.
- **O sub-agente RODA o gate:** delegacao pela tool `Agent`, com `model`
  obrigatorio. Para so MEDIR baseline sem consertar nada, use o sub-agente
  `Explore` ou `Plan`, que nao tem Edit nem Write | e trava natural contra o
  revisor virar corretor. Para a onda de correcao, use um agente com escrita
  (`haos:dev-backend`, `haos:dev-frontend`, `haos:devops`) com write-set explicito.
- Gate longo (suite inteira, build) vai com `run_in_background: true`.

Uma instrucao que mande o main rodar o comando **nao funciona aqui**. Se a escada
pedir execucao, ela vira briefing de sub-agente.

Tier de modelo (obrigatorio em todo `Agent`, ver §1.1 do CLAUDE.md):

| Etapa | Tier |
|---|---|
| Medir baseline, contar ocorrencia, inventariar | `haiku` |
| Rodar gate conhecido, corrigir lote mecanico | `sonnet` |
| Decidir escada, causa raiz de falha, promover para bloqueante | `opus` |
| Julgar se o gate vale o atrito, sintese final ao dono | `fable` |

## Descoberta primeiro

Leia manifests, scripts e CI existentes. Identifique a stack e os comandos
oficiais dela. **Nao instale ferramenta nova quando o projeto ja tem gate
equivalente.**

Especifico da casa: o corpus do HAOS e **Python, PowerShell e Markdown**. **Nao se
instala ESLint nem Biome global** aqui. O gate se apoia no que ja existe no projeto
(pytest, ruff, mypy, PSScriptAnalyzer, os proprios scripts de guard em
`~/.claude/hooks/`) e nas suites de guard que ja rodam verdes.

## Escada de promocao

Suba um degrau por vez. Nunca pule para BLOQUEAR sem passar por ZERAR.

1. `OBSERVAR`: rode o gate atual e salve **baseline reproduzivel** (numero, comando
   exato, data). Sem numero nao ha degrau seguinte.
2. `CONTER`: mudanca nova nao pode aumentar a contagem de falhas conhecidas.
3. `REDUZIR`: corrija em lotes mecanicos, com write-set pequeno e teste junto.
4. `ZERAR`: confirme zero **no escopo definido**, sem esconder arquivo, sem
   exclude novo, sem `# noqa` em massa.
5. `BLOQUEAR`: promova para erro ou para o CI **somente** depois de estabilidade
   comprovada e rollback testado.

**Nao confunda zero warnings com comportamento correto.** O conjunto minimo, quando
aplicavel, inclui: lint, typecheck, testes, build, varredura de segredo e **um
teste do sintoma ou da jornada critica** que motivou o trabalho.

## Contrato por lote

Todo lote sai com estes campos preenchidos. Lote sem contrato nao entra:

- baseline e meta numerica;
- regra ou ferramenta, com versao;
- arquivos, todos sob **owner unico** (um agente por arquivo por onda);
- classificacao `MECANICA` ou `COMPORTAMENTAL`;
- comando de verificacao e o resultado dele, com tag `[verifiquei: <comando> -> <o que vi>]`;
- stop-loss e rollback;
- risco residual.

## Fronteiras duras

Mudanca de configuracao global, auto-fix amplo ou supressao em massa **exige tarefa
separada**, nunca vai de carona num lote. Alteracao externa, push, merge,
publicacao, envio, gasto ou remocao destrutiva continua bloqueada ate OK explicito
do dono.
