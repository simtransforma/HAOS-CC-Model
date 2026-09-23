#!/usr/bin/env python3
"""
main-guard - PreToolUse hook (Claude Code).

Objetivo: o orquestrador (o "main" da sessao) so LE. Toda mutacao (escrever,
apagar, enviar, instalar, commitar) vira trabalho de um sub-agente,
lancado pela ferramenta Agent/Task. Sub-agentes nao passam por este guard.

Matcher no settings.json: Bash|PowerShell|Edit|Write|MultiEdit|NotebookEdit.

== Decisoes de projeto (cada uma fecha um furo real) ==
1. FAIL-CLOSED em tudo. Payload que nao e objeto JSON, JSON quebrado, null,
   campo com tipo errado, excecao inesperada: DENY com exit 0. Como o hook
   so e chamado para ferramentas de mutacao, negar no erro nao trava a
   sessao: so nega aquela chamada.
2. FECHADO ATE CONFIGURAR. Sem perfil (HAOS_GUARD_PROFILE ou PROJECT_ROOTS
   em guard_common.py), ou com marcador "<...>" de fabrica, toda mutacao e
   negada em qualquer pasta, com a instrucao de configuracao na mensagem.
   Leitura continua liberada.
3. O CWD NUNCA DESLIGA A TRAVA. O guard vale em qualquer pasta. O escopo de
   Edit/Write e resolvido pelo caminho do arquivo (relativo resolvido contra
   o cwd, '..' resolvido).
4. ALLOWLIST, NAO DENYLIST. Bash so passa se TODO segmento for leitura
   conhecida. O comando e partido em &&, ||, ;, |, &, quebra de linha. Fica
   negado de saida: $( ), crase, <( ), >( ), $'...', subshell ( ), aspas
   abertas, heredoc sem terminador, heredoc SEM aspas cujo corpo tenha
   substituicao (heredoc COM aspas: o corpo e dado e nao e analisado),
   redirect de escrita para arquivo (so /dev/null e duplicacao de descritor
   como 2>&1 passam), prefixo de ambiente perigoso (PATH=, LD_PRELOAD=...),
   binario chamado por caminho (./ls, /bin/rm). Wrapper opaco (python x.py,
   bash x.sh, -File y.ps1, npm run) fica fora da allowlist: e negado sem ler
   o script.
5. BINARIO DE LEITURA COM MODO DE ESCRITA E CHECADO POR FLAG: sed (-i, w, W,
   e, -f), awk (system, pipe, redirect, -f), sort (-o), uniq (2o arquivo),
   tree (-o, -R), find (-delete, -exec, -fprint...), git (subcomando e flag:
   config so le, branch/tag/stash/worktree/remote so listam, sem -c, sem
   --output, sem --upload-pack), gh (so subcomandos de leitura; api so GET
   sem -f/-F/--input), curl (so GET/HEAD, sem corpo, sem arquivo de saida,
   sem -K, sem @arquivo, so http/https), docker (so ps/logs/inspect/...),
   rg (--pre, --hostname-bin), printf (-v), date (-s), file (-C). Expansao
   que atribui variavel (${X:=v}) tambem e negada: variavel atribuida pode
   virar flag escondida do comando seguinte.
6. CAMINHO PROTEGIDO (settings.json, settings.local.json, .git/, .githooks/,
   a pasta destes hooks e os arquivos da trava por nome) e negado ANTES de
   qualquer outra regra, inclusive no modo manutencao.
7. SEM AUTO-DESARME. Nao existe arquivo de bypass: nenhum arquivo que o
   modelo consiga criar muda a decisao deste guard. O unico relaxamento e o
   MODO MANUTENCAO, pela variavel de ambiente HAOS_GUARD_MAINTENANCE=1,
   definida por voce no shell que abre o Claude Code, so na sessao de
   manutencao. Nunca coloque essa variavel no settings.json: la ela viraria
   permanente. Em manutencao, o orquestrador pode escrever DENTRO do perfil;
   caminho protegido e caminho fora do perfil continuam negados. Limite
   honesto: em manutencao o Bash e checado so por TEXTO (melhor esforco); a
   protecao forte de caminho, com '..' e symlink resolvidos, e a de Edit/Write.
8. LIMITE DO MODELO: um guard de leitura nao controla saida de dado por GET
   (ex.: curl de uma URL que carrega o valor de uma variavel de ambiente).
   Segredo nao deve morar em variavel de ambiente da sessao do orquestrador.

== Como distingue orquestrador de sub-agente ==
Payload de sub-agente traz `agent_id` (texto nao-vazio). O do orquestrador
nao traz. agent_id de outro tipo (numero, lista) conta como orquestrador.

== Contrato ==
Negar: stdout JSON com permissionDecision=deny, exit 0.
Permitir: exit 0 sem saida.
Referencia: https://docs.claude.com/en/docs/claude-code/hooks
"""
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import guard_common as gc
except Exception:  # sem o modulo comum nao ha como decidir: nega.
    sys.stdout.write('{"hookSpecificOutput": {"hookEventName": "PreToolUse", '
                     '"permissionDecision": "deny", "permissionDecisionReason": '
                     '"BLOQUEADO: guard_common.py ausente ou quebrado ao lado de main_guard.py."}}')
    sys.exit(0)

