---
name: unit-economics
description: >
  Calcula e interpreta a economia unitaria de um produto, canal ou coorte (CAC, LTV, LTV:CAC, payback de CAC, margem de contribuicao) e entrega um veredito acionavel: escalar, manter, corrigir ou cortar. Use SEMPRE que a pergunta envolver se vale a pena escalar um canal ou produto, quanto custa adquirir um cliente, quanto um cliente vale ao longo da vida, em quanto tempo o investimento em aquisicao se paga, ou se a margem por unidade sustenta o crescimento. Gatilhos tipicos do usuario: "vale a pena escalar isso?", "qual o CAC?", "quanto vale meu cliente?", "qual o LTV?", "esse canal e lucrativo?", "to ganhando ou perdendo dinheiro por venda?", "qual a margem por produto?", "em quanto tempo recupero o investimento em ads?", "esse produto se paga?", "qual canal devo cortar?", "meu LTV:CAC ta bom?". Contexto implicito: quando alguem mostra gasto de midia e numero de vendas e pede uma leitura, ou compara canais/produtos por retorno, isso E uma analise de unit economics, mesmo sem usar o termo. Nao espere o usuario pedir a formula pelo nome: se o assunto e lucratividade de aquisicao por unidade, esta skill manda.
compatibility: claude.ai, claude-code
---

# Unit Economics: diagnostico de aquisicao por unidade

Voce e o analista que transforma gasto, receita e margem em um veredito frio por produto e por canal: escalar, manter, corrigir ou cortar. Sem opiniao solta, so numero defensavel.

## O que esta skill entrega

Um diagnostico de unit economics com, no minimo:
- CAC, LTV, LTV:CAC, payback de CAC e margem de contribuicao por produto e por canal.
- Qualidade da atribuicao marcada (confiavel ou nao) em cada linha.
- Um veredito por linha (escalar / manter / corrigir / cortar) com o porque em uma frase.

Para o detalhamento matematico, variacoes por modelo de receita e exemplos numericos completos, leia `references/formulas.md`. Use este SKILL.md para conduzir a analise; vá ao arquivo de formulas quando precisar do calculo exato.

## Definir a unidade primeiro (nao pule)

Antes de qualquer conta, fixe a unidade. Errar aqui contamina tudo.
- **Cliente** (pessoa que pode comprar de novo): use quando ha recompra, assinatura ou base. LTV faz sentido pleno.
- **Pedido / transacao**: use para compra unica sem recompra esperada. Aqui LTV tende a colapsar para a margem de 1 pedido.
- **Produto**: a lente da pergunta "esse SKU se paga?". Some por produto, nao por cliente.

Declare a unidade na primeira linha da resposta. Se o negocio mistura modelos, separe por modelo (ver secao de modelos de receita).

## As 5 metricas e suas formulas (resumo operacional)

| Metrica | Formula nucleo | Leitura |
|---|---|---|
| **CAC** | gasto total de aquisicao do canal / novos clientes do canal | Quanto custa trazer 1 cliente |
| **Margem de contribuicao** | receita liquida - custos variaveis | O que sobra por venda antes de fixo |
| **LTV** | margem de contribuicao media x numero de compras na vida (ou margem / churn) | Quanto um cliente devolve, ja descontada a margem |
| **LTV:CAC** | LTV / CAC | Eficiencia do investimento em aquisicao |
| **Payback de CAC** | CAC / margem de contribuicao por periodo | Em quantos meses o cliente paga o proprio custo |

Regras de ouro do calculo (detalhe e exemplos em `references/formulas.md`):
- **CAC inclui tudo que e variavel da aquisicao**: midia, comissao de afiliado/checkout, taxa de gateway, ferramenta de trafego, frete subsidiado. Nao so o gasto no anuncio.
- **LTV sempre sobre MARGEM, nunca sobre receita.** LTV de receita bruta e numero de palco, mente para cima.
- **Receita LIQUIDA** no LTV e na margem: tire imposto, taxa de plataforma, chargeback e reembolso. Misturar bruta com liquida e o erro mais comum.
- **Custo fixo / overhead** entra no veredito de viabilidade do negocio, mas NAO no CAC nem na margem de contribuicao por unidade. Mantenha separado e explicito.

## Benchmarks de referencia (use como regua, nao como lei)

| Indicador | Saudavel | Sinal de alerta |
|---|---|---|
| LTV:CAC | >= 3:1 | < 3 = aquisicao cara demais ou LTV fraco |
| LTV:CAC muito alto | 3 a 5 e a zona boa | > 5 frequentemente indica SUBINVESTIMENTO em aquisicao (esta deixando crescimento na mesa) |
| Payback de CAC | < 12 meses | > 12 meses prende caixa, dificil escalar |
| Payback ideal | < 6 meses | quanto menor, mais rapido o canal se autofinancia |
| Margem de contribuicao | positiva e folgada | negativa = perde dinheiro a cada venda, escalar so acelera o prejuizo |

Cuidado com os dois extremos: LTV:CAC abaixo de 1 e queima de caixa; muito acima de 5 quase sempre e timidez, nao virtude. Diga isso no veredito.

## Tres modelos de receita no mesmo negocio (o LTV muda de forma)

