# 04 Hooks

A camada que transforma regra em mecanismo. Se um hook responde bloqueio, a ferramenta nao roda.

Referencia oficial do mecanismo: [Hooks](https://docs.claude.com/en/docs/claude-code/hooks).

---

## 1. Como funciona

Um hook e um programa comum. O Claude Code chama ele num momento definido, manda um JSON pela entrada
padrao e le a resposta. O contrato e simples.

| Evento | Quando dispara | Pode bloquear? |
|---|---|---|
| `SessionStart` | Sessao abre, retoma ou e limpa | Nao. Injeta contexto |
| `UserPromptSubmit` | Voce envia uma mensagem | Sim. Pode injetar contexto tambem |
| `PreToolUse` | Antes de qualquer ferramenta rodar | **Sim. E aqui que mora a trava** |
| `PostToolUse` | Depois da ferramenta rodar | Nao. Serve para registro |
| `Stop` | Fim de turno do assistente | Nao. Serve para fechar e capturar |
| `PostCompact` | Depois de compactar o contexto | Nao. Serve para reinjetar o essencial |

O hook e selecionado por um `matcher`, que casa com o nome da ferramenta.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell|Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "python \"<SEU_CAMINHO>/.claude/hooks/main_guard.py\"", "timeout": 10 }
        ]
      }
    ]
  }
}
```

---

## 2. A Regra de Ouro, explicada

A pergunta que o orquestrador faz antes de agir nao e "posso usar essa ferramenta?". E:

> **"isso muda estado, apaga ou envia algo, ou e so leitura?"**

Leitura pura ele faz direto, em qualquer volume. Mutacao ele delega para um agente especialista. Isso
nao depende de ele lembrar: o guard bloqueia.

### O que passa

Leitura, local ou remota: listar, ler, contar, medir, procurar, ver estado de servico, ver historico
de versao, consultar com uma consulta somente de leitura, fazer uma requisicao de leitura.

Tambem passam formas compostas de leitura: entrar num diretorio e ler, encadear filtros de texto.
Envelopador de script (`python -c`, `python x.py`, `bash x.sh` etc.) fica fora da allowlist e e
negado sem ler o conteudo (ver decisao "Dois" abaixo), mesmo que o script em si so leia.

### O que nao passa, em nenhuma hipotese

| Categoria | Exemplos |
|---|---|
| **Caminho protegido** | Diretorio dos proprios hooks de guarda, arquivo de configuracao do sistema de hooks, ganchos de versionamento, e qualquer caminho extra que voce listar em `HAOS_GUARD_PROTECTED` (ex: a pasta de segredo do seu projeto - a lista fixa do pacote NAO inclui uma pasta de segredo por padrao, voce precisa declarar a sua) |
| **Script que envia ou emite** | Nao existe checagem por nome: qualquer envelopador de script (`python x.py`, `bash x.sh`, `-File y.ps1`, `npm run`...) fica fora da allowlist e e negado sem ler o conteudo, em qualquer pasta |
| **Envio externo** | Requisicao que escreve, cria ou apaga em servico de terceiro |
| **Destrutivo e infra** | Publicar no repositorio remoto, apagar, descartar mudanca local, matar processo, parar ou remover container, agendar tarefa, espelhar diretorio com remocao, esvaziar registro de sistema, escrever no banco |

### As tres decisoes de projeto que fazem isso funcionar

**Um. Comando encadeado e avaliado inteiro.** Se qualquer parte de uma cadeia sai da lista de leitura,
o comando todo e bloqueado. Nao existe contrabandear uma escrita depois de um `&&`.

**Dois. Envelopador opaco e bloqueado sem leitura.** Um comando do tipo "roda esse script" e bloqueado
por natureza, sem tentar interpretar o conteudo do script. Motivo: lista de proibicao baseada em texto
**falha aberta**, e falha aberta em seguranca nao e falha, e porta.

**Tres. O `cwd` nunca desliga a trava, em nenhuma pasta.** O guard vale em qualquer diretorio atual,
com ou sem perfil configurado. O que o perfil (variavel de ambiente `HAOS_GUARD_PROFILE` ou
`PROJECT_ROOTS` no codigo) decide e outra coisa: onde Edit/Write e a rotina de manutencao tem
permissao de ESCREVER. Esse escopo de escrita e resolvido pelo `file_path` do payload (relativo
resolvido contra o `cwd`, `..` resolvido, symlink seguido), nunca pelo diretorio atual da sessao.
Perfil vazio ou ainda com o marcador de fabrica falha fechado (nega toda mutacao com instrucao de
configuracao), nunca libera tudo em silencio.

### O regime

Este pacote traz um unico regime, sem variavel para trocar: **o orquestrador so le, toda mutacao vira
agente**. Quem decide se um caso e "trivial o suficiente" para o orquestrador fazer direto **nao e o
orquestrador**: e a allowlist de leitura do guard. Se voce quiser um regime intermediario (por exemplo
uma cota contavel de mutacao trivial fora de producao), isso e uma extensao que voce escreve por cima
deste guard, nao algo que vem pronto aqui.

---

## 3. Os hooks deste modelo

| Hook | Evento | O que faz | Por que existe |
|---|---|---|---|
| `main_guard.py` | PreToolUse | A trava principal. Bloqueia mutacao do orquestrador, avalia cadeia inteira, falha fechada | Sem ela o orquestrador vira executor solitario e a revisao some |
| `model_guard.py` | PreToolUse em criacao de agente | Bloqueia spawn que nao declara o nivel de modelo | Escolher modelo e a disciplina que primeiro se perde na pressa |
| `handoff_guard.py` | PreToolUse em criacao de agente | Exige que a entrega entre agentes passe por caminho de artefato, nao por resumo | Resumo intermediario perde detalhe e inventa consenso |
| `antidesistencia.py` | PreToolUse | Detecta a frase "nao e possivel" ou "nao existe" e cobra o esgotamento das fontes | Desistir cedo e o modo de falha mais caro que existe |
| `redact.py` | biblioteca | Redige segredo **antes** de escrever em log | Nasceu de um incidente: o proprio guard registrava a linha de comando completa e gravava chave em texto claro |
| `session_start.py` | SessionStart | Injeta estado, pendencia e alerta no comeco da sessao | Sessao que nasce sem contexto refaz trabalho |
| `session_end.py` | Stop | Captura o que aconteceu e alimenta a memoria | Aprendizado que nao e capturado no ato se perde |
| `post_compact.py` | PostCompact | Reinjeta o essencial depois da compactacao | Compactacao come regra junto com conversa |
| `prompt_router.py` | UserPromptSubmit | Reconhece prefixo de modo, avisa de rito ativo, injeta o que a tarefa exige | Roteamento manual nao escala |
| `selftest.py` | manual | Valida a instalacao e prova que o guard bloqueia | Instalacao silenciosamente aberta e pior que instalacao ausente |

---

## 4. Quatro licoes duras sobre hooks

**Uma. Falhe fechada.** Se o hook nao entendeu, ele bloqueia. Um guard que libera na duvida nao e um
guard, e um registro de acontecimentos.

**Duas. O hook nao pode editar a si mesmo.** O orquestrador nao tem permissao de escrever nos arquivos
de guarda nem no arquivo de configuracao que liga os hooks. Sem isso a trava se desarma sozinha no
primeiro pedido de conveniencia.

**Tres. Redija antes de escrever.** Se o hook registra o comando bloqueado, ele registra tambem o
cabecalho de autenticacao que vinha junto. Redija na hora de escrever, nunca depois. E preserve o
**nome** do campo, so tire o valor: saber que havia autenticacao ali importa para o diagnostico.

**Quatro. Mede antes de apertar.** Uma medicao dos bloqueios reais mostrou que quase 80 por cento eram
leitura pura barrada por **formato**, nao por risco. Guard que bloqueia leitura sem risco ensina a
pessoa a desligar o guard. A lista de leitura permitida foi afinada, e a trava de mutacao nao se
mexeu.

---

## 5. Escrevendo o seu hook

```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
args = data.get("tool_input", {}) or {}

if deve_bloquear(tool, args):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Explique o motivo E o caminho certo."
        }
    }))
    sys.exit(0)

sys.exit(0)   # silencio quer dizer liberado
```

Tres cuidados que economizam horas.

1. **A mensagem de bloqueio e documentacao.** Diga o motivo e diga o que fazer em vez disso. Bloqueio
   mudo faz o modelo tentar de novo do mesmo jeito.
2. **Respeite o tempo limite.** Hook lento trava toda a sessao. Dez segundos e generoso.
3. **Nunca escreva o argumento cru no log.** Use a redacao antes.
