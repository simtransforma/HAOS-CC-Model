<div align="center">

# HAOS-CC-Model

### HAU Autonomous Operations Squad - Modelo Aberto para Claude Code

**Sistema multiagente de referencia, pronto para clonar e adaptar: orquestrador com trava de delegacao por hook, 30 agentes especialistas, skills sob demanda, memoria persistente entre sessoes e governanca humana em ponto critico.**

*by [**HAU Solucoes Digitais**](https://github.com/simtransforma)*

[![Plugin Claude Code](https://img.shields.io/badge/claude--code-plugin-blue?logo=anthropic)](https://claude.com/claude-code)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](.claude-plugin/plugin.json)
[![Agents](https://img.shields.io/badge/agentes-30-green)](#agentes-30)
[![Commands](https://img.shields.io/badge/commands-44-orange)](#comandos-44)
[![Skills](https://img.shields.io/badge/skills-25-purple)](#skills-25)
[![Departments](https://img.shields.io/badge/departamentos-8-yellow)](#departamentos-8)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

</div>

---

> **Este repositorio e um modelo de referencia, nao a operacao real.** Ele mostra a estrutura, as
> regras e os mecanismos de um sistema multiagente que roda em producao ha meses, sem nenhum dado
> da operacao que o originou: sem segredo, sem endereco de infraestrutura, sem skill amarrada a
> cliente ou marca. Voce clona, adapta e instala na sua maquina. O modelo interno completo (privado)
> e o HAOS_CC; este e a versao publica e sanitizada dele.

---

## O que e o HAOS?

**HAOS (HAU Autonomous Operations Squad)** e um framework para [Claude Code](https://claude.com/claude-code) que transforma o terminal numa squad inteira operada por IA: agentes especializados organizados em departamentos, pipeline de governanca, memoria persistente entre sessoes e gates humanos antes de acao irreversivel.

**Nao sao chatbots.** Os agentes executam: geram codigo, copy, analise, plano, campanha. Param e pedem aprovacao quando vao publicar, gastar ou enviar algo.

Na pratica sao **seis camadas** que se encaixam.

| Camada | O que faz | Onde mora |
|---|---|---|
| **Lei** | O CLAUDE.md que define identidade, regras inegociaveis e roteamento | `~/.claude/CLAUDE.md` |
| **Orquestrador** | A sessao principal. Classifica o pedido, executa o trivial, delega o resto | sessao do Claude Code |
| **Agentes** | 30 especialistas com missao, tom e limite proprios | `agents/` |
| **Skills** | Conhecimento sob demanda que o modelo carrega quando o assunto aparece | `skills/` |
| **Hooks** | Codigo que intercepta a ferramenta antes de ela rodar e pode bloquear | `hooks/` |
| **Memoria** | Registro duravel de decisao, erro e procedimento, com fechamento ritualizado | `~/.claude/projects/` |

### Por que isso importa?

- **Especializacao real**: cada agente tem identidade, framework e regras "nunca". Nao e um modelo generico fazendo tudo.
- **Governanca incorporada por mecanismo, nao por boa intencao**: um hook PreToolUse bloqueia mutacao do orquestrador antes de ela rodar. Regra que depende do modelo lembrar de obedecer e sugestao; regra que um hook trava e regra.
- **A pergunta certa nao e "posso usar essa ferramenta?"**: e "isso muda estado, apaga ou envia algo, ou e so leitura?". Leitura o orquestrador faz direto, em qualquer volume; mutacao ele sempre delega para um agente especialista.
- **Memoria eterna**: hooks SessionStart/Stop/PostCompact preservam contexto entre sessoes, sem exigir que voce reexplique a mesma coisa toda vez.
- **Plug-and-play**: instala como plugin oficial do Claude Code, namespace `/haos:*`.
- **Open source (MIT)**: clone, adapte, contribua.

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

A regra que precede todas as outras dentro da lei se chama **verificar antes de afirmar**: proibe
declarar como fato qualquer coisa sobre estado de sistema, mecanismo ou historico sem checar. A
heuristica que sustenta ela vale copiar mesmo que voce nao use mais nada deste repositorio:

> **"nao achei em X" nunca e "nao existe".** Uma amostra nao prova o todo. Antes de cravar qualquer
> negativo ou absoluto, trate a frase como hipotese a refutar: cheque por outro caminho e consulte a
> memoria.

Detalhe completo em [docs/07-REGRAS.md](docs/07-REGRAS.md).

---

## Instalacao em 5 passos

### Pre-requisitos

| Item | Versao minima | Para que |
|---|---|---|
| [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) | atual | o runtime |
| Python | 3.10+ | roda os hooks |
| Git | 2.30 | versiona e fecha tarefa |
| PowerShell 7 ou bash | atual | scripts de fechamento |

### Passo 1: clone

```bash
git clone https://github.com/simtransforma/HAOS-CC-Model.git
cd HAOS-CC-Model
```

### Passo 2: instale a lei

Copie o exemplo para o seu diretorio de configuracao e edite os blocos marcados com `<...>`: seu
nome, seu fuso, para quem voce delega o que.

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

Copie os hooks. O settings.json de exemplo so pode ser copiado por cima se voce ainda nao tem
um; se ja tem, funda apenas os blocos hooks e env, nunca sobrescreva o arquivo inteiro.

```bash
cp -r hooks/. ~/.claude/hooks/

# so se voce AINDA NAO TEM ~/.claude/settings.json:
cp examples/settings.json.example ~/.claude/settings.json
```

Edite as variaveis do bloco env, incluindo HAOS_GUARD_PROFILE com a raiz real do seu projeto
(sem ela o guard fica fechado em qualquer pasta ate voce configurar). Nenhuma variavel guarda
segredo: elas guardam **caminhos** e o **nome** do arquivo onde os seus segredos moram. Detalhe
completo em [INSTALL.md](INSTALL.md#36-configure-as-variaveis).

### Passo 5: valide

```bash
python hooks/selftest.py
```

O selftest confirma duas coisas: que voce configurou o perfil do guard com a raiz real do seu
projeto, sem deixar o marcador de fabrica; e que uma bateria extensa de vetores de bypass (comando
encadeado, redirecionamento disfarcado, auto-desarme, spawn sem tier de modelo, entre outros)
continua sendo bloqueada. Se qualquer vetor passar como liberado quando deveria bloquear, a
instalacao esta errada e o sistema esta aberto: nao siga em frente, veja [INSTALL.md](INSTALL.md).

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

**3. O hook do roteador de modelo confere.** Spawn sem modelo declarado e bloqueado. Spawn com
modelo declarado passa e fica registrado.

**4. O agente trabalha.** Ele le o codigo, escreve o teste que falha, implementa, roda o teste,
mostra a saida. Ele nao diz "pronto", ele mostra a evidencia.

**5. O revisor entra.** Um segundo agente le tudo que a tarefa mudou, incluindo arquivo novo ainda
nao versionado, e devolve achados. Estourar o numero de rodadas de revisao nao aprova o trabalho:
defeito que sobrou vira pendencia explicita.

**6. O fechamento roda.** Um passo unico decide se houve aprendizado duravel; se houve, vira
memoria; se nao, so fecha; commit e espelho da memoria acontecem no mesmo passo. Este pacote traz a
doutrina e o hook de captura (session_end.py), nao o comando pronto de fechamento: veja
[docs/05-MEMORIA.md](docs/05-MEMORIA.md#5-o-ritual-de-fechamento).

O ganho nao e velocidade, e que o caminho errado fica dificil de percorrer.

---

## Departamentos (8)

| Departamento | Entry-point | Agentes | Foco |
|---|---|:-:|---|
| `/haos:conselho` | estrategista-chefe | 4 | Estrategia, decisoes criticas, conflitos |
| `/haos:criativo` | copy-specialist | 5 | Copy, design, video, conteudo, social |
| `/haos:trafego` | traffic-master | 3 | Midia paga, tracking |
| `/haos:dados` | data-analyst | 4 | Analise, BI, pesquisa, due diligence |
| `/haos:funnel` | funnel-architect | 4 | Funis, automacao, CRM, email |
| `/haos:produto` | product-manager | 4 | PM, UX, dev frontend/backend |
| `/haos:orquestracao` | qa-reviewer | 4 | QA, PM, compliance, devops |
| `/haos:seguranca` | chuck-norris | 2 | Security, concierge para entrada sem destino |

---

## Agentes (30)

Cada agente tem identidade, framework de fases, principios "norte", regras "nunca" e formato de
retorno estruturado (CONCLUIDO / BLOQUEADO / REVISAO). Criterio para criar o seu:
[docs/02-AGENTES.md](docs/02-AGENTES.md).

<details>
<summary><b>@conselho (4)</b></summary>

- **main** - orquestrador principal: classifica, roteia, consolida, nunca executa mutacao sozinho
- **estrategista-chefe** - posicionamento, cenarios, priorizacao de portfolio, decisao de expansao
- **diretor-criativo** - direcao criativa, poder de veto, brand guidelines, revisao de 10 dimensoes
- **cmo** - ROI, funil, critica de criativo, questiona decisao comercial e exige dado
</details>

<details>
<summary><b>@criativo (5)</b></summary>

- **copy-specialist** - copy de conversao (headline, VSL, email, WhatsApp, landing, carrossel), sempre com variacao A/B
- **content-strategist** - calendario editorial, briefing de conteudo, estrategia cross-platform, analise de performance organica
- **designer** - producao visual (carrossel, banner, thumbnail, social card), acessibilidade e mobile-first
- **videomaker** - roteiro, storyboard, edicao de video curto e longo, obsessao pelos 3 primeiros segundos
- **sm-social** - execucao de calendario, gestao de comunidade, metrica semanal por plataforma, crise de reputacao
</details>

<details>
<summary><b>@trafego (3)</b></summary>

- **traffic-master** - plano de midia, briefing ao media-buyer, publico/budget/KPI, debrief de ciclo
- **media-buyer** - execucao tatica: setup, otimizacao diaria, scaling, protocolo de crise
- **tracking-engineer** - pixel, evento, CAPI, GTM/GA4, UTM, green light de tracking antes de campanha subir
</details>

<details>
<summary><b>@dados (4)</b></summary>

- **data-analyst** - diagnostico diario, relatorio semanal, analise de funil, sempre termina com recomendacao
- **bi-engineer** - pipeline ETL, modelagem star schema, dashboard, integracao de nova fonte de dado
- **pesquisador** - concorrencia, tendencia, benchmark, publico-alvo; toda entrega tem fonte e data
- **auditor-confianca** - due diligence de empresa e fornecedor por OSINT legal, score com gate bloqueante, nunca envia sem OK
</details>

<details>
<summary><b>@funnel (4)</b></summary>

- **funnel-architect** - jornada ponta a ponta, sistema de tags, especificacao de funil e handoff tecnico
- **automation-engineer** - workflow de automacao, webhook, integracao entre plataforma, idempotencia
- **crm-specialist** - pipeline comercial, cadencia de follow-up, script de objecao, higiene de base
- **email-marketer** - sequencia (boas-vindas, nutricao, lancamento, reativacao), segmentacao, deliverability
</details>

<details>
<summary><b>@produto (4)</b></summary>

- **product-manager** - discovery, PRD, priorizacao RICE, metrica de produto, plano de lancamento
- **ux-researcher** - teste de usabilidade, heuristica de Nielsen, WCAG, jornada, recomendacao priorizada
- **dev-frontend** - landing page, checkout, componente, Core Web Vitals, tracking no codigo, acessibilidade
- **dev-backend** - endpoint, integracao externa, webhook, migracao de dado, hardening de backend
</details>

<details>
<summary><b>@orquestracao (4)</b></summary>

- **qa-reviewer** - gate antes de publicar/deployar, parecer formal APROVADO / AJUSTES / REPROVADO
- **project-manager** - WBS, dependencia, kanban, progresso com evidencia, escalonamento no tempo certo
- **compliance-officer** - legislacao, politica de plataforma, poder de veto sobre publicacao de risco alto
- **devops** - deploy, rollback, troubleshooting de producao, secret, backup, resposta a incidente
</details>

<details>
<summary><b>@seguranca (2)</b></summary>

- **chuck-norris** - auditoria de servidor/container, hardening, vetting de skill externa, revisao OWASP, audit-only
- **concierge** - roteador de entrada sem destino explicito; classifica e encaminha, nao executa
</details>

---

## Comandos (44)

### Operacao (8)
| Comando | Funcao |
|---|---|
| `/haos:setup` | Wizard de configuracao inicial |
| `/haos:menu` | Menu interativo principal |
| `/haos:base` | Visao geral do sistema |
| `/haos:agentes` | Lista os 30 agentes |
| `/haos:departamentos` | Lista os 8 departamentos |
| `/haos:rito` | Pipeline Rito v2 (13 fases, so marketing/lancamento) |
| `/haos:main` | Aciona o orquestrador diretamente |
| `/haos:concierge` | Roteador para quem nao sabe qual agente acionar |

### Departamentos (8)
`/haos:conselho` - `/haos:criativo` - `/haos:trafego` - `/haos:dados` - `/haos:funnel` - `/haos:produto` - `/haos:orquestracao` - `/haos:seguranca`

### Agentes (30)
Cada um dos 30 agentes tem seu proprio atalho `/haos:{nome}` - ex.: `/haos:cmo`, `/haos:dev-backend`, `/haos:copy-specialist`, `/haos:auditor-confianca`.

Indice completo: `commands/`.

---

## Skills (25)

Skills carregadas sob demanda, quando o assunto aparece na conversa.

| Categoria | Skills |
|---|---|
| **Desenvolvimento** | `software-engineer`, `software-architecture`, `design-principles` |
| **Marketing e produto** | `copywriting`, `unit-economics` |
| **Pesquisa e verificacao** | `haos-deep-research`, `haos-query-expansion`, `haos-source-quality-auditor`, `haos-claim-verification`, `haos-research-report-writer` |
| **Governanca e execucao HAOS** | `haos-auditoria-master`, `haos-execution-waves`, `haos-handoff-artefato`, `haos-memory-provenance`, `haos-memory-triple`, `haos-model-router`, `haos-multi-agent-review`, `haos-project-sanitation`, `haos-quality-gates`, `haos-structural-refactor`, `token-optimizer` |
| **Operacao de sessao** | `long-running-agent`, `servidor-compartilhado`, `session-handoff` |
| **Meta (skill sobre skill)** | `skill-creator` |

Anatomia de uma SKILL.md e como escrever a sua: [docs/03-SKILLS.md](docs/03-SKILLS.md).

---

## Memoria persistente (hooks automaticos)

| Hook | Quando dispara | O que faz |
|---|---|---|
| `session_start.py` | Inicio de cada sessao | Injeta estado, pendencia e alerta |
| `session_end.py` | Fim de cada resposta (Stop) | Captura o que aconteceu e alimenta a memoria |
| `post_compact.py` | Apos compactacao do contexto | Reinjeta o essencial |
| `prompt_router.py` | Envio de cada mensagem | Reconhece prefixo de modo, avisa de rito ativo |

Memoria vive em `~/.claude/projects/{seu-projeto}/memory/`, descoberta dinamicamente pelo cwd
(sem caminho fixo em codigo). Camadas, regra de frescor e ritual de fechamento em
[docs/05-MEMORIA.md](docs/05-MEMORIA.md).

---

## Documentacao por camada

| Documento | O que voce encontra |
|---|---|
| [docs/01-ARQUITETURA.md](docs/01-ARQUITETURA.md) | Como as camadas se encaixam, fluxo de uma tarefa, decisoes de projeto e o que foi descartado |
| [docs/02-AGENTES.md](docs/02-AGENTES.md) | Os 30 agentes, o que cada um faz, quando aciona, e como criar o seu |
| [docs/03-SKILLS.md](docs/03-SKILLS.md) | O que e uma skill, como o modelo escolhe, anatomia de um SKILL.md |
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
  gateway de pagamento e marketplace especificos. Nao servem para voce e carregariam dado de
  terceiro. Ficou de fora; entrou a **estrutura** e exemplos neutros que mostram o padrao.
- **Segredo de qualquer tipo.** Nenhuma chave, token ou senha. O sistema referencia credencial pelo
  **nome da variavel**, nunca pelo valor.
- **Endereco de infraestrutura.** Sem IP, sem dominio proprio, sem nome de container, sem caminho
  pessoal de maquina. Onde havia um, entrou um marcador tipo `<SEU_CAMINHO>`.
- **A memoria acumulada.** Memoria e da operacao que a gerou. O modelo traz o **mecanismo**, vazio,
  pronto para voce encher com a sua.

---

## Contribuindo

Leia [CONTRIBUTING.md](CONTRIBUTING.md). Resumo: issue antes de pull request grande, portugues do
Brasil na documentacao, nenhum dado real de ninguem em exemplo.

**Achou vulnerabilidade?** Veja [SECURITY.md](SECURITY.md) para reporte responsavel.

---

## Licenca

[MIT](LICENSE) (c) 2026 [Gian Marco Menegussi Scaglianti](https://github.com/simtransforma)

---

## Referencias e credito de origem

Quase nada aqui foi inventado do zero. O original e a **costura**: juntar as pecas abaixo num
sistema unico com travas de verdade. Lista completa, com o que veio de cada uma:
[docs/08-REFERENCIAS.md](docs/08-REFERENCIAS.md).

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
| **superpowers** | Brainstorming, escrita de plano, desenvolvimento orientado a subagente, depuracao sistematica, verificacao antes de concluir | [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| **claude-mem** | A camada de memoria de sessao e a captura automatica ao fim da sessao | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) |
| **Obsidian** | O espelho legivel da memoria duravel, em markdown com links entre notas | [obsidian.md](https://obsidian.md) |
| **gitleaks** | A varredura de segredo que roda antes de commit e no historico | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| **OWASP Top 10** | O checklist de auditoria do agente de seguranca | [owasp.org](https://owasp.org/www-project-top-ten/) |
| **BMAD Method** | Papeis de agente com portao de aprovacao entre fases, que inspirou o Rito | [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) |
| **AIOS** | O vocabulario de sistema operacional de agentes: escalonador, kernel, camada de memoria | [agiresearch/AIOS](https://github.com/agiresearch/AIOS) |
| **Test Driven Development** (Kent Beck) | O ciclo vermelho, verde, refatora, adaptado para trabalho de agente | [Livro](https://www.oreilly.com/library/view/test-driven-development/0321146530/) |
| **Conventional Commits** | O padrao de mensagem de commit do fechamento | [conventionalcommits.org](https://www.conventionalcommits.org) |

### O que nasceu de incidente proprio

Regras que nao vieram de livro, vieram de coisa que deu errado. Estao aqui sem o contexto da
operacao que as gerou, porque o aprendizado vale e o dado nao e seu.

| Regra | Incidente que a gerou |
|---|---|
| **"nao achei em X" nunca e "nao existe"** | Um agente olhou uma unica listagem de containers, nao achou um servico e declarou que ele nao existia. O servico existia, instalado no host, fora do alcance daquele comando |
| **Redigir segredo antes de escrever em disco** | Um hook de seguranca registrava a linha de comando completa que bloqueava. Comando com header de autenticacao virou chave em texto claro no log. A correcao foi redigir antes da escrita, nunca depois |
| **Portao anti-desistencia** | Um agente declarou "nao tenho acesso" depois de procurar credencial em um unico lugar. O acesso existia, documentado numa skill que ele nunca leu. Virou regra: esgotar quatro fontes antes de dizer que esta bloqueado |
| **O orquestrador nao executa** | A trava foi desligada por conveniencia. Em pouco mais de um mes o orquestrador tinha construido um projeto inteiro sozinho, sem revisao e sem delegar. Foi religada e nunca mais desligada |
| **Dono unico de arquivo por onda** | Tres agentes commitando no mesmo repositorio em paralelo causaram corrida de indice no git. Virou regra: um dono por arquivo, no maximo tres agentes por onda |
| **Nome de variavel, nunca valor** | Segredo apareceu em relatorio de diagnostico. Virou regra absoluta: cita-se o nome da variavel, o valor nunca sai |
| **Placeholder de redacao tem que ser burro** | Um marcador de redacao criativo, longo e com hash, foi lido pelo proprio detector de segredo como string de alta entropia. O remedio virou o problema. Placeholder passou a ser minusculo e obvio |

---

<div align="center">

**Construido com agentes, para agentes.**

[Instalacao](#instalacao-em-5-passos) - [Documentacao](#documentacao-por-camada) - [Issues](https://github.com/simtransforma/HAOS-CC-Model/issues) - [Contribuindo](CONTRIBUTING.md)

**Criado por** [Gian Marco Menegussi Scaglianti](https://github.com/simtransforma) / HAU Solucoes Digitais

</div>
