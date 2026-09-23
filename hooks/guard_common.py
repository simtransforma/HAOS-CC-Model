#!/usr/bin/env python3
"""
guard_common.py - pecas compartilhadas pelos hooks de guarda.

Um lugar so para: perfil do projeto, leitura do payload, normalizacao de
caminho, caminhos protegidos, saida de DENY, log e a lista de modelos
validos. Os guards importam daqui; nada aqui decide sozinho.

== PERFIL (obrigatorio, e o unico ajuste da instalacao) ==
O perfil e a lista de RAIZES do(s) seu(s) projeto(s): caminhos absolutos.
Duas formas de preencher (vence a primeira que existir):
  1. Variavel de ambiente HAOS_GUARD_PROFILE, no bloco "env" do
     ~/.claude/settings.json. Varias raizes separadas por ";".
     Ex.: "HAOS_GUARD_PROFILE": "/home/ana/meu-projeto;/home/ana/outro"
     No Windows use barra normal: "C:/Users/ana/meu-projeto".
  2. A constante PROJECT_ROOTS logo abaixo.
Se a variavel existir mas estiver vazia, o perfil conta como NAO configurado
(ela nao cai para a constante).

Sem perfil, ou com qualquer marcador "<...>" de fabrica, o guard fica
FECHADO: bloqueia toda mutacao do orquestrador, em qualquer pasta, e a
mensagem de bloqueio diz como configurar. Nao existe "desligado ate
configurar".

O que o perfil muda: o guard vale em QUALQUER pasta (o cwd nunca desliga a
trava). O perfil diz onde fica o seu projeto; Edit/Write fora dele e
negado sempre, e o modo manutencao (ver main_guard.py) so libera escrita
dentro dele.
"""
import datetime
import json
import os
import posixpath
import re
import sys

# <AJUSTE> Raizes absolutas do(s) seu(s) projeto(s). Ou deixe como esta e use
# a variavel HAOS_GUARD_PROFILE (recomendado).
PROJECT_ROOTS = [
    "<seu-projeto>",
]

SETUP_HINT = (
    "Configure o perfil: no ~/.claude/settings.json, bloco \"env\", defina "
    "\"HAOS_GUARD_PROFILE\": \"<caminho absoluto do seu projeto>\" (varias raizes "
    "separadas por ';', barra normal '/' tambem no Windows), ou preencha "
    "PROJECT_ROOTS em hooks/guard_common.py. Depois rode: python hooks/selftest.py"
)

HERE = os.path.dirname(os.path.abspath(__file__))

# Arquivos que sao a propria trava. Protegidos por NOME em qualquer pasta, e
# a pasta deste modulo inteira tambem (inclui logs e qualquer arquivo novo).
GUARD_FILENAMES = (
    "main_guard.py", "model_guard.py", "handoff_guard.py", "antidesistencia.py",
    "redact.py", "guard_common.py", "selftest.py", "hooks.json",
)

# --------------------------------------------------------------------------
# Modelos validos para spawn de sub-agente (model_guard.py). UNICO lugar.
# Aceita o tier (alias do Claude Code), o alias com janela longa ("opus[1m]")
# e o nome completo ("claude-opus-5-5", "claude-sonnet-4-5-20250929",
# "claude-opus-5-5[1m]"). "inherit" NAO vale: a ideia e escolher o tier de
# proposito. Para aceitar um tier novo, acrescente-o em MODEL_TIERS.
# --------------------------------------------------------------------------
MODEL_TIERS = ("haiku", "sonnet", "opus", "fable")
_TIER_ALT = "|".join(MODEL_TIERS)
_MODEL_RE = re.compile(
    r"^(?:(?:" + _TIER_ALT + r")|claude-(?:" + _TIER_ALT + r")-[0-9][0-9a-z.\-]*)(?:\[1m\])?$"
)


def is_valid_model(value):
    if not isinstance(value, str):
        return False
    return bool(_MODEL_RE.match(value.strip().lower()))


# --------------------------------------------------------------------------
# Caminhos
# --------------------------------------------------------------------------

def norm_path(p, base=None):
    """Caminho em forma canonica para comparacao: barras '/', minusculo,
    '..' resolvido, '/c/x' do Git Bash vira 'c:/x', '~' expandido. Relativo
    e resolvido contra `base` (o cwd do payload)."""
    if not isinstance(p, str):
        raise TypeError("caminho nao-string")
    s = p.strip().replace("\\", "/")
    if s.startswith("~"):
        s = os.path.expanduser(s).replace("\\", "/")
    m = re.match(r"^/([a-zA-Z])(/|$)", s)
    if m and os.name == "nt":
        s = m.group(1) + ":/" + s[3:]
    absolute = s.startswith("/") or re.match(r"^[a-zA-Z]:/", s) is not None
    if not absolute and base:
        s = norm_path(base) + "/" + s
    drive = ""
    m = re.match(r"^([a-zA-Z]:)(/.*)?$", s)
    if m:
        drive, s = m.group(1), (m.group(2) or "/")
    s = posixpath.normpath(s) if s else s
    if s == ".":
        s = ""
    return (drive + s).lower().rstrip("/") or "/"


