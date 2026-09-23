---
name: haos-multi-agent-review
description: >-
  Contrato de orquestracao para revisao em ondas: ate tres revisores read-only com
  eixos distintos, fingerprint e deduplicacao de achado por causa raiz, contradicao
  resolvida por evidencia (nunca por maioria), owner unico por arquivo na correcao
  e reverificacao fresca antes de concluir. Fica ACIMA do /code-review nativo, que
  e single-pass e de um revisor so. Use SEMPRE que a mudanca tiver risco relevante,
  tocar varios modulos ou exigir mais de uma especialidade (correcao mais seguranca
  mais performance), quando dois agentes derem parecer conflitante, quando a
  revisao anterior deixou passar bug, ou antes de mexer em codigo que emite nota
  fiscal, gera cobranca, dispara mensagem, movimenta estoque ou gasta dinheiro.
  Gatilhos tipicos do usuario: "revisa com mais de um agente", "poe dois olhando
  isso", "quero segunda opiniao nesse codigo", "junta os achados", "esses dois se
  contradisseram", "revisa direito antes de subir", "isso aqui e critico, nao pode
  passar bug", "tira o duplicado desse relatorio". NAO use para mudanca pequena num
  arquivo so: ali um revisor basta, use /code-review. NAO use para decisao de
  negocio ou estrategia: a sintese daquilo e do conclave (/conclave). NAO use para
  montar o gate em si: isso e haos-quality-gates.
metadata:
  version: 1.0.0
  autor: Gian Marco Menegussi Scaglianti
  portado_de: <toolkit-codex-interno>/.agents/skills/haos-multi-agent-review (26/08/2026)
  portado_em: 2026-09-04
---

# HAOS Multi-Agent Review

Use em mudanca com risco relevante, varios modulos ou mais de uma especialidade.
Para mudanca pequena, **um revisor adequado basta** | nao gaste onda inteira nisso.

## Onde esta skill se encaixa

O `/code-review` nativo e **single-pass**: um revisor, uma passada, sem dedup entre
pareceres. Esta skill e a camada **acima** dele: ela orquestra varias passadas
(inclusive varias chamadas de `/code-review` com eixos diferentes), consolida os
achados e resolve contradicao. Quando a revisao for de **decisao** e nao de codigo,
o lugar natural da sintese e o conclave do HAOS (`/conclave`), nao esta skill.

## Quem executa

O main **orquestra**: define escopo, spawna as ondas, consolida, decide. Ele e
bloqueado pelo `main_guard.py` de editar projeto e de rodar comando fora da
allowlist de leitura, entao **quem revisa e quem corrige e sempre sub-agente**.

- **Revisor = `Explore` ou `Plan`.** Eles nao tem Edit, Write nem NotebookEdit:
  a regra "revisor nao corrige arquivo" vira trava fisica, nao promessa. Use
  tambem `haos:qa-reviewer` e `haos:chuck-norris` (audit-only) quando o eixo pedir.
- **Corretor = agente com escrita** (`haos:dev-backend`, `haos:dev-frontend`,
  `haos:devops`), com write-set disjunto declarado no briefing.
- Revisores da mesma onda vao em **uma unica mensagem com varias tool calls**, para
  rodarem em paralelo. Revisao longa vai com `run_in_background: true`.
- `model` e **obrigatorio** em todo `Agent`: `sonnet` para eixo mecanico ou
  checklist, `opus` para correcao, causa raiz, seguranca e verificacao adversarial,
  `fable` para a sintese final e para o juizo de qualidade. Na duvida entre dois
  tiers, **sobe**.

## Contrato

1. Registre objetivo, escopo, criterios de aceite e **baseline** antes de spawnar.
2. **Onda de revisao:** no maximo tres revisores, todos read-only, **cada um com um
   eixo distinto** (ex.: correcao, seguranca, performance). Revisor nao corrige.
3. Cada achado sai com **severidade `P0` a `P3`**, arquivo e local, evidencia,
   impacto e correcao proposta. Evidencia com tag `[verifiquei: <comando> -> <o que
   vi>]`; o que for deducao sai marcado `[hipotese]`.
4. O orquestrador consolida, remove duplicata e **resolve contradicao por
   evidencia, nunca por maioria de votos**.
5. **Onda de correcao:** no maximo tres executores com write-sets disjuntos. Cada
   arquivo tem **um unico owner por onda**.
6. O revisor final **nao pode ser o owner** da correcao que ele valida.
7. Rode de novo os checks que provam cada claim **antes** de concluir.

Passagem de bastao entre agentes vai por **artefato em disco**: o proximo agente
recebe o CAMINHO do arquivo, nunca o resumo do main (skill `haos-handoff-artefato`,
gate no hook `handoff_guard`).

## Fingerprint de achado

Use uma chave estavel:

```text
<regra>|<arquivo>|<simbolo-ou-linha>|<sintoma>
```

Achados com a **mesma causa raiz** viram um item consolidado, mesmo que os
revisores tenham descrito o sintoma com palavras diferentes. Preserve todas as
evidencias relevantes e **indique explicitamente quando os revisores discordarem**:
divergencia escondida vira bug em producao.

## Saida minima

```text
STATUS: APROVADO | AJUSTES NECESSARIOS | BLOQUEADO
ESCOPO REVISADO:
BASELINE:
ACHADOS P0-P3:
CORRECOES APLICADAS:
VERIFICACAO FRESCA:
RISCO RESIDUAL:
```

Alteracao externa, push, merge, publicacao, envio, gasto ou remocao destrutiva
continua bloqueada ate OK explicito do dono.
