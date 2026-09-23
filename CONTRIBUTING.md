# Contribuindo

Obrigado pelo interesse. Este repositorio e um **modelo de referencia**, entao contribuicao boa aqui
tem um formato especifico.

---

## O que ajuda muito

- **Corrigir erro ou trecho confuso na documentacao.** O objetivo e alguem que nunca viu o sistema
  entender. Se um trecho te travou, ele vai travar outra pessoa.
- **Agente ou skill generico** que sirva a qualquer contexto, sem amarra a uma empresa.
- **Hook novo** que resolva um problema real, com a explicacao do problema junto.
- **Relato de instalacao** em ambiente diferente: outro sistema operacional, outro shell, outra versao
  de Python. Isso vale ouro e quase ninguem manda.

## O que nao entra

- **Qualquer dado real.** Nome, telefone, e-mail, documento, endereco de servidor, identificador de
  conta, valor financeiro. Nem em exemplo, nem em teste, nem em comentario.
- **Skill amarrada a uma empresa ou cliente.** Ela e util para voce e ruido para todo mundo. Mantenha
  num repositorio proprio e privado.
- **Segredo de qualquer tipo**, ainda que expirado.
- **Dependencia pesada** sem justificativa. O modelo roda com Python e Git. Cada dependencia nova
  precisa defender a propria existencia.

---

## Como contribuir

### Mudanca pequena

Abra o pull request direto. Descreva o que mudou e por que.

### Mudanca grande

Abra uma issue primeiro. Descreva o problema antes da solucao. Evita voce gastar tempo numa direcao
que nao vai ser aceita.

### O padrao

| Item | Regra |
|---|---|
| **Idioma** | Portugues do Brasil na documentacao. Codigo e nome de arquivo em ingles ou portugues sem acento |
| **Commit** | [Conventional Commits](https://www.conventionalcommits.org). Mensagem objetiva, no imperativo |
| **Documentacao** | Tabela e lista antes de paragrafo. Explique o **porque**, nao so o **como** |
| **Exemplo** | Dado obviamente ficticio. Use marcadores no formato `<SEU_CAMINHO>` |
| **Agente e skill** | Siga a estrutura de [docs/02-AGENTES.md](docs/02-AGENTES.md) e [docs/03-SKILLS.md](docs/03-SKILLS.md) |

### Antes de abrir o pull request

```bash
python hooks/selftest.py          # a instalacao continua valida
gitleaks dir . --no-banner        # nenhum segredo entrou
grep -rniE "@[a-z0-9.-]+\.(com|br)" . --exclude-dir=.git   # nenhum contato real
```

O terceiro comando vai achar os links de documentacao das referencias. Confira se o que aparece e so
isso.

---

## Regra da referencia

**Toda ideia que veio de fora e creditada com link.** Se voce trouxe um padrao de outro projeto,
livro ou artigo, adicione a linha correspondente em [docs/08-REFERENCIAS.md](docs/08-REFERENCIAS.md)
no mesmo pull request. Credito nao e cortesia, e parte do produto.

Se a sua contribuicao nasceu de um problema que voce viveu, conte o problema **sem expor o contexto**.
"Nasceu de um incidente de deploy" ensina. O nome do cliente nao.

---

## Codigo de conduta

Seja direto e seja respeitoso. Critica a ideia, nunca a pessoa. Quem reporta um problema de seguranca
esta ajudando, mesmo quando o tom vier duro.
