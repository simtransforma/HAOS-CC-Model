#!/usr/bin/env python3
"""
redacao de segredo ANTES de escrever em disco.

MOTIVO: um guard que grava no log a linha de comando COMPLETA transforma um
`curl` com header de autenticacao em chave em texto claro no disco. No
sistema de origem isso gerou dezenas de achados de scanner de segredo e
travou commits ate a causa ser encontrada.

PRINCIPIO: redigir ANTES da escrita, nunca depois. Preservar o NOME do
header/parametro (o log continua util pra diagnostico: saber que havia um
header de auth importa; o valor nao).

CENTRALIZACAO: modulo unico importado pelos hooks que gravam texto bruto em
disco (main_guard, handoff_guard, antidesistencia, session_end). Um so lugar
pra manter os padroes. Quem importa usa try/except e, se o import falhar,
cai num fallback FAIL-CLOSED (nao grava o texto), nunca em texto claro.
"""
import re

_PLACEHOLDER = "[REDACTED]"

# Placeholder da credencial-em-URL: BURRO e MINUSCULO de proposito.
# Placeholder "criativo" (maiusculo, com underscore, longo) e lido pelo
# proprio scanner de segredo como string de alta entropia e vira falso
# positivo. Alem disso a substituicao COLAPSA usuario+senha num unico token
# SEM ":", entao o resultado ("postgresql://redacted@host:5432/db") deixa de
# casar com regra de string de conexao com senha. Redacao que gera novo
# achado nao e redacao, e ruido.
_URL_PLACEHOLDER = "redacted"

# Nomes de header/parametro cujo VALOR e segredo. O nome fica, o valor sai.
_AUTH_NAMES = (
    "x-n8n-api-key", "apikey", "api-key", "x-api-key", "authorization",
    "user-token", "user-secret-key", "x-auth-token", "x-access-token",
    "x-goog-api-key", "private-token", "x-auth-key", "x-auth-email-token",
    "access-token", "auth-token", "token", "secret", "password", "senha",
    "client-secret", "x-hub-signature", "x-hub-signature-256",
)

_NAME_ALT = "|".join(re.escape(n) for n in _AUTH_NAMES)

_PATTERNS = [
    # 1) Header em estilo HTTP: "Nome: valor" (curl -H, JSON de header, etc).
    #    O valor vai ate a aspa/fim de token. Preserva o nome e o separador.
    re.compile(r"(?i)(" + _NAME_ALT + r")(\s*:\s*)([^\s\"'][^\"']*)"),
    # 2) Authorization Bearer/Basic sem depender do padrao acima ter casado.
    re.compile(r"(?i)\b(Bearer|Basic)(\s+)([A-Za-z0-9\-\._~\+/=]{8,})"),
    # 3) Par chave=valor (query string, env inline, JSON sem aspas).
    #    A aspa de FECHAMENTO e OPCIONAL ("\"?" e "'?"): o guard TRUNCA a
    #    linha antes de gravar, e o corte no meio do valor deixa a aspa de
    #    abertura orfa. Exigir a aspa final fazia a regra falhar EM ABERTO
    #    exatamente no formato que o guard fabrica.
    re.compile(r"(?i)\b([A-Za-z0-9_\-]*(?:api[_\-]?key|apikey|key|access[_\-]?token|"
               r"auth[_\-]?token|secret|token|password|senha|passwd|pwd)"
               r"[A-Za-z0-9_\-]*)(\s*[=:]\s*)(\"[^\"]*\"?|'[^']*'?|[^\s&\"';|]+)"),
    # 4) Formatos de chave reconheciveis por si so (mesmo sem nome do campo).
    re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\bAIza[A-Za-z0-9_\-]{10,}"),
    re.compile(r"\bAKIA[A-Za-z0-9]{12,}"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{16,}"),
    re.compile(r"\baact_[A-Za-z0-9_\-\+/=]{16,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{8,}"),
    # JWT: o TERCEIRO segmento (assinatura) e opcional. Um JWT cortado pelo
    # truncamento do log (cabecalho + miolo, 1 ponto so) passaria batido se a
    # assinatura fosse exigida, e cabecalho + miolo ja e material sensivel.
    re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}(?:\.[A-Za-z0-9_\-]*)?"),
    # 5) Chave de roteador de modelos com prefixo proprio. O padrao "sk-"
    #    acima ja cobre; esta regra e defesa em profundidade.
    re.compile(r"\bsk-or-v1-[A-Za-z0-9]{16,}"),
    # 6) Access token da Graph API (EAA...). Nao e coberto pelos padroes
    #    anteriores nem pelo conjunto padrao dos scanners de segredo.
    re.compile(r"\bEAA[A-Za-z0-9]{25,}"),
]

# Credencial embutida em URL: protocolo://usuario:senha@host. Num incidente
# real, uma string de conexao com senha escapou para um log porque nenhum
# padrao olhava para o userinfo da URL (a variavel de senha ao lado foi
# redigida; a URL nao). Por isso este padrao existe e roda primeiro.
#
# Preserva o PROTOCOLO e todo o resto (host, porta, database, query): o log
# continua dizendo A QUE banco alguem tentou conectar. Redige usuario E senha
# (o usuario as vezes carrega o identificador do projeto, tambem sensivel).
#
# Fronteiras da senha: nao pode conter espaco, "/", aspa ou "@": assim o
# match para no PRIMEIRO "@" plausivel e nao engole texto vizinho quando a
# URL aparece no meio de uma linha de log.
_URL_CRED_PATTERNS = [
    re.compile(
        r"(?i)\b([a-z][a-z0-9+.\-]{1,15}://)"      # 1: protocolo:// (preservado)
        r"[^\s:/@\"'<>]{0,128}"                    #    usuario (redigido; {0,..} cobre "redis://:senha@host")
        r":"
        r"[^\s/@\"'<>]{1,256}"                     #    senha (redigida)
        r"@"
    ),
]

# Indices 0,1,2 preservam grupos 1 e 2 (nome + separador) e redigem o grupo 3.
_KEEP_NAME = {0: True, 1: True, 2: True}


def redact(text):
    """Devolve o texto com valores de credencial trocados por [REDACTED],
    preservando o nome do header/parametro. Fail-closed: se algo der errado
    na redacao, devolve um marcador em vez do texto original (o log perde
    detalhe, mas NUNCA vaza segredo)."""
    try:
        if text is None:
            return ""
        s = str(text)
        # Credencial em URL vem PRIMEIRO: a senha de uma string de conexao
        # costuma ser curta e sem formato reconhecivel, entao nenhum padrao
        # generico abaixo a pegaria. Rodando antes, o "@host" ja sai do
        # caminho e nao confunde os padroes de chave=valor.
        for pat in _URL_CRED_PATTERNS:
            s = pat.sub(lambda m: m.group(1) + _URL_PLACEHOLDER + "@", s)
        for i, pat in enumerate(_PATTERNS):
            if i in _KEEP_NAME:
                s = pat.sub(lambda m: m.group(1) + m.group(2) + _PLACEHOLDER, s)
            else:
                s = pat.sub(_PLACEHOLDER, s)
        return s
    except Exception:
        return "[REDACTED-ERRO-NA-REDACAO]"