try:
    from redact import redact as _redact
except Exception:  # sem redacao, o log perde o texto em vez de vazar segredo
    def _redact(text):
        return "[REDACTED-MODULO-AUSENTE]"


BLOCKED_TOOLS = {"Bash", "PowerShell", "Edit", "Write", "NotebookEdit", "MultiEdit"}
FILE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
LOG_NAME = "main_guard.log"

DENY_REASON = (
    "BLOQUEADO: isso muda estado, apaga ou envia algo (ou nao foi possivel "
    "confirmar que e leitura pura). O orquestrador so le; mutacao e trabalho "
    "de um sub-agente especialista. Delegue via Agent/Task."
)


class _Unsafe(Exception):
    pass


# ---------------------------------------------------------------------------
# 1. Scanner de shell: parte o comando em segmentos e nega construcoes que
#    executam codigo escondido. Respeita aspas simples, duplas e escape.
# ---------------------------------------------------------------------------

def _check_param_expansion(cmd, i):
    """${X:=v}, ${X=v} atribuem variavel (e a variavel pode virar flag de um
    comando seguinte); ${X@P} expande prompt. Qualquer um desses = nega."""
    k = cmd.find("}", i)
    body = cmd[i + 2:] if k == -1 else cmd[i + 2:k]
    if "=" in body or "@P" in body or k == -1:
        raise _Unsafe("expansao de parametro que atribui ou executa (${...=...})")


_SAFE_REDIRECT_TARGETS = {"/dev/null", "/dev/stdout", "/dev/stderr", "nul"}
_WORD_STOP = " \t\n;&|<>()"


