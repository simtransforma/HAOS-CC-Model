#!/usr/bin/env python3
"""
anti-desistencia - PreToolUse hook (Claude Code) para o spawn de sub-agente
(Agent / Task). INJETOR, nao bloqueador.

== Problema que resolve (caso real do sistema de origem) ==
Um sub-agente precisava publicar um arquivo numa nuvem de terceiro. Procurou
credencial em UM lugar, nao achou, e declarou "nao tenho acesso". Estava
ERRADO: o acesso existia por API e estava documentado numa skill que ele
nunca leu. O operador corrigiu na mao.

Causa estrutural: gates injetados via `additionalContext` do evento
`UserPromptSubmit` SO disparam em mensagem do usuario humano. Sub-agente
nunca recebe. Somado ao fato de que um sub-agente tem MENOS fontes que o
orquestrador (sem MCP, sem base vetorial), ele fica sem nenhuma regra
mandando esgotar o que resta antes de desistir. Este hook fecha esse buraco:
prefixa um gate de "esgote antes de desistir" no proprio `prompt` do
sub-agente, via `hookSpecificOutput.updatedInput`.

== FAIL-OPEN (decisao consciente, o OPOSTO do main_guard) ==
Este hook roda em TODO spawn de agente. main_guard e fail-CLOSED porque e
guard de seguranca: na duvida, bloqueia. Aqui e o contrario: se QUALQUER
coisa der errado (stdin malformado, campo ausente, prompt nao-string,
excecao inesperada), o hook devolve saida NEUTRA e deixa o spawn passar
INTACTO. Um bug aqui NAO pode impedir o sistema de spawnar agentes. Nada
neste arquivo pode gerar `permissionDecision: deny`.

== Garantias ==
- Nunca destroi o prompt original: injeta BLOCO + "\n\n" + prompt completo.
- Se `prompt` ausente ou nao-string: nao mexe (saida neutra).
- Idempotente: se o MARCADOR ja estiver no prompt (re-spawn, ou o
  orquestrador ja incluiu o texto), nao injeta de novo.
- tool_name fora de {Agent, Task}: nao mexe.
- Vale em qualquer pasta (sem escopo por cwd) e nao tem arquivo de bypass.

== Extensao: gate de dominio (opcional) ==
O sistema de origem usa este mesmo hook para injetar TAMBEM um segundo bloco
com o "guia mestre" de um dominio de negocio sensivel (ex.: um playbook
operacional que so quem opera aquele negocio tem). Esse segundo bloco foi
removido deste modelo publico de proposito — ele carregava nome de
fornecedor, cidade de operacao e numero de caso real. O padrao fica
documentado abaixo em `DOMINIO_BLOCO` como esqueleto vazio: se voce tem um
playbook interno que um sub-agente PRECISA ler antes de agir em determinado
assunto, e aqui que voce prefixa isso.

Referencia: https://docs.claude.com/en/docs/claude-code/hooks
"""
import sys, json, os, datetime

SPAWN_TOOLS = {"Agent", "Task"}

_HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(
    (os.environ.get("HAOS_GUARD_LOG_DIR") or "").strip() or _HERE, "antidesistencia.log")
LOG_MAX_BYTES = 2 * 1024 * 1024

# Redacao de segredo antes de escrever no log (mesmo padrao do handoff_guard).
try:
    from redact import redact as _redact
except Exception:  # pragma: no cover
    def _redact(text):
        return "[REDACTED-MODULO-AUSENTE]"

# Marcador de idempotencia. Tem que ser literal e unico; e por ele que o hook
# reconhece que o bloco ja esta no prompt.
MARKER = "GATE ANTI-DESISTENCIA (obrigatorio)"

# Onde mora a memoria eterna do seu sistema: variavel HAOS_MEMORY_DIR no
# bloco "env" do settings.json. Sem ela, o texto aponta a pasta de forma
# generica em vez de inventar um caminho.
MEMORY_DIR = ((os.environ.get("HAOS_MEMORY_DIR") or "").strip()
              or "a pasta de memoria do projeto (defina HAOS_MEMORY_DIR)")

# --- Gate de dominio opcional (ver docstring). Deixe DOMINIO_BLOCO = "" se
# voce nao tiver um playbook proprio para injetar. ---
DOMINIO_MARKER = "GATE DE DOMINIO (opcional)"
DOMINIO_BLOCO = ""  # ex.: "<seu bloco de playbook de dominio aqui>"

