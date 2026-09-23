#!/usr/bin/env python3
"""
session_start.py — SessionStart hook (Claude Code).

Dispara quando a sessao abre, retoma ou e limpa (`matcher`: startup|resume|
clear|compact — configure no seu `hooks.json`). Nao pode bloquear nada;
so injeta `additionalContext` no inicio da conversa.

== Por que existe ==
Sessao que nasce sem contexto refaz trabalho: pede de novo o que ja foi
decidido, esquece um bloqueio que ficou pendente, ignora uma skill que
already resolveu o mesmo problema semana passada. Este hook injeta um
resumo BARATO (poucas linhas) do que importa saber agora, lido de disco —
nunca de rede, para nao travar a abertura da sessao com timeout.

== O que este modelo publico injeta (versao simplificada) ==
1. As `N` memorias mais recentes do seu diretorio de memoria (nome do
   arquivo + primeira linha), se o diretorio existir.
2. Um aviso se houver um arquivo de "rito"/plano ativo (ver ESTADO_ATIVO_PATH).
Adapte a lista do que injetar ao seu proprio sistema de memoria — o ponto
fixo e "leia barato, do disco, e resuma antes de empurrar para o modelo".
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

# Onde fica a memoria eterna do seu sistema e o arquivo de rito/plano ativo.
# So por variavel de ambiente (bloco "env" do settings.json). Sem a variavel,
# o item correspondente simplesmente nao e injetado.
MEMORY_DIR = (os.environ.get("HAOS_MEMORY_DIR") or "").strip()
ESTADO_ATIVO_PATH = (os.environ.get("HAOS_ESTADO_ATIVO") or "").strip()

MAX_MEMORIAS = 5


def _memorias_recentes():
    try:
        if not os.path.isdir(MEMORY_DIR):
            return []
        arquivos = [
            os.path.join(MEMORY_DIR, f) for f in os.listdir(MEMORY_DIR)
            if f.endswith(".md")
        ]
        arquivos.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        out = []
        for p in arquivos[:MAX_MEMORIAS]:
            try:
                with open(p, encoding="utf-8") as fh:
                    primeira = fh.readline().strip().lstrip("#").strip()
            except Exception:
                primeira = ""
            out.append("- %s: %s" % (os.path.basename(p), primeira[:120]))
        return out
    except Exception:
        return []


def _rito_ativo():
    try:
        if not os.path.exists(ESTADO_ATIVO_PATH):
            return None
        with open(ESTADO_ATIVO_PATH, encoding="utf-8") as fh:
            estado = json.load(fh)
        fase = estado.get("fase_atual")
        if fase:
            return "Rito ativo, fase %s. Rode o comando de status antes de comecar algo novo." % fase
    except Exception:
        return None
    return None


def main():
    partes = []

    memorias = _memorias_recentes()
    if memorias:
        partes.append("Memorias recentes:\n" + "\n".join(memorias))

    rito = _rito_ativo()
    if rito:
        partes.append(rito)

    if not partes:
        sys.exit(0)
        return

    contexto = "\n\n".join(partes)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": contexto,
        }
    }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # SessionStart nunca pode travar a abertura da sessao.
        sys.exit(0)