def _split_command(cmd):
    cmd = cmd.replace("\r\n", "\n").replace("\r", "\n")
    segs, buf = [], []
    i, n = 0, len(cmd)
    in_s = in_d = False
    heredocs = []  # (delimitador, com_aspas, tira_tab)

    def flush():
        s = "".join(buf).strip()
        if s:
            segs.append(s)
        del buf[:]

    while i < n:
        c = cmd[i]
        if in_s:
            buf.append(c)
            if c == "'":
                in_s = False
            i += 1
            continue
        if c == "\\":
            if i + 1 < n and cmd[i + 1] == "\n":  # continuacao de linha
                i += 2
                continue
            buf.append(cmd[i:i + 2])
            i += 2
            continue
        if cmd.startswith("${", i):
            _check_param_expansion(cmd, i)
        if in_d:
            if c == '"':
                in_d = False
            elif c == "`" or cmd.startswith("$(", i):
                raise _Unsafe("substituicao de comando dentro de aspas duplas")
            buf.append(c)
            i += 1
            continue
        # ---- fora de aspas ----
        if c == "'":
            in_s = True
            buf.append(c)
            i += 1
            continue
        if c == '"':
            in_d = True
            buf.append(c)
            i += 1
            continue
        if c == "`" or cmd.startswith("$(", i):
            raise _Unsafe("substituicao de comando ($( ) ou crase)")
        if cmd.startswith("$'", i):
            raise _Unsafe("aspas ANSI-C $'...'")
        if cmd.startswith("<(", i) or cmd.startswith(">(", i):
            raise _Unsafe("substituicao de processo <( ) ou >( )")
        if cmd.startswith("<<<", i):
            buf.append(" ")
            i += 3
            continue
        if cmd.startswith("<<", i):
            j = i + 2
            strip = False
            if j < n and cmd[j] == "-":
                strip, j = True, j + 1
            while j < n and cmd[j] in " \t":
                j += 1
            word, quoted = [], False
            while j < n and cmd[j] not in _WORD_STOP:
                ch = cmd[j]
                if ch in "'\"":
                    k = cmd.find(ch, j + 1)
                    if k == -1:
                        raise _Unsafe("heredoc com aspas abertas no delimitador")
                    word.append(cmd[j + 1:k])
                    quoted, j = True, k + 1
                    continue
                if ch == "\\" and j + 1 < n:
                    word.append(cmd[j + 1])
                    quoted, j = True, j + 2
                    continue
                word.append(ch)
                j += 1
            delim = "".join(word)
            if not delim:
                raise _Unsafe("heredoc sem delimitador")
            heredocs.append((delim, quoted, strip))
            buf.append(" ")
            i = j
            continue
        if cmd.startswith("<>", i):
            raise _Unsafe("redirect de leitura e escrita <>")
        if cmd.startswith("<&", i):
            buf.append(" ")
            i += 2
            continue
        if c == "<":
            buf.append(" ")
            i += 1
            continue
        if c == ">" or cmd.startswith("&>", i):
            amp_first = c == "&"
            j = i + 2 if amp_first else i + 1
            if j < n and cmd[j] == ">":
                j += 1
            if j < n and cmd[j] == "|":
                j += 1
            dup = False
            if not amp_first and j < n and cmd[j] == "&":
                dup, j = True, j + 1
            while j < n and cmd[j] in " \t":
                j += 1
            k = j
            while k < n and cmd[k] not in _WORD_STOP:
                k += 1
            target = cmd[j:k]
            if dup:
                if not re.fullmatch(r"\d+|-", target):
                    raise _Unsafe("redirect de escrita para arquivo (>&)")
            elif target.lower() not in _SAFE_REDIRECT_TARGETS:
                raise _Unsafe("redirect de escrita para arquivo (%s)" % (target or "vazio"))
            while buf and buf[-1].isdigit():  # descritor do redirect (2>...)
                buf.pop()
            buf.append(" ")
            i = k
            continue
        if cmd.startswith("&&", i) or cmd.startswith("||", i):
            flush()
            i += 2
            continue
        if c in ";|&":
            flush()
            i += 1
            continue
        if c in "()":
            raise _Unsafe("subshell ou agrupamento com parenteses")
        if c == "#" and not "".join(buf).strip(" \t") or (c == "#" and buf and buf[-1] in " \t"):
            k = cmd.find("\n", i)
            i = n if k == -1 else k
            continue
        if c == "\n":
            flush()
            i += 1
            for delim, quoted, strip in heredocs:
                found = False
                while i < n:
                    k = cmd.find("\n", i)
                    line = cmd[i:] if k == -1 else cmd[i:k]
                    i = n if k == -1 else k + 1
                    if (line.lstrip("\t") if strip else line) == delim:
                        found = True
                        break
                    if not quoted and ("`" in line or "$(" in line):
                        raise _Unsafe("heredoc sem aspas com substituicao de comando no corpo")
                if not found:
                    raise _Unsafe("heredoc sem terminador")
            heredocs = []
            continue
        buf.append(c)
        i += 1

    if in_s or in_d:
        raise _Unsafe("aspas abertas")
    if heredocs:
        raise _Unsafe("heredoc sem corpo")
    flush()
    return segs


# ---------------------------------------------------------------------------
# 2. Allowlist por binario, com checagem de flag onde o binario sabe escrever.
# ---------------------------------------------------------------------------

_SIMPLE_READ = {
    "ls", "cat", "head", "tail", "wc", "stat", "grep", "egrep", "fgrep", "df", "du",
    "free", "uptime", "whoami", "id", "uname", "echo", "ps", "pwd", "which",
    "cut", "tr", "jq", "true", "false", "diff", "basename", "dirname", "realpath",
    "readlink", "md5sum", "sha1sum", "sha256sum", "nproc", "cd",
}

