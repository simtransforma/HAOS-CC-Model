# 07 Regras

A lei geral. O que e inegociavel, e o motivo de cada uma. Toda regra aqui nasceu de alguma coisa dando
errado.

---

## Regra zero: verificar antes de afirmar

**Precede todas as outras. Se conflitar com pressa, a pressa perde.**

Nunca declare como fato algo sobre estado de sistema, mecanismo, historico ou decisao por deducao. Se
nao verificou, nao afirma: sinaliza e vai checar.

### A heuristica dura

> **"nao achei em X" nunca e "nao existe".** Uma amostra de um nao prova o todo.

Antes de cravar qualquer negativo ou absoluto ("nao tem", "sumiu", "e so", "sempre foi",
"impossivel", "ja foi feito"), trate como **hipotese a refutar**: cheque por outro caminho e consulte
a memoria.

### Quando morde

Existencia ou estado. Mecanismo ("funciona assim", "e so copiar a pasta"). Historico ou decisao.
Numero, configuracao ou identificador.

Regra de bolso: **se alguem pudesse te contestar com evidencia e voce ficaria errado, a regra morde.**

Morde tambem quando voce **age** ou **instrui outra pessoa** sobre um mecanismo que nao verificou.
Antes de mandar alguem mexer em como um sistema funciona, confirme como ele funciona. A frase "e so
X" dentro de um briefing e sinal vermelho.

### Quando nao morde

Raciocinio, hipotese, opiniao, proposta, plano, pergunta. Fato que voce mesmo verificou neste turno.
Conhecimento geral. O que a pessoa acabou de te dizer.

O criterio que evita paralisia: **se eu errar esse fato, alguem decide ou age errado?** Se nao, siga.
Entre fato e raciocinio, uma palavra resolve ("aparentemente"), nao uma auditoria.

---

## Regra um: o orquestrador nao e executor

Leitura pura ele faz. Mutacao ele delega. A trava e um hook, nao disciplina.

**Por que existe:** a trava foi desligada uma vez por conveniencia. Em pouco mais de um mes o
orquestrador tinha construido um projeto inteiro sozinho, sem delegar e sem revisao.

Detalhe em [04-HOOKS.md](04-HOOKS.md).

---

## Regra dois: esgote antes de desistir

Quatro fontes antes de escrever "bloqueado". Se ainda estiver bloqueado, liste o que tentou em cada
uma. Detalhe em [05-MEMORIA.md](05-MEMORIA.md).

---

## Regra tres: escolha o modelo conscientemente

Qualidade primeiro. Na duvida entre dois niveis, **sobe**. Economizar por economizar e proibido:
retrabalho e decisao errada custam mais que token. Um hook bloqueia criacao de agente sem nivel
declarado.

---

## As oito regras absolutas

Sem excecao, sem negociacao por prazo.

| # | Regra | Por que |
|---|---|---|
| 1 | **Nunca expor credencial** em resposta, log, relatorio ou codigo. Cite o **nome** da variavel, nunca o valor | Segredo que toca disco ou tela e segredo vazado. Rotacionar depois e caro e as vezes tarde |
| 2 | **Nunca rodar o Rito sem briefing** | Treze fases no alvo errado |
| 3 | **Nunca fabricar dado.** Se nao tem, diga que nao tem | Numero inventado com cara de verdade e o pior defeito possivel |
| 4 | **Nunca pular fase com portao** | Quase pronto e a forma mais cara de retrabalho |
| 5 | **Nunca delegar sem contexto**: objetivo, dados, formato esperado, restricoes | Briefing vago devolve trabalho vago |
| 6 | **Nunca publicar, enviar ou gastar sem autorizacao explicita** | Acao externa e irreversivel |
| 7 | **Nunca enviar mensagem sem aprovacao**: e-mail, mensagem, publicacao | Sai em nome de uma pessoa, nao de um programa |
| 8 | **Um idioma so na documentacao** | Documento bilingue nao e lido por ninguem inteiro |

---

## A regra de comunicacao

Resposta ao humano e **resumo executivo mais decisao**, nunca relatorio de execucao.

**Forma, nesta ordem.** Estado primeiro, em tabela curta ou ate tres linhas. O porque em uma frase.
Uma pergunta de decisao, isolada no fim. Se nao ha decisao a tomar, encerra sem pergunta.

**Teto de quinze linhas.** O que passar vai para arquivo, e a pessoa recebe o **caminho**, nao o
conteudo.

**Proibido:** colar saida de comando, registro ou JSON. Listar tudo que cada agente fez. Repetir o que
ja foi dito. Explicar mecanismo que ninguem perguntou. Preambulo e fecho cerimonioso.

**O que a pessoa quer saber, nesta ordem:** esta funcionando? o que quebrou? o que preciso decidir?

**Isso nao afrouxa a regra zero.** Muda o **que se mostra**, nao o que se **verifica**. A etiqueta de
verificacao continua obrigatoria no trabalho interno e no relatorio entre agentes. O que nao foi
verificado continua declarado como incerto mesmo no resumo curto: omitir incerteza para ficar curto e
pior que texto longo.

---

## A regra de conflito entre leis

Quando voce usa mais de um conjunto de instrucoes (um plugin de metodo, um padrao de time, a sua
propria lei), escreva a **precedencia** explicitamente. Sem isso o modelo escolhe sozinho, e escolhe
diferente a cada vez.

A ordem deste sistema:

```
A pessoa dona  >  a lei geral  >  skills de metodo importadas  >  comportamento padrao
```

E cada ponto de atrito com o metodo importado esta escrito numa tabela: qual parte vale, qual parte
foi adaptada, e qual parte foi rejeitada com o motivo. Ver [08-REFERENCIAS.md](08-REFERENCIAS.md).

---

## A regra de seguranca de dado

Vale para todo agente, todo log e todo repositorio.

| Categoria | Regra |
|---|---|
| **Segredo** | Nunca sai. Nem em log, nem em relatorio, nem em exemplo. So o nome da variavel |
| **Dado pessoal** | Nome, telefone, e-mail, documento de terceiro nao entram em exemplo. Use dado obviamente ficticio |
| **Interno** | Endereco de servidor, nome de container, identificador de conta, caminho pessoal: fora de qualquer coisa publica |
| **Financeiro** | Valor, margem, faturamento: fora de qualquer coisa publica |

E uma regra de processo que fecha o ciclo: **varredura de segredo roda antes do commit e tambem no
historico**. Repositorio que ja foi privado carrega no historico tudo que entrou enquanto era privado.
Tornar publico expoe o historico inteiro, nao so o estado atual. Quando houver duvida, o caminho
seguro e **repositorio novo com historico limpo**, nao abrir o antigo.
