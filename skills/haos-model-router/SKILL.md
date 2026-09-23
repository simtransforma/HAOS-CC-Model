---
name: haos-model-router
description: "Matriz de decisao de qual modelo usar em cada tarefa do HAOS (Model Router). Use SEMPRE antes de spawnar qualquer Agent ou Workflow, e sempre que a pergunta for \"qual modelo usar\", \"escolher modelo\", \"que tier de modelo\", \"roteamento de modelo\", \"custo de token\", \"custo-beneficio de modelo\", \"haiku ou sonnet ou opus ou fable\", \"effort do workflow\". Cobre TAMBEM a TARIFA DE SPAWN: quando vale spawnar e quando NAO vale, custo real de um spawn, briefing enxuto e reuso de agente vivo por SendMessage. Use tambem quando a pergunta for \"vale a pena delegar isso\", \"faco eu ou delego\", \"quanto custa abrir um sub-agente\", \"por que o mix de modelo esta caro\". Define tier por tipo de tarefa com qualidade primeiro e custo-beneficio segundo."
---

# HAOS Model Router

Autor: Gian Marco Menegussi Scaglianti. Decisao permanente do dono do projeto.

## Principio (nao negociavel)

1. **Qualidade primeiro.** O objetivo e a tarefa sair CERTA na primeira vez.
2. **Custo-beneficio segundo.** Dentro do que entrega qualidade, escolher o mais barato.
3. **Economia nunca por si so.** Nao existe "usar haiku pra poupar" quando a tarefa pede julgamento.
4. **Na duvida entre dois tiers, SOBE.** Retrabalho, decisao errada ou mensagem externa errada custa muito mais que a diferenca de token.
5. **O main (orquestrador) fica no modelo da sessao.** O router decide o modelo dos SUB-AGENTES, nao o do main.

## Matriz por tipo de tarefa

| Tipo de tarefa | Tier | Por que | Quando subir / descer |
|---|---|---|---|
| Varredura, inventario, leitura em massa, grep, listagem de arquivos | `haiku` | Trabalho mecanico, criterio ja dado, volume alto | SOBE pra sonnet se a varredura exige INTERPRETAR o que achou (nao so achar) |
| Formatacao, conversao de formato, extracao deterministica de campo, renomear em lote | `haiku` | Regra explicita, zero ambiguidade | SOBE se o formato de destino for ambiguo ou se houver dado sujo/heterogeneo |
| Resumo mecanico de log, contagem, checagem de existencia | `haiku` | Saida verificavel objetivamente | SOBE se o resumo vira base de decisao |
| Codigo de rotina, script, CRUD, integracao com API ja conhecida | `sonnet` | Padrao conhecido, custo-beneficio otimo | SOBE pra opus se e codigo de producao critico, concorrencia, idempotencia ou dinheiro |
| Analise de dados padrao, relatorio, dashboard de metrica ja definida | `sonnet` | Pipeline conhecido | SOBE pra opus/fable se a analise vai virar decisao de midia ou investimento |
| QA de checklist, conferencia item a item contra criterio escrito | `sonnet` | Criterio existe, so aplicar | SOBE pra opus se o QA e adversarial (procurar o que ninguem viu) |
| Documentacao tecnica, POP, README | `sonnet` | Estrutura conhecida | SOBE se o doc define contrato entre times/sistemas |
| Arquitetura de sistema, decisao tecnica com trade-off | `opus` | Erro aqui contamina tudo que vem depois | SOBE pra fable se a decisao tem impacto estrategico/financeiro alto |
| Debugging profundo de causa raiz, bug intermitente, corrupcao de dado | `opus` | Exige hipotese, refutacao e leitura de sistema inteiro | Nunca desce |
| Seguranca, auditoria, hardening, revisao de guard/permissao | `opus` | Falso negativo custa incidente | SOBE pra fable em auditoria de escopo amplo |
| Refatoracao ampla, migracao de dados, mudanca de contrato | `opus` | Efeito colateral em cadeia | Nunca desce |
| Verificacao adversarial (provar que o fix esta errado) | `opus` | O papel e achar o que passou | SOBE pra fable quando fecha entrega para o dono |
| Estrategia, posicionamento, plano de campanha | `fable` | Julgamento aberto, sem gabarito | Nunca desce |
| Conselho / conclave / segunda opiniao de decisao | `fable` | Qualidade do julgamento e o produto | Nunca desce |
| Copy de conversao de alto valor (VSL, carta, oferta, headline principal) | `fable` | Diferenca de tier vira diferenca de faturamento | Copy operacional de baixo risco pode descer pra sonnet |
| Briefing que gera GASTO ou MENSAGEM EXTERNA (ativar campanha, disparo, envio) | `fable` | Irreversivel; erro sai pra fora | Nunca desce |
| Sintese final de multi-agente, consolidacao de entrega | `fable` | E o ponto onde o erro dos outros e pego ou passa | Nunca desce |
| Julgamento de qualidade (isso esta bom o suficiente?) | `fable` | Exige gosto e padrao alto | Nunca desce |

