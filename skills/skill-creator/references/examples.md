# Exemplos de Skills — Bom vs Ruim

---

## Exemplo 1: Skill de Extração de PDF

### ❌ Ruim (verboso, description vaga)

```yaml
---
name: pdf-extractor
description: Ajuda a extrair conteúdo de arquivos PDF.
---

# PDF Extractor

Este skill ajuda você a extrair texto de arquivos PDF. O formato PDF
(Portable Document Format) é amplamente utilizado para documentos.
Para extrair texto, você precisa de uma biblioteca Python adequada.
Existem várias opções disponíveis, mas pdfplumber é recomendado por
ser fácil de usar e suportar a maioria dos casos.

## Como usar
Primeiro instale a biblioteca com pip install pdfplumber. Depois
abra o arquivo e extraia o texto página por página...
```

### ✅ Bom (conciso, description com gatilhos)

```yaml
---
name: pdf-extractor
description: >
  Extrai texto, tabelas e imagens de arquivos PDF. Use esta skill sempre
  que o usuário mencionar PDF, quiser "ler um PDF", "extrair dados de PDF",
  "processar arquivo PDF", ou enviar um arquivo .pdf. Também aciona quando
  o usuário quer converter PDF para outro formato.
compatibility: claude.ai, claude-code
---

# PDF Extractor

Extrai conteúdo de PDFs usando pdfplumber (texto/tabelas) ou PyMuPDF (imagens).

## Extração de texto
```python
import pdfplumber
with pdfplumber.open("arquivo.pdf") as pdf:
    texto = "\n".join(p.extract_text() for p in pdf.pages)
```

## Extração de tabelas
```python
with pdfplumber.open("arquivo.pdf") as pdf:
    tabelas = pdf.pages[0].extract_tables()
```

Instalar se necessário: `pip install pdfplumber`
```

---

## Exemplo 2: Skill de Criação de Agente (Alta Liberdade)

### ✅ Bom (alta liberdade, pesquisa obrigatória)

```yaml
---
name: agent-builder
description: >
  Pesquisa, arquiteta e constrói agentes completos a partir de uma descrição.
  Use sempre que o usuário disser "quero um agente que...", "cria um bot...",
  "preciso automatizar...", "monta um workflow que...", ou descrever qualquer
  sistema autônomo. SEMPRE pesquisa na web antes de recomendar stack ou custo.
---

# Agent Builder

Arquiteta e constrói agentes sob demanda.

## Fluxo
1. Entender a necessidade (máx 3 perguntas se faltar info)
2. Pesquisar ferramentas e preços atuais (obrigatório)
3. Apresentar arquitetura + custo estimado para aprovação
4. Construir todos os arquivos
5. Entregar com present_files
```

---

## Exemplo 3: Skill de Migration de Banco (Baixa Liberdade)

### ✅ Bom (baixa liberdade, script exato)

```yaml
---
name: db-migration
description: >
  Executa migrations de banco de dados PostgreSQL de forma segura.
  Use quando o usuário pedir para "rodar migration", "atualizar o banco",
  "aplicar mudanças no schema", ou mencionar migration + PostgreSQL/banco.
  Nunca improvise a sequência — siga o script exato.
---

# DB Migration

⚠️ Operação crítica. Siga exatamente os passos abaixo, sem variações.

## Sequência obrigatória

```bash
# 1. Backup antes de qualquer coisa
pg_dump -U postgres mydb > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Rodar migration com verificação
python scripts/migrate.py --verify --backup

# 3. Confirmar sucesso
python scripts/migrate.py --status
```

**Não adicione flags extras. Não pule o backup. Se qualquer passo falhar, pare e reporte.**
```

---

## Tabela de Referência Rápida

| Tipo de Skill | Liberdade | Pesquisa Web | Arquivos de Ref |
|--------------|-----------|--------------|-----------------|
| Criativa/Escrita | Alta | Raramente | Não |
| Análise/Revisão | Alta-Média | Às vezes | Sim (exemplos) |
| Integração de API | Média | Sempre | Sim (docs) |
| Build/Deploy | Baixa | Sempre | Sim (scripts) |
| Operação crítica | Baixíssima | Não | Sim (scripts exatos) |
