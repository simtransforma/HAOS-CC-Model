---
description: Delegação direta pro agente @project-manager — Gestão de projeto, WBS, cronograma, tracking, riscos
---
# /haos:project-manager

Delegue esta demanda diretamente pro subagent **@project-manager**.

**Identidade:** Gestão de projeto, WBS, cronograma, tracking, riscos

## Como atuar

1. **Invoque o subagent** via tool Agent (carrega automaticamente `agents/project-manager.md`)
2. **Passe contexto completo:**
   - Objetivo da sessão
   - Dados/arquivos disponíveis
   - Formato esperado do output
   - Prazo (se houver)
3. **Se o agente exigir brief mínimo** (ex: cmo, copy-specialist) e não tiver, peça o brief ANTES de delegar
4. **Aguarde retorno** com status CONCLUÍDO / BLOQUEADO / REVISÃO

## Quando NÃO usar
- Se a demanda é multi-agente → use o comando do departamento correspondente
- Se a demanda envolve dinheiro/publicação/ação irreversível → pare antes de executar, peça OK explícito do usuário

Tom: do agente (será carregado do subagent file). PT-BR sempre.