_SAFE_ENV_PREFIX = re.compile(r"^(LC_[A-Z]+|LANG|LANGUAGE|TZ|NO_COLOR|TERM|COLUMNS|LINES)$")

# sed: script precisa casar com uma gramatica pequena e so de leitura.
_SED_ADDR = r"(?:\d+(?:~\d+)?|\$|/(?:[^/\\\n]|\\.)*/I?)"
_SED_RANGE = _SED_ADDR + r"(?:\s*,\s*(?:" + _SED_ADDR + r"|[+~]\d+))?"
_SED_SUBST = (r"s(?P<d>[^\w\s\\])(?:(?!(?P=d))[^\\\n]|\\.)*(?P=d)"
              r"(?:(?!(?P=d))[^\\\n]|\\.)*(?P=d)[gpiImM0-9]*")
_SED_ITEM = re.compile(r"\s*(?:" + _SED_RANGE + r")?\s*!?\s*(?:[pdqQ=nNlhHgGxz]|" + _SED_SUBST
                       + r")\s*(?:;|\n|$)")
_SED_LONG_OK = {"--quiet", "--silent", "--regexp-extended", "--posix", "--null-data",
                "--zero-terminated", "--unbuffered", "--debug", "--sandbox", "--separate"}


def _sed_script_ok(s):
    s = s.strip()
    if not s:
        return False
    pos = 0
    while pos < len(s):
        m = _SED_ITEM.match(s, pos)
        if not m or m.end() == pos:
            return False
        pos = m.end()
    return True


def _sed_ok(args):
    scripts, i = [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            if not scripts and i + 1 < len(args):
                scripts.append(args[i + 1])
            break
        if a.startswith("--"):
            if a in _SED_LONG_OK:
                i += 1
                continue
            if a.startswith("--expression="):
                scripts.append(a.split("=", 1)[1])
                i += 1
                continue
            if a == "--expression" and i + 1 < len(args):
                scripts.append(args[i + 1])
                i += 2
                continue
            return False  # --in-place, --file e o resto
        if a.startswith("-") and len(a) > 1:
            flags, k = a[1:], 0
            while k < len(flags):
                f = flags[k]
                if f in "nErzsu":
                    k += 1
                    continue
                if f == "e":
                    rest = flags[k + 1:]
                    if rest:
                        scripts.append(rest)
                    elif i + 1 < len(args):
                        scripts.append(args[i + 1])
                        i += 1
                    else:
                        return False
                    break
                return False  # -i, -f, -l e qualquer outra
            i += 1
            continue
        if not scripts:
            scripts.append(a)
        i += 1
    return bool(scripts) and all(_sed_script_ok(s) for s in scripts)


def _awk_ok(args):
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--":
            i += 1
            break
        if a in ("-F", "-v"):
            i += 2
            continue
        if a.startswith("-F") or a.startswith("-v"):
            i += 1
            continue
        if a.startswith("-"):
            return False  # -f arquivo, -i include, --exec...
        break
    if i >= len(args):
        return False
    return not re.search(r"system|[|>]|@", args[i])


def _sort_ok(args):
    for a in args:
        if a.startswith("--output") or a.startswith("--compress-program"):
            return False
        if a.startswith("-") and not a.startswith("--") and "o" in a[1:]:
            return False
    return True


def _uniq_ok(args):
    pos, i = 0, 0
    while i < len(args):
        a = args[i]
        if a in ("-f", "-s", "-w", "--skip-fields", "--skip-chars", "--check-chars"):
            i += 2
            continue
        if a.startswith("-") and a != "-":
            i += 1
            continue
        pos += 1
        i += 1
    return pos <= 1


def _tree_ok(args):
    return not any(a.startswith(("-o", "--output", "-R")) for a in args)


_FIND_DENY = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fls", "-fprint",
              "-fprint0", "-fprintf"}


def _find_ok(args):
    return not any(a in _FIND_DENY for a in args)


def _rg_ok(args):
    return not any(a.startswith(("--pre", "--hostname-bin")) for a in args)


def _printf_ok(args):
    # printf -v VAR atribui variavel, que depois pode virar flag de outro comando
    return not any(a.startswith("-v") for a in args)