MARKER_BASE = (
    MARKER + ": antes de declarar BLOQUEADO, \"nao tenho acesso\", \"nao e possivel\","
    "\"nao existe\", \"nao consegui\" ou \"esta bloqueado\", voce DEVE esgotar nesta ordem: "
    "(1) memoria eterna em " + MEMORY_DIR + " (grep pelo tema e pelo nome do servico); "
    "(2) skills do projeto e skills privadas locais "
    "(a resposta MUITAS VEZES esta numa skill que voce ainda nao leu: procure pelo nome do "
    "servico, ex. o nome do sistema externo em questao); (3) credencial pelo NOME da variavel "
    "no seu arquivo de segredos (nunca conclua \"sem credencial\" sem procurar o nome certo la); "
    "(4) o codigo/servidor real por OUTRO caminho alem do primeiro que voce tentou. "
    "REGRA DURA: \"nao achei em X\" NUNCA e \"nao existe\"; uma amostra nao prova o todo. "
    "Se depois de esgotar ainda estiver bloqueado, reporte BLOQUEADO listando EXPLICITAMENTE "
    "o que voce tentou em CADA uma das 4 fontes. Desistir sem esgotar e falha de execucao, "
    "nao e resposta valida. "
    "LASTRO OBRIGATORIO NO RELATORIO: toda afirmacao de causa, estado ou mecanismo tem que sair "
    "com tag [verifiquei: <comando> -> <o que vi>]; o que for deducao, suposicao ou inferencia "
    "nao testada sai marcado como [hipotese] ou [a confirmar]. Afirmacao sem tag vira fato falso "
    "na mao de quem receber o relatorio."
)

BLOCO = (
    (DOMINIO_MARKER + ": " + DOMINIO_BLOCO + "\n\n" if DOMINIO_BLOCO else "")
    + MARKER_BASE
)


def _rotate_log_if_needed():
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > LOG_MAX_BYTES:
            old = LOG_PATH + ".old"
            if os.path.exists(old):
                os.remove(old)
            os.rename(LOG_PATH, old)
    except Exception:
        pass


def _log(line):
    try:
        line = _redact(line)
        _rotate_log_if_needed()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _emit(data):
    try:
        sys.stdout.buffer.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    except Exception:
        pass
    sys.exit(0)


def _neutro():
    """Saida neutra: deixa passar sem modificar nada. Este e o caminho de
    fail-open e tambem o caminho normal para tudo que nao e spawn no escopo."""
    _emit({"continue": True, "suppressOutput": True})


def inject(prompt):
    """Funcao pura de injecao. Retorna (novo_prompt, motivo).

    novo_prompt is None => nao mexer (o chamador emite saida neutra).
    """
    if not isinstance(prompt, str):
        return None, "prompt_ausente_ou_nao_string"
    if MARKER in prompt:
        return None, "ja_injetado"
    return BLOCO + "\n\n" + prompt, "injetado"


def main():
    try:
        try:
            raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        except Exception:
            raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        _neutro()
        return

    if not isinstance(data, dict):
        _neutro()
        return

    try:
        tool = data.get("tool_name") or ""
        if tool not in SPAWN_TOOLS:
            _neutro()
            return

        ti = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
        novo, motivo = inject(ti.get("prompt"))

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _log("%s | tool=%s | acao=%s | subagent=%s | len_orig=%s"
             % (ts, tool, motivo, str(ti.get("subagent_type") or ""),
                len(ti.get("prompt")) if isinstance(ti.get("prompt"), str) else "-"))

        if novo is None:
            _neutro()
            return

        # ATENCAO (bug real ja pego em spawn ao vivo): `updatedInput` SUBSTITUI
        # o tool_input inteiro, NAO faz merge de campos. Uma versao anterior
        # devolvia so {"prompt": novo} e o runtime perdia `description`,
        # `subagent_type` e `model`, quebrando TODO spawn de agente com
        # "The required parameter `description` is missing". Sempre devolver o
        # tool_input COMPLETO com apenas o prompt trocado.
        novo_input = dict(ti)
        novo_input["prompt"] = novo

        _emit({
            "continue": True,
            "suppressOutput": True,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": novo_input,
            },
        })
    except Exception as e:  # FAIL-OPEN absoluto
        _log("%s | EXCECAO_FAIL_OPEN=%s" % (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type(e).__name__))
        _neutro()


if __name__ == "__main__":
    main()
