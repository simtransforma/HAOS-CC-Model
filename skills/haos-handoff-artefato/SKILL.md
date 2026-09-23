---
name: haos-handoff-artefato
description: >-
  Handoff por artefato entre agentes do HAOS. Use SEMPRE que a saida de um
  agente entrar no trabalho de outro (diretor-criativo -> dev, copy -> designer,
  estrategista -> media-buyer) ou quando o dono for olhar o resultado com o olho
  (design, LP, criativo, copy publicada, PDF). A saida do agente A vai pro DISCO
  e o agente B recebe o CAMINHO do arquivo, nunca o resumo do main. Existe
  porque o main comprime a saida do especialista antes de repassar e o proximo
  agente inventa o que faltou.
metadata:
  version: "1.0"
  autor: Gian Marco Menegussi Scaglianti
  marca: HAOS
  type: procedimento
---

# HAOS - Handoff por Artefato

## O caso que originou esta skill (leia, e o argumento inteiro)

O diretor-criativo produziu uma spec visual pixel a pixel de uma peca de campanha:
hex, tipografia, peso, espacamento, hierarquia. O main leu a spec, resumiu e
briefou o dev com **"preto e dourado"**. O dev inventou o resto.

A squad produziu. O especialista foi chamado. O main delegou certo. E o
resultado ficou **indistinguivel de nao ter chamado especialista nenhum**.

A falha nao foi de delegacao, foi de **transporte**: o main e um compressor com
perda entre a saida de A e a entrada de B. Um agente nao le o transcript do
outro; ele le o que o main digitou no prompt dele. Se o main digitou um resumo,
o resumo E a spec, e tudo que ficou de fora vira invencao do executor.

**Solucao: tirar o main do caminho do conteudo.** A spec vai pro disco. O
executor recebe o CAMINHO e a ordem de ler o arquivo inteiro. O main transporta
um ponteiro, nao um resumo. Ponteiro nao comprime.

---

## a. Quando usar (gatilho objetivo)

**OBRIGATORIA quando:**

1. **A saida de um agente entra no trabalho de outro.** Qualquer encadeamento:
   diretor-criativo -> dev-frontend, copy-specialist -> designer,
   estrategista-chefe -> media-buyer, pesquisador -> copy-specialist,
   funnel-architect -> automation-engineer.
2. **O dono vai olhar o resultado com o olho.** Design, landing page, criativo,
   copy publicada, PDF, apresentacao. Ai a fidelidade visual/textual e o
   produto; "mais ou menos" e defeito.

**FORA do gatilho (nao use, so atrapalha):**

- Diagnostico, leitura, consulta, auditoria ("por que o container caiu?").
- Infra e comando de servidor.
- Tarefa de agente unico, sem encadeamento e sem entrega visual.

Na duvida: **o proximo agente vai precisar de um DETALHE que so existe na cabeca
do anterior?** Se sim, artefato em disco. Se nao, toca o barco.

**Gatilhos textuais reais** (frases do dono que quase sempre significam
encadeamento): "manda o dev montar isso", "pega o que o criativo fez e", "usa a
spec do", "aplica esse design na pagina", "transforma isso em LP".

---

## b. Pre-requisitos

- Pasta base do handoff (ja existe, e versionada e commitada pelo `finish_task`):
  `workspace/_handoff/` na raiz do repo da sessao. Exemplo absoluto na arvore
  canonica: `<SEU_CAMINHO>\workspace\_handoff\`. Fallback,
  ultimo candidato e so enquanto o legado existir:
  `<SEU_CAMINHO_LEGADO>\workspace\_handoff\`
- Os agentes envolvidos precisam de `Read` e `Write` (sub-agente ja tem: o
  `main_guard` libera sub-agente por padrao).
- Skill relacionada, NAO substituida por esta: `verification-before-completion`
  ("Iron Law: no completion claims without fresh verification evidence"). Esta
  skill diz **onde** a evidencia mora no encadeamento de agentes; a outra diz
  que sem evidencia fresca nao existe "concluido". As duas valem juntas.

---

## c. Passo a passo

### Convencao de pasta

```
workspace/_handoff/<AAAAMMDD>-<slug-da-tarefa>/
    01-diretor-criativo-spec-visual.md
    02-copy-specialist-copy-lp.md
    03-dev-frontend-conformidade.md
