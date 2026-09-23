---
name: haos-execution-waves
description: >-
  Contrato de execucao em ondas paralelas do HAOS: quebra um objetivo em tarefas
  com dono unico por arquivo, monta o grafo de dependencias, roda no maximo 3
  agentes por onda e so fecha item com evidencia verificavel. Dois modos: PLAN
  (gera EXECUTION_PLAN.md) e EXECUTE (gera EXECUTION_EVIDENCE.md). Use SEMPRE que
  a tarefa tiver 3 ou mais frentes independentes, precisar paralelizar
  sub-agentes, dividir trabalho entre agentes, decidir quem mexe em qual arquivo,
  ou quando duas frentes podem se atropelar no mesmo arquivo, workflow n8n, funil
  do CRM, campanha, tabela do banco ou audiencia. Gatilhos tipicos do usuario:
  "divide isso entre os agentes", "roda em paralelo", "quebra em ondas", "sobe 3
  agentes ao mesmo tempo", "quem mexe em que arquivo", "faz tudo isso de uma
  vez", "isso da pra paralelizar?", "esses dois vao se atropelar", "monta o plano
  de execucao", "organiza a execucao disso". NAO use para tarefa de um agente so,
  nem para planejamento que nao vai virar execucao (isso e writing-plans ou
  planning-with-files).
metadata:
  version: 1.0.0
  autor: Gian Marco Menegussi Scaglianti
  marca: HAOS
  type: procedimento
  portado_de: <toolkit-codex-interno>/.agents/skills/haos-execution-waves (26/08/2026)
  portado_em: 2026-09-04
  adaptacoes: >-
    fork_turns->Agent tool; commit pelo sub-agente owner; handoff por artefato;
    RECURSOS_COMPARTILHADOS/MUTACAO/ROLLBACK
---

# HAOS Execution Waves

O HAOS ja paraleliza (CLAUDE.md §10), mas hoje paraleliza **sem regra formal de
colisao**: dois sub-agentes podem receber o mesmo arquivo, o mesmo workflow do
n8n ou a mesma campanha e um sobrescrever o outro sem ninguem perceber. Esta
skill e o contrato que fecha esse buraco: **1 dono por recurso, dependencia
explicita, no maximo 3 agentes por onda, revisor read-only e evidencia
verificavel antes de qualquer item virar CONCLUIDO**.

Portada do toolkit do Codex (26/08/2026), com as regras traduzidas para o mundo
do Claude Code. As traducoes estao marcadas em cada secao; nao copie a versao do
Codex por cima, ela quebra o guard desta casa.

---

## 1. Os dois modos

| Modo | O que faz | O que NAO faz |
|---|---|---|
| `PLAN` | Transforma objetivo ou briefing em `EXECUTION_PLAN.md`. Decide ondas, donos, dependencias, recursos e gates. | Nao implementa nada. Nao spawna executor. |
| `EXECUTE` | Valida um `EXECUTION_PLAN.md` existente, roda as ondas e registra `EXECUTION_EVIDENCE.md` ao lado do plano. | Nao inventa item novo fora do plano. Nao pula gate externo. |

Se voce esta em `EXECUTE` e o plano nao existe, **volte para `PLAN`**. Executar
sem plano escrito e exatamente a falha que esta skill previne.

---

## 2. Onde os artefatos moram (handoff por artefato)

O plano e a evidencia nascem dentro da convencao de handoff do HAOS
(skill `haos-handoff-artefato`, hook `handoff_guard.py`), no repo da sessao:

```
workspace/_handoff/<AAAAMMDD>-<slug-da-tarefa>/
    00-EXECUTION_PLAN.md          <- modo PLAN grava aqui
    01-dev-backend-cliente-api.md <- artefato do item 01
    02-copy-specialist-copy-lp.md <- artefato do item 02
    03-qa-reviewer-conformidade.md
    99-EXECUTION_EVIDENCE.md      <- modo EXECUTE fecha aqui
```

Regras herdadas da `haos-handoff-artefato`, que continuam valendo integralmente:

- **O main transporta o CAMINHO, nunca o resumo.** O prompt do sub-agente aponta
  o arquivo e diz explicitamente que o conteudo nao foi resumido de proposito.
- **Cada agente grava o SEU arquivo numerado.** Reescrever o arquivo do anterior
  apaga a autoria e destroi a rastreabilidade.
- **Scratchpad nao serve.** Artefato de onda e evidencia, precisa sobreviver a
  sessao e ser commitado.

Por isso cada tarefa do plano declara o campo `ARTEFATO`: o caminho exato do
arquivo que ela produz dentro dessa pasta. Tarefa sem `ARTEFATO` declarado nao
entra na onda.

---

## 3. Contrato do plano

O `00-EXECUTION_PLAN.md` declara, nesta ordem:

1. objetivo, escopo, fora de escopo e criterios de aceite;
2. o caminho exato de **todo** arquivo que pode ser criado ou alterado;
3. a tabela de itens (schema abaixo);
4. riscos, lacunas e decisoes ainda pendentes;
5. comandos locais de validacao e o resultado esperado de cada um.

### Schema da tarefa

| Campo | Obrigatorio | O que e |
|---|---|---|
| `ID` | sim | Identificador curto e estavel (`01`, `02`). Dependencia so aponta ID existente. |
| `ONDA` | sim | Numero da onda. Item so entra em onda cujas dependencias ja terminaram. |
| `OBJETIVO` | sim | Uma frase, verificavel. "Melhorar X" nao e objetivo. |
| `ARQUIVOS` | sim | Caminhos absolutos ou relativos a raiz do repo. Sem curinga. |
| `RECURSOS_COMPARTILHADOS` | sim | Recurso NAO-arquivo que o item toca: workflow do n8n (por ID), funil ou automacao de CRM, campanha ou conjunto de midia paga, tabela do Supabase, audiencia, container, DNS, template de mensagem. `nenhum` e resposta valida e explicita. |
| `MUTACAO` | sim | `LOCAL` (so disco desta maquina/repo), `EXTERNAL_READ` (le API/servidor sem mudar nada), `EXTERNAL_WRITE` (muda estado fora do repo). |
| `ROLLBACK` | so se `EXTERNAL_WRITE` | Como desfazer, em comando ou passo concreto. Sem rollback escrito, o item nao roda. |
| `DEPENDE_DE` | sim | Lista de IDs. Vazio e valido. O grafo tem que ser aciclico. |
| `OWNER` | sim | O agente que executa. Um unico dono por arquivo, na execucao inteira. |
| `MODEL` | sim | Tier do owner: `haiku`/`sonnet`/`opus`/`fable`. Ver §5. |
| `REVISOR` | sim | Agente diferente do owner, read-only. Ver §7. |
| `ARTEFATO` | sim | Caminho do `.md` que o item grava na pasta de handoff. |
| `EVIDENCIA` | sim | O comando de validacao e o resultado esperado. |
| `GATE_EXTERNO` | sim | `nao` ou a acao externa que exige OK do dono. Ver §8. |

### O campo que o toolkit original nao tinha

`RECURSOS_COMPARTILHADOS` foi acrescentado no porte, por pedido do
funnel-architect (parecer de 25/08/2026). Motivo: **`ARQUIVOS` sozinho e
insuficiente nesta casa**. Duas tarefas com arquivos completamente disjuntos
ainda colidem quando as duas editam o mesmo workflow do n8n, o mesmo funil do
CRM, a mesma campanha de midia paga, a mesma tabela do warehouse ou a mesma
audiencia. Nesses casos a colisao nao aparece no `git status`: aparece em
producao, depois.

`MUTACAO` e `ROLLBACK` vieram junto pelo mesmo motivo: o risco de uma onda
paralela nao e proporcional ao numero de arquivos, e sim a quantidade de estado
externo que ela mexe.

---

## 4. Regras duras de colisao

1. **Um arquivo, um owner, a execucao inteira.** Nao existe "os dois mexem, mas
   em partes diferentes do arquivo".
