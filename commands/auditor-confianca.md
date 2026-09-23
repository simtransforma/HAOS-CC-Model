---
description: Delegação direta pro agente @auditor-confianca | due diligence de empresa/fornecedor por OSINT legal, padrão DEEP_AUDIT
---
# /haos:auditor-confianca

Delegue esta demanda diretamente pro subagent **@auditor-confianca**.

**Identidade:** Due diligence de empresa e pessoa jurídica por OSINT legal, score de confiança, conselho e alternativas com faixa de orçamento

## Como atuar

1. **Invoque o subagent** via tool Agent (carrega automaticamente `agents/auditor-confianca.md`)
2. **Passe contexto completo:**
   - Empresa alvo: nome, site, CNPJ ou registro, país, produto ou serviço
   - Decisão que a auditoria apoia: comprar, contratar, indicar, parceria, investir, comparar ou evitar
   - Categoria e jurisdição
   - Profundidade: padrão é **DEEP_AUDIT** para fornecedor, compra, contratação, consultoria, advisory e high-ticket
   - Dados/arquivos disponíveis (proposta, print, contrato que o operador já tenha)
   - Formato esperado do output
   - Prazo (se houver)
3. **Se faltar dado crítico** para resolver homônimo ou jurisdição, peça o brief ANTES de delegar
4. **Aguarde retorno** com status CONCLUÍDO / BLOQUEADO / REVISÃO NECESSÁRIA

## Fechamento: ele prepara, o operador decide

O agente salva o relatório Markdown e o PDF em `workspace/_handoff/<AAAAMMDD>-auditor-<empresa>/`, valida o PDF, devolve o **caminho absoluto** mais um resumo de até 5 linhas, e **para** com `Entrega WhatsApp/Evolution: AGUARDANDO OK DO OPERADOR`.

O envio por WhatsApp só acontece se o operador autorizar explicitamente no turno. Ausência de envio não rebaixa o status da auditoria.

## Quando NÃO usar
- Pesquisa de mercado, tendência, público-alvo ou mapeamento genérico de concorrente → `/haos:pesquisador`
- Auditoria de segurança de sistema, servidor ou container → `/haos:chuck-norris`
- Viabilidade financeira da compra em si (ROI, payback, runway) → um agente financeiro dedicado (fora do escopo deste modelo publico), ou peça o parecer junto se voce tiver um
- Se a demanda é multi-agente → use o comando do departamento correspondente (`/haos:dados`)
- Se a demanda envolve dinheiro/publicação/ação irreversível → pare antes de executar, peça OK explícito do usuário

Tom: do agente (será carregado do subagent file). PT-BR sempre.