def _date_ok(args):
    for a in args:
        if a.startswith("--set"):
            return False
        if a.startswith("-") and not a.startswith("--") and "s" in a[1:]:
            return False
    return True


def _file_ok(args):
    return not any(a in ("-C", "--compile") for a in args)


# git
_GIT_GLOBAL_OK = {"--no-pager", "-P", "--no-optional-locks"}
_GIT_SIMPLE_READ = {"status", "log", "show", "diff", "rev-parse", "ls-files", "rev-list",
                    "cat-file", "show-ref", "merge-base", "describe", "count-objects",
                    "ls-remote", "shortlog", "blame"}
_GIT_BAD_ARG_PREFIX = ("--output", "--upload-pack", "--receive-pack", "--exec",
                       "--open-files-in-pager", "--ext-diff")
_GIT_LIST_ARGFLAGS = ("--contains", "--no-contains", "--merged", "--no-merged",
                      "--points-at", "--sort", "--format")
_BRANCH_FLAGS = {"-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "--show-current",
                 "--no-color", "--color", "--no-column", "--column", "-i", "--ignore-case"}
_TAG_FLAGS = {"--no-column", "--column", "-i", "--ignore-case", "--no-color", "--color"}


def _git_listing_ok(rest, flags, extra_flag_re=None):
    listing, i = False, 0
    while i < len(rest):
        t = rest[i]
        if t in ("--list", "-l"):
            listing = True
            i += 1
            continue
        if t in flags or (extra_flag_re and re.fullmatch(extra_flag_re, t)):
            i += 1
            continue
        if t.startswith(tuple(f + "=" for f in _GIT_LIST_ARGFLAGS)):
            i += 1
            continue
        if t in _GIT_LIST_ARGFLAGS:
            i += 2
            continue
        if t.startswith("-") or not listing:
            return False
        i += 1
    return True


def _git_config_ok(rest):
    if not rest:
        return False
    if rest[0] in ("get", "list"):
        return True
    if rest[0] in ("set", "unset", "rename-section", "remove-section", "edit"):
        return False
    bad = {"--add", "--unset", "--unset-all", "--replace-all", "--rename-section",
           "--remove-section", "-e", "--edit"}
    good = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l",
            "--get-color", "--get-colorbool"}
    if any(t in bad for t in rest):
        return False
    return any(t in good for t in rest)


def _git_ok(args):
    i = 0
    while i < len(args) and args[i].startswith("-"):
        if args[i] in _GIT_GLOBAL_OK:
            i += 1
            continue
        if args[i] == "-C":
            i += 2
            continue
        return False  # -c, --exec-path, --git-dir...
    if i >= len(args):
        return False
    sub, rest = args[i], args[i + 1:]
    for t in rest:
        tl = t.lower()
        if tl.startswith(_GIT_BAD_ARG_PREFIX) or "ext::" in tl or tl.startswith("fd::"):
            return False
    if sub in _GIT_SIMPLE_READ:
        return True
    if sub == "config":
        return _git_config_ok(rest)
    if sub == "branch":
        return _git_listing_ok(rest, _BRANCH_FLAGS)
    if sub == "tag":
        return _git_listing_ok(rest, _TAG_FLAGS, r"-n\d*")
    if sub == "stash":
        return bool(rest) and rest[0] in ("list", "show")
    if sub == "worktree":
        return bool(rest) and rest[0] == "list"
    if sub == "remote":
        return not rest or rest == ["-v"] or rest == ["--verbose"] or rest[0] in ("show", "get-url")
    return False


# gh
_GH_READ = {("repo", "view"), ("repo", "list"), ("run", "list"), ("run", "view"),
            ("pr", "view"), ("pr", "list"), ("pr", "diff"), ("pr", "checks"), ("pr", "status"),
            ("issue", "view"), ("issue", "list"), ("issue", "status"), ("release", "list"),
            ("release", "view"), ("workflow", "list"), ("workflow", "view"), ("auth", "status")}


