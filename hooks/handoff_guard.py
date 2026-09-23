#!/usr/bin/env python3
"""
handoff-guard - PreToolUse hook (Claude Code) para a ferramenta de spawn de
sub-agente (Agent / Task).

== Problema que este hook existe para resolver ==
O orquestrador delega certo, mas COMPRIME a saida de um agente antes de
passar pro proximo. Caso real do sistema de origem: um agente de design
produziu uma spec visual pixel a pixel de uma peca de campanha e o
orquestrador briefou o dev com "preto e dourado". O dev inventou o resto. A
squad produziu; o orquestrador nao conectou a saida de um na entrada do
outro. Resultado indistinguivel de nao ter chamado especialista.

Mecanismo correto (skill `haos-handoff-artefato`): a saida do agente A vai
pro DISCO em `workspace/_handoff/<AAAAMMDD>-<slug>/NN-<agente>-<tipo>.md` e
o agente B recebe o CAMINHO com ordem de ler o arquivo inteiro, nunca o
resumo do orquestrador.

== Regra unica, stateless ==
Se o campo `prompt` do spawn casa com PALAVRA DE ARTEFATO (spec, design,
copy, layout, criativo, wireframe, mockup, landing, LP, arte, KV) E com
VERBO DE PRODUCAO (criar, escrever, montar, construir, implementar, aplicar,
gerar, redesenhar, refazer), entao o prompt precisa conter pelo menos UM
caminho de arquivo (path Windows, path POSIX, ou nome de arquivo com
extensao). Sem caminho nenhum = veredito DENY.

Token de escape: `[HANDOFF: N-A]` em qualquer lugar do prompt libera direto
(tarefa de agente unico, sem encadeamento).

== Estado de rollout recomendado ==
Comece com `ENFORCE_DEFAULT = False` (modo LOG: so registra o veredito que
TERIA dado). Calibre sobre o historico real de spawns do seu proprio uso
antes de ligar o enforce — e assim que este hook nasceu: rodado em modo LOG
sobre centenas de spawns reais antes de travar de verdade. Ligar o enforce e
decisao de quem opera o sistema, nao do agente.
Override por env var: HAOS_HANDOFF_ENFORCE=1/0.

== Contrato com o Claude Code ==
- Payload PreToolUse chega por stdin em JSON.
- Permitir = exit 0 sem output. Negar = stdout JSON permissionDecision=deny.
- Fail-open em JSON invalido/payload inesperado: nunca trava a sessao.
- Nome da ferramenta: o matcher registrado no settings.json e `Agent|Task`
  (o bundle do Claude Code mapeia Task -> Agent internamente; o hook aceita
  os dois nomes).

Referencia: https://docs.claude.com/en/docs/claude-code/hooks
"""
import sys, json, os, datetime, re, unicodedata

# === REDACAO DE SEGREDO ANTES DA ESCRITA EM DISCO ===
# Este guard grava no log os primeiros 200 chars do PROMPT do sub-agente, que
# pode conter credencial colada no briefing. Mesmo tratamento do main_guard:
# redacao dentro de _log(), antes do write. Import fail-closed.
try:
    from redact import redact as _redact
except Exception:  # pragma: no cover
    def _redact(text):
        return "[REDACTED-MODULO-AUSENTE]"


# MODO LOG deliberado por padrao. Ligar o enforce e decisao explicita do
# dono do sistema, depois de olhar o log por um tempo.
ENFORCE_DEFAULT = False
_env = os.environ.get("HAOS_HANDOFF_ENFORCE")
ENFORCE = (_env == "1") if _env is not None else ENFORCE_DEFAULT

# Sem escopo por cwd: vale em qualquer pasta. Sem arquivo de bypass: o unico
# interruptor e HAOS_HANDOFF_ENFORCE, que so voce define no ambiente.

SPAWN_TOOLS = {"Agent", "Task"}

_HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(
    (os.environ.get("HAOS_GUARD_LOG_DIR") or "").strip() or _HERE, "handoff_guard.log")

LOG_MAX_BYTES = 2 * 1024 * 1024

