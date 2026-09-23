# 06 Rito

Um pipeline de 13 fases com portao bloqueante entre cada uma. Serve para projeto grande, onde o custo
de comecar pelo lugar errado e alto.

---

## 1. Quando usar e quando nao usar

| Use o Rito quando | Nao use quando |
|---|---|
| O projeto vai gastar dinheiro ou tempo relevante | A tarefa cabe em uma sessao |
| Varias areas precisam entregar em ordem | Voce so precisa de uma resposta |
| Comecar pelo passo errado custa caro | O caminho ja esta claro |
| Voce precisa de rastro de decisao | E manutencao de rotina |

Rito e caro de proposito. Aplicar em tarefa pequena e desperdicio, e o sistema orienta a nao fazer.

---

## 2. Como aciona

Uma mensagem que comeca com `#` mais o briefing. O Rito **sempre** comeca na fase 1, mesmo que voce
ache que ja sabe tudo.

```
# Lancar o produto novo em 60 dias, orcamento definido, meta de vendas definida
```

Dois comandos de controle:

- `abortar rito` salva o estado e para
- `retomar rito` le o estado e continua da proxima fase pendente

---

## 3. As 13 fases

Uma fase por vez. O portao e bloqueante: sem ele cumprido, a proxima nao abre.

| Fase | Nome | Quem trabalha | Portao para seguir |
|---|---|---|---|
| 1 | Entrada e validacao | Orquestrador, gerente de projeto | Briefing validado e confirmado por voce |
| 2 | Pesquisa e diagnostico | Pesquisador, analista de dados, direcao de marketing | Diagnostico com dado real, documentado |
| 3 | Estrategia e posicionamento | Estrategista chefe, direcao de marketing, direcao criativa | Estrategia aprovada pelo conselho |
| 4 | Planejamento tatico | Gerente de projeto, estrategista de midia, arquiteto de funil | Escopo, lista de tarefas e cronograma aprovados |
| 5 | Texto e mensagens | Especialista em texto, e-mail, relacionamento | Textos aprovados por direcao criativa e conformidade |
| 6 | Design e pecas | Designer, video, conteudo | Pecas aprovadas pela direcao criativa |
| 7 | Funil e automacao | Arquiteto de funil, automacao, desenvolvimento | Funil testado de ponta a ponta |
| 8 | Midia | Estrategista de midia, comprador, rastreamento | Campanhas configuradas e **nao ativadas** |
| 9 | Rastreamento e dados | Rastreamento, engenharia de dados, analise | Fluxo de dados funcionando |
| 10 | Qualidade e conformidade | Revisor, conformidade, gerente de projeto | Ambos aprovados. Nao e um ou outro |
| 11 | Publicacao e ativacao | Infraestrutura, midia, redes | **Gasta dinheiro. Exige a sua autorizacao explicita** |
| 12 | Monitoramento e otimizacao | Midia, dados, estrategia | Relatorio de desempenho |
| 13 | Retrospectiva | Direcao, gerente de projeto, orquestrador | Aprendizados documentados na memoria |

---

## 4. As quatro regras que fazem o Rito funcionar

**Uma. A fase 1 nunca e pulada.** Mesmo que voce peca para pular. O briefing e onde o projeto inteiro
e salvo ou perdido, e e a fase mais barata de todas. Um projeto que comeca com briefing vago produz
treze fases de trabalho no alvo errado.

**Duas. O portao e bloqueante de verdade.** "A fase 5 esta quase pronta, comeca a 6" nao existe.
Quase pronto e a forma mais cara de retrabalho.

**Tres. A fase 8 configura e nao ativa.** Separar preparacao de ativacao e o que permite a fase 10
revisar com tudo pronto e ainda assim reversivel.

**Quatro. A fase 11 e a unica que gasta.** Ela exige autorizacao humana explicita. Nenhum agente ativa
nada sozinho, em nenhuma hipotese.

---

## 5. O estado

Depois de cada fase o estado e salvo em disco: qual fase, o que foi decidido, o que ficou pendente,
quais artefatos existem e onde.

```json
{
  "rito_id": "2026-09-23-lancamento",
  "fase_atual": 5,
  "fases_concluidas": [1, 2, 3, 4],
  "portoes": { "1": "aprovado", "2": "aprovado", "3": "aprovado", "4": "aprovado" },
  "artefatos": { "diagnostico": "<caminho>", "estrategia": "<caminho>" },
  "pendencias": ["falta a aprovacao de conformidade do texto do anuncio"]
}
```

Isso e o que permite retomar dias depois sem refazer nada, e o que permite outra pessoa continuar de
onde voce parou.

---

## 6. O conclave

Para decisao de risco alto, o Rito abre uma sessao de conselho com quatro etapas.

| Etapa | O que acontece |
|---|---|
| **Debate** | Varios agentes opinam em paralelo, sem ver a resposta um do outro |
| **Critico** | Um agente pontua cada opiniao e aponta a falha de cada uma |
| **Advogado do diabo** | Um agente tenta derrubar a opcao vencedora |
| **Sintetizador** | Um agente consolida e entrega a recomendacao com o nivel de confianca |

Se a confianca ficar abaixo de um piso, a decisao **sobe para o humano**, apresentada como opcao A
contra opcao B, nao como recomendacao unica.

Os quatro principios que guiam o conclave: empirismo (o que o dado diz), concentracao (que 20 por
cento gera 80 por cento do resultado), inversao (o que faria isso falhar) e antifragilidade (o que
melhora se der errado).

A ideia de papeis com portao de aprovacao entre fases vem do
[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD).
