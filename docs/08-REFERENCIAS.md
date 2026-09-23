# 08 Referencias e credito de origem

Este sistema e uma **costura**, nao uma invencao. A maior parte das pecas veio de outro lugar. Esta
pagina diz de onde veio cada uma, o que exatamente foi aproveitado, e onde nos discordamos da fonte.

---

## 1. A plataforma

Tudo roda em cima do Claude Code, da Anthropic. Sem ele nao ha sistema.

| Recurso | O que veio dele | Documentacao |
|---|---|---|
| **Claude Code** | Sessao, ferramentas, permissoes, plugins, subagentes | [Visao geral](https://docs.claude.com/en/docs/claude-code/overview) |
| **Hooks** | Todo o mecanismo de trava: eventos, contrato de entrada e saida, decisao de permissao | [Hooks reference](https://docs.claude.com/en/docs/claude-code/hooks) |
| **Subagents** | O formato de agente, o cabecalho, a lista de ferramentas, a descricao como gatilho | [Subagents](https://docs.claude.com/en/docs/claude-code/sub-agents) |
| **Agent Skills** | O formato SKILL.md, o carregamento sob demanda, a descricao que dispara | [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) |
| **CLAUDE.md** | A ideia de um arquivo de memoria lido em toda sessao | [Memory](https://docs.claude.com/en/docs/claude-code/memory) |
| **Plugins** | O empacotamento de agentes, skills, comandos e hooks num pacote instalavel | [Plugins](https://docs.claude.com/en/docs/claude-code/plugins) |
| **Model Context Protocol** | O padrao aberto de conexao com ferramenta externa | [modelcontextprotocol.io](https://modelcontextprotocol.io) |

---

## 2. Metodos de terceiros

### superpowers

Plugin oficial de exemplo, da Anthropic.
[claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

**O que veio:** brainstorming, escrita de plano, desenvolvimento orientado a subagente, depuracao
sistematica, pedido e recebimento de revisao de codigo, despacho de agentes em paralelo, e verificacao
antes de concluir.

**Onde discordamos, e por que.** A propria skill do superpowers diz que a lei do projeto vence ela.
Este sistema escreve essa precedencia numa tabela, em vez de deixar implicito.

| Ponto | O que o superpowers propoe | O que este sistema faz |
|---|---|---|
| Escolha de modelo | O modelo mais barato que der conta | Qualidade primeiro. Na duvida entre dois niveis, sobe |
| Skill antes de qualquer resposta | Sempre | So em trabalho de codigo ou produto. Pergunta, status e operacao seguem a regra de resposta curta |
| Apagar e recomecar no ciclo de teste | Vale amplo | Vale para codigo com suite de teste, e apaga so o que foi escrito na mesma tarefa. Nunca codigo de producao que ja existia |
| Fechar ramo de desenvolvimento | Menu proprio de finalizacao | O fechamento e o ritual proprio do sistema. Publicacao e mesclagem so com autorizacao humana |
| Paralelismo | Despacho paralelo | Obedece a regra de dono unico por arquivo e no maximo tres por onda |
| Limite de rodadas de revisao | Encerra ao estourar | Estourar **nao aprova**. Defeito que sobrou vira pendencia explicita |

### claude-mem

[thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)

**O que veio:** a camada de memoria de sessao e a captura automatica no fim da sessao.

**O que aprendemos operando:** toda camada de memoria um dia degrada. Quando a busca vetorial caiu, o
comportamento certo foi cair para a busca por texto no disco **e declarar no relatorio que pulou a
camada**. Tempo esgotado numa ferramenta nunca e prova de ausencia de conhecimento. Virou regra em
[05-MEMORIA.md](05-MEMORIA.md).

### Obsidian

[obsidian.md](https://obsidian.md)

**O que veio:** o espelho legivel da memoria duravel. Markdown com links entre notas, que a pessoa
navega sem abrir o terminal.

### gitleaks

[gitleaks/gitleaks](https://github.com/gitleaks/gitleaks)

**O que veio:** a varredura de segredo, com regras proprias somadas as padrao, rodando antes do commit
e tambem sobre o historico inteiro.

**O que aprendemos operando:** o placeholder de redacao tem que ser **burro**. Um marcador criativo,
longo e com hash, foi lido pelo proprio gitleaks como string de alta entropia e travou o commit. O
remedio virou o problema. Placeholder passou a ser minusculo e obvio.

### OWASP Top 10

[owasp.org](https://owasp.org/www-project-top-ten/)

**O que veio:** o checklist de auditoria de aplicacao do agente de seguranca, das dez categorias.

### BMAD Method

[BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)

**O que veio:** papeis de agente encadeados com portao de aprovacao entre fases, que inspirou o Rito.

### AIOS

[agiresearch/AIOS](https://github.com/agiresearch/AIOS)

**O que veio:** o vocabulario de sistema operacional de agentes. Escalonador, kernel, camada de
memoria, gerente de contexto. Ajudou a nomear as camadas.

### Test Driven Development

Kent Beck. [Livro](https://www.oreilly.com/library/view/test-driven-development/0321146530/)

**O que veio:** o ciclo vermelho, verde, refatora. Adaptado: escrever a prova que falha antes de
implementar.

**Onde adaptamos:** nem todo trabalho tem suite de teste. Para automacao, infraestrutura e texto a
prova e outra: falha provocada de proposito, teste de ponta a ponta, e a etiqueta de verificacao.

### Conventional Commits

[conventionalcommits.org](https://www.conventionalcommits.org)

**O que veio:** o padrao de mensagem de commit do fechamento de tarefa.

---

## 3. O que nasceu de incidente proprio

Estas nao vieram de fonte externa. Vieram de coisa que deu errado na operacao. Estao aqui sem o
contexto que as gerou, porque o aprendizado e generalizavel e o dado nao e de ninguem alem de quem o
viveu.

| Regra | O incidente |
|---|---|
| **"nao achei em X" nunca e "nao existe"** | Um agente olhou uma unica listagem de containers, nao achou um servico e declarou que ele nao existia. O servico existia, instalado direto no host, invisivel para aquele comando. Virou a heuristica central da regra zero |
| **"e so X" e sinal vermelho no briefing** | Um agente instruiu outro dizendo que a migracao era "so copiar a pasta". Nao era: o alvo tinha um registro em banco. A regra passou a morder tambem sobre o **briefing**, nao so sobre a afirmacao |
| **Redigir antes de escrever em disco** | O hook de seguranca registrava a linha de comando completa que bloqueava. Comando com cabecalho de autenticacao virou chave em texto claro no log e travou o versionamento da memoria por dias. A redacao passou a acontecer antes da escrita, preservando o nome do campo e removendo so o valor |
| **Portao anti desistencia** | Um agente declarou "nao tenho acesso" depois de procurar credencial em um unico lugar. O acesso existia, documentado numa skill que ele nunca abriu. Virou a regra das quatro fontes |
| **A trava nao se desliga** | A trava do orquestrador foi desligada por conveniencia. Em pouco mais de um mes ele tinha construido um projeto inteiro sozinho, sem revisao. Foi religada, e um conselho posterior rejeitou por unanimidade desligar de novo. O caminho passou a ser afinar a lista de leitura permitida, nao afrouxar a trava de mutacao |
| **Medir antes de apertar** | A medicao dos bloqueios reais mostrou que quase 80 por cento eram leitura pura barrada por formato, nao por risco. Guard que atrapalha sem motivo ensina a pessoa a desligar o guard |
| **Dono unico de arquivo por onda** | Tres agentes commitando no mesmo repositorio em paralelo causaram corrida de indice no git. Virou regra de paralelismo |
| **O agente ve menos que o orquestrador** | Agentes tem menos fontes disponiveis que a sessao principal. O briefing precisa dizer isso, e as fontes obrigatorias do portao anti desistencia sao todas de disco e linha de comando justamente por causa disso |
| **Inventario nao mora na lei** | Contagem de skills e de agentes escrita no documento envelheceu em dias e passou a mentir com cara de verdade. Inventario e descoberto ao vivo |
| **Documento congelado tem que se anunciar** | Copias antigas do arquivo de lei continuavam sendo lidas como se fossem vigentes. Toda copia congelada passou a abrir com um aviso dizendo que e foto de um commit, nao lei |
| **Historico privado vira historico publico** | Um repositorio privado acumula, por meses, conteudo que so fazia sentido enquanto era privado. Abrir a visibilidade expoe o historico inteiro, nao o estado atual. Por isso este modelo nasceu como repositorio **novo**, e nao como abertura do antigo |

---

## 4. Licenca e uso

Este modelo e MIT. Use, adapte, redistribua. Se ele te ajudar, um link de volta e bem-vindo e nao e
obrigatorio.

As fontes citadas acima tem cada uma a sua propria licenca. Verifique antes de redistribuir codigo
delas.
