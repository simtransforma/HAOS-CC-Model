---
name: haos-claim-verification
description: Verify claims for HAOS research. Use before finalizing reports, checking factual statements, validating market/legal/technical/medical/financial claims, or separating fact from inference.
---

# HAOS Claim Verification

Validar afirmacoes antes da entrega.

## Workflow

1. Extrair claims do rascunho ou pedido.
2. Classificar cada claim:
   - `FATO`
   - `OBSERVACAO`
   - `ESTIMATIVA`
   - `INFERENCIA`
   - `HIPOTESE`
   - `OPINIAO`
3. Exigir evidencia adequada ao risco.
4. Procurar contraevidencia para claims centrais.
5. Rebaixar, qualificar ou remover claims sem suporte.

## Gates

- Claim atual ou instavel: verificar com fonte recente.
- Claim legal, financeiro, medico ou seguranca: usar fonte primaria/oficial quando possivel.
- Claim numerico: fonte, data, metodologia e unidade.
- Claim sobre concorrente: somente fontes publicas e sem copiar conteudo.
- Claim sem fonte: marcar como `NAO VERIFICADO`.

## Formato

```markdown
| Claim | Tipo | Evidencia | Contraevidencia | Confianca | Decisao |
|---|---|---|---|---|---|
| ... | FATO | fonte A/B | nenhuma encontrada | alta | manter |
```
