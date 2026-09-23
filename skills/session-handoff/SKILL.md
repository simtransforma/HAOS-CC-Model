---
name: session-handoff
description: >-
  Cria documento de handoff CURADO (nao exaustivo) para retomar sessao com
  zero ambiguidade: estado atual, decisao tomada, proximo passo, arquivo
  critico e pegadinha conhecida. Use quando o dono pedir "salva o estado",
  "cria um handoff", "preciso pausar", contexto ficando cheio, marco grande
  concluido, ou "carrega o handoff"/"retoma de onde parou". Diferente de
  `session-full-dump` (dump exaustivo e sem curadoria de TUDO que a sessao fez)
  e de `haos-handoff-artefato` (handoff de artefato ENTRE agentes na mesma
  tarefa, nao entre sessoes).
---

# Handoff de Sessao

Cria documento de handoff que permite a um agente novo (ou a voce mesmo, numa
sessao futura) continuar o trabalho sem ambiguidade. Resolve o problema de
esgotamento de contexto em tarefa longa.

## Quando usar esta skill x as outras duas de handoff do HAOS

| Skill | Escopo | Quando usar |
|---|---|---|
| `session-handoff` (esta) | ENTRE SESSOES do mesmo trabalho, retomada por qualquer agente/dia | "salva isso pra eu continuar amanha", contexto ficando cheio, pausa de trabalho longo |
| `session-full-dump` | Dump EXAUSTIVO e deterministico de tudo que uma sessao fez (ferramenta, arquivo, comando, sub-agente) | Auditoria, "o que essa sessao fez de A a Z", nao precisa de curadoria |
| `haos-handoff-artefato` | Handoff de ARTEFATO entre AGENTES na MESMA tarefa (diretor-criativo -> dev, copy -> designer) | Encadeamento de sub-agente dentro do Rito ou de uma delegacao, artefato vai pro disco em `workspace/_handoff/` |

Esta skill e a mais "leve" das tres: um documento curado e legivel, nao um
dump bruto nem um artefato tecnico para outro especialista.

## Ajustes de doutrina HAOS

- Guardar handoff em `memory/handoffs/`, nunca em `.claude/handoffs/`.
- Em trabalho de sistema HAOS, criar handoff em
  `<SEU_CAMINHO>/memory/handoffs/` (raiz canonica do seu repo).
- Em trabalho de projeto/cliente especifico, criar handoff em
  `memory/handoffs/` daquele projeto quando existir; senao usar o workspace
  atual.
- Nunca escrever segredo, valor de token, cookie, senha, chave privada ou
  conteudo de `.env` num handoff. Registrar so o NOME da variavel de ambiente
  (MASTER.env, CLAUDE.md §11).
- Se a tarefa mencionar HAOS, Rito, Mega Brain, agente, seguranca, deploy,
  servidor ou Cloudflare, carregar o CLAUDE.md (usuario + projeto) antes de
  criar ou retomar um handoff.
- Acao externa sensivel continua bloqueada sem OK explicito do dono; um
  handoff pode DOCUMENTAR uma aprovacao pendente, mas nunca executa-la
  (CLAUDE.md §3, item 6).

## Selecao de modo

**Criando um handoff?** O dono quer salvar o estado atual, pausar o trabalho,
ou o contexto esta ficando cheio.
- Seguir: Fluxo CRIAR abaixo.

**Retomando de um handoff?** O dono quer continuar trabalho anterior, carregar
contexto, ou menciona um handoff existente.
- Seguir: Fluxo RETOMAR abaixo.

**Sugestao proativa?** Depois de trabalho substancial (5+ edicoes de arquivo,
debug complexo, decisao arquitetural grande), sugerir:
> "Fizemos progresso significativo. Considere criar um handoff para preservar
> esse contexto para sessoes futuras. Diga 'cria handoff' quando quiser."

## Fluxo CRIAR

### Passo 1: Gerar o scaffold

```bash
python scripts/create_handoff.py [slug-da-tarefa]
```

Exemplo: `python scripts/create_handoff.py implementando-auth-usuario`

**Para handoff de continuacao** (encadeado com trabalho anterior):
```bash
python scripts/create_handoff.py "auth-parte-2" --continues-from 2026-09-15-auth.md
```

O script:
- Cria `memory/handoffs/` se nao existir.
- Gera nome de arquivo com timestamp.
- Pre-preenche: timestamp, caminho do projeto, branch git, commit recente,
  arquivo modificado.
- Adiciona link de cadeia de handoff, se for continuacao.
- Mostra o caminho do arquivo gerado para edicao.

### Passo 2: Completar o documento

Abrir o arquivo gerado e preencher toda secao `[TODO: ...]`. Priorizar:

1. **Resumo do Estado Atual**, o que esta acontecendo agora.
2. **Contexto Importante**, informacao critica que o proximo agente PRECISA
   saber.
3. **Proximos Passos Imediatos**, claro e acionavel.
4. **Decisoes Tomadas**, escolha com motivo, nao so o resultado.

Usar a estrutura de [references/handoff-template.md](references/handoff-template.md)
como guia.

