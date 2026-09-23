# Unit Economics: formulas, variacoes e exemplos numericos

Detalhamento matematico da skill `unit-economics`. As formulas sao firmes; a interpretacao adapta ao negocio. Todos os exemplos usam numeros ilustrativos neutros.

## 1. CAC (Custo de Aquisicao de Cliente)

### CAC por canal (sempre prefira este)
```
CAC_canal = custo_total_de_aquisicao_do_canal / novos_clientes_atribuidos_ao_canal
```
`custo_total_de_aquisicao` = midia + comissao de afiliado/checkout + taxa de gateway + ferramenta de trafego + frete/brinde subsidiado + qualquer custo variavel ligado a trazer o cliente. NAO inclui salario fixo do time nem aluguel (isso e overhead, ver secao 8).

### CAC blended
```
CAC_blended = custo_total_de_aquisicao_de_todos_os_canais / total_de_novos_clientes
```
Util para visao macro, perigoso para decisao. A media esconde canal ruim. Use so como referencia de teto, decida sempre pelo CAC por canal.

**Exemplo.** Canal A: gastou 6.000 e trouxe 100 clientes, CAC_A = 60. Canal B: gastou 6.000 e trouxe 20 clientes, CAC_B = 300. Blended = 12.000 / 120 = 100. O blended de 100 mascara que o canal B custa 5x o A. Decisao no blended escalaria o conjunto; decisao por canal corta ou conserta o B.

## 2. Margem de contribuicao

### Por unidade
```
margem_contribuicao_unidade = receita_liquida_unidade - custos_variaveis_unidade
```
`receita_liquida` = preco - imposto - taxa de plataforma - reembolso/chargeback esperado.
`custos_variaveis` = COGS (produto/frete/impressao), taxa de pagamento, comissao de venda.

### Percentual de margem de contribuicao
```
margem_% = margem_contribuicao_unidade / receita_liquida_unidade
```

**Exemplo.** Preco 197. Imposto + taxa de plataforma = 27. Receita liquida = 170. Custos variaveis (produto 40 + frete 20 + gateway 8) = 68. Margem de contribuicao = 170 - 68 = 102. Margem_% = 102 / 170 = 60%.

A margem de contribuicao e o combustivel que paga o CAC. Se ela for menor que o CAC, voce perde dinheiro na primeira venda e so recupera (se recuperar) na recompra.

## 3. LTV (Lifetime Value)

**Sempre sobre margem de contribuicao, nunca sobre receita.**

### LTV simples (numero de compras observado)
```
LTV = margem_contribuicao_media_por_compra x numero_medio_de_compras_na_vida
```

### LTV por churn (recorrencia / recompra)
```
LTV = margem_contribuicao_por_periodo / churn_por_periodo
```
`churn` = fracao da base que sai por periodo. Tempo de vida medio = 1 / churn.

### LTV com margem percentual sobre receita recorrente
```
LTV = (receita_media_por_periodo x margem_%) / churn_por_periodo
```

**Exemplo recorrencia.** Mensalidade liquida 100, margem 70% (margem mensal = 70), churn mensal 5% (0,05). Vida media = 1 / 0,05 = 20 meses. LTV = 70 / 0,05 = 1.400. Se alguem usasse receita em vez de margem: 100 / 0,05 = 2.000, inflado em 43%.

**Cuidado com horizonte.** Em compra unica sem recompra observada, numero_medio_de_compras tende a 1, entao LTV = margem de 1 pedido. Projetar 5 compras sem dado real e fantasia. Use o que foi medido ou marque "projecao".

## 4. LTV:CAC ratio

```
LTV:CAC = LTV / CAC
```

| Faixa | Leitura |
|---|---|
| < 1 | Perde dinheiro por cliente. Cortar ou consertar. |
| 1 a 3 | Sobrevive, sem folga para escalar agressivo. Otimizar CAC ou margem. |
| 3 a 5 | Zona saudavel. Escalar. |
| > 5 | Eficiente demais costuma significar SUBINVESTIMENTO em aquisicao: da para gastar mais e capturar mais mercado. Questionar timidez. |

**Exemplo.** LTV 1.400, CAC 350. Ratio = 4:1. Saudavel, escalar. Se CAC fosse 120, ratio = 11,7:1, sinal forte de que da para investir muito mais em aquisicao.

