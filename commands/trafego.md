---
description: "Broadcast pro departamento @trafego — entry-point: @traffic-master. Foco: Mídia paga, gestão de campanhas, tracking"
---
# /haos:trafego — Departamento Trafego

Esta é uma demanda pro **departamento @trafego**.

**Entry-point:** @traffic-master
**Agentes do departamento:** traffic-master, media-buyer, tracking-engineer
**Foco:** Mídia paga, gestão de campanhas, tracking

## Como atuar

1. **Avalie a demanda**: é pra 1 agente específico do departamento ou pra vários?
2. **Se 1 agente**: delegue direto via tool Agent invocando o subagent (ler `agents/{nome}.md`) com contexto completo
3. **Se vários (multi-agente)**: orquestre delegação em paralelo (criar N sub-agentes em paralelo), depois consolide
4. **Sempre passe:** objetivo, dados disponíveis, formato esperado, prazo, e as skills aplicáveis, nomeadas

## Retorno esperado dos sub-agentes
Cada um deve retornar com status: **CONCLUÍDO** / **BLOQUEADO** (especificar bloqueio) / **REVISÃO** (precisa validação humana).

Tom do departamento: ajuste ao foco (Mídia paga, gestão de campanhas, tracking). PT-BR sempre.