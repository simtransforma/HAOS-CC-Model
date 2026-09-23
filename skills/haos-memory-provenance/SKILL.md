---
name: haos-memory-provenance
description: >-
  Regras de qualidade, proveniencia e deduplicacao de CONTEUDO antes de gravar
  memoria no HAOS (o que merece virar memoria, envelope obrigatorio, escrita
  idempotente, prova real de fechamento remoto). NAO substitui `/haos:evoluir`
  nem `haos-memory-triple`: esta skill diz O QUE gravar e como evitar
  duplicata/lixo; o evoluir e o EXECUTOR que grava, faz commit e faz readback.
  Use antes de qualquer `/haos:evoluir` que vai CAPITALIZAR, ou sempre que for
  decidir manualmente se um fato vira memoria.
---

# HAOS Memory Provenance

Complementa `haos-memory-triple` (as 3 camadas de backup: local, Obsidian/OneDrive,
GitHub privado) e `/haos:evoluir` (`<SEU_CAMINHO>/commands/haos/evoluir.md`,
o executor real do fechamento). Esta skill nao reimplementa o mecanismo do evoluir,
so define a doutrina de PROVENIENCIA E QUALIDADE do que entra na memoria.

## O que merece memoria

Registre apenas fatos duraveis, decisoes, causa raiz, procedimento reutilizavel,
restricoes, evidencias e proximo passo. Nao grave conversa inteira, raciocinio
interno, dados pessoais desnecessarios, tokens, cookies ou conteudo de cofre.
Isso e exatamente o Gate de Valor da Fase 0 do evoluir (CAPITALIZA x SO FECHA):
leia aquele gate antes de decidir gravar algo fora do fluxo do evoluir.

## Envelope obrigatorio (proveniencia do CONTEUDO)

Este envelope descreve o FATO em si. Nao confundir com a chave de idempotencia
da EXECUCAO do evoluir (`sessionId` + `taskKey` + `revision`, ver Fase 6/8 do
evoluir): as duas coisas coexistem, uma descreve o conteudo, a outra evita
reabrir a mesma tarefa duas vezes.

```yaml
session_slug: nome-estavel-da-sessao
scope: projeto-ou-sistema
kind: decisao | aprendizado | procedimento | incidente | handoff
summary: fato compacto
source: arquivo-comando-ou-evidencia
observed_at: ISO-8601
confidence: confirmed | inferred | pending
supersedes: id-ou-null
```

## Escrita idempotente

1. Procure registro equivalente pelo `session_slug`, `kind` e causa raiz (Fase 2
   do evoluir, "Reconciliacao anti-duplicata", ja faz isso: grep no disco da
   memoria eterna ANTES de escrever).
2. Atualize o item existente; nao crie duplicata por execucao (UPDATE > CREATE,
   regra 5 do evoluir).
3. Grave a versao sanitizada no repo da sessao e no repo GitHub privado
   `<SEU_REPO_DE_MEMORIA>` (feito pelo `finish_task.ps1`, Fase 8 do evoluir).
4. Atualize a subpasta organizada da sessao no Obsidian
   (`<SEU_VAULT>/05-Memoria-Eterna`, destino
   primario desde 22/08/2026).
5. Envie ao Mnemoverse (MCP `mnemoverse`) como camada adicional redigida, nunca
   como fonte unica: o hook `session_start.py` le a memoria LOCAL no boot, nao
   o Mnemoverse. So Mnemoverse sem espelho local cria sessao paralela cega.
6. Deixe o `claude-mem` capturar contexto operacional pelo runtime isolado dele;
   nao escreva diretamente no banco dele fora de API documentada. **Camada
   degradada** (CLAUDE.md §0, camada 2): busca vetorial fora do ar desde
   04/09/2026, cair para grep no disco quando essa camada nao responder.
7. Faca readback de cada destino e compare campos-chave antes de declarar salvo.

Git commit deve selecionar somente os artefatos da sessao. Push continua exigindo
OK explicito do dono (CLAUDE.md §3, item 6). Falha em uma camada deve ser
reportada sem apagar as camadas que passaram.

Para diario global, opt-out, captura prospectiva e separacao dos destinos,
aplicar tambem `references/diario-e-readback.md`.

## Prova de fechamento remoto (NAO reimplementar, so verificar)

O evoluir ja implementa o readback obrigatorio de Mnemoverse (`memory_write` +
`memory_read` de conferencia, item E4 de 18/09/2026) e de GBrain
(`get_page`/`search` so quando o proprio evoluir gravou algo la, com tabela de
readback na Fase 9). Esta skill so reforca os PRINCIPIOS por tras dessa tabela:

Fila local, health HTTP 200 e busca semantica vazia nao provam, respectivamente,
ingestao, processamento concluido ou ausencia de um registro. Usar identidade
de tarefa/revisao (`sessionId`+`taskKey`+`revision` no evoluir), leitura exata
e recibo independente por destino.

No Mnemoverse, transportar o delta curado da revisao, ligado ao `taskKey` e
`revision`, e ao hash da proveniencia completa mantida no recibo local. Nao
repetir um envelope por destino: o filtro semantico pode rejeitar esse pacote
redundante como baixa novidade. Uma resposta `IMPORTANCE_FILTERED` (ou
equivalente) nao e readback nem sucesso. Ela autoriza repacotar somente quando
o servidor confirmou que nenhum atom foi criado, nao existe recibo remoto e a
identidade + hash da proveniencia permanecem iguais. Timeout, resposta ambigua
e conflito continuam fail-closed e nunca podem ser reenviados por inferencia.

Para falhas de captura, atraso e erros de provider, aplicar
`references/diagnostico-captura-fila.md`. Preservar registros nao confirmados;
nao apagar lacunas ou filas para transformar um indicador em sucesso.

## Integridade do fechamento automatico

- O log `_brain/evoluir-log.jsonl` vincula cada tarefa ao par `sessionId`+
  `taskKey`; um marcador `CAPITALIZA` isolado sem `revision` coerente nao prova
  integridade.
- Divergencia, log conhecido ausente ou migracao pendente resultam em
  `[a confirmar]`, nunca em ausencia presumida de tarefa (Regra #0 do
  CLAUDE.md de usuario, gate anti-desistencia).
- Preservar o `taskKey` depois de estado terminal para validar o recibo mesmo
  sem ponteiro automatico.
- Se dois registros apontarem para tarefas terminais diferentes da mesma sessao,
  o log canonico (`_brain/evoluir-log.jsonl`) prevalece. Qualquer tarefa ativa,
  ponteiro corrompido ou identidade ausente continua fail-closed.
- Aceitar o recibo do evoluir somente como a ultima linha nao vazia do log, com
  um unico marcador coerente com `taskKey`, gate e readbacks.
- Varredura integral da memoria eterna pertence a manutencao administrativa
  (ex.: auditoria de memorias orfas); o hook de abertura/fechamento de sessao
  deve permanecer limitado e fail-closed.

---

Origem: portado do Codex (`<toolkit-codex-interno>/.agents/skills/haos-memory-provenance`,
20/09/2026). Adaptado: substituido `finish-task-haos.ps1`/`.codex/*` pelo par real
do HAOS (`/haos:evoluir` + `finish_task.ps1`); trocada a chave de idempotencia
generica `task_id`/`revision` pela chave real do evoluir (`sessionId`+`taskKey`+
`revision`); ligado o "diario global" ao Obsidian vault real; marcado o
`claude-mem` como camada degradada conforme CLAUDE.md §0.
Credito: Gian Marco Menegussi Scaglianti.