def _gh_api_ok(rest):
    i = 0
    while i < len(rest):
        t = rest[i]
        method = None
        if t in ("-X", "--method"):
            method = rest[i + 1] if i + 1 < len(rest) else ""
            i += 1
        elif t.startswith("--method="):
            method = t.split("=", 1)[1]
        elif t.startswith("-X"):
            method = t[2:]
        elif t.startswith(("-f", "-F", "--field", "--raw-field", "--input")):
            return False
        if method is not None and method.upper() not in ("GET", "HEAD"):
            return False
        i += 1
    return True


def _gh_ok(args):
    if not args:
        return False
    if args[0] == "api":
        return _gh_api_ok(args[1:])
    return len(args) >= 2 and (args[0], args[1]) in _GH_READ


# curl
_CURL_DENY_LONG = ("--data", "--json", "--form", "--upload-file", "--output", "--remote-name",
                   "--config", "--dump-header", "--cookie-jar", "--trace", "--libcurl",
                   "--stderr", "--create-dirs", "--output-dir", "--etag-save", "--hsts",
                   "--alt-svc", "--quote")
_CURL_SHORT_DENY = set("dFToOKDcQ")
_CURL_SHORT_ARG = set("AbCeEHhmPrtuUwxYyz")


def _curl_method_ok(m):
    return m.upper() in ("GET", "HEAD")


def _curl_ok(args):
    for a in args:
        if a.startswith("@") or ("=@" in a) or (a.startswith("-") and not a.startswith("--") and "@" in a):
            return False  # @arquivo: conteudo local vai para a rede
        m = re.match(r"^([A-Za-z][A-Za-z0-9+.\-]*)://", a)
        if m and m.group(1).lower() not in ("http", "https"):
            return False  # gopher, dict, telnet, ftp...: payload arbitrario
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            name, eq, val = a.partition("=")
            if name.startswith(_CURL_DENY_LONG):
                return False
            if name == "--request":
                m = val if eq else (args[i + 1] if i + 1 < len(args) else "")
                if not _curl_method_ok(m):
                    return False
                i += 1 if eq else 2
                continue
            i += 1
            continue
        if a.startswith("-") and len(a) > 1:
            flags, k = a[1:], 0
            while k < len(flags):
                f = flags[k]
                if f in _CURL_SHORT_DENY:
                    return False
                if f == "X":
                    m = flags[k + 1:]
                    if not m:
                        m = args[i + 1] if i + 1 < len(args) else ""
                        i += 1
                    if not _curl_method_ok(m):
                        return False
                    break
                if f in _CURL_SHORT_ARG:
                    if not flags[k + 1:]:
                        i += 1
                    break
                k += 1
            i += 1
            continue
        i += 1
    return True


def _docker_ok(args):
    return bool(args) and args[0] in ("ps", "logs", "inspect", "port", "images", "stats",
                                      "version", "info", "top")


_CHECKED = {
    "sed": _sed_ok, "awk": _awk_ok, "gawk": _awk_ok, "sort": _sort_ok, "uniq": _uniq_ok,
    "tree": _tree_ok, "find": _find_ok, "rg": _rg_ok, "printf": _printf_ok,
    "date": _date_ok, "file": _file_ok,
    "git": _git_ok, "gh": _gh_ok, "curl": _curl_ok, "docker": _docker_ok,
}


def _is_readonly_segment(seg):
    tokens = shlex.split(seg, posix=True)
    if not tokens:
        return True, ""
    while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
        name = tokens[0].split("=", 1)[0]
        if not _SAFE_ENV_PREFIX.match(name):
            return False, "prefixo de ambiente %s= muda o que o comando executa" % name
        tokens = tokens[1:]
    if not tokens:
        return True, ""
    binary = tokens[0]
    if "/" in binary or "\\" in binary:
        return False, "binario chamado por caminho (%s)" % binary
    if binary in _SIMPLE_READ:
        return True, ""
    check = _CHECKED.get(binary)
    if check is None:
        return False, "'%s' nao esta na allowlist de leitura" % binary
    if check(tokens[1:]):
        return True, ""
    return False, "'%s' com subcomando ou flag que escreve, envia ou executa" % binary


