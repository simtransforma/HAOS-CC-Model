# Instalacao

Guia detalhado. Para a versao curta, veja os cinco passos no [README](README.md).

---

## 1. Pre requisitos

| Item | Versao minima | Como conferir |
|---|---|---|
| Claude Code | atual | `claude --version` |
| Python | 3.10 | `python --version` |
| Git | 2.30 | `git --version` |
| Shell | PowerShell 7 ou bash | |

Os hooks e o `hooks.json` deste pacote chamam o executor pelo nome `python` (nao `py -3`,
nao `python3`). Confirme que `python` responde na sua maquina (`python --version`); se so `python3`
ou o launcher `py` existirem, troque o comando nos arquivos que chamam hook (`settings.json` e/ou
`hooks.json`) antes de seguir.

---

## 2. Onde cada coisa vai

```
~/.claude/
  CLAUDE.md          <- a lei geral. Carregada em toda sessao, em qualquer pasta
  settings.json      <- liga os hooks e define as variaveis de ambiente
  agents/            <- os agentes
  skills/            <- as skills
  commands/          <- os comandos de atalho
  hooks/             <- os hooks e o autoteste
  projects/          <- a memoria, criada pelo proprio sistema. Nao versione
```

Regra que evita a maior dor de cabeca: **`~/.claude/projects/` nunca entra em repositorio publico**.
E onde a memoria mora, e memoria e da operacao, nao do modelo.

---

## 3. Passo a passo

### 3.1 Clone

```bash
git clone https://github.com/<SEU_USUARIO>/HAOS-CC-Model.git
cd HAOS-CC-Model
```

### 3.2 Faca backup do que voce ja tem

Se voce ja usa Claude Code, guarde o que existe antes de sobrescrever.

```bash
cp -r ~/.claude ~/.claude.backup.$(date +%Y%m%d)
```

### 3.3 Instale a lei

```bash
cp examples/CLAUDE.md.example ~/.claude/CLAUDE.md
```

Abra e edite. Procure por `<` e resolva cada marcador. Os obrigatorios sao poucos.

| Marcador | O que por |
|---|---|
| `<SEU_IDIOMA>` | O idioma em que o assistente deve responder (ex.: `portugues do Brasil`) |
| `<SEU_CAMINHO>` | A raiz absoluta onde `~/.claude` mora na sua maquina (usado em varios exemplos de caminho) |
| `<SEUS_CAMINHOS_PROTEGIDOS>` | Pastas ou arquivos que nunca podem ser mexidos sem OK explicito seu (segredo, config de producao, etc.) |
| `<SEU_NOME>` | Como o sistema deve te chamar |
| `<COMO_TE_CHAMAR>` | Pronome ou forma de tratamento, se for diferente do nome |
| `<SEU_FUSO>` | Seu fuso horario |
| `<DESCREVA:...>` | Instrucao livre indicada pelo proprio marcador; leia o texto ao redor dele antes de preencher |
| `<SUA_AREA>` / `<SEU_AGENTE>` | O dominio de trabalho e o agente responsavel por ele, se voce for adaptar o roteamento de delegacao |
| `<SEU_CAMINHO_DE_SEGREDOS>` | O caminho do arquivo onde suas variaveis de ambiente moram. **Esse arquivo fica fora do repositorio** |

Nao ha secao de servidor no `CLAUDE.md.example` atual: se o seu projeto nao opera servidor,
simplesmente nao adicione uma.

### 3.4 Instale agentes, skills e comandos

```bash
mkdir -p ~/.claude/agents ~/.claude/skills ~/.claude/commands
cp -r agents/.   ~/.claude/agents/
cp -r skills/.   ~/.claude/skills/
cp -r commands/. ~/.claude/commands/
```

### 3.5 Ligue os hooks

```bash
mkdir -p ~/.claude/hooks
cp -r hooks/. ~/.claude/hooks/
```

Se voce **nao tem** um `settings.json`:

```bash
cp examples/settings.json.example ~/.claude/settings.json
```

Se voce **ja tem**, nao sobrescreva. Abra os dois e funda apenas as chaves `hooks` e `env`.

