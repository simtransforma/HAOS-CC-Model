---
name: haos-structural-refactor
description: >-
  Detecta god files e modulos inchados com um scanner deterministico read-only,
  confirma o risco no codigo real (nunca pela contagem de linhas sozinha) e produz
  um plano de refatoracao incremental por costuras naturais. Dois modos: AUDIT
  (padrao, read-only, delegado a sub-agente) e APPLY (escrita, so com pedido claro
  de implementacao mais gate do dono). Use SEMPRE que a tarefa for identificar
  arquivo grande demais, dividir modulo monolitico, separar responsabilidades
  misturadas, planejar extracao de modulo, definir teto de linhas, ou avaliar se
  vale refatorar por tamanho. Use TAMBEM em modo AUDIT automatico, sem o usuario
  pedir, como PREFLIGHT antes de qualquer alteracao substancial em modulo ja
  existente: rode o scanner no menor escopo afetado antes de editar, para saber se
  voce esta prestes a engordar um arquivo que ja e candidato a risco estrutural.
  Gatilhos tipicos do usuario: "esse arquivo ta gigante", "quebra esse modulo",
  "isso ta monolitico", "ta impossivel de manter", "separa por responsabilidade",
  "esse .py tem 3 mil linhas", "acha os god files", "qual arquivo ta inchado",
  "poe um limite de linhas", "divide esse arquivo". NAO use para refatoracao de
  logica ou caca a bug: isso e systematic-debugging. NAO use para desenhar
  arquitetura nova do zero: isso e software-architecture (haos:software-architecture).
  NAO use para montar gate de CI: isso e haos-quality-gates.
metadata:
  version: 1.0.0
  autor: Gian Marco Menegussi Scaglianti
  portado_de: <toolkit-codex-interno>/.agents/skills/haos-structural-refactor (03/09/2026)
  portado_em: 2026-09-04
  adaptacoes: >-
    AUDIT delegado (main nao roda python); Graphify->mcp__gbrain__code_*;
    scanner validado por execucao
---

# HAOS Structural Refactor

Opere em `AUDIT` por padrao. Trate tamanho apenas como **sinal de triagem**: um
arquivo acima do teto e candidato a inspecao, **nao e prova de divida tecnica**.
Arquivo de 900 linhas coeso e com dono claro pode estar certo; arquivo de 200
linhas que mistura parsing, I/O e regra de negocio pode estar errado.

---

## 1. Quem executa (leia isto ANTES de qualquer coisa)

**O main nao roda o scanner.** No Claude Code o hook `main_guard.py` esta em
ENFORCE e bloqueia fisicamente o main de rodar `python`, `py`, `pwsh`, `npm` e de
editar arquivo de projeto. A allowlist do main e **so de leitura**.
`[verifiquei: CLAUDE.md §1 -> "ENFORCE ligado (ENFORCE_DEFAULT = True)", allowlist explicita de leitura pura]`

Portanto:

| Papel | O que faz |
|---|---|
| **Main** | Le (`Read`/`Grep`/`Glob`), define escopo e teto, **spawna o sub-agente que roda o scanner**, le o relatorio devolvido, prioriza e decide. |
| **Sub-agente do AUDIT** | Roda o scanner, inspeciona os candidatos no codigo real, devolve o relatorio. Read-only. |
| **Sub-agente do APPLY** | Escreve. So entra depois do gate. |

### Briefing pronto para colar no sub-agente do AUDIT

Resolva `<skill-dir>` como o diretorio que contem este `SKILL.md`, hoje
`<SEU_CAMINHO>/skills/haos-structural-refactor`. O comando:

```bash
py -3 "<SEU_CAMINHO>/skills/haos-structural-refactor/scripts/scan_structural_risk.py" "<root>" --max-lines 350 --format markdown
```

Variantes: `--format json` para consumo estruturado, `--output <arquivo>` para
gravar o relatorio (o script **recusa sobrescrever** arquivo existente). O scanner
nunca altera o que analisa e **nunca imprime o conteudo dos arquivos**, so caminho
e contagem.
`[verifiquei: py -3 scripts/scan_structural_risk.py --help -> exit 0, flags root/--max-lines/--format/--output]`

Escolha do tipo de sub-agente:

