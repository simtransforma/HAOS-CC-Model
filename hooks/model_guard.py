#!/usr/bin/env python3
"""
model-guard - PreToolUse hook (Claude Code) para o spawn de sub-agente
(ferramenta Agent / Task).

== Por que existe ==
Antes de qualquer execucao, o orquestrador escolhe de proposito o modelo de
cada sub-agente, com qualidade primeiro. Sem trava, ele herda o modelo da
sessao por inercia e o roteamento vira acaso.

== Regra unica ==
Spawn do ORQUESTRADOR (sem agent_id) precisa de `tool_input.model` valido.
Ausente, "inherit", tipo errado ou fora da lista = DENY.
Sub-agente (agent_id preenchido) passa. Vale em qualquer pasta: o cwd nao
desliga a trava.

== Modelos aceitos ==
A lista mora num lugar so: MODEL_TIERS em guard_common.py. Hoje:
haiku, sonnet, opus, fable; o alias com janela longa ("opus[1m]") e o nome
completo ("claude-opus-5-5", "claude-sonnet-4-5-20250929"). Para aceitar um
tier novo, acrescente-o la.

== Contrato ==
Payload ilegivel, JSON quebrado ou tipo errado: DENY com exit 0 (o hook so
roda em spawn de agente, entao negar no erro nao trava a sessao).
Nao existe arquivo de bypass: nenhum arquivo que o modelo consiga criar
muda a decisao.
Matcher no settings.json: Agent|Task.
Referencia: https://docs.claude.com/en/docs/claude-code/hooks
Skill companheira: haos-model-router (quando usar cada tier).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import guard_common as gc
except Exception:
    sys.stdout.write('{"hookSpecificOutput": {"hookEventName": "PreToolUse", '
                     '"permissionDecision": "deny", "permissionDecisionReason": '
                     '"BLOQUEADO: guard_common.py ausente ou quebrado ao lado de model_guard.py."}}')
    sys.exit(0)

SPAWN_TOOLS = {"Agent", "Task"}
LOG_NAME = "model_guard.log"

DENY_REASON = (
    "BLOQUEADO pelo Model Router: declare `model` explicitamente neste spawn "
    "(tiers aceitos: " + ", ".join(gc.MODEL_TIERS) + ", ou o nome completo do modelo). "
    "Qualidade primeiro; na duvida entre dois tiers, SOBE. Guia rapido: tier baixo = "
    "mecanico, varredura, formatacao; tier medio = rotina, codigo padrao, analise; "
    "tier alto = causa raiz, arquitetura, seguranca, verificacao adversarial. "
    "Inclua no briefing a linha: MODELO: <tier> porque <motivo>."
)


def _log(line):
    gc.write_log(LOG_NAME, "%s | %s" % (gc.now(), line))


def main():
    try:
        try:
            data = gc.read_payload()
        except gc.InvalidPayload as e:
            _log("deny | payload invalido | %s" % e)
            gc.deny("BLOQUEADO: payload invalido (%s). Na duvida o guard nega." % e)

        tool = data.get("tool_name")
        if not isinstance(tool, str):
            gc.deny("BLOQUEADO: payload invalido (tool_name ausente ou nao-texto).")
        if tool not in SPAWN_TOOLS:
            gc.allow()
        if gc.is_subagent(data):
            gc.allow()

        ti = data.get("tool_input")
        if not isinstance(ti, dict):
            gc.deny("BLOQUEADO: payload invalido (tool_input nao e objeto).")
        model = ti.get("model")
        ok = gc.is_valid_model(model)
        _log("%s | model=%s | subagent_type=%s"
             % ("allow" if ok else "deny", model if isinstance(model, str) else "<ausente>",
                str(ti.get("subagent_type") or "")[:60]))
        if ok:
            gc.allow()
        gc.deny(DENY_REASON)
    except SystemExit:
        raise
    except Exception as e:
        gc.deny("BLOQUEADO: erro interno do model_guard (%s)." % type(e).__name__)


if __name__ == "__main__":
    main()
