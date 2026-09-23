---
description: "Broadcast pro departamento @produto — entry-point: @product-manager. Foco: PM, UX, desenvolvimento frontend/backend"
---
# /haos:produto — Departamento Produto

Esta é uma demanda pro **departamento @produto**.

**Entry-point:** @product-manager
**Agentes do departamento:** product-manager, ux-researcher, dev-frontend, dev-backend
**Foco:** PM, UX, desenvolvimento frontend/backend

## Como atuar

1. **Avalie a demanda**: é pra 1 agente específico do departamento ou pra vários?
2. **Se 1 agente**: delegue direto via tool Agent invocando o subagent (ler `agents/{nome}.md`) com contexto completo
3. **Se vários (multi-agente)**: orquestre delegação em paralelo (criar N sub-agentes em paralelo), depois consolide
4. **Sempre passe:** objetivo, dados disponíveis, formato esperado, prazo, e as skills aplicáveis, nomeadas

**Skills obrigatórias deste departamento:** interface, site, landing, dashboard ou componente vai para @dev-frontend ou @ux-researcher com as skills de design/polish visual — não incluídas nesta versão pública. Alteração substancial em módulo existente exige preflight `haos-structural-refactor` em modo `AUDIT` antes de editar. Com 3+ frentes, planejar a execução por `haos-execution-waves`.

## Retorno esperado dos sub-agentes
Cada um deve retornar com status: **CONCLUÍDO** / **BLOQUEADO** (especificar bloqueio) / **REVISÃO** (precisa validação humana).

Tom do departamento: ajuste ao foco (PM, UX, desenvolvimento frontend/backend). PT-BR sempre.