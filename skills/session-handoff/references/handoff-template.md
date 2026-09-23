# Template de Handoff

Use esta estrutura ao criar documento de handoff. O script de scaffold
(`scripts/create_handoff.py`) pre-preenche as secoes de metadado; complete o
resto com o contexto real da sessao.

## Sumario

- Metadado da Sessao
- Resumo do Estado Atual
- Entendimento do Codebase (arquitetura, arquivos criticos, padroes)
- Trabalho Concluido (tarefa, arquivo, decisao)
- Trabalho Pendente (proximo passo, bloqueio, item adiado)
- Contexto para o Agente que Retoma (contexto critico, premissa, pegadinha)
- Estado do Ambiente
- Recursos Relacionados

---

# Handoff: [TITULO_DA_TAREFA]

## Metadado da Sessao
- Criado: [TIMESTAMP]
- Projeto: [CAMINHO_DO_PROJETO]
- Branch: [BRANCH_GIT]
- Duracao aproximada da sessao: [DURACAO_APROX]

## Resumo do Estado Atual

[Um paragrafo: o que estava sendo feito, status atual e onde parou]

## Entendimento do Codebase

### Visao de Arquitetura

[Insight de arquitetura descoberto nesta sessao: como o sistema esta
estruturado, componentes principais, fluxo de dado]

### Arquivos Criticos

| Arquivo | Proposito | Relevancia |
|---|---|---|
| caminho/do/arquivo | O que este arquivo faz | Por que importa para esta tarefa |

### Padroes Descobertos

[Padrao, convencao ou idioma importante encontrado neste codebase que o
proximo agente deve seguir]

## Trabalho Concluido

### Tarefas Finalizadas

- [x] Tarefa 1, descricao breve do que foi feito
- [x] Tarefa 2, descricao breve

### Arquivos Modificados

| Arquivo | Mudanca | Motivo |
|---|---|---|
| caminho/do/arquivo | Descricao da mudanca | Por que a mudanca foi feita |

### Decisoes Tomadas

| Decisao | Opcoes consideradas | Motivo |
|---|---|---|
| Escolheu X em vez de Y | X, Y, Z | Por que X foi escolhido |

## Trabalho Pendente

### Proximos Passos Imediatos

1. [Acao mais critica, o que fazer primeiro]
2. [Segunda prioridade]
3. [Terceira prioridade]

### Bloqueios/Perguntas Abertas

- [ ] Bloqueio: [descricao] - Precisa de: [o que falta para desbloquear]
- [ ] Pergunta: [aspecto pouco claro] - Sugestao: [resolucao possivel]

### Itens Adiados

- Item 1 (adiado porque: [motivo, ex.: fora do escopo, precisa de decisao do dono])

## Contexto para o Agente que Retoma

### Contexto Importante

[Informacao critica que o proximo agente PRECISA saber para continuar bem;
esta e a secao mais importante do handoff]

### Premissas Assumidas

- Premissa 1: [o que foi assumido como verdadeiro]
- Premissa 2: [outra premissa]

### Pegadinhas Potenciais

- [Coisa que pode confundir um agente novo: caso extremo, comportamento nao
  obvio]

## Estado do Ambiente

### Ferramenta/Servico Usado

- [Ferramenta/Servico]: [configuracao ou estado relevante]

### Processo Ativo

- [Processo em background, dev server ou watcher que pode estar rodando]

### Variavel de Ambiente

- [Nome da variavel que importa para este trabalho; NUNCA incluir valor]
- Regra HAOS: nunca incluir valor de token, senha, cookie, chave privada ou
  conteudo de `.env`. So o NOME da variavel (MASTER.env, ver CLAUDE.md §11).

## Recursos Relacionados

- [Link para documentacao relevante]
- [Caminho de arquivo relacionado]
- [Recurso externo consultado]

---

## Notas de Uso do Template

Ao preencher este template:
1. Ser especifico e concreto, descricao vaga nao ajuda o proximo agente.
2. Incluir caminho de arquivo com numero de linha quando relevante
   (ex.: `src/auth.ts:142`).
3. Priorizar as secoes "Contexto Importante" e "Proximos Passos Imediatos".
4. Nunca incluir dado sensivel (chave de API, senha, token).
5. Focar em O QUE e POR QUE, o motivo e o que faz o handoff valer a pena.

---

Origem: Codex, 20/09/2026 (`references/handoff-template.md`). Traduzido para
PT-BR e a regra de zero segredo ligada ao MASTER.env real do HAOS (CLAUDE.md §11).
Credito: Gian Marco Menegussi Scaglianti.