def classify_bash(cmd):
    """(True, "") se o comando inteiro e leitura pura; (False, motivo) se nao."""
    try:
        segs = _split_command(cmd)
        for s in segs:
            ok, why = _is_readonly_segment(s)
            if not ok:
                return False, why
        return True, ""
    except _Unsafe as e:
        return False, str(e)
    except Exception as e:  # erro de analise = mutacao
        return False, "comando nao analisavel (%s)" % type(e).__name__


# ---------------------------------------------------------------------------
# 3. Decisao
# ---------------------------------------------------------------------------

def _log(line):
    gc.write_log(LOG_NAME, "%s | %s" % (gc.now(), line), _redact)


def _deny(motivo, detalhe=""):
    _log("deny | %s | %s" % (motivo, detalhe[:300]))
    gc.deny(motivo)


def _decide(data):
    tool = data.get("tool_name")
    if not isinstance(tool, str):
        _deny("BLOQUEADO: payload invalido (tool_name ausente ou nao-texto).")
    if tool not in BLOCKED_TOOLS:
        gc.allow()
    if gc.is_subagent(data):
        gc.allow()

    cwd = data.get("cwd")
    if cwd is None or cwd == "":
        cwd = os.getcwd()
    if not isinstance(cwd, str):
        _deny("BLOQUEADO: payload invalido (cwd nao-texto).")
    ti = data.get("tool_input")
    if not isinstance(ti, dict):
        _deny("BLOQUEADO: payload invalido (tool_input nao e objeto).")

    roots, estado = gc.load_profile()
    configured = estado == "ok"
    maintenance = os.environ.get("HAOS_GUARD_MAINTENANCE") == "1"
    cwd_n = gc.norm_path(cwd)
    setup = "BLOQUEADO: guard sem perfil configurado (%s), entao toda mutacao fica fechada. %s" % (
        estado, gc.SETUP_HINT)

    if tool in FILE_TOOLS:
        fp = ti.get("notebook_path") if tool == "NotebookEdit" else None
        fp = fp if fp is not None else ti.get("file_path")
        if not isinstance(fp, str) or not fp.strip():
            _deny("BLOQUEADO: payload invalido (file_path ausente ou nao-texto).")
        fpn = gc.norm_path(fp, base=cwd_n)
        fpr = gc.real_norm_path(fp, cwd)  # segue symlink; None se nao resolver
        if gc.is_protected_path(fpn) or (fpr and gc.is_protected_path(fpr)):
            _deny("BLOQUEADO: caminho protegido (settings, .git, hooks da trava). "
                  "Nem o modo manutencao libera: edite voce mesmo, com revisao.", fpn)
        if not configured:
            _deny(setup, fpn)
        roots_all = roots + [r2 for r2 in (gc.real_norm_path(r, None) for r in roots) if r2]
        if not gc.path_in_roots(fpn, roots) or (fpr and not gc.path_in_roots(fpr, roots_all)):
            _deny("BLOQUEADO: arquivo fora do perfil do projeto (%s). O orquestrador nao "
                  "escreve fora das raizes em HAOS_GUARD_PROFILE." % fpn, fpn)
        if maintenance:
            _log("allow | manutencao | %s | %s" % (tool, fpn))
            gc.allow()
        _deny(DENY_REASON, fpn)

    cmd = ti.get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        _deny("BLOQUEADO: payload invalido (command ausente ou nao-texto).")

    if tool == "Bash":
        readonly, why = classify_bash(cmd)
        if readonly:
            gc.allow()
    else:  # PowerShell: sem allowlist de leitura neste modelo
        why = "PowerShell nao tem allowlist de leitura neste modelo"

    if not configured:
        _deny(setup, cmd)
    if maintenance and gc.path_in_roots(cwd_n, roots) and not gc.text_touches_protected(cmd):
        _log("allow | manutencao | %s | %s" % (tool, cmd[:300]))
        gc.allow()
    _deny("%s Motivo: %s." % (DENY_REASON, why), cmd)


def main():
    try:
        try:
            data = gc.read_payload()
        except gc.InvalidPayload as e:
            _deny("BLOQUEADO: payload invalido (%s). Na duvida o guard nega." % e)
        _decide(data)
        gc.allow()
    except SystemExit:
        raise
    except Exception as e:
        _deny("BLOQUEADO: erro interno do guard (%s). Na duvida o guard nega." % type(e).__name__)


if __name__ == "__main__":
    main()
