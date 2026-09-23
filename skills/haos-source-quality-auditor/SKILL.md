---
name: haos-source-quality-auditor
description: Audit source quality for HAOS research. Use when evaluating web pages, papers, reports, news, market data, regulatory sources, competitor claims, or any research source before trusting it.
---

# HAOS Source Quality Auditor

Classificar confiabilidade antes de usar fonte como evidencia.

## Score

Dar nota `A`, `B`, `C`, `D` ou `X`:

- `A`: fonte primaria/oficial, paper revisado, dado bruto, documento legal, metodologia clara.
- `B`: fonte secundaria confiavel, relatorio reconhecido, jornalismo com autoria e fontes.
- `C`: blog/artigo util, mas com vies, pouca metodologia ou dado de segunda mao.
- `D`: opiniao, venda, conteudo sem autoria/data, fonte fraca.
- `X`: fonte inadequada, suspeita, privada, sem acesso, potencialmente fraudulenta ou perigosa.

## Criterios

- autoria e autoridade;
- data e atualidade;
- metodologia;
- fonte primaria ou secundaria;
- conflito de interesse;
- possibilidade de verificacao independente;
- jurisdicao/escopo;
- estabilidade temporal;
- risco de SEO spam ou afiliado;
- risco de cherry-picking.

## Formato

```markdown
| Fonte | Tipo | Data | Score | Pode sustentar claim? | Observacao |
|---|---|---:|---|---|---|
| ... | oficial | 2026-05-25 | A | sim | ... |
```
