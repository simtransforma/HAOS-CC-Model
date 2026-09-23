# 01 Arquitetura

Como as seis camadas se encaixam, o caminho que uma tarefa percorre, e as decisoes de projeto que
explicam por que o sistema tem esse formato e nao outro.

---

## 1. O principio que organiza tudo

**Regra que depende de o modelo lembrar de obedecer e sugestao. Regra que um programa bloqueia e
regra.**

Todo o resto sai daqui. Quando uma politica importa de verdade, ela nao vive so no texto do prompt:
ela vira um hook que responde bloqueio. Quando ela e apenas orientacao de qualidade, vive no texto.

A consequencia pratica e que este sistema tem duas metades que precisam estar de acordo.

| Metade | Onde vive | O que acontece se voce mentir para ela |
|---|---|---|
| A lei escrita | CLAUDE.md, agentes, skills | O modelo se desalinha e voce percebe na resposta |
| A trava executavel | `hooks/` | A ferramenta simplesmente nao roda |

Se a lei escrita diz uma coisa e o hook faz outra, **o hook ganha** e a lei escrita esta errada.

---

## 2. O caminho de uma tarefa

```
 1. VOCE pede
        |
 2. UserPromptSubmit hook  ---> injeta contexto, roteia, avisa de rito ativo
        |
 3. ORQUESTRADOR classifica
        |
        +-- e leitura pura?  ------ sim ---> faz direto (qualquer volume)
        |
        +-- muda estado, apaga ou envia?
                    |
 4.                 v
        PreToolUse guard  ---> bloqueia se estiver fora do permitido
                    |
 5.         delega para AGENTE
                    |
        PreToolUse model guard ---> bloqueia se o spawn nao declarar o modelo
                    |
 6.        AGENTE executa e carrega SKILLS sob demanda
                    |
 7.        AGENTE devolve resultado com evidencia
                    |
 8.        REVISOR le tudo que mudou e devolve achados
                    |
 9.        FECHAMENTO: memoria, commit, espelho
                    |
        Stop hook ---> captura de sessao e digest
```

Nenhuma dessas etapas e opcional por pressa. O portao que mais gente tenta pular e o 8, e e o que
mais devolve defeito.

---

## 3. As camadas, uma a uma

### Camada 1: a lei

Um arquivo markdown carregado em toda sessao. Contem identidade, tom, regras absolutas, tabela de
roteamento e o criterio de delegacao. Ver [07-REGRAS.md](07-REGRAS.md).

Decisao de projeto importante: **a lei geral mora no diretorio de usuario, nao no repositorio do
projeto**. Uma sessao aberta na pasta errada nascia sem regra nenhuma quando a lei inteira vivia num
arquivo de projeto. A divisao ficou assim.

| Arquivo | Escopo | Carrega quando |
|---|---|---|
| `~/.claude/CLAUDE.md` | A lei geral, portatil | Toda sessao, qualquer pasta |
| `<projeto>/CLAUDE.md` | Doutrina do projeto | So dentro daquele projeto |

A numeracao das secoes e a mesma nos dois de proposito, para que um link para "secao 1.c" continue
valido de qualquer lado. Se os dois divergirem, vence o de usuario.

### Camada 2: o orquestrador

A sessao principal. Ele nao e um executor com permissao total, e um **despachante**. O criterio de um
segundo.

| Situacao | Acao |
|---|---|
| Leitura pura, qualquer volume | Faz ele mesmo |
| Muda estado, apaga ou envia | Delega sempre |
| Especializado, volumoso ou paralelizavel | Delega sempre |
| Trivial e rapido, sem mutacao | Faz ele mesmo |

### Camada 3: os agentes

Trinta especialistas com missao fechada. Ver [02-AGENTES.md](02-AGENTES.md).

Decisao de projeto: **agente nao e chatbot, e executor**. Ele recebe briefing, faz, e devolve
artefato. Ele nao pergunta de volta a nao ser que a acao seja externa e irreversivel.

### Camada 4: as skills

Conhecimento sob demanda. Ver [03-SKILLS.md](03-SKILLS.md).

Decisao de projeto: **nenhuma contagem de skills fica escrita na lei**. A lista e descoberta ao vivo
na sessao. Documento que guarda inventario envelhece e passa a mentir; documento que guarda regra
nao.

### Camada 5: os hooks

A trava. Ver [04-HOOKS.md](04-HOOKS.md).

Decisao de projeto: **falha fechada**. Se o hook nao consegue entender o comando, ele bloqueia. Um
envelopador opaco, do tipo "roda esse script", e bloqueado sem tentar ler o conteudo, porque lista de
proibicao baseada em texto falha aberta.

### Camada 6: a memoria

Ver [05-MEMORIA.md](05-MEMORIA.md).