DENY_REASON = (
    "HANDOFF POR ARTEFATO: este spawn produz ou consome spec/design/copy e o prompt\n"
    "nao aponta nenhum arquivo. E assim que um handoff morre: a spec existe, o\n"
    "proximo agente recebe so um resumo de duas palavras.\n"
    "Corrija: grave a saida do produtor em workspace/_handoff/<data>-<slug>/ e passe\n"
    "o CAMINHO no prompt do consumidor, com ordem de ler o arquivo inteiro.\n"
    "Skill: haos-handoff-artefato.\n"
    "Tarefa de agente unico, sem encadeamento? Escreva no prompt: [HANDOFF: N-A]"
)

# ---------------------------------------------------------------------------
# Regra
# ---------------------------------------------------------------------------

# Palavras de artefato. \b em volta para nao casar dentro de outra palavra
# (ex.: "arte" NAO casa em "artefato"/"partes").
ARTIFACT_RE = re.compile(
    r"\b("
    r"spec|specs|"
    r"design|designs|"
    r"copy|copies|"
    r"layout|layouts|"
    r"criativo|criativos|criativa|criativas|"
    r"wireframe|wireframes|"
    r"mockup|mockups|"
    r"landing|"
    r"lp|lps|"
    r"arte|artes|"
    r"kv|kvs"
    r")\b",
    re.IGNORECASE,
)

# Verbos de producao.
#
# PEGADINHA: stem curto + `\w*` ora fica CEGO ora fica GULOSO em portugues.
#   - Cego: "aplic\w*" nao casa "aplique" (troca c->qu); "cri[ae]r?" casa "crie"
#     mas nao "criem" (o \b final bate no "m").
#   - Guloso: "cri\w*" casaria "crise", "crime", "criterio", "crianca".
# Solucao: terminacoes EXPLICITAS por verbo (infinitivo, imperativo singular e
# plural, gerundio e o substantivo de acao quando ele e usado como pedido).
VERB_RE = re.compile(
    r"\b("
    r"cri(?:ar|e|em|a|am|ando|acao|açao)|criação|"
    r"escrev(?:er|a|am|endo)|escrita|"
    r"mont(?:ar|e|em|a|am|ando|agem)|"
    r"constr(?:uir|ua|uam|oi|uindo|ucao|ução)|construção|"
    r"implement(?:ar|e|em|a|am|ando|acao|ação)|"
    r"aplic(?:ar|a|am|ando|acao|ação)|apliqu(?:e|em)|"
    r"ger(?:ar|e|em|a|am|ando|acao|ação)|"
    r"redesenh(?:ar|e|em|a|am|ando|o)|"
    r"refaz(?:er|em)?|refa(?:ca|ça|cam|çam)|refeit[oa]s?|refacao|refação"
    r")\b",
    re.IGNORECASE,
)

# Token de escape, tolerante a espacamento e caixa.
ESCAPE_RE = re.compile(r"\[\s*handoff\s*:\s*n\s*-?\s*a\s*\]", re.IGNORECASE)

# Caminhos de arquivo.
# 1) Windows: C:\... ou C:/...
PATH_WIN_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|]+")
# 2) POSIX absoluto: /opt/algo/x  (exige pelo menos dois niveis)
PATH_POSIX_RE = re.compile(r"(?:^|[\s\"'(=])/(?:[\w.\-]+/)+[\w.\-]+")
# 3) Relativo com separador: workspace/_handoff/x  ou  workspace\_handoff\x
PATH_REL_RE = re.compile(r"\b[\w.\-]+[\\/](?:[\w.\-]+[\\/])*[\w.\-]+\b")
# 4) Nome de arquivo com extensao conhecida.
PATH_FILE_RE = re.compile(
    r"\b[\w.\-]+\.(?:md|markdown|txt|json|ya?ml|csv|tsv|sql|py|js|mjs|cjs|ts|tsx|jsx|"
    r"html|htm|css|scss|pdf|png|jpe?g|gif|svg|webp|sh|ps1|bat|env|ini|toml|xml|log|"
    r"docx?|xlsx?|pptx?|fig|psd|ai)\b",
    re.IGNORECASE,
)


