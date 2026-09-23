# 02 Agentes

Um agente e um especialista com missao fechada. Ele nao conversa, ele entrega.

---

## 1. O que e um agente aqui

Tecnicamente, um arquivo markdown em `agents/` com um cabecalho de metadados e um corpo de
instrucoes. O Claude Code le a `description` do cabecalho para decidir quando aquele agente e o certo
para a tarefa. Formato oficial documentado em
[Subagents](https://docs.claude.com/en/docs/claude-code/sub-agents).

Conceitualmente, um agente e a resposta a uma pergunta simples: **quem deveria fazer isso, se este
fosse um time de gente?**

### O que um agente tem

| Parte | Para que serve |
|---|---|
| `name` | Identificador. E como voce chama ele com `@nome` |
| `description` | Quando acionar. Escrita em voz de gatilho, com exemplos de pedido real |
| `tools` | O que ele pode usar. Agente de leitura nao ganha ferramenta de escrita |
| `model` | O nivel de modelo padrao dele |
| Corpo | Missao, tom, framework de trabalho, formato de saida, e a lista do que ele nunca faz |

> **Nota sobre as tabelas de skill dentro de cada agente.** Os 30 arquivos vieram do sistema de
> origem quase sem edicao de conteudo (so sanitizacao de dado pessoal). Alguns citam skill de
> dominio (ex.: integracao com um ERP ou marketplace especifico) que **nao existe neste
> repositorio**, porque skill de cliente/marca fica fora por definicao (ver
> [README](../README.md#o-que-este-modelo-nao-traz)). Isso e proposital: a tabela mostra o
> **padrao** de como um agente declara e prioriza suas skills, nao uma lista fechada. Ao adaptar
> um agente, apague a linha da skill que voce nao tem e troque pela sua, seguindo
> [03-SKILLS.md](03-SKILLS.md).

### O que faz um agente bom

Quatro coisas, em ordem de importancia.

1. **Um "nunca" explicito.** A parte mais valiosa de um agente nao e o que ele faz, e o que ele se
   recusa a fazer. O agente de seguranca nao corrige codigo de aplicacao, ele audita e recomenda. O
   revisor de qualidade nao aprova por cansaco quando as rodadas acabam.
2. **Um formato de saida fixo.** Se toda entrega sai no mesmo formato, voce compara duas entregas e
   automatiza a proxima etapa.
3. **Um framework, nao um estilo.** "Seja rigoroso" nao e instrucao. "Classifique cada achado em tres
   niveis e termine com um veredito executivo" e.
4. **Um retorno estruturado.** Todo agente termina em um de tres estados: concluido, bloqueado, ou
   precisa de decisao humana. Bloqueado exige listar o que foi tentado.

---

## 2. Os 30 agentes

Eles se agrupam em oito departamentos. Voce pode chamar o departamento em vez da pessoa quando sabe a
area e nao sabe quem.

### Orquestracao e qualidade

| Agente | Quando aciona |
|---|---|
| `main` | Ponto de entrada. Classifica a demanda, roteia, consolida o resultado |
| `concierge` | Mensagem chega sem destino claro e precisa ser interpretada antes de rotear |
| `project-manager` | Planejar escopo, dividir em tarefas, montar cronograma, destravar bloqueio |
| `qa-reviewer` | Portao antes de publicar, deployar ou ativar qualquer coisa |
| `compliance-officer` | Verificar se a peca viola legislacao de privacidade, publicidade ou consumo |

### Engenharia

| Agente | Quando aciona |
|---|---|
| `dev-backend` | API, integracao, webhook, dado, automacao de servidor |
| `dev-frontend` | Pagina, checkout, componente, interface |
| `devops` | Deploy, rollback, container, servidor, diagnostico de producao |
| `automation-engineer` | Fluxo de automacao entre ferramentas, webhook, integracao sem codigo |
| `chuck-norris` | Seguranca: auditoria de servidor e de codigo, triagem de skill externa, resposta a incidente |

### Dados

| Agente | Quando aciona |
|---|---|
| `data-analyst` | Diagnostico de numero, relatorio periodico, analise de funil |
| `bi-engineer` | Pipeline de dados, modelagem de tabela, painel |
| `tracking-engineer` | Auditoria de rastreamento, evento, pixel, medicao de conversao |

### Estrategia

| Agente | Quando aciona |
|---|---|
| `estrategista-chefe` | Posicionamento, analise de cenario, decisao macro de negocio |
| `cmo` | Diagnostico de funil, retorno sobre investimento, plano de marketing |
| `product-manager` | Descoberta de produto, documento de requisitos, priorizacao de roteiro |
| `pesquisador` | Inteligencia competitiva, pesquisa de mercado, levantamento de fonte |
| `auditor-confianca` | Diligencia previa sobre empresa ou fornecedor antes de assinar ou gastar |
| `ux-researcher` | Teste de usabilidade, analise heuristica, auditoria de acessibilidade |

### Criacao

| Agente | Quando aciona |
|---|---|
| `diretor-criativo` | Conceito de campanha, direcao de arte, consistencia de marca |
| `copy-specialist` | Texto de conversao: titulo, roteiro, pagina, sequencia |
| `designer` | Peca visual, banner, miniatura, identidade aplicada |
| `videomaker` | Producao e edicao de video |
| `content-strategist` | Conteudo organico, calendario editorial, construcao de audiencia |

### Aquisicao

| Agente | Quando aciona |
|---|---|
| `traffic-master` | Plano de midia, estrategia de canal, estrutura de conta |
| `media-buyer` | Execucao tatica: montar campanha, otimizar, escalar, testar |
| `funnel-architect` | Desenho da jornada de ponta a ponta |

### Relacionamento

| Agente | Quando aciona |
|---|---|
| `crm-specialist` | Funil comercial, cadencia de contato, gestao de oportunidade |
| `email-marketer` | Sequencia de e-mail, automacao de nutricao, reativacao de base |
| `sm-social` | Publicacao, comunidade, atendimento em rede social |

---

## 3. Como criar o seu agente

### Passo 1: responda tres perguntas

- Que tipo de pedido deveria cair nele, em palavras que voce realmente usaria?
- O que ele **nunca** pode fazer, nem se voce pedir com pressa?
- Como a entrega dele se parece? Desenhe a saida antes de escrever o prompt.

### Passo 2: escreva o cabecalho

```markdown
---
name: meu-agente
description: >
  Uma frase do que ele faz. Depois os gatilhos, em voz de usuario:
  "revisa isso", "monta o plano de X", "por que Y quebrou". Diga tambem
  quando NAO usar, apontando o agente certo.
tools: Read, Grep, Glob, Bash, Skill
model: sonnet
---
```

A `description` e a parte que mais importa. E ela que decide se o agente e chamado. Escreva gatilho
de verdade, do jeito que a pessoa fala, e diga explicitamente quando nao usar.

### Passo 3: escreva o corpo, nesta ordem

1. **Identidade e tom.** Quem ele e em duas linhas.
2. **Norte.** De tres a cinco principios inegociaveis.
3. **Briefing obrigatorio.** O que ele precisa saber antes de comecar. Se faltar, ele pergunta.
4. **Framework.** As fases do trabalho dele, na ordem.
5. **Saida padrao.** O formato fixo da entrega.
6. **Retorno estruturado.** Concluido, bloqueado ou precisa de decisao.
7. **Nunca.** A lista de recusas.

### Passo 4: teste com um pedido ambiguo

Bom agente acerta o pedido claro. Agente **muito** bom sabe dizer "isso nao e comigo, e com fulano".
Teste com um pedido de fronteira e veja se ele redireciona.
