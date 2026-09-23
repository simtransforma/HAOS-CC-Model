#!/usr/bin/env python3
"""
prompt_router.py — UserPromptSubmit hook (Claude Code).

Dispara toda vez que voce (humano) envia uma mensagem. Pode injetar
`additionalContext` e, se quiser, bloquear (nao usado aqui: este router so
reconhece modo e injeta contexto, nunca nega).

== Por que existe ==
Roteamento manual nao escala: se toda sessao depende de voce lembrar de
dizer "abre o rito" ou "fala com o agente X", cedo ou tarde alguem esquece
e a tarefa roda no modo errado (agente generico fazendo trabalho que devia
ir para um especialista, ou uma tarefa de varias fases rodando sem plano).

== Os modos que este modelo publico reconhece ==
| Prefixo   | Modo                                            |
|-----------|--------------------------------------------------|
| `#`       | Rito — pipeline de fases com gate entre cada uma  |
| `@agente` | Direto — rotear para um sub-agente especifico     |
| `@depto`  | Broadcast — rotear para o entry-point do depto    |
| (nenhum)  | Concierge — interpretar e decidir na hora         |

Ajuste `AGENTES` e `DEPARTAMENTOS` para o seu proprio mapa de agentes (ver
`agents/`). O router NAO precisa saber os detalhes de cada agente — so
precisa saber que o nome existe e, opcionalmente, qual arquivo de contexto
injetar.
"""
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

# <AJUSTE> troque pelos nomes reais dos seus agentes/departamentos.
AGENTES = {
    "dev-backend", "dev-frontend", "devops", "qa-reviewer", "project-manager",
}
DEPARTAMENTOS = {
    "conselho", "trafego", "dados", "produto", "seguranca",
}

RITO_PREFIX_RE = re.compile(r"^\s*#")
MENCAO_RE = re.compile(r"^\s*@([a-zA-Z0-9_\-]+)")


def _detecta_modo(prompt: str):
    if RITO_PREFIX_RE.match(prompt or ""):
        return "RITO", None
    m = MENCAO_RE.match(prompt or "")
    if m:
        alvo = m.group(1).lower()
        if alvo in AGENTES:
            return "DIRETO", alvo
        if alvo in DEPARTAMENTOS:
            return "BROADCAST", alvo
    return "CONCIERGE", None


def _bloco_para(modo, alvo):
    if modo == "RITO":
        return (
            "MODO RITO detectado (prefixo `#`). Siga o pipeline de fases "
            "definido no seu CLAUDE.md/skill de rito: Fase 1 (intake) e "
            "OBRIGATORIA e nunca pode ser pulada, mesmo se pedirem para "
            "pular. Uma fase por vez, com gate bloqueante entre cada."
        )
    if modo == "DIRETO":
        return "MODO DIRETO: rotear esta tarefa para o agente `%s`." % alvo
    if modo == "BROADCAST":
        return "MODO BROADCAST: rotear para o entry-point do departamento `%s`." % alvo
    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)
        return

    prompt = data.get("prompt") if isinstance(data, dict) else None
    if not isinstance(prompt, str) or not prompt.strip():
        sys.exit(0)
        return

    modo, alvo = _detecta_modo(prompt)
    bloco = _bloco_para(modo, alvo)
    if not bloco:
        sys.exit(0)
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": bloco,
        }
    }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