> **Windows: nunca cole um caminho com barra invertida (`\`) dentro do JSON.** `"C:\Users\voce\..."`
> quebra o parser (`\U` e `\u` sao sequencias de escape validas em JSON e o resto nao e). Use barra
> normal mesmo em caminho local: `"C:/Users/voce/.claude"`. Se colar e o `settings.json` parar de
> carregar, esse e o primeiro suspeito.

### 3.6 Configure as variaveis

No bloco `env` do `settings.json`:

| Variavel | Para que |
|---|---|
| `HAOS_GUARD_PROFILE` | **Obrigatoria, e o unico ajuste que liga a trava de verdade.** Raiz(es) absoluta(s) do seu projeto, separadas por `;` se for mais de uma. Sem ela (ou com o marcador de fabrica `<seu-projeto>`), o guard fica FECHADO em qualquer pasta: bloqueia toda mutacao do orquestrador ate voce configurar. Nao existe "aberto por omissao" |
| `HAOS_HOME` | Onde mora a sua configuracao. So usada no texto do seu `CLAUDE.md`; nenhum hook le esta variavel |
| `HAOS_MEMORY_DIR` | Onde a memoria duravel e gravada. Lida por `antidesistencia.py`, `session_start.py` e `session_end.py`. O `<SEU_PROJETO>` dentro do caminho e o nome/slug do seu projeto, nao um marcador de outra tabela |
| `HAOS_SECRETS_FILE` | O **caminho** do seu arquivo de variaveis. Nunca o conteudo. So usada no texto do seu `CLAUDE.md`; nenhum hook le esta variavel |
| `HAOS_GUARD_PROTECTED` (opcional) | Caminhos extra que o guard nunca deixa o orquestrador editar, alem da lista fixa (`settings.json`, `.git/`, pasta dos hooks). Varias separadas por `;` |
| `HAOS_GUARD_LOG_DIR` (opcional) | Pasta onde `main_guard.py`, `model_guard.py`, `handoff_guard.py` e `antidesistencia.py` gravam log. Sem ela, cada um grava do lado do proprio arquivo `.py` |
| `HAOS_HANDOFF_ENFORCE` (opcional) | `0` ou `1`. Liga o bloqueio de `handoff_guard.py`; por padrao (`0`/ausente) ele so registra o veredito no log e nunca bloqueia — ver [docs/04-HOOKS.md](docs/04-HOOKS.md) |

Nenhuma delas guarda segredo. Elas guardam caminho.

> **Nunca coloque `HAOS_GUARD_MAINTENANCE` aqui.** Essa variavel liga o modo manutencao do
> `main_guard.py` (libera escrita do orquestrador dentro do perfil). Ela e definida **so no shell**
> da sessao de manutencao, nunca no `settings.json` — la ela viraria permanente e a trava de mutacao
> deixaria de valer para sempre.

### 3.7 Ajuste os guards (obrigatorio antes do selftest)

Os hooks `main_guard.py` e `model_guard.py` (os dois que decidem ALLOW/DENY de verdade)
compartilham o mesmo ponto de ajuste, centralizado em `hooks/guard_common.py` e marcado com
`<AJUSTE>`. `handoff_guard.py` e `antidesistencia.py` **nao** usam esse perfil — sao stateless em
relacao a projeto, controlados pelas proprias variaveis (`HAOS_HANDOFF_ENFORCE` e `HAOS_MEMORY_DIR`,
ver 3.6). Duas formas de preencher o perfil do guard principal, vale a primeira que existir:

1. Definir `HAOS_GUARD_PROFILE` no bloco `env` do `settings.json` (ver 3.6) — recomendado.
2. Editar a constante `PROJECT_ROOTS` em `hooks/guard_common.py` diretamente, trocando
   `"<seu-projeto>"` pela raiz absoluta real do seu projeto (barra normal, mesmo no Windows).

Sem um dos dois, o guard funciona (fica fechado, nao libera mutacao sem controle), mas ainda nao
protege o **seu** projeto especificamente: ele so nega tudo, em qualquer pasta, ate ser configurado.
O selftest (passo 4) falha explicitamente enquanto esse ajuste nao for feito, e a mensagem de erro
dele diz exatamente o que preencher.

---

## 4. Validacao

```bash
python ~/.claude/hooks/selftest.py
```

O autoteste **nao** confere versao de Python, presenca do CLAUDE.md, nem contagem de agentes ou
skills: ele confere se a trava de verdade esta ligada, em duas partes.

| Parte | O que confere | Resultado esperado |
|---|---|---|
| 1. Configuracao real | Se `HAOS_GUARD_PROFILE` (ou `PROJECT_ROOTS`) foi preenchido com uma raiz real, sem o marcador `<seu-projeto>` de fabrica | perfil configurado, contagem de raizes > 0 |
| 2. Bateria de vetores | Dezenas de casos contra `main_guard.py`, `model_guard.py` e `antidesistencia.py`: payload invalido, encadeamento (`&&`, `||`, quebra de linha, `$()`, crase, heredoc), redirecionamento e flags de escrita disfarcadas, git/gh/curl que mutam, tentativa de auto-desarme do guard, spawn de sub-agente sem tier de modelo, e leituras legitimas que **nao** podem ser bloqueadas | todo caso bate o esperado, nenhum vetor fura |

Se a parte 1 falhar (perfil nao configurado) ou qualquer caso da parte 2 nao bater, o script termina
com "a trava NAO esta confiavel" e sai com codigo de erro. So imprime "TUDO OK" quando as duas partes
passam de verdade.

> Se o autoteste apontar falha, o sistema esta instalado **aberto ou incompleto**. Isso e pior que
> nao ter instalado, porque voce vai confiar numa trava que nao existe. Pare, releia a mensagem de
> erro (ela diz o que falhou) e volte ao passo 3.7 antes de seguir.

### Teste manual

Abra uma sessao nova e peca algo destrutivo obviamente fora do permitido. A resposta certa e um
bloqueio com explicacao e com o caminho alternativo. Se o comando rodar, o hook nao esta ligado.

---

## 5. Diagnostico

| Sintoma | Causa provavel | O que fazer |
|---|---|---|
| Hook nao roda, nenhum efeito | Caminho errado no `settings.json` | Use caminho absoluto. Confira barra e maiusculas |
| "python nao encontrado" | Os hooks chamam o comando `python`; sua maquina so tem `python3` ou o launcher `py` | Troque `python` por `python3` (ou `py -3`) nos comandos de `settings.json`/`hooks.json` |
| A sessao trava alguns segundos a cada comando | Hook lento | Baixe o tempo limite e tire trabalho pesado do caminho critico |
| O guard bloqueia leitura inofensiva | Lista de leitura permitida curta demais | Adicione o comando a lista. **Nunca** afrouxe a trava de mutacao para resolver isso |
| A lei nao parece estar valendo | Arquivo no lugar errado | Ela tem que estar em `~/.claude/CLAUDE.md`, nao so na pasta do projeto |
| Skill nunca dispara | Descricao vaga | Reescreva com gatilhos literais, nas palavras que voce usa de verdade |
| Agente errado e chamado | Duas descricoes se sobrepoem | Adicione "quando **nao** usar" nas duas |

---

## 6. Desinstalar

**Nao apague as pastas inteiras.** `~/.claude/agents`, `~/.claude/skills`, `~/.claude/hooks` e
`~/.claude/commands` podem conter arquivos seus ou de outro pacote, de antes desta instalacao.
Remova so o que este pacote trouxe, usando a mesma lista de nomes de arquivo do passo 3.4/3.5 (os
mesmos que apareceram em `git ls-files agents skills commands hooks` no repo clonado):

```bash
# a partir da raiz do repo clonado (HAOS-CC-Model), NAO de ~/.claude
for f in agents/*.md; do rm -f "$HOME/.claude/agents/$(basename "$f")"; done
for d in skills/*/; do rm -rf "$HOME/.claude/skills/$(basename "$d")"; done
for f in commands/*.md; do rm -f "$HOME/.claude/commands/$(basename "$f")"; done
for f in hooks/*.py hooks/*.json; do rm -f "$HOME/.claude/hooks/$(basename "$f")"; done
mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.off
```

Se voce fez o backup do passo 3.2, a forma mais segura e restaurar so os itens que voce tinha antes
a partir de `~/.claude.backup.<data>`, em vez de apagar por nome.

E tire o bloco `hooks` do `settings.json` (nao o arquivo inteiro, se ele tinha outra coisa sua). A
sua memoria em `~/.claude/projects/` nao e tocada.

---

## 7. Adaptando ao seu contexto

Este modelo veio de uma operacao de marketing e tecnologia. Se o seu trabalho e outro, mexa nesta
ordem.

1. **Troque os agentes.** Os trinta aqui sao um ponto de partida. Apague os que nao servem e escreva
   os seus seguindo [docs/02-AGENTES.md](docs/02-AGENTES.md). Um agente que voce nunca chama e ruido.
2. **Esvazie as skills.** Comece com as de sistema e de metodo. Escreva as suas na terceira vez que
   explicar a mesma coisa.
3. **Mantenha os hooks.** Eles sao a parte agnostica. A trava, o roteador de modelo e a redacao de
   segredo servem a qualquer contexto.
4. **Adapte o Rito.** Treze fases vieram de projeto de lancamento. Se o seu fluxo tem cinco etapas,
   use cinco. O que importa e o portao bloqueante, nao o numero.