def real_norm_path(p, cwd):
    """Mesmo caminho com symlink resolvido (os.path.realpath), normalizado.
    None se nao der para resolver. Um link dentro do projeto que aponta para
    um arquivo protegido nao pode servir de atalho."""
    try:
        s = os.path.expanduser(p.strip())
        if not os.path.isabs(s) and isinstance(cwd, str) and cwd:
            s = os.path.join(cwd, s)
        return norm_path(os.path.realpath(s))
    except Exception:
        return None


def is_placeholder(value):
    return "<" in value or ">" in value


def load_profile():
    """Devolve (raizes_normalizadas, estado). estado == "ok" ou o motivo."""
    raw = os.environ.get("HAOS_GUARD_PROFILE")
    if raw is not None:
        items = [x.strip() for x in raw.split(";")]
        origem = "HAOS_GUARD_PROFILE"
    else:
        items = [x.strip() for x in PROJECT_ROOTS if isinstance(x, str)]
        origem = "PROJECT_ROOTS"
    items = [x for x in items if x]
    if not items:
        return [], "perfil vazio (%s)" % origem
    if any(is_placeholder(x) for x in items):
        return [], "perfil ainda com marcador de fabrica <...> (%s)" % origem
    roots = []
    for x in items:
        n = norm_path(x)
        if n in ("/", "") or re.match(r"^[a-z]:/?$", n):
            return [], "perfil com raiz de disco inteira (%s): escolha a pasta do projeto" % origem
        roots.append(n)
    return roots, "ok"


def path_in_roots(path_norm, roots):
    for r in roots:
        if path_norm == r or path_norm.startswith(r + "/"):
            return True
    return False


def extra_protected():
    raw = os.environ.get("HAOS_GUARD_PROTECTED") or ""
    return [x.strip().replace("\\", "/").lower() for x in raw.split(";") if x.strip()]


def is_protected_path(path_norm):
    """Caminhos que o orquestrador NUNCA edita, nem em manutencao."""
    parts = path_norm.split("/")
    base = parts[-1] if parts else ""
    if base in ("settings.json", "settings.local.json"):
        return True
    if ".git" in parts or ".githooks" in parts:
        return True
    if base in GUARD_FILENAMES or base.endswith("_bypass"):
        return True
    here = norm_path(HERE)
    if path_norm == here or path_norm.startswith(here + "/"):
        return True
    if "/.claude/hooks/" in path_norm + "/":
        return True
    for s in extra_protected():
        if s in path_norm:
            return True
    return False


def text_touches_protected(text):
    """Checagem TEXTUAL para Bash, so usada no modo manutencao. E melhor
    esforco: texto nao prova o que o shell vai tocar (variavel montada em
    tempo de execucao escapa). A protecao forte de caminho e a de Edit/Write.
    Aspas e barra invertida sao removidas antes, para '.cl""aude' nao passar."""
    t = re.sub(r"[\"'\\]", "", text).lower()
    needles = ["settings.json", "settings.local.json", ".git", ".claude",
               "_bypass", norm_path(HERE)]
    needles += list(GUARD_FILENAMES) + extra_protected()
    return any(n in t for n in needles)


# --------------------------------------------------------------------------
# Payload, saida e log
# --------------------------------------------------------------------------

class InvalidPayload(Exception):
    pass


def read_payload():
    """Le o stdin e devolve um dict. Qualquer coisa fora disso levanta
    InvalidPayload (o guard decide o que fazer; os guards de seguranca negam)."""
    try:
        raw = sys.stdin.buffer.read()
    except Exception:
        raise InvalidPayload("stdin ilegivel")
    try:
        text = raw.decode("utf-8")
    except Exception:
        raise InvalidPayload("stdin nao e UTF-8")
    if not text.strip():
        raise InvalidPayload("payload vazio")
    try:
        data = json.loads(text)
    except Exception:
        raise InvalidPayload("JSON invalido")
    if not isinstance(data, dict):
        raise InvalidPayload("payload nao e objeto JSON")
    return data


def is_subagent(data):
    """Payload de sub-agente traz agent_id (texto nao-vazio). O do
    orquestrador nao traz. Qualquer outro tipo conta como orquestrador."""
    a = data.get("agent_id")
    return isinstance(a, str) and a.strip() != ""


def deny(reason):
    out = json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False)
    try:
        sys.stdout.buffer.write(out.encode("utf-8"))
        sys.stdout.flush()
    except Exception:
        pass
    sys.exit(0)


def allow():
    sys.exit(0)


def log_path(name):
    d = (os.environ.get("HAOS_GUARD_LOG_DIR") or "").strip() or HERE
    return os.path.join(d, name)


def write_log(name, line, redact_fn=None):
    try:
        if redact_fn is not None:
            line = redact_fn(line)
        p = log_path(name)
        if os.path.exists(p) and os.path.getsize(p) > 2 * 1024 * 1024:
            old = p + ".old"
            if os.path.exists(old):
                os.remove(old)
            os.rename(p, old)
        with open(p, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