### Passo 3: Validar o handoff

```bash
python scripts/validate_handoff.py <arquivo-do-handoff>
```

O validador checa:
- [ ] Nenhum placeholder `[TODO: ...]` restante.
- [ ] Secao obrigatoria presente e preenchida.
- [ ] Nenhum segredo potencial detectado (chave de API, senha, token).
- [ ] Arquivo referenciado existe.
- [ ] Score de qualidade (0-100).

**Nao finalizar um handoff com segredo detectado ou score abaixo de 70.**

### Passo 4: Confirmar o handoff

Reportar ao dono:
- Local do arquivo de handoff.
- Score de validacao e alerta, se houver.
- Resumo do contexto capturado.
- Primeiro item de acao para a proxima sessao.

## Fluxo RETOMAR

### Passo 1: Listar handoff disponivel

```bash
python scripts/list_handoffs.py
```

Mostra todo handoff com data, titulo e status de conclusao.

### Passo 2: Checar desatualizacao

```bash
python scripts/check_staleness.py <arquivo-do-handoff>
```

Nivel de desatualizacao:
- **FRESH**: seguro retomar, mudanca minima desde o handoff.
- **SLIGHTLY_STALE**: revisar mudanca, depois retomar.
- **STALE**: verificar contexto com cuidado antes de retomar.
- **VERY_STALE**: considerar criar um handoff novo.

O script checa: tempo desde a criacao, commit desde o handoff, arquivo
alterado desde o handoff, divergencia de branch, arquivo referenciado
ausente.

### Passo 3: Carregar o handoff

Ler o documento de handoff inteiro antes de tomar qualquer acao.

Se o handoff for parte de uma cadeia (tem link "Continua de"), ler tambem o
handoff anterior linkado para contexto completo.

### Passo 4: Verificar contexto

Seguir o checklist em
[references/resume-checklist.md](references/resume-checklist.md):

1. Verificar diretorio do projeto e branch git.
2. Checar se bloqueio ja foi resolvido.
3. Validar se premissa ainda vale.
4. Revisar arquivo modificado por conflito.
5. Checar estado do ambiente.

### Passo 5: Comecar o trabalho

Comecar pelo item 1 de "Proximos Passos Imediatos" do documento de handoff.

Referenciar estas secoes durante o trabalho:
- "Arquivos Criticos" para local importante.
- "Padroes Descobertos" para convencao a seguir.
- "Pegadinhas Potenciais" para evitar problema conhecido.

### Passo 6: Atualizar ou encadear handoff

Enquanto trabalha:
- Marcar item concluido em "Trabalho Pendente".
- Adicionar descoberta nova na secao relevante.
- Para sessao longa: criar um handoff novo com `--continues-from` para
  encadear.

## Encadeamento de handoff

Para projeto longo, encadear handoff para manter linhagem de contexto:

```
handoff-1.md (trabalho inicial)
    |
handoff-2.md --continues-from handoff-1.md
    |
handoff-3.md --continues-from handoff-2.md
```

Cada handoff da cadeia:
- Linka com o predecessor.
- Pode marcar handoff antigo como substituido.
- Da uma trilha de contexto para agente novo.

Ao retomar de uma cadeia, ler o handoff mais recente primeiro, depois
referenciar predecessor conforme necessario.

## Local de armazenamento

Handoff fica em: `memory/handoffs/`

Convencao de nome: `AAAA-MM-DD-HHMMSS-[slug].md`

Exemplo: `2026-09-20-143022-implementando-auth.md`

## Recursos

### scripts/

| Script | Proposito |
|---|---|
| `create_handoff.py [slug] [--continues-from <arquivo>]` | Gerar handoff novo com scaffold inteligente |
| `list_handoffs.py [caminho]` | Listar handoff disponivel num projeto |
| `validate_handoff.py <arquivo>` | Checar completude, qualidade e seguranca |
| `check_staleness.py <arquivo>` | Avaliar se o contexto do handoff ainda e atual |

### references/

- [handoff-template.md](references/handoff-template.md), estrutura completa
  do template com orientacao.
- [resume-checklist.md](references/resume-checklist.md), checklist de
  verificacao para agente que retoma.

**Nota:** a versao Codex desta skill referenciava `evals/model-expectations.md`
e `evals/test-scenarios.md`. A pasta `evals/` existe mas esta VAZIA la e nao
foi portada aqui: `[verifiquei: find na pasta evals do Codex -> 0 arquivos]`.

---

Origem: portado do Codex (`<toolkit-codex-interno>/.agents/skills/session-handoff`,
20/09/2026, README + SKILL.md fundidos num so arquivo, ja que o README so
duplicava o SKILL.md em ingles). Adaptado: traduzido para PT-BR; tabela
diferenciando esta skill de `session-full-dump` e `haos-handoff-artefato`
(as duas ja existentes no HAOS); scripts Python copiados sem alteracao de
logica (ja eram genericos, sem caminho hardcoded do Codex), so o comentario
de cabecalho do `create_handoff.py` trocou "Codex/HAOS" por "HAOS".
Credito: Gian Marco Menegussi Scaglianti.
