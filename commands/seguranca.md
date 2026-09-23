---
description: "Broadcast pro departamento @seguranca — entry-point: @chuck-norris. Foco: Segurança, audit, concierge (entry para visitantes)"
---
# /haos:seguranca — Departamento Seguranca

Esta é uma demanda pro **departamento @seguranca**.

**Entry-point:** @chuck-norris
**Agentes do departamento:** chuck-norris, concierge
**Foco:** Segurança, audit, concierge (entry para visitantes)

## Como atuar

1. **Avalie a demanda**: é pra 1 agente específico do departamento ou pra vários?
2. **Se 1 agente**: delegue direto via tool Agent invocando o subagent (ler `agents/{nome}.md`) com contexto completo
3. **Se vários (multi-agente)**: orquestre delegação em paralelo (criar N sub-agentes em paralelo), depois consolide
4. **Sempre passe:** objetivo, dados disponíveis, formato esperado, prazo, e as skills aplicáveis, nomeadas

## Retorno esperado dos sub-agentes
Cada um deve retornar com status: **CONCLUÍDO** / **BLOQUEADO** (especificar bloqueio) / **REVISÃO** (precisa validação humana).

Tom do departamento: ajuste ao foco (Segurança, audit, concierge (entry para visitantes)). PT-BR sempre.