Decisao de projeto: **memoria nunca fecha questao sobre estado vivo**. Container no ar, porta aberta,
processo rodando: so o comando ao vivo responde. Se a memoria e o servidor divergem, o servidor ganha
e a memoria e corrigida.

---

## 4. Modos de operacao

O sistema atende de quatro jeitos, escolhidos pelo prefixo do que voce escreve.

| Modo | Como aciona | Quando usar |
|---|---|---|
| **Concierge** | Sem prefixo | Padrao. Pergunta, status, tarefa pequena |
| **Direto** | `@nome-do-agente` | Voce ja sabe quem resolve |
| **Departamento** | `@nome-do-departamento` | Voce sabe a area, nao a pessoa |
| **Rito** | `#` mais o briefing | Projeto grande, com portoes. Ver [06-RITO.md](06-RITO.md) |

---

## 5. Roteamento de modelo

Antes de qualquer delegacao o orquestrador escolhe conscientemente o modelo do agente, e anuncia a
escolha em uma linha. A regra e qualidade primeiro: **na duvida entre dois niveis, sobe**.

| Nivel | Tipo de tarefa |
|---|---|
| Rapido e barato | Varredura, inventario, busca em massa, formatacao, extracao deterministica |
| Intermediario | Codigo de rotina, script, integracao conhecida, analise padrao, relatorio |
| Forte | Arquitetura, causa raiz, seguranca, refatoracao ampla, verificacao adversarial |
| Topo | Estrategia, conselho, decisao que gera gasto, sintese final, julgamento de qualidade |

Um hook bloqueia qualquer criacao de agente que nao declare o nivel escolhido. Isso existe porque
escolher o modelo e exatamente o tipo de disciplina que se perde na pressa.

### A tarifa de criar um agente

Criar um agente novo nao e de graca, e o custo nao acompanha o tamanho da tarefa: a inicializacao
domina. Medicao do sistema de origem: o piso ficou perto de 88 mil tokens e um minuto, a mediana em
183 mil tokens e oito minutos. Cinco criacoes triviais custaram cerca de 678 mil tokens contra uma
faixa de 10 a 40 mil se o orquestrador tivesse feito na mao.

Por isso o sistema tem uma regra que parece contradizer "delegue sempre" e nao contradiz.

> **Nunca crie um agente para o que voce resolve em ate cinco chamadas de leitura.**
> "Na duvida, delegue" vale para especialidade, volume, paralelismo e acao externa. Nunca para o
> trivial.

E, quando o agente ja esta aberto, retome a conversa com ele em vez de criar outro: criar de novo
paga a inicializacao inteira outra vez.

Briefing enxuto tambem faz parte: objetivo, dados, **caminho do artefato**, formato e restricoes.
Nunca colar o relatorio inteiro dentro do briefing.

---

## 6. Paralelismo

Tres ou mais frentes independentes podem rodar juntas. Com duas regras que nasceram de dor.

1. **Dono unico de arquivo por onda.** Dois agentes escrevendo no mesmo arquivo, ou commitando no
   mesmo repositorio ao mesmo tempo, causam corrida de indice no git e trabalho perdido.
2. **No maximo tres agentes por onda.** Acima disso a consolidacao custa mais que o ganho.

E quando um agente entrega para o outro, o artefato vai para o disco e o segundo recebe o **caminho**,
nunca o resumo feito pelo orquestrador. Resumo intermediario perde detalhe e inventa consenso.

---

## 7. O que foi tentado e descartado

Vale mais que a lista do que funcionou.

| Tentativa | Por que foi descartada |
|---|---|
| Desligar a trava do orquestrador so um pouco | Em pouco mais de um mes ele tinha construido um projeto inteiro sozinho, sem delegar e sem revisao. Religada e nunca mais desligada |
| Lista de proibicao por texto do comando | Falha aberta. Um envelopador opaco passa. A trava passou a ser por ferramenta e por caminho, nao por palavra |
| Manter inventario de skills e agentes na lei | Envelhece em dias e passa a mentir com cara de verdade. Inventario e descoberto ao vivo |
| Redigir segredo depois de escrever o log | Tarde demais, o segredo ja tocou o disco. Passou a redigir antes da escrita |
| Placeholder de redacao longo e criativo | O proprio detector de segredo leu como string de alta entropia e travou o commit. Placeholder virou minusculo e obvio |
| Acumular runtimes de agente no servidor sem dono | Virou zoologico: varios runtimes sem manifesto e sem rito de desligamento. Trocado por um checklist de admissao com dono nomeado e botao de desligar em um comando |
| Bloquear leitura por forma do comando | Uma medicao mostrou que quase 80 por cento dos bloqueios reais eram leitura pura barrada por formato, nao por risco. A lista de leitura permitida foi afinada |