| Situacao | `subagent_type` | `model` |
|---|---|---|
| So rodar o scanner e devolver a tabela | `Explore` | `haiku` |
| Rodar o scanner **e** interpretar os candidatos no codigo | `haos:dev-backend` | `sonnet` |
| Julgar costura, contrato publico, risco de quebra | `Plan` ou `haos:dev-backend` | `opus` |

`model` e **obrigatorio** em todo `Agent`: o hook `model_guard.py` esta em
ENFORCE e bloqueia o spawn sem tier valido.

---

## 2. Preflight automatico (a skill entra sozinha)

Antes de **qualquer alteracao substancial em modulo ja existente** (refatorar,
acrescentar responsabilidade nova, mexer em arquivo que voce nao conhece), rode o
`AUDIT` no **menor escopo afetado**, nao no repo inteiro. Custo de segundos, evita
engordar um arquivo que ja passou do teto.

Nao e preciso o usuario pedir. Nao vale a pena para arquivo novo, script isolado
ou correcao de uma linha.

---

## 3. AUDIT

1. **Ground truth fresca:** estado do worktree (`git status`), manifests, estrutura
   e os comandos oficiais de teste do projeto. Preserve alteracao preexistente que
   voce nao criou.
2. **Rode o scanner** (via sub-agente, §1) e **inspecione cada candidato no codigo
   real**. Avalie mistura de responsabilidades, coesao, fan-in/fan-out, contratos
   publicos, estado compartilhado, cobertura de teste e historico de mudanca.
   **Nao conclua risco pela contagem de linhas isolada.**
3. **Baseline e validacoes:** carregue `haos-quality-gates` para fixar o baseline
   numerico e a escada de gates da stack antes de propor qualquer mexida.
4. **Ondas e ownership:** carregue `haos-execution-waves` para montar o plano por
   ondas com dono unico por arquivo, dependencias, artefato e evidencia.
5. **Grafo de codigo:** quando o impacto for transversal, houver contrato
   compartilhado ou a arquitetura for desconhecida, use os MCPs **nativos** desta
   casa em vez de qualquer indexador externo:

   | Pergunta | Ferramenta |
   |---|---|
   | Onde este simbolo e definido? | `mcp__gbrain__code_def` |
   | Quem chama isto (raio de impacto direto)? | `mcp__gbrain__code_callers` |
   | O que isto chama? | `mcp__gbrain__code_callees` |
   | Raio de impacto transitivo, por profundidade | `mcp__gbrain__code_blast` |
   | Toda mencao literal (rename, deprecacao) | `mcp__gbrain__code_refs` |
   | Cadeia de execucao ate o efeito colateral | `mcp__gbrain__code_flow` |

   **Confirme no codigo toda relacao que o grafo apontar.** O grafo orienta a
   busca; ele nao substitui a leitura. **Nao instale Graphify** e nao leia indice
   de outro runtime.
   Atencao: MCP so existe para o **main**. Sub-agente nao enxerga MCP | se o AUDIT
   precisa do grafo, quem consulta e o main, e ele passa o resultado no briefing.

6. **Entregue** candidatos priorizados, evidencias, costuras naturais, plano por
   ondas, testes previstos e risco residual. Permaneca **read-only**.

### Costuras naturais

Fronteira de dominio, adaptador de I/O, parsing, validacao, persistencia,
apresentacao e componente com estado independente. **Extraia por essas fronteiras.**
Nao divida so para baixar um numero: corte arbitrario troca um arquivo grande por
tres arquivos acoplados, que e pior.

---

## 4. APPLY

Entre em `APPLY` **somente quando o usuario pedir implementacao**. Refatoracao
ampla, transversal ou com varios modulos exige primeiro baseline e plano e, depois,
**OK explicito do dono** no gate apresentado antes da primeira escrita.

1. Revalide ground truth e baseline **imediatamente antes** de editar.
2. Preserve API publica, comportamento observavel e compatibilidade, salvo mudanca
   de contrato explicitamente aprovada.
3. **Delegue.** O main nao escreve. Owner e `haos:dev-backend`, `haos:dev-frontend`
   ou `haos:devops`, com write-set explicito.
