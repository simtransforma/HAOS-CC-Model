#!/usr/bin/env python3
"""
session_end.py — Stop hook (Claude Code).

Dispara ao fim de cada turno do assistente. Nao pode bloquear nada. Serve
para CAPTURAR: se algo digno de virar memoria aconteceu neste turno,
registrar antes que o contexto seja perdido no proximo compact.

== Por que existe ==
Aprendizado que nao e capturado no ato se perde. Esperar "consolidar no
fim da sessao" garante esquecimento parcial — o modelo so lembra o que
ainda esta na janela de contexto NA HORA de consolidar.

== O que este modelo publico faz (versao simplificada) ==
Le o ultimo turno pelo transcript_path que o Claude Code passa no payload,
procura por um marcador textual simples (ex.: o operador escreveu
"decisao:" ou "aprendizado:" na conversa) e, se achar, acrescenta uma linha
num arquivo de captura no seu diretorio de memoria. Isso NAO substitui um
pipeline de captura de verdade (classificacao, dedupe, gate de valor) — so
mostra o ponto de entrada. Adapte para o seu proprio motor de memoria.

Garantias: sem HAOS_MEMORY_DIR definido, nao grava nada (nao inventa pasta);
o texto passa pelo redact.py ANTES de ir para o disco; linha que ja esta no
arquivo de captura nao e gravada de novo (o hook roda a cada turno e le a
cauda do transcript, entao sem isso o mesmo marcador se repetiria).
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from redact import redact as _redact
except Exception:  # sem redacao, nao grava texto do transcript
    _redact = None

MEMORY_DIR = (os.environ.get("HAOS_MEMORY_DIR") or "").strip()
CAPTURE_FILE = os.path.join(MEMORY_DIR, "_captura_bruta.md") if MEMORY_DIR else ""

_MARKER_RE = re.compile(r"(?i)^(decisao|aprendizado|bloqueio)\s*:\s*(.+)$")


def _extrai_marcadores(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    achados = []
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            for linha in fh.readlines()[-200:]:  # so a cauda: barato, recente
                try:
                    evento = json.loads(linha)
                except Exception:
                    continue
                texto = ""
                conteudo = evento.get("message", {}).get("content")
                if isinstance(conteudo, str):
                    texto = conteudo
                elif isinstance(conteudo, list):
                    texto = " ".join(
                        b.get("text", "") for b in conteudo if isinstance(b, dict)
                    )
                for trecho in texto.splitlines():
                    m = _MARKER_RE.match(trecho.strip())
                    if m:
                        achados.append("%s: %s" % (m.group(1).lower(), m.group(2).strip()))
    except Exception:
        return achados
    return achados


def main():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)
        return

    if not CAPTURE_FILE or _redact is None:
        sys.exit(0)
        return
    transcript_path = data.get("transcript_path") if isinstance(data, dict) else None
    if not isinstance(transcript_path, str):
        sys.exit(0)
        return
    achados = [_redact(a) for a in _extrai_marcadores(transcript_path)]
    if not achados:
        sys.exit(0)
        return

    try:
        os.makedirs(MEMORY_DIR, exist_ok=True)
        ja = ""
        if os.path.exists(CAPTURE_FILE):
            with open(CAPTURE_FILE, encoding="utf-8", errors="replace") as fh:
                ja = fh.read()
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        novos = []
        for item in achados:
            if ("] " + item + "\n") not in ja and item not in novos:
                novos.append(item)
        if novos:
            with open(CAPTURE_FILE, "a", encoding="utf-8") as fh:
                for item in novos:
                    fh.write("- [%s] %s\n" % (ts, item))
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
