# HAOS CC Model

### Sistema multi agente para Claude Code: orquestrador, agentes especialistas, skills, hooks de seguranca e memoria persistente

> Este repositorio e um **modelo de referencia**. Ele mostra a estrutura, as regras e os mecanismos
> de um sistema multi agente que roda em producao ha meses, sem nenhum dado da operacao que o
> originou. Voce clona, adapta e instala na sua maquina.

**Licenca:** MIT | **Idioma:** portugues do Brasil | **Plataforma:** [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)

---

## Sumario

1. [O problema que isso resolve](#o-problema-que-isso-resolve)
2. [O que e o HAOS](#o-que-e-o-haos)
3. [Arquitetura em uma imagem](#arquitetura-em-uma-imagem)
4. [As seis camadas](#as-seis-camadas)
5. [Instalacao em 5 passos](#instalacao-em-5-passos)
6. [Exemplo de uso de ponta a ponta](#exemplo-de-uso-de-ponta-a-ponta)
7. [Documentacao por camada](#documentacao-por-camada)
8. [O que este modelo nao traz](#o-que-este-modelo-nao-traz)
9. [Referencias e credito de origem](#referencias-e-credito-de-origem)

---

## O problema que isso resolve

Quem usa um assistente de codigo por muito tempo esbarra sempre nos mesmos quatro problemas.

**Um.** O assistente afirma coisas que nao verificou. Ele olha um comando, nao acha o que procurava
e conclui que a coisa nao existe. Decisao certa em cima de premissa falsa custa caro.

**Dois.** O assistente principal faz tudo sozinho. Ele le, escreve, deploya, apaga. A janela de
contexto entope, a qualidade cai e um comando destrutivo passa sem ninguem revisar.

**Tres.** Nada e lembrado. A cada sessao nova o mesmo erro volta, a mesma pegadinha e redescoberta,
a mesma explicacao e dada de novo.

**Quatro.** Tarefa grande vira improviso. Nao existe um rito que force diagnostico antes de
estrategia, estrategia antes de execucao, e QA antes de gastar dinheiro.

O HAOS ataca os quatro com mecanismo, nao com boa intencao escrita no prompt. Regra que depende de o
modelo lembrar de obedecer e sugestao. Regra que um hook bloqueia e regra.

---

## O que e o HAOS

HAOS quer dizer **Autonomous Operations Squad**. Na pratica sao seis camadas que se encaixam.

| Camada | O que faz | Onde mora |
|---|---|---|
| **Lei** | O arquivo CLAUDE.md que define identidade, regras inegociaveis e roteamento | `~/.claude/CLAUDE.md` |
| **Orquestrador** | A sessao principal. Classifica o pedido, executa o trivial, delega o resto | sessao do Claude Code |
| **Agentes** | 30 especialistas com missao, tom e limites proprios | `agents/` |
| **Skills** | Conhecimento sob demanda que o modelo carrega quando o assunto aparece | `skills/` |
| **Hooks** | Codigo que intercepta a ferramenta antes de ela rodar e pode bloquear | `hooks/` |
| **Memoria** | Registro duravel de decisao, erro e procedimento, com fechamento ritualizado | `~/.claude/projects/` |

A ideia central e simples de enunciar e dificil de manter: **o orquestrador nao e executor**. Ele le,
decide e distribui. Quem muda estado e um agente especialista, com briefing explicito e com um hook
vigiando.

---

## Arquitetura em uma imagem

```
                            VOCE
                              |
                              v
              +-------------------------------+
              |   CLAUDE.md  (a lei geral)    |
              |   carregada em toda sessao    |
              +---------------+---------------+
                              v
              +-------------------------------+
              |        ORQUESTRADOR           |
              |  classifica . roteia . fecha  |
              +---+-----------------------+---+
                  |                       |
        leitura pura                 muta estado
        (faz direto)                 (delega sempre)
                  |                       |
                  v                       v
        +--------------+        +-------------------+
        |  Read  Grep  |        |  HOOK PreToolUse  |  <-- bloqueia
        |  Glob  ls    |        |  (a trava fisica) |      o que
        +--------------+        +---------+---------+      nao passa
                                          v
                              +-----------------------+
                              |  AGENTE ESPECIALISTA  |
                              |  dev . devops . qa .  |
                              |  copy . dados . sec   |
                              +-----------+-----------+
                                          |  carrega sob demanda
                                          v
                              +-----------------------+
                              |        SKILLS         |
                              |  o conhecimento que   |
                              |  o assunto exigir     |
                              +-----------+-----------+
                                          v
                              +-----------------------+
                              |   HOOK Stop / fecho   |
                              |  memoria . commit .   |
                              |  espelho . aprendizado|
                              +-----------------------+
```

---

## As seis camadas

### 1. A lei (CLAUDE.md)

Um arquivo de texto carregado em toda sessao, em qualquer pasta. Define quem o assistente e, como
ele fala, o que ele nunca faz e para quem ele delega o que.

A regra que precede todas as outras se chama **verificar antes de afirmar**. Ela proibe declarar como
fato qualquer coisa sobre estado de sistema, mecanismo ou historico sem ter checado. E ela traz uma
heuristica dura que vale a pena copiar mesmo que voce nao use mais nada deste repositorio:

> **"nao achei em X" nunca e "nao existe".** Uma amostra nao prova o todo. Antes de cravar qualquer
> negativo ou absoluto, trate a frase como hipotese a refutar: cheque por outro caminho e consulte a
> memoria.

Detalhe completo em [docs/07-REGRAS.md](docs/07-REGRAS.md).

### 2. O orquestrador

A sessao principal. A pergunta que ele faz antes de agir nao e "posso usar essa ferramenta?", e
**"isso muda estado, apaga ou envia algo, ou e so leitura?"**.

Leitura pura ele faz direto, em qualquer volume. Mutacao ele delega. Isso nao e disciplina, e travado
por hook.

### 3. Os agentes

Trinta especialistas. Cada um e um arquivo markdown com missao, tom, framework de trabalho, formato
de saida e uma lista de coisas que ele nunca faz. Eles nao conversam, eles entregam.

Lista completa e criterio de acionamento em [docs/02-AGENTES.md](docs/02-AGENTES.md).

### 4. As skills

Conhecimento empacotado que o modelo carrega quando o assunto aparece, e ignora quando nao aparece. E
o que permite ter centenas de paginas de procedimento sem entupir a janela de contexto.

Como funciona e como escrever a sua em [docs/03-SKILLS.md](docs/03-SKILLS.md).

### 5. Os hooks

A parte que transforma regra em mecanismo. Um hook e um programa que o Claude Code chama antes ou
depois de um evento. Se ele devolve bloqueio, a ferramenta nao roda.

O que cada hook intercepta e por que em [docs/04-HOOKS.md](docs/04-HOOKS.md).

### 6. A memoria

Tres camadas, da mais barata para a mais cara: arquivos markdown de memoria duravel, memoria de
sessao vetorial, e a fonte viva (o codigo e o servidor de verdade). A regra de frescor manda: para
estado que muda sozinho, so o comando ao vivo fecha a questao.

Fluxo e ritual de fechamento em [docs/05-MEMORIA.md](docs/05-MEMORIA.md).

---

## Instalacao em 5 passos

### Pre requisitos

| Item | Versao minima | Para que |
|---|---|---|
| [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) | atual | o runtime |
| Python | 3.10 | roda os hooks |
| Git | 2.30 | versiona e fecha tarefa |
| PowerShell 7 ou bash | atual | scripts de fechamento |

### Passo 1: clone

```bash
git clone https://github.com/<SEU_USUARIO>/HAOS-CC-Model.git
cd HAOS-CC-Model
```

### Passo 2: instale a lei

Copie o exemplo para o seu diretorio de configuracao e edite os blocos marcados com `<...>`. Sao
poucos: seu nome, seu fuso e para quem voce delega o que.

```bash
cp examples/CLAUDE.md.example ~/.claude/CLAUDE.md
```

### Passo 3: instale agentes, skills e comandos

```bash
cp -r agents/.   ~/.claude/agents/
cp -r skills/.   ~/.claude/skills/
cp -r commands/. ~/.claude/commands/
```

### Passo 4: ligue os hooks

Copie os hooks. O `settings.json` de exemplo so pode ser copiado por cima se voce **ainda nao tem
um**; se ja tem, funda apenas os blocos `hooks` e `env`, nunca sobrescreva o arquivo inteiro.

```bash
cp -r hooks/. ~/.claude/hooks/

# so se voce AINDA NAO TEM ~/.claude/settings.json:
cp examples/settings.json.example ~/.claude/settings.json
```

Edite as variaveis do bloco `env`, incluindo `HAOS_GUARD_PROFILE` com a raiz real do seu projeto
(sem ela o guard fica fechado em qualquer pasta ate voce configurar). Nenhuma variavel guarda
segredo: elas guardam **caminhos** e o **nome** do arquivo onde os seus segredos moram. Detalhe
completo em [INSTALL.md](INSTALL.md#36-configure-as-variaveis).

### Passo 5: valide

```bash
python hooks/selftest.py
```

O selftest confirma duas coisas: (1) que voce configurou o perfil do guard com a raiz real do seu
projeto, sem deixar o marcador de fabrica; (2) que uma bateria extensa de vetores de bypass (comando
encadeado, redirecionamento disfarcado, auto-desarme, spawn sem tier de modelo, entre outros) continua
sendo bloqueada. Ele nao confere versao de Python nem contagem de agentes/skills. Detalhe completo em
[INSTALL.md](INSTALL.md#4-validacao).

Se qualquer vetor passar como liberado quando deveria bloquear, a instalacao esta errada e o sistema
esta aberto. Nao siga em frente. O guia de diagnostico esta em [INSTALL.md](INSTALL.md).

---

## Exemplo de uso de ponta a ponta

Cenario: voce pede uma alteracao numa API e quer que o sistema faca direito.

**1. Voce escreve o pedido.**

```
Preciso de um endpoint novo de exportacao de relatorio, com paginacao e limite de 500 linhas.
```

**2. O orquestrador classifica.** Codigo de produto, mutacao, especializado. Nao e leitura pura,
entao ele nao faz na mao. Ele escolhe o agente e o modelo, e anuncia a escolha.

```
MODELO: sonnet porque e implementacao de rotina em stack conhecida
Delegando para dev-backend com a skill de desenvolvimento orientado a teste.
```

**3. O hook do roteador de modelo confere.** Spawn sem modelo declarado e bloqueado. Spawn com modelo
declarado passa e fica registrado.

**4. O agente trabalha.** Ele le o codigo, escreve o teste que falha, implementa, roda o teste, mostra
a saida. Ele nao diz "pronto", ele mostra a evidencia.

**5. O revisor entra.** Um segundo agente le tudo que a tarefa mudou, incluindo arquivo novo ainda nao
versionado, e devolve achados. Estourar o numero de rodadas de revisao nao aprova o trabalho: defeito
que sobrou vira pendencia explicita.

**6. O fechamento roda.** O conceito: um comando unico decide se houve aprendizado duravel; se houve,
vira memoria; se nao, so fecha; commit e espelho da memoria acontecem no mesmo passo. **Este pacote
traz a doutrina e o hook de captura (`session_end.py`), nao o comando pronto** — ver
[docs/05-MEMORIA.md](docs/05-MEMORIA.md#5-o-ritual-de-fechamento).

O ganho nao e velocidade, e que o caminho errado fica dificil de percorrer.

---

## Documentacao por camada

| Documento | O que voce encontra |
|---|---|
| [docs/01-ARQUITETURA.md](docs/01-ARQUITETURA.md) | Como as camadas se encaixam, fluxo de uma tarefa, decisoes de projeto e o que foi descartado |
| [docs/02-AGENTES.md](docs/02-AGENTES.md) | Os 30 agentes, o que cada um faz, quando aciona, e como criar o seu |
| [docs/03-SKILLS.md](docs/03-SKILLS.md) | O que e uma skill, como o modelo escolhe, anatomia de um SKILL.md, como escrever a sua |
| [docs/04-HOOKS.md](docs/04-HOOKS.md) | Cada hook, o que intercepta, por que existe, e a Regra de Ouro explicada |
| [docs/05-MEMORIA.md](docs/05-MEMORIA.md) | As camadas de memoria, a regra de frescor, o ritual de fechamento |
| [docs/06-RITO.md](docs/06-RITO.md) | O pipeline de 13 fases com portoes bloqueantes |
| [docs/07-REGRAS.md](docs/07-REGRAS.md) | A lei geral: o que e inegociavel e por que |
| [docs/08-REFERENCIAS.md](docs/08-REFERENCIAS.md) | Fonte de cada ideia que veio de fora, com link |
| [INSTALL.md](INSTALL.md) | Instalacao detalhada, validacao e diagnostico |
| [SECURITY.md](SECURITY.md) | Modelo de ameaca, o que o sistema protege e o que nao protege |

---

## O que este modelo nao traz

Transparencia e parte do modelo. Isto aqui **nao** vem no pacote, de proposito.

- **Skills de cliente e de marca.** O sistema de origem tem dezenas de skills amarradas a ERP, CRM,
  gateway de pagamento e marketplaces especificos. Elas nao servem para voce e carregariam dado de
  terceiro. Ficaram de fora. O que entra e a **estrutura** e alguns exemplos neutros que mostram o
  padrao.
- **Segredo de qualquer tipo.** Nenhuma chave, token ou senha. O sistema referencia credencial pelo
  **nome da variavel**, nunca pelo valor, e isso e uma regra do proprio sistema.
- **Endereco de infraestrutura.** Sem IP, sem dominio proprio, sem nome de container, sem caminho
  pessoal de maquina. Onde havia um, entrou um marcador tipo `<SEU_CAMINHO>` ou `<SEUS_CAMINHOS_PROTEGIDOS>`.
- **A memoria acumulada.** Memoria e da operacao que a gerou. O modelo traz o **mecanismo** de
  memoria, vazio, pronto para voce encher com a sua.

---

## Referencias e credito de origem

Quase nada aqui foi inventado do zero. O que e original e a **costura**: juntar as pecas abaixo num
sistema unico com travas de verdade. Cada peca e creditada. A lista completa, com o que exatamente
veio de cada uma, esta em [docs/08-REFERENCIAS.md](docs/08-REFERENCIAS.md).

### Base da plataforma

| Origem | O que veio dela | Link |
|---|---|---|
| **Claude Code** (Anthropic) | O runtime inteiro: sessao, ferramentas, plugin, subagentes | [docs.claude.com](https://docs.claude.com/en/docs/claude-code/overview) |
| **Hooks** (Anthropic) | O mecanismo de interceptacao e o contrato de bloqueio | [Hooks reference](https://docs.claude.com/en/docs/claude-code/hooks) |
| **Subagents** (Anthropic) | O formato de agente: frontmatter, ferramentas permitidas, descricao que dispara | [Subagents](https://docs.claude.com/en/docs/claude-code/sub-agents) |
| **Agent Skills** (Anthropic) | O formato SKILL.md e o carregamento sob demanda | [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) |
| **Model Context Protocol** | O padrao de conexao com ferramenta externa | [modelcontextprotocol.io](https://modelcontextprotocol.io) |

### Ideias e padroes de terceiros

| Origem | O que veio dela | Link |
|---|---|---|
| **superpowers** | Brainstorming, escrita de plano, desenvolvimento orientado a subagente, depuracao sistematica, verificacao antes de concluir. A nossa lei declara a precedencia entre as duas | [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| **claude-mem** | A camada de memoria de sessao e a captura automatica ao fim da sessao | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) |
| **Obsidian** | O espelho legivel da memoria duravel, em markdown com links entre notas | [obsidian.md](https://obsidian.md) |
| **gitleaks** | A varredura de segredo que roda antes de commit e no historico | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| **OWASP Top 10** | O checklist de auditoria do agente de seguranca | [owasp.org](https://owasp.org/www-project-top-ten/) |
| **BMAD Method** | Papeis de agente com portao de aprovacao entre fases, que inspirou o Rito | [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) |
| **AIOS** | O vocabulario de sistema operacional de agentes: escalonador, kernel, camada de memoria | [agiresearch/AIOS](https://github.com/agiresearch/AIOS) |
| **Test Driven Development** (Kent Beck) | O ciclo vermelho, verde, refatora, adaptado para trabalho de agente | [Livro](https://www.oreilly.com/library/view/test-driven-development/0321146530/) |
| **Conventional Commits** | O padrao de mensagem de commit do fechamento | [conventionalcommits.org](https://www.conventionalcommits.org) |

### O que nasceu de incidente proprio

Estas regras nao vieram de livro. Vieram de coisa que deu errado. Estao aqui sem o contexto da
operacao que as gerou, porque o aprendizado vale e o dado nao e seu.

| Regra | Incidente que a gerou |
|---|---|
| **"nao achei em X" nunca e "nao existe"** | Um agente olhou uma unica listagem de containers, nao achou um servico e declarou que ele nao existia. O servico existia, instalado no host, fora do alcance daquele comando |
| **Redigir segredo antes de escrever em disco** | Um hook de seguranca registrava a linha de comando completa que bloqueava. Comando com header de autenticacao virou chave em texto claro no log. A correcao foi redigir antes da escrita, nunca depois |
| **Portao anti desistencia** | Um agente declarou "nao tenho acesso" depois de procurar credencial em um unico lugar. O acesso existia e estava documentado numa skill que ele nunca leu. Virou regra: esgotar quatro fontes antes de dizer que esta bloqueado |
| **O orquestrador nao executa** | A trava foi desligada por conveniencia. Em pouco mais de um mes o orquestrador tinha construido um projeto inteiro sozinho, sem revisao e sem delegar. Foi religada e nunca mais desligada |
| **Dono unico de arquivo por onda** | Tres agentes commitando no mesmo repositorio em paralelo causaram corrida de indice no git. Virou regra: um dono por arquivo, no maximo tres agentes por onda |
| **Nome de variavel, nunca valor** | Segredo apareceu em relatorio de diagnostico. Virou regra absoluta: cita se o nome da variavel, o valor nunca sai |
| **Placeholder de redacao tem que ser burro** | Um marcador de redacao criativo, longo e com hash, foi lido pelo proprio detector de segredo como string de alta entropia. O remedio virou o problema. Placeholder passou a ser minusculo e obvio |

---

## Contribuindo

Leia [CONTRIBUTING.md](CONTRIBUTING.md). Resumo: issue antes de pull request grande, portugues do
Brasil na documentacao, e nenhum dado real de ninguem em exemplo.

## Licenca

MIT. Veja [LICENSE](LICENSE).

## Autoria

Sistema concebido e mantido por **Gian Marco Menegussi Scaglianti**. Este modelo publico e uma versao
sanitizada do sistema em producao, preparada para servir de ponto de partida a quem quiser montar o
seu.