```

Regras do nome:
- `<AAAAMMDD>` = data de abertura da tarefa (ex.: `20260805`).
- `<slug-da-tarefa>` = minusculo, sem acento, com hifen (ex.: `landing-page-nova`).
- `NN-` = ordem na cadeia, com dois digitos. **A numeracao e o que deixa a cadeia
  legivel por um `ls` simples**: da pra ver quem produziu, em que ordem, e se o
  arquivo de conformidade do executor existe, sem abrir nada.
- Depois do `NN-`, o nome do agente que produziu, depois o tipo do conteudo.

### Por que aqui e nao no scratchpad

O scratchpad (`AppData\Local\Temp\claude\...\scratchpad`) e **temporario,
escopado por sessao e invisivel pro dono**. Serve pra rascunho e arquivo
intermediario descartavel.

O artefato de handoff e o oposto disso: e **EVIDENCIA**. Precisa
(1) sobreviver a sessao, porque a auditoria do "por que a pagina saiu diferente
da spec" acontece dias depois; (2) ser commitado pelo `finish_task.ps1`, que
versiona o repo da sessao; (3) ser abrivel pelo dono direto no storage
compartilhado do time, sem pedir nada pra ninguem. Rascunho no scratchpad, evidencia no `workspace/`.

### Bloco do PRODUTOR (colar no prompt do agente A)

```
SAIDA EM DISCO (OBRIGATORIA):
Grave a spec COMPLETA em:
...\workspace\_handoff\<data>-<slug>\01-<seu-agente>-<tipo>.md
Escreva para outro agente EXECUTAR sem te perguntar nada: valores concretos
(hex, px, fonte, peso, ordem das secoes), nao adjetivos. "Preto e dourado
elegante" nao e spec. Sua resposta pra mim pode ser resumo; o ARQUIVO nao pode.
```

### Bloco do CONSUMIDOR (colar no prompt do agente B)

```
ARTEFATO DE ENTRADA (LER INTEIRO ANTES DE QUALQUER ACAO):
<caminho absoluto do arquivo>

Leia esse arquivo com Read, do inicio ao fim, antes de escrever uma linha.
Ele E a especificacao. Eu (main) NAO resumi o conteudo dele aqui de proposito:
o que vale e o arquivo, nao o que esta escrito neste briefing.
PROIBIDO inventar cor, tipografia, espacamento, secao, texto ou ordem que nao
esteja no arquivo. Faltou algo na spec? PARE e pergunte. Nao preencha lacuna
com bom senso.

ENTREGA (as duas, senao a tarefa nao esta feita):
1. O build/arquivo pedido.
2. Um arquivo `NN-<seu-agente>-conformidade.md` NA MESMA PASTA do artefato de
   entrada, com uma linha por requisito da spec:

| # | Requisito (trecho LITERAL da spec) | Onde implementei (arquivo:linha) | Bate? | Divergencia e por que |

   "Bate?" = SIM / NAO / N-A. Requisito da spec sem linha na tabela = tarefa
   incompleta. NAO sem justificativa = tarefa incompleta.
