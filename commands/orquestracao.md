---
description: "Broadcast pro departamento @orquestracao — entry-point: @qa-reviewer. Foco: QA, PM, compliance, devops"
---
# /haos:orquestracao — Departamento Orquestracao

Esta é uma demanda pro **departamento @orquestracao**.

**Entry-point:** @qa-reviewer
**Agentes do departamento:** qa-reviewer, project-manager, compliance-officer, devops
**Foco:** QA, PM, compliance, devops

## Como atuar

1. **Avalie a demanda**: é pra 1 agente específico do departamento ou pra vários?
2. **Se 1 agente**: delegue direto via tool Agent invocando o subagent (ler `agents/{nome}.md`) com contexto completo
3. **Se vários (multi-agente)**: orquestre delegação em paralelo (criar N sub-agentes em paralelo), depois consolide
4. **Sempre passe:** objetivo, dados disponíveis, formato esperado, prazo, e as skills aplicáveis, nomeadas

## Retorno esperado dos sub-agentes
Cada um deve retornar com status: **CONCLUÍDO** / **BLOQUEADO** (especificar bloqueio) / **REVISÃO** (precisa validação humana).

Tom do departamento: ajuste ao foco (QA, PM, compliance, devops). PT-BR sempre.