2. **Duas tarefas so rodam juntas se as tres condicoes valerem:** nao ha
   dependencia **transitiva** entre elas (A depende de B que depende de C: A e C
   nao sao paralelas), **e** o conjunto `ARQUIVOS` e disjunto, **e** o conjunto
   `RECURSOS_COMPARTILHADOS` e disjunto.
3. **Maximo 3 agentes por onda.** Casa com o §10 do CLAUDE.md ("3+ subsistemas
   independentes -> paralelizar"): 3 e o teto, nao a meta. Duas frentes
   independentes = 2 agentes, e esta certo.
4. **DAG sem ciclo.** `DEPENDE_DE` que fecha ciclo invalida o plano inteiro, nao
   so o item.
5. **Incerteza degrada para serial.** Se voce nao tem certeza de que dois itens
   sao disjuntos, eles **nao** sao. Serializa. O custo de uma onda a mais e
   minutos; o custo de dois agentes se sobrescrevendo e retrabalho mais um bug
   que ninguem consegue reproduzir.
6. **Se nao existe agente especializado real para o item, o main assume o
   roteamento e delega ao agente generico.** Nao invente nome de agente: a lista
   viva de `subagent_type` e a da sessao.

---

## 5. Como paralelizar de verdade aqui (traducao do `fork_turns`)

**`fork_turns` NAO EXISTE no Claude Code.** No Codex, a delegacao declarava
`fork_turns: none|N`. Aqui a delegacao e o tool `Agent`, e o equivalente e outro:

| Conceito no Codex | Equivalente real no Claude Code |
|---|---|
| `fork_turns: none` | Uma chamada de `Agent` com `run_in_background: false`, prompt fechado e auto-contido. O sub-agente nao continua a conversa do main. |
| `fork_turns: N` | Nao tem equivalente. Se o item precisa de varias rodadas, ou o prompt esta mal fechado, ou o item precisa ser quebrado em dois. |
| Rodar N agentes em paralelo | **Varias chamadas de `Agent` na MESMA resposta.** E isso que gera paralelismo: uma resposta com 3 blocos `Agent`. Chamadas em respostas diferentes sao seriais. |
| Fila de agente longo | `run_in_background: true` quando a proxima acao do main nao depende do resultado. |

Parametros que toda delegacao de onda declara:

- `model` (**obrigatorio**): tier do §1.1 do CLAUDE.md. O hook
  `model_guard.py` bloqueia o spawn sem `model` valido
  (`{haiku, sonnet, opus, fable}`, mais o nome completo do modelo).
- `subagent_type`: o agente da tabela do §4 do CLAUDE.md, ou `Explore`/`Plan`
  para revisao read-only.
- `run_in_background`: `false` no padrao de onda (voce quer o resultado antes de
  abrir a proxima onda).
- prompt: objetivo, contexto, **caminho do artefato de entrada**, saida esperada,
  criterio de qualidade, limites e dependencias. Prompt de onda tambem carrega o
  bloco de consumidor da `haos-handoff-artefato`.

---

## 6. Quem escreve e quem commita (regra INVERTIDA no porte)

**Esta e a traducao mais importante do porte. A regra do Codex, copiada ao pe da
letra, quebraria o guard desta casa.**

No Codex/toolkit valia: *"o implementador nao commita; o integrador seleciona o
staging"*. Aqui e o contrario, porque o main e **fisicamente bloqueado** de
escrever, commitar e pushar pelo hook `main_guard.py`.

Como fica:

| Papel | O que faz | O que NAO faz |
|---|---|---|
| **Main (orquestrador)** | Escreve o plano em disco? Nao: **delega ate isso**, porque `Write` fora de `~/.claude` e bloqueado. Le (`Read`/`Grep`/`Glob`), monta as ondas, spawna, le o artefato de cada item, decide a proxima onda, consolida e fecha com `/haos:evoluir`. | Nao edita arquivo de projeto, nao roda comando que muda estado, **nao commita a onda**. |
| **Sub-agente OWNER** | Escreve os arquivos do item, grava o proprio artefato, roda a validacao, e **commita a propria onda** (`git add` dos SEUS arquivos + `git commit`). | Nao toca em arquivo de outro owner. Nao commita arquivo que nao e dele. **Nao da `push`** sem OK (gate externo, §8). |
| **Sub-agente REVISOR** | Le e emite parecer. | Nao corrige, nao edita, nao commita. |

Regras de commit da onda:

1. O owner commita **somente os seus `ARQUIVOS`**, por caminho explicito. Nunca
   `git add -A`, nunca `git add .`: numa onda paralela isso captura o trabalho
   dos outros agentes pela metade.
2. Mensagem de commit em PT-BR, objetiva, citando o `ID` do item.
3. O fechamento final da tarefa continua sendo do main, via `/haos:evoluir`
   (CLAUDE.md §22), que chama o `finish_task.ps1` na Fase 8. Nao rode os dois.

---

## 7. Revisor read-only (aqui e trava fisica, nao promessa)

O revisor tem que ser **diferente do owner** e atuar **read-only**: aponta, nao
corrige. Se achou problema, o item volta ao owner.

No Codex isso era regra de comportamento, obedecida na confianca. Aqui existe
garantia estrutural: `subagent_type: Explore` e `subagent_type: Plan` **nao tem
`Edit`, `Write` nem `NotebookEdit` na lista de ferramentas**. Um revisor spawnado
com um desses tipos e incapaz de escrever, mesmo se o prompt mandar.
`[verifiquei: listagem de agent types da sessao -> Explore e Plan descritos como "All tools except Agent, Artifact, ..., Edit, Write, NotebookEdit"]`

Para revisao com parecer formal de gate (aprovado / ajustes / reprovado), use
`haos:qa-reviewer`, que tambem nao tem `Edit`/`Write` (tools: Read, Grep, Glob,
Bash, WebFetch).

---

## 8. Gates externos

Exige **OK explicito do dono, pedido pelo main, antes de rodar**: publicar,
enviar mensagem, gastar dinheiro, deploy, `git push`, merge, alterar servidor,
Cloudflare, DNS, banco remoto, campanha ativa, ou qualquer remocao destrutiva.

- Todo item com `MUTACAO: EXTERNAL_WRITE` cai aqui por definicao, e so roda com
  `ROLLBACK` escrito.
- **Planejamento nunca concede autorizacao.** Ter passado pelo modo `PLAN` nao
  autoriza nada: o OK e por acao, no momento da acao.
- Sem OK aplicavel, o item fica `BLOQUEADO` e a execucao **continua** nos itens
  independentes e locais. Onda nao para inteira por causa de um gate.

---

## 9. Execucao e evidencia

Antes de cada onda: confira o worktree (`git status`) e **preserve alteracao
preexistente**. Alteracao nao rastreada que voce nao criou nao se descarta.

Um item so vira `CONCLUIDO` quando a evidencia prevista foi **executada, lida e
registrada** com comando, resultado e arquivos observados. Falha de validacao
devolve o item ao owner; conflito de escopo bloqueia o item.

O `99-EXECUTION_EVIDENCE.md` traz, por item:

```
## ID 02 | <objetivo>
STATUS: CONCLUIDO | BLOQUEADO | REVISAO NECESSARIA
OWNER: <agente> (model: <tier>)
ARQUIVOS ALTERADOS: <lista real, do git status/diff>
ARTEFATO: <caminho>
VALIDACOES: [verifiquei: <comando> -> <o que vi>]
REVISAO: <revisor> -> <parecer>
COMMIT: <hash curto> | nao commitado (motivo)
PENDENCIAS: <lista ou "nenhuma">
```

Fechamento do documento: `STATUS GERAL`, evidencias e proximos passos.

**Lastro obrigatorio.** Toda afirmacao de causa, estado ou mecanismo sai com
`[verifiquei: <comando> -> <o que vi>]`. Deducao nao testada sai como
`[hipotese]` ou `[a confirmar]`. Afirmacao sem tag vira fato falso na mao do
main (CLAUDE.md §0 e §0.1).

---

## 10. Verificacao (rode antes de declarar a tarefa fechada)

| O que verificar | Comando / acao | Resultado esperado |
|---|---|---|
| Pasta da cadeia existe | `ls workspace/_handoff/<data>-<slug>/` | `00-EXECUTION_PLAN.md`, os artefatos numerados e `99-EXECUTION_EVIDENCE.md` |
| Plano tem schema completo | `Read` no `00-EXECUTION_PLAN.md` | todo item com os 14 campos do §3 preenchidos |
| Nenhum arquivo com dois donos | conferir a coluna `ARQUIVOS` do plano inteiro | zero repeticao de caminho entre owners diferentes |
| Nenhum recurso externo com dois donos | conferir `RECURSOS_COMPARTILHADOS` | zero repeticao entre itens da mesma onda |
| DAG sem ciclo | percorrer `DEPENDE_DE` | todo ID citado existe e nao volta em si mesmo |
| Teto de 3 respeitado | contar itens por `ONDA` | no maximo 3 por onda |
| Evidencia real | `Read` no `99-EXECUTION_EVIDENCE.md` | toda validacao com tag `[verifiquei: ...]`, nenhum `CONCLUIDO` sem comando |
| Commit por owner | `git log --oneline -n <N>` | um commit por item concluido, citando o ID |

---

## 11. Pegadinhas

1. **Chamada de `Agent` em respostas diferentes NAO e paralelismo.** Se voce
   spawnar um por vez e esperar cada retorno, a onda virou fila. Paralelo e o
   mesmo bloco de resposta.
2. **`git add -A` numa onda paralela e desastre silencioso.** Um owner captura o
   trabalho meio-pronto de outro e commita. Sempre por caminho explicito.
3. **Arquivos disjuntos nao garantem itens disjuntos.** Dois agentes podem editar
   codigo diferente e quebrar o mesmo workflow do n8n. E para isso que existe
   `RECURSOS_COMPARTILHADOS`.
4. **Nao existe "revisor que ja aproveita e conserta".** Revisor que corrige vira
   segundo owner do arquivo e destroi o dono unico. Se ele tem `Edit`, foi
   spawnado com o tipo errado.
5. **O main nao "resolve rapidinho" um item.** Alem de bloqueado pelo hook, isso
   tira o item do plano e a evidencia some. Delega, mesmo que pareca menor.
6. **Plano sem `EVIDENCIA` executavel e plano decorativo.** "Testar se funciona"
   nao e evidencia; `pytest -q tests/test_x.py -> 12 passed` e.
7. **Item bloqueado por gate nao trava a onda.** Marque `BLOQUEADO`, siga nos
   independentes, e leve o gate ao dono numa pergunta so, no fim.
8. **Degradar para serial nao e derrota.** O contrato existe para evitar
   retrabalho, nao para maximizar agentes simultaneos.

---

## 12. Rollback da propria skill

O modo `PLAN` so cria arquivo novo em pasta propria (`workspace/_handoff/`) e nao
tem passo destrutivo. O modo `EXECUTE` herda o risco dos itens: quem carrega
rollback e cada item com `MUTACAO: EXTERNAL_WRITE`, no proprio campo `ROLLBACK`.

Se uma cadeia foi aberta com data ou slug errado, **nao apague**: crie a pasta
certa e deixe um `00-ABORTADA.md` de uma linha na errada, apontando para onde a
cadeia migrou. Evidencia nao se deleta, se marca.

---

## Skills relacionadas

- `haos-handoff-artefato`: como o artefato viaja entre agentes. Esta skill **usa**
  a convencao de pasta dela.
- `haos-model-router`: matriz completa de escolha de tier para o campo `MODEL`.
- `verification-before-completion`: nao existe concluido sem evidencia fresca.
  Vale junto, nao e substituida.
- `writing-plans` e `planning-with-files`: planejamento sem contrato de onda. Se
  a tarefa nao vai virar execucao paralela, use aquelas.

---

Autor: **Gian Marco Menegussi Scaglianti** (HAU Solucoes Digitais / HAOS).
Portada de `<toolkit-codex-interno>/.agents/skills/haos-execution-waves` em 04/09/2026.