```

### Passo do MAIN antes de declarar concluido

Nao e opcional e nao vale de memoria: precisa de **tool call visivel no
transcript** (Regra #0 / VBA).

```bash
# 1. a cadeia existe e esta completa?
ls "<SEU_CAMINHO>/workspace/_handoff/<exemplo-de-pasta>/"
```

```
# 2. ler o arquivo de conformidade com a ferramenta Read (nao com cat, nao "de cabeca")
Read: ...\workspace\_handoff\20260101-exemplo-tarefa\03-dev-frontend-conformidade.md
```

Veredito:
- Arquivo de conformidade **ausente** -> NAO concluido.
- Qualquer **NAO sem justificativa** na coluna "Divergencia" -> NAO concluido.
- Requisito da spec **sem linha** na tabela -> NAO concluido.

Em qualquer um dos tres: **re-spawn do executor** passando o mesmo caminho do
artefato mais a lista das linhas que falharam. Nao refaca voce mesmo (Regra de
Ouro §1) e nao aceite "ajustei" sem a tabela atualizada.

---

## d. Verificacao

| O que verificar | Comando/acao | Resultado esperado |
|---|---|---|
| Pasta da cadeia existe | `ls workspace/_handoff/<data>-<slug>/` | 2+ arquivos, numerados em ordem |
| Produtor gravou spec concreta | `Read` no `01-*.md` | valores (hex/px/fonte), nao adjetivo |
| Consumidor leu de fato | tabela de conformidade cita trecho LITERAL da spec | trecho bate com o arquivo `01-*` |
| Cobertura | 1 linha por requisito da spec | nenhum requisito orfao |
| Gate automatico registrou | `tail <SEU_CAMINHO>/hooks/handoff_guard.log` | linha `verdict=ALLOW why=aponta_arquivo` no spawn do consumidor |

---

## e. Pegadinhas

1. **Resumo do main e o inimigo, nao o atalho.** Se voce (main) escrever no
   prompt do consumidor "a spec diz preto e dourado, o arquivo esta em X", o
   agente ancora no seu resumo e le o arquivo por cima. Passe o CAMINHO e diga
   explicitamente que voce NAO resumiu de proposito.
2. **"Resposta pra mim" nao e artefato.** O texto que o sub-agente devolve no
   final da execucao dele morre no transcript e ja vem comprimido pelo proprio
   agente. Se nao foi pro disco com `Write`, nao existe pro proximo.
3. **Adjetivo nao e spec.** "Elegante", "premium", "clean", "com respiro" nao
   sao executaveis. Se o artefato do produtor tem adjetivo no lugar de valor, o
   handoff ja nasceu quebrado: devolva pro produtor ANTES de spawnar o executor.
4. **Conformidade sem trecho literal e teatro.** Se a coluna "Requisito" tiver
   parafrase em vez de citacao, o executor pode ter conferido a spec que ele
   imaginou. Exija trecho copiado.
5. **N-A e valido, NAO silencioso nao e.** Requisito que nao se aplica ao build
   entregue pode ser N-A com uma linha de motivo. NAO sem motivo = incompleto.
6. **Scratchpad some.** Ja aconteceu de artefato "salvo" em pasta temporaria
   sumir antes da auditoria. Se o dono nao consegue abrir pelo storage
   compartilhado, nao serve como evidencia.
7. **Cadeia longa nao vira arquivo unico.** Cada agente grava o SEU arquivo
   numerado. Reescrever o `01-` com o conteudo do `02-` apaga a autoria e
   destroi a rastreabilidade de quem decidiu o que.
8. **O gate automatico esta em MODO LOG.** O hook `handoff_guard` HOJE nao
   bloqueia nada, so registra o que teria bloqueado. Nao confie nele como rede
   de seguranca: quem garante o handoff e este procedimento.

---

## f. Rollback

Nao ha passo destrutivo: a skill so CRIA arquivos novos em pasta propria
(`workspace/_handoff/`). Nunca sobrescreve arquivo de projeto.

Se uma cadeia foi aberta errada (slug/data errados), **nao apague**: crie a
pasta certa e deixe a errada com um `00-ABORTADA.md` de uma linha dizendo pra
onde a cadeia migrou. Artefato e evidencia; evidencia nao se deleta, se marca.

Se o gate automatico atrapalhar um spawn legitimo (falso positivo), o caminho e
o token de escape no prompt, **nunca** desregistrar o hook:

```
[HANDOFF: N-A]
```

---

## Gate automatico (contexto)

- Hook: `<SEU_CAMINHO>/hooks/handoff_guard.py`
- Evento: `PreToolUse`, matcher `Agent|Task`
- Estado: **MODO LOG** (`ENFORCE_DEFAULT = False`). Ligar o enforce e decisao do
  dono, nao do agente.
- Regra: prompt de spawn com palavra de artefato (spec, design, copy, layout,
  criativo, wireframe, mockup, landing, LP, arte, KV) **E** verbo de producao
  (criar, escrever, montar, construir, implementar, aplicar, gerar, redesenhar,
  refazer) precisa conter pelo menos um caminho de arquivo.
- Calibragem sobre um historico real de spawns em producao: baixa taxa de
  acerto (na casa de poucos por cento). Trate como sinal fraco, nao como
  rede de seguranca.
- Log: `<SEU_CAMINHO>/hooks/handoff_guard.log`

---

Autor: **Gian Marco Menegussi Scaglianti** (HAU Solucoes Digitais / HAOS).
