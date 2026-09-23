#!/usr/bin/env python3
"""
post_compact.py — PostCompact hook (Claude Code).

Dispara depois que o Claude Code compacta o contexto (resume a conversa
para caber na janela). Nao pode bloquear nada; so injeta `additionalContext`.

== Por que existe ==
Compactacao come regra junto com conversa: o resumo automatico preserva o
QUE foi feito, mas costuma derrubar a REGRA sob a qual foi feito (a Regra de
Ouro, o regime ativo, um bloqueio que ainda esta pendente). Sem reinjecao,
a sessao pos-compact reaprende as regras por tentativa e erro.

== O que este modelo publico reinjeta (versao simplificada) ==
As mesmas poucas linhas fixas que importam SEMPRE estarem presentes: como o
guard decide (ler vs. mutar) e um lembrete de checar se ha um rito/plano
em andamento. Mantenha isto CURTO —
e reinjetado toda vez que o contexto aperta, entao ele mesmo nao pode ser o
motivo de apertar de novo.
"""
import json
import os
import sys

BLOCO_FIXO = (
    "Lembrete pos-compactacao: a pergunta antes de qualquer acao continua "
    "sendo \"isso muda estado, apaga ou envia algo, ou e so leitura?\". "
    "Leitura voce faz direto; mutacao delega a um sub-agente especializado "
    "com o `model` do tier certo declarado no spawn. Se havia um rito ou "
    "plano em andamento antes da "
    "compactacao, confira o estado dele antes de comecar algo novo."
)


def main():
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostCompact",
            "additionalContext": BLOCO_FIXO,
        }
    }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