def _has_file_path(prompt: str) -> bool:
    """True se o prompt aponta algum arquivo/caminho.

    Deliberadamente PERMISSIVO: falso positivo aqui = liberar um spawn que
    talvez devesse ser barrado (sub-bloqueio). Falso negativo = barrar
    trabalho legitimo. Para um gate novo, sub-bloquear e o erro barato.
    """
    if not prompt:
        return False
    for rx in (PATH_WIN_RE, PATH_POSIX_RE, PATH_REL_RE, PATH_FILE_RE):
        try:
            if rx.search(prompt):
                return True
        except Exception:
            continue
    return False


def _fold(text: str) -> str:
    """Tira acento (NFKD + remove marcas de combinacao).

    PEGADINHA REAL: o payload chega em UTF-8, mas se o stdin for decodificado
    com a codepage do console do Windows em vez de UTF-8 explicito, acento
    vira mojibake ("soluÃ§Ãµes") e QUALQUER regex com acento erra o alvo em
    silencio — o gate ficaria cego justamente nos prompts com acentuacao.
    Duas defesas: (1) ler o stdin como BYTES e decodificar UTF-8 explicitamente
    (ver main()); (2) dobrar o texto para ASCII antes de casar, aqui.
    """
    try:
        return "".join(
            c for c in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(c)
        )
    except Exception:
        return text


def evaluate(prompt: str):
    """Retorna (veredito, motivo_curto). Veredito: ALLOW | DENY.

    Funcao pura, sem I/O: e isso que o selftest exercita.
    """
    p = _fold(prompt or "")
    if ESCAPE_RE.search(p):
        return "ALLOW", "escape_token"
    has_artifact = bool(ARTIFACT_RE.search(p))
    has_verb = bool(VERB_RE.search(p))
    if not (has_artifact and has_verb):
        return "ALLOW", "fora_do_gatilho(artefato=%s,verbo=%s)" % (has_artifact, has_verb)
    if _has_file_path(p):
        return "ALLOW", "aponta_arquivo"
    return "DENY", "artefato+verbo_sem_caminho"


# ---------------------------------------------------------------------------
# Plumbing (molde: main_guard.py)
# ---------------------------------------------------------------------------

def _allow():
    sys.exit(0)


def _deny(reason: str):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def _rotate_log_if_needed():
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > LOG_MAX_BYTES:
            old = LOG_PATH + ".old"
            if os.path.exists(old):
                os.remove(old)
            os.rename(LOG_PATH, old)
    except Exception:
        pass


def _log(line: str):
    try:
        line = _redact(line)
        _rotate_log_if_needed()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def main():
    try:
        # Le como BYTES e decodifica UTF-8 explicitamente: no Windows,
        # sys.stdin.read() usa a codepage do console e transforma acento em
        # mojibake (ver _fold). Fallback para sys.stdin se buffer nao existir.
        try:
            raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        except Exception:
            raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        # Fail-open: payload ilegivel nunca trava a sessao.
        _allow()
        return

    if not isinstance(data, dict):
        _allow()
        return

    tool = data.get("tool_name") or ""
    if tool not in SPAWN_TOOLS:
        _allow()
        return

    ti = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    prompt = ti.get("prompt")
    if not isinstance(prompt, str):
        prompt = ""
    subagent = str(ti.get("subagent_type") or "")

    agent_id_raw = data.get("agent_id")
    origin = ("SUBAGENT:" + str(agent_id_raw).strip()) if (
        agent_id_raw is not None and str(agent_id_raw).strip() != ""
    ) else "MAIN"

    try:
        verdict, why = evaluate(prompt)
    except Exception as e:
        verdict, why = "ALLOW", "erro_na_regra:%s" % type(e).__name__

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Redigir ANTES de truncar, nunca depois: se o corte em 200 chars cair no
    # meio de um valor de credencial, a aspa fica orfa e o padrao de redacao
    # deixa de casar. Texto ja redigido pode ser cortado a vontade.
    flat = _redact(" ".join(str(prompt).split()))[:200]
    _log(
        "%s | mode=%s | origin=%s | tool=%s | "
        "verdict=%s | why=%s | subagent=%s | prompt=%s"
        % (ts, "ENFORCE" if ENFORCE else "LOG", origin, tool,
           verdict, why, subagent, flat)
    )

    if verdict == "DENY" and ENFORCE:
        _deny(DENY_REASON)
        return
    _allow()


if __name__ == "__main__":
    main()