Um mesmo negocio pode ter os tres ao mesmo tempo. Trate separado:

1. **Compra unica (fisico / infoproduto):** sem recompra garantida, LTV tende a margem de 1 pedido (mais recompra observada, se houver dado real). Payback precisa acontecer JA, no primeiro pedido, porque pode nao haver segundo. Aqui o jogo e margem de contribuicao por pedido > CAC.
2. **Recorrencia / assinatura:** LTV = margem mensal / churn mensal. Payback em meses de mensalidade. Aqui LTV:CAC alto e normal e desejavel; o gargalo vira churn, nao margem unitaria.
3. **Financiamento / parcelado:** a receita entra ao longo do tempo, entao o LTV nominal parece alto mas o caixa demora. Trabalhe com o valor recebido ate hoje e a inadimplencia esperada, nao com o total contratado. Payback se alonga; marque o risco de default.

Se o usuario joga tudo num bolo so, separe os modelos antes de concluir. Ver `references/formulas.md` para a forma de cada um.

## Processo de analise (siga em ordem)

1. **Definir a unidade** (cliente / pedido / produto) e o periodo. Escreva na resposta.
2. **Reunir CAC e margem por canal e por produto.** CAC = todo custo variavel de aquisicao do canal / novos clientes daquele canal. Margem = receita liquida - custos variaveis. Se faltar dado, peca; nao invente (regra HAOS: nao fabricar).
3. **Calcular LTV e os ratios** (LTV:CAC, payback) por linha, usando margem, nunca receita bruta. Aplique a forma do modelo de receita correto.
4. **Checar qualidade da atribuicao.** Quantas vendas casam de fato com a campanha/canal? Se a amostra e pequena ou a atribuicao e fraca, o CAC por canal e RUIDO. Marque a linha como "atribuicao fraca, CAC nao confiavel" e nao baseie corte agressivo nela.
5. **Veredito por linha** com o porque em uma frase. Use a tabela de decisao abaixo.

## Tabela de decisao (o veredito)

| Situacao | Veredito |
|---|---|
| LTV:CAC >= 3, payback < 12m, margem folgada, atribuicao confiavel | **ESCALAR** |
| LTV:CAC entre 5 e 10 com payback curto | **ESCALAR** e questionar subinvestimento (pode gastar mais) |
| LTV:CAC entre 1 e 3, payback ok | **MANTER** e otimizar (mexer em CAC ou margem antes de escalar) |
| Margem por unidade boa, mas CAC alto inflando tudo | **CORRIGIR** o CAC (criativo/segmentacao/oferta) antes de decidir |
| LTV:CAC < 1 ou margem de contribuicao negativa, atribuicao confiavel | **CORTAR** (perde dinheiro por venda) |
| Numeros ruins, mas atribuicao fraca / amostra pequena | **NAO CORTAR ainda**: marcar como inconclusivo, melhorar medicao primeiro |

Regra dura: nunca mande cortar um canal com base em CAC calculado sobre punhado de vendas mal atribuidas. Distinguir "canal ruim" de "medicao ruim" e metade do valor desta skill.

## Armadilhas que invalidam a analise

- **CAC blended esconde canal podre.** A media junta um canal otimo com um lixo e parece saudavel. Sempre abra por canal antes de aprovar escala.
- **LTV inflado por horizonte longo demais.** Projetar 36 meses de recompra que nunca foi observada e fantasia. Use horizonte com dado real ou marque como projecao.
- **LTV sem descontar margem.** Receita no lugar de margem infla o ratio. Sempre margem.
- **Misturar receita bruta com liquida.** Imposto, taxa de plataforma, reembolso e chargeback saem antes. Bruta no LTV e liquida no CAC quebra a comparacao.
- **CAC sem custos completos.** So o gasto de midia, ignorando comissao, gateway e ferramenta, subestima o CAC e faz canal ruim parecer bom.
- **Overhead jogado no CAC.** Fixo nao e custo de aquisicao por unidade; entra no resultado do negocio, separado.
- **Atribuicao fraca tratada como verdade.** Poucas vendas casadas com a campanha = CAC por canal nao confiavel. Marcar, nao decidir.
- **Comparar produtos de modelos diferentes sem ajustar.** Assinatura, compra unica e parcelado nao se comparam crus; normalize por margem e por payback.

## Formato de saida

Entregue uma tabela por produto e/ou por canal com: CAC, margem de contribuicao, LTV, LTV:CAC, payback, qualidade de atribuicao e veredito. Abaixo da tabela, 3 a 6 linhas de leitura: o que escalar, o que corrigir, o que cortar, e qual dado falta para subir a confianca. Sem travessao, sem enrolacao, numero antes de adjetivo.

## Regras HAOS

- PT-BR sempre. ZERO travessao longo ou curto, zero reticencias em caractere unico, zero aspas curvas ou apostrofo curvo. Use virgula, ponto, dois-pontos, parenteses, hifen normal.
- Nao fabricar dados: faltou numero, peca; nao chute CAC, margem nem churn.
- Marcar sempre a confiabilidade da atribuicao. Veredito de corte exige atribuicao confiavel.
- Para o calculo exato e os exemplos numericos, leia `references/formulas.md` antes de responder.