4. No maximo **tres unidades independentes por onda**, com ownership exclusivo e
   write-sets disjuntos. Serialize arquivo ou recurso compartilhado. Isso e o
   contrato de `haos-execution-waves`: siga o schema de tarefa dela, incluindo
   `RECURSOS_COMPARTILHADOS`, `MUTACAO` e `ROLLBACK`.
5. Teste cada unidade apos a mudanca e rode os gates de integracao da onda,
   conforme a escada de `haos-quality-gates`.
6. Revisor **diferente do owner**, read-only. Use `haos-multi-agent-review` quando a
   refatoracao tocar varios modulos ou exigir mais de um eixo. `Explore` e `Plan`
   nao tem `Edit`/`Write`: a regra "revisor nao corrige" vira trava fisica.
7. **Proibido commit por sub-agente fora do proprio write-set.** Nada de push,
   merge, deploy ou acao externa sem OK do dono.
8. **Interrompa a onda** se contrato quebrar, teste regredir, a costura se mostrar
   artificial ou o worktree divergir de forma relevante.

---

## 5. Saida minima

```text
STATUS: AUDIT CONCLUIDO | APPLY CONCLUIDO | REVISAO NECESSARIA | BLOQUEADO
ESCOPO:
BASELINE:
CANDIDATOS E EVIDENCIAS:
COSTURAS NATURAIS:
ONDAS E OWNERSHIP:
VALIDACOES:
RISCO RESIDUAL:
```

Toda afirmacao de causa, estado ou mecanismo sai com
`[verifiquei: <comando> -> <o que vi>]`. Deducao nao testada sai como `[hipotese]`
ou `[a confirmar]` (CLAUDE.md §0 e §0.1).

---

## 6. O scanner

`scripts/scan_structural_risk.py`, stdlib pura (`argparse`, `json`, `os`, `sys`,
`pathlib`), sem dependencia externa. Ignora `node_modules`, `dist`, `build`,
`.venv`, `__pycache__` e afins, lockfiles, minificados e gerados
(`*.generated.*`, `_pb2.py`), e nao segue symlink nem junction. Cobre ~60
extensoes (Python, TS/JS, Go, Rust, Java, C/C++, PHP, Ruby, PowerShell, SQL,
Terraform, Solidity, HTML/CSS, Vue/Svelte).

**Validado por execucao nesta casa em 04/09/2026, nao por leitura de imports:**

- `py -3 scripts/scan_structural_risk.py --help` -> exit 0.
- `py -3 -m unittest discover -s tests -v` -> **6 testes, 6 OK**, incluindo o que
  prova que o conteudo do arquivo escaneado nunca aparece na saida e o que prova
  que os arquivos escaneados nao mudam (bytes e mtime iguais).
- AUDIT real em `<SEU_CAMINHO>/hooks` (`--max-lines 350`): 28 arquivos,
  9.838 linhas, **10 candidatos**, com `main_guard.py` (1.362 linhas),
  `finish_task.ps1` (873) e `prompt_router.py` (780) no topo.

Ou seja: **a propria casa tem alvo real**. Isso e triagem, nao veredito | cada um
desses dez ainda precisa de inspecao no codigo antes de virar plano.

---

## 7. Skills irmas (como se encadeiam)

- **`haos-quality-gates`** | fixa o baseline numerico e a escada
  `OBSERVAR -> CONTER -> REDUZIR -> ZERAR -> BLOQUEAR` **antes** de a refatoracao
  comecar, para que a divisao do arquivo nao esconda regressao.
- **`haos-execution-waves`** | fornece o contrato da execucao: dono unico por
  arquivo, DAG de dependencias, teto de 3 agentes por onda, artefato em
  `workspace/_handoff/` e evidencia por item.
- **`haos-multi-agent-review`** | revisa o resultado com ate tres revisores
  read-only de eixos distintos, deduplica achado por causa raiz e resolve
  contradicao por evidencia, nunca por maioria.
- `haos-handoff-artefato` | o artefato viaja por caminho em disco, nunca por
  resumo do main.
- `verification-before-completion` | nada vira concluido sem evidencia fresca.

---

Autor: **Gian Marco Menegussi Scaglianti** (HAU Solucoes Digitais / HAOS).
Portada de `<toolkit-codex-interno>/.agents/skills/haos-structural-refactor` em
04/09/2026.