## 5. Payback de CAC

```
payback_em_periodos = CAC / margem_contribuicao_por_periodo
```

| Payback | Leitura |
|---|---|
| < 6 meses | Otimo, canal se autofinancia rapido |
| 6 a 12 meses | Aceitavel |
| > 12 meses | Prende caixa, dificil escalar com capital proprio |

**Exemplo.** CAC 350, margem mensal 70. Payback = 350 / 70 = 5 meses. Bom. Em compra unica, o payback tem que acontecer no proprio pedido: margem do pedido 102 e CAC 60, payback = imediato (0,6 do primeiro pedido), sobra 42 de lucro de contribuicao na primeira venda.

## 6. Variacao por modelo de receita

### a) Compra unica (fisico / infoproduto)
- LTV = margem de contribuicao do pedido x compras observadas (frequentemente 1).
- Payback tem que ser no primeiro pedido. Nao conte com segundo que nao foi medido.
- Veredito: margem_contribuicao_pedido > CAC e condicao minima de vida.

### b) Recorrencia / assinatura
- LTV = margem_mensal / churn_mensal. Vida = 1 / churn.
- Payback em meses de mensalidade.
- LTV:CAC alto e esperado e bom; o gargalo vira o churn. Reduzir churn 1 ponto muda o LTV mais que cortar CAC.

### c) Financiamento / parcelado
- Receita entra ao longo do tempo. LTV contratado parece alto, mas o caixa demora.
- Trabalhe com valor_recebido_ate_hoje e desconte inadimplencia esperada:
```
LTV_caixa = sum(parcelas_recebidas x margem_%) - perda_por_default_esperada
```
- Payback se alonga; o risco de default reduz o LTV efetivo. Marque sempre a taxa de inadimplencia assumida.

## 7. Coorte (cohort)

Agrupe clientes pelo periodo de aquisicao (ex: clientes que entraram em janeiro) e acompanhe margem acumulada por mes desde a entrada. A coorte revela:
- Quando o payback realmente acontece (curva de margem acumulada cruza o CAC).
- Se o LTV projetado bate com o realizado (compare coortes maduras com a projecao feita no dia 0).
- Degradacao ou melhora de qualidade entre safras de canais diferentes.

Sem coorte, LTV vira media cega que mistura cliente novo com antigo.

## 8. Overhead e o resultado do negocio

Overhead (salario fixo, aluguel, software base, time) NAO entra no CAC nem na margem de contribuicao por unidade. Ele entra no resultado consolidado:
```
lucro_operacional = (margem_contribuicao_total) - custo_fixo_total
```
Unit economics positiva (LTV:CAC saudavel) com overhead alto demais ainda da prejuizo no consolidado. Por isso o veredito por unidade responde "vale escalar este canal/produto", e o resultado operacional responde "o negocio fecha no azul". Sao perguntas diferentes; nao misture.

## 9. Qualidade da atribuicao (gate de confianca)

Antes de confiar no CAC por canal, cheque:
- Quantas vendas casaram de fato com a campanha/canal (via UTM, pixel, cupom, pergunta no checkout)?
- A janela de atribuicao e razoavel para o ciclo de compra?
- A amostra e grande o suficiente? Poucas vendas = CAC instavel.

Heuristica pratica: com menos de ~30 conversoes atribuidas no periodo, o CAC por canal tem ruido alto. Marque a linha como "atribuicao fraca, CAC nao confiavel" e nao baseie um corte agressivo nela. Melhor decisao: melhorar a medicao antes de matar o canal.

## 10. Checklist de sanidade (rode antes de entregar)

- [ ] Unidade definida (cliente / pedido / produto) e escrita na resposta.
- [ ] CAC por canal, nao so blended.
- [ ] CAC inclui comissao, gateway, ferramenta, nao so midia.
- [ ] LTV sobre margem, nao sobre receita.
- [ ] Receita liquida (sem imposto, taxa, reembolso) em todo lugar.
- [ ] Horizonte de LTV com dado real ou marcado como projecao.
- [ ] Modelo de receita correto aplicado (unica / recorrencia / parcelado).
- [ ] Overhead fora do CAC e da margem de contribuicao.
- [ ] Atribuicao classificada (confiavel / fraca) por linha.
- [ ] Veredito por linha com o porque em uma frase.