## Regra de effort (Workflow)

O parametro `effort` (`low` / `medium` / `high` / `xhigh` / `max`) e ortogonal ao modelo.

- Mecanico e deterministico: `low`.
- Trabalho padrao (codigo, analise, doc): `medium`.
- Verificacao, juizo, decisao, sintese final: `high` ou acima.
- Nunca economizar effort em fase de verificacao. E exatamente ali que a economia custa caro.

## Composicao em Workflow

- Fase mecanica DESCE (haiku/sonnet, effort low/medium).
- Fase de verificacao, decisao ou sintese SOBE (opus/fable, effort high+).
- Declarar `model` explicitamente em CADA `agent()` do script e em cada item de `meta.phases`.
- Workflow sem `model` declarado = roteamento por acaso. Nao aceitar.

## Como declarar

- Ferramenta `Agent`: parametro `model` OBRIGATORIO, valor em `haiku` | `sonnet` | `opus` | `fable`.
- No briefing do sub-agente, incluir uma linha:
  `MODELO: <tier> porque <motivo em 1 frase>`
- Ao spawnar, o main mostra ao dono essa mesma linha, curta, sem enrolacao. Uma linha por agente.

Exemplo:
```
MODELO: opus porque e causa raiz de bug intermitente em producao, nao rotina.
MODELO: haiku porque e varredura de arquivo com criterio ja fechado.
```

## Anti-padroes (nao fazer)

- `haiku` em tarefa que exige julgamento, trade-off ou juizo de qualidade.
- `fable` em grep, listagem ou conversao de formato.
- Economizar tier na fase de VERIFICACAO de qualquer pipeline.
- Spawnar Agent sem declarar `model` (o guard `model_guard.py` bloqueia).
- Escolher tier "porque a sessao ja estava nele". Herdar nao e decidir.
- Descer tier em tarefa que gera gasto, envio externo ou alteracao irreversivel.

## Trava fisica

O hook PreToolUse `model_guard.py` bloqueia qualquer chamada de `Agent` feita pelo MAIN dentro do escopo protegido sem `model` valido declarado. Sub-agentes nao sao afetados. `Workflow` nao e bloqueado pelo hook (o script e texto); a disciplina ali vem do `GATE MODELO` injetado a cada prompt pelo `prompt_router.py` e desta skill.

---

## Tarifa de spawn

Decisao do dono do projeto, tomada apos um conclave interno sobre quando o orquestrador deve
executar direto e quando deve delegar.

**O fato que gerou a regra.** Spawn nao e gratis e o custo NAO e proporcional a tarefa: o **boot do
sub-agente** domina. Piso medido de um spawn: **88k tokens e 1 minuto**. Mediana: **183k tokens e
8,3 minutos**. Nesta semana, **5 spawns triviais custaram 678k tokens** contra 10-40k se o main
tivesse feito na mao: **94% a 99% de desperdicio**. Escolher tier certo (secao acima) resolve metade
do problema; a outra metade e **nao pagar boot por nada**.

### Matriz: quando spawnar x quando NAO spawnar

| SPAWNAR (o boot se paga) | NAO SPAWNAR (o boot e o custo inteiro) |
|---|---|
| **3+ frentes independentes** rodando em paralelo | Tarefa que o main resolve em **ate 5 tool-calls de LEITURA** (ler arquivo, grep, checar existencia, `git status`, health check) |
| **Especialidade de produto** da tabela §4 do CLAUDE.md (copy, design, estrategia, midia, tracking, CRM) | **Reler o que o main JA tem em contexto**: o sub-agente vai ler de novo, do zero, e cobrar boot por isso |
| **Varredura volumosa**: mais de ~15 arquivos ou ~2.000 linhas, onde o ruido queimaria o contexto do main | **Verificacao visual de UI**: sub-agente NAO tem browser; quem olha a tela e o main |
| **Acao externa ou irreversivel** (publicar, enviar, ativar campanha, deploy, push, delete) | **Passo que exige MCP**: sub-agente NAO enxerga MCP (sem grafo de conhecimento, sem base vetorial de conhecimento, sem memoria de sessao, sem MCP de CRM/ERP proprio) |
| **Briefing que gera GASTO** ou mensagem para fora | **Transporte de arquivo sem julgamento**: o main move/copia/renomeia e delega so o MIOLO que exige juizo |
| **Escrita bloqueada pelo guard** (`main_guard.py` em ENFORCE) fora da allowlist de leitura | Passo unico dentro de uma cadeia que o main ja esta conduzindo, so para "ter um segundo par de olhos" sem hipotese concreta a testar |

