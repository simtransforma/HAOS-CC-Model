# 03 Skills

Skill e conhecimento que o modelo carrega quando o assunto aparece, e ignora quando nao aparece.

---

## 1. O problema que a skill resolve

Voce tem trezentas paginas de procedimento: como falar com cada API, quais pegadinhas cada
integracao tem, o padrao de codigo da casa, o tom de voz da marca.

Se voce cola tudo no prompt, a janela de contexto acaba antes da tarefa comecar. Se voce nao cola
nada, o modelo improvisa e reinventa o que ja estava resolvido.

A skill e a saida: o conteudo fica no disco, e so a **descricao** de cada skill fica visivel o tempo
todo. Quando a descricao casa com o assunto, o modelo abre o arquivo. Formato oficial documentado em
[Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills).

```
Sempre visivel:     [nome]  +  [descricao de uma a tres linhas]     ~50 tokens por skill
Carregado sob
demanda:            SKILL.md inteiro + references/ + scripts/       milhares de tokens
```

---

## 2. Anatomia

```
skills/
  minha-skill/
    SKILL.md              <- obrigatorio. Cabecalho + corpo
    references/           <- opcional. Documento longo, tabela, mapa de API
      detalhes.md
    scripts/              <- opcional. Codigo pronto para rodar
      cliente.py
    assets/               <- opcional. Modelo, imagem, esquema
```

### O cabecalho

```markdown
---
name: minha-skill
description: >
  O que ela faz. Depois os gatilhos, nas palavras reais de quem pede.
  Depois quando NAO usar, apontando a alternativa.
---
```

**A descricao e a skill.** O corpo so e lido se a descricao ganhar a disputa. Uma descricao boa tem
tres partes:

1. **O que faz**, em uma frase objetiva.
2. **Gatilhos**, com as palavras que a pessoa realmente escreve. Nao "gestao de dados relacionais",
   e sim "roda uma consulta", "le a tabela", "conecta no banco".
3. **Quando nao usar**, apontando para onde ir em vez disso.

### O corpo

Sem tamanho fixo, mas com uma regra de ouro: **o que resolve 80 por cento dos casos fica no
`SKILL.md`; o resto vai para `references/`**. Se o corpo passou de umas quinhentas linhas, quebre.

---

## 3. Como o modelo escolhe

Ele nao "procura" a skill. As descricoes ja estao no contexto desde o inicio da sessao. Quando a
tarefa chega, ele reconhece a correspondencia e abre o arquivo.

Isso tem tres consequencias praticas que mudam como voce escreve.

| Consequencia | O que fazer |
|---|---|
| Descricao vaga nao dispara | Escreva gatilho literal, incluindo giria e erro de escrita comum |
| Descricao ampla dispara errado | Diga explicitamente quando **nao** usar |
| Duas skills parecidas se anulam | Funda as duas, ou deixe clara a fronteira dentro da descricao de cada uma |

---

## 4. As quatro familias de skill

Este modelo separa skill em quatro tipos, e a fronteira importa na hora de decidir o que publicar.

| Familia | Exemplo | Vai para um modelo publico? |
|---|---|---|
| **De sistema** | Roteador de modelo, ondas de execucao, entrega por artefato, portoes de qualidade | Sim. E o coracao do metodo |
| **De metodo** | Depuracao sistematica, pesquisa profunda, refatoracao estrutural, auditoria de skill | Sim |
| **De plataforma** | Padrao para trabalhar com um servico externo generico | Sim, se nao carregar identificador de conta |
| **De cliente** | Integracao com o ERP especifico, dado da marca, procedimento de um cliente | **Nao.** Fica privada, sempre |

A quarta familia e a que causa vazamento. Ela nasce util e cresce colecionando identificador de
conta, telefone de contato, caminho interno e nome de cliente. Mantenha essas skills num repositorio
privado desde o primeiro dia.

---

## 5. Como escrever a sua

### Passo 1: espere a terceira repeticao

Nao escreva skill por antecipacao. Escreva quando voce explicou a mesma coisa pela terceira vez, ou
quando o modelo errou o mesmo ponto pela segunda.

### Passo 2: comece pela pegadinha

A parte mais valiosa de uma skill nao e a documentacao da ferramenta, que o modelo ja conhece. E o
que **so quem se queimou sabe**: o parametro que parece opcional e nao e, o modo de conexao que
derruba o banco, o campo que muda de formato entre duas rotas do mesmo servico.

Abra a skill com isso. Titule de "pegadinhas" e coloque antes da referencia.

### Passo 3: prefira exemplo executavel a prosa

Um trecho de codigo que funciona vale dez paragrafos explicando o conceito. Se houver script, ponha
em `scripts/` e cite o caminho.

### Passo 4: credencial por nome, nunca por valor

Escreva "a chave esta na variavel `SERVICO_API_KEY`". Nunca escreva a chave. Esta regra vale dentro
da skill, no log, no relatorio e na resposta.

### Passo 5: datar o que envelhece

Preco, limite de requisicao, versao de API e endereco mudam. Marque com a data em que voce conferiu,
para o proximo leitor saber o quanto confiar.

---

## 6. Higiene e triagem

Skill vinda de fora e superficie de ataque. Antes de instalar qualquer skill de terceiro, passe pelos
quatro passos de triagem.

| Etapa | O que checar |
|---|---|
| **1. Metadados** | Nome no padrao, versao coerente, autor verificavel, descricao que bate com o conteudo |
| **2. Escopo de permissao** | Leitura de diretorio de chave de acesso ou de credencial de nuvem: bloquear. Shell irrestrito: bloquear por padrao. Rede irrestrita: revisao manual |
| **3. Conteudo** | Sinal critico: baixar e executar num cano so, ofuscacao em base64, abertura de porta reversa, leitura de arquivo de usuarios do sistema. Sinal de alerta: elevacao de privilegio, escrita em diretorio de sistema, chamada a dominio desconhecido |
| **4. Nome parecido** | Comparar com a skill legitima que ela imita. Uma letra de diferenca no nome do autor e o golpe classico de cadeia de suprimentos |

Veredito em quatro niveis: segura, atencao, perigosa, bloqueada. Critico ou bloqueada nao se negocia.
