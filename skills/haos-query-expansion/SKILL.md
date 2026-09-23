---
name: haos-query-expansion
description: Generate robust research queries for HAOS deep research. Use before web searches, Brave/Tavily/Firecrawl collection, market research, academic research, regulatory research, competitor analysis, or claim verification.
---

# HAOS Query Expansion

Gerar queries antes da coleta para evitar pesquisa rasa.

## Saida padrao

Entregar grupos de queries:

- principais;
- sinonimos e termos leigos;
- termos tecnicos;
- entidades/pessoas/empresas/produtos;
- fontes oficiais;
- fontes criticas/contraevidencia;
- recortes por pais/idioma;
- recortes por periodo;
- queries de arquivo: PDF, relatorio, estudo, guideline;
- queries de forum/comunidade quando etico e publico.

## Regras

- Criar queries em PT-BR e ingles quando isso aumentar cobertura.
- Incluir operadores quando util: `site:`, `"frase exata"`, `filetype:pdf`, `after:`, `before:`.
- Para regulatorio, priorizar orgaos oficiais.
- Para mercado, incluir concorrentes, alternativas, reviews, precos, anuncios e reclamacoes.
- Para ciencia, incluir `systematic review`, `meta-analysis`, `guideline`, `trial`, `cohort`, `preprint`.
- Para claim verification, criar queries que tentem provar e refutar a afirmacao.

## Formato

```markdown
## Query Plan
**Pergunta:** ...
**Hipoteses:** ...

### Busca ampla
- ...

### Fontes oficiais
- ...

### Contraevidencia
- ...

### Proxima iteracao
- ...
```
