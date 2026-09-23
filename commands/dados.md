---
description: "Broadcast pro departamento @dados — entry-point: @data-analyst. Foco: Análise de dados, BI, pesquisa de mercado"
---
# /haos:dados — Departamento Dados

Esta é uma demanda pro **departamento @dados**.

**Entry-point:** @data-analyst
**Agentes do departamento:** data-analyst, bi-engineer, pesquisador, auditor-confianca
**Foco:** Análise de dados, BI, pesquisa de mercado

## Como atuar

1. **Avalie a demanda**: é pra 1 agente específico do departamento ou pra vários?
2. **Se 1 agente**: delegue direto via tool Agent invocando o subagent (ler `agents/{nome}.md`) com contexto completo
3. **Se vários (multi-agente)**: orquestre delegação em paralelo (criar N sub-agentes em paralelo), depois consolide
4. **Sempre passe:** objetivo, dados disponíveis, formato esperado, prazo, e as skills aplicáveis, nomeadas

**Skills e agentes obrigatórios deste departamento:** due diligence de empresa, fornecedor, compra, consultoria ou oferta high-ticket vai para @auditor-confianca no padrão `DEEP_AUDIT`, sem envio automático: o PDF fica pronto e o envio só sai com OK do Gian.

## Retorno esperado dos sub-agentes
Cada um deve retornar com status: **CONCLUÍDO** / **BLOQUEADO** (especificar bloqueio) / **REVISÃO** (precisa validação humana).

Tom do departamento: ajuste ao foco (Análise de dados, BI, pesquisa de mercado). PT-BR sempre.