**Regra de bolso:** *o spawn tem que comprar alguma coisa que o main nao tem* - especialidade,
volume que queimaria contexto, paralelismo, ou uma trava fisica. Se ele so repete o que o main faria,
voce pagou 88k de boot por nada.

> Este pacote nao inclui um regime de "cota de mutacao trivial" para o orquestrador: toda
> mutacao fora da allowlist de leitura pura vai para sub-agente (Regra de Ouro, ver docs).
> Se voce quiser um regime de cota, e uma extensao que voce escreve por cima deste guard,
> nao algo que este pacote traz pronto.

### Modelo por classe (com as metas do piloto)

| Classe de trabalho | Tier | Meta |
|---|---|---|
| Mecanico deterministico: inventario, grep em massa, formatacao, extracao de campo, contagem | `haiku` | **haiku >= 25% dos spawns** |
| Rotina: codigo padrao, script, integracao conhecida, relatorio, QA de checklist | `sonnet` | o volume do meio |
| Julgamento tecnico: causa raiz, arquitetura, seguranca, refatoracao ampla, verificacao adversarial | `opus` | **opus <= 45% dos spawns** |
| Julgamento aberto: estrategia, conclave, copy de alto valor, sintese final, acao externa | `fable` | sem teto |

**Mix medido em 03-06/09/2026: opus 67%, haiku 2,5%.** Isso e roteamento por inercia, nao decisao.
As metas medem o **MIX ao longo da semana**, nao a tarefa isolada: "na duvida entre dois tiers,
SOBE" (Principio 4) continua valendo caso a caso e **vence a meta** quando os dois conflitam. A meta
nao autoriza descer tier em tarefa que pede julgamento; ela cobra que o mecanico DESCA.

### Briefing enxuto (teto de 6 linhas)

Briefing de 3 paginas e a forma mais cara de pagar boot duas vezes: o texto entra no contexto do
sub-agente inteiro, e o que ele precisava era o **caminho**.

```
OBJETIVO: <1 frase, o resultado esperado>
DADOS: <caminho absoluto do artefato / comando que produz o dado>   # NUNCA colar relatorio inteiro
FORMATO: <o que voltar: tabela, diff, lista de caminhos, veredito>
RESTRICOES: <o que NAO tocar, arquivos de outro agente, nada de push/envio>
MODELO: <tier> porque <motivo em 1 frase>
LASTRO: toda causa/estado/mecanismo com [verifiquei: <comando> -> <o que vi>]; o resto [hipotese]
```

Se um artefato precisa ir de um agente para outro, vai pelo **DISCO**: grave e passe o **caminho**
(skill `haos-handoff-artefato`, gate no hook `handoff_guard`). Resumo do main no meio do
caminho apaga evidencia e ainda custa token nas duas pontas.

### Reuso: `SendMessage` antes de spawn novo

Agente **ja aberto** se retoma com **`SendMessage`** (pelo id ou nome), e ele **mantem o contexto
dele** - verificado em uso nesta sessao: 5 retomadas de agente sem perder estado. Spawn novo paga o
**boot inteiro de novo** e comeca do zero, sem o que ele ja descobriu.

Antes de spawnar, a pergunta e: **"ja tem alguem aberto que sabe disso?"** Se tem, `SendMessage`.
`ListAgents` mostra quem esta vivo.

### Onde o main pode trabalhar sem pagar nada

O **scratchpad da sessao e livre para o main** (arquivo temporario, resultado intermediario, script
de apoio, dado bruto de analise). Escrever ali nao e "executar tarefa de squad", e memoria de
trabalho - nao existe motivo para spawnar um agente so para criar um arquivo temporario.

### Anti-padroes de tarifa (somam aos anti-padroes de tier acima)

- Spawnar para ler UM arquivo cujo caminho o main ja conhece.
- Spawnar para conferir algo que o main acabou de ver na tela neste mesmo turno.
- Spawnar `opus` para inventario ou listagem (e `haiku`; era 67% do mix).
- Colar o relatorio inteiro do agente A no briefing do agente B, em vez do caminho do artefato.
- Abrir agente NOVO para continuar o trabalho de um agente que ainda esta vivo.
- Spawnar sub-agente para um passo que so o main consegue fazer (MCP, browser) - ele volta BLOQUEADO
  e o boot foi perdido.
- Usar "na duvida, DELEGUE" como desculpa para o trivial: a frase vale para **ESPECIALIDADE,
  VOLUME, PARALELISMO e ACAO EXTERNA**, nunca para as 5 leituras que o main faz em 30 segundos.
