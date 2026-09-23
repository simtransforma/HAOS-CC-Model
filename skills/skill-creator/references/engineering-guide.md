# Guia de Engenharia de Skills

Baseado nas melhores práticas oficiais da Anthropic (docs atualizados 2025-2026).

---

## Estrutura Obrigatória do SKILL.md

```markdown
---
name: nome-da-skill              # kebab-case, 1-64 chars
description: >
  [O que faz]. [Quando usar — frases específicas que devem disparar].
  [Contextos que devem disparar mesmo sem as palavras exatas].
  Seja "pushy" — Claude tende a sub-acionar skills.
compatibility: claude.ai, claude-code   # opcional
allowed-tools: Bash, Write             # opcional, só Claude Code CLI
---

# Título da Skill

[Uma frase explicando o papel da skill.]

[Se houver referências: "Leia references/X.md antes de começar."]

---

## Seção 1
...

## Seção 2
...
```

---

## Princípios de Engenharia

### 1. Concisão é o principal valor

O contexto é um bem público. Cada token do SKILL.md compete com:
- Histórico da conversa
- System prompt
- Metadata de outras skills

**Regra:** Só adicione o que Claude não sabe. Teste cada parágrafo:
> "Claude já sabe isso? Se sim, delete."

❌ Verboso:
```
PDF (Portable Document Format) é um formato amplamente usado que contém
texto e imagens. Para extrair texto você precisa de uma biblioteca...
```

✅ Conciso:
```
Use pdfplumber para extração de texto:
import pdfplumber
with pdfplumber.open("f.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

---

### 2. Grau de Liberdade Correto

Calibre a especificidade ao risco da tarefa:

| Situação | Abordagem | Exemplo |
|----------|-----------|---------|
| Muitos caminhos válidos | **Alta liberdade** — instrução textual | Revisão de código |
| Padrão preferido existe | **Média liberdade** — pseudocódigo/template com parâmetros | Geração de relatório |
| Operação frágil/crítica | **Baixa liberdade** — script exato, sem variações | Migration de banco |

Analogia: ponte estreita com abismos → instruções exatas. Campo aberto → direção geral.

---

### 3. Progressive Disclosure (3 Níveis)

```
Nível 1: Metadata (name + description)
         → Sempre em contexto. ~100 tokens. Claude decide se aciona.

Nível 2: Corpo do SKILL.md
         → Carregado quando skill é acionada. Manter < 300-500 linhas.

Nível 3: references/ e templates/
         → Carregados sob demanda. Sem limite de tamanho.
```

**Regra de ouro:** Se o SKILL.md estiver chegando em 400+ linhas, mova conteúdo para `references/`.

---

### 4. Description = Mecanismo de Disparo

A `description` é o campo mais crítico. Claude lê só ela para decidir se usa a skill.

**Deve conter:**
- O que a skill faz (1 frase)
- Frases exatas que devem disparar ("quero uma skill que...", "cria um agente...")
- Contextos implícitos (quando o usuário não usa as palavras exatas)
- Instrução "pushy" explícita para combater sub-acionamento

**Template de description eficaz:**
```yaml
description: >
  [O que faz em 1 frase]. Use esta skill sempre que o usuário [frase 1],
  [frase 2], [frase 3], ou qualquer variação. Também aciona quando
  [contexto implícito sem palavras exatas]. [Instrução de não pular].
```

---

### 5. Arquivos de Referência

Use `references/` para:
- Guias detalhados (> 50 linhas)
- Exemplos extensos
- Documentação de APIs
- Tabelas de decisão complexas

Use `templates/` para:
- Arquivos de saída reutilizáveis
- Boilerplates de código
- Estruturas de documento

Sempre referencie no SKILL.md quando ler:
```markdown
Leia `references/guide.md` antes de começar.
```

---

### 6. Checklist Final (use antes de empacotar)

Ver `references/checklist.md`.

---

## Estrutura de Pastas por Complexidade

### Skill simples (1 arquivo):
```
minha-skill/
└── SKILL.md
```

### Skill média (com referências):
```
minha-skill/
├── SKILL.md
└── references/
    └── guide.md
```

### Skill complexa (multi-domínio):
```
minha-skill/
├── SKILL.md
├── references/
│   ├── guide.md
│   ├── examples.md
│   └── aws.md / gcp.md / azure.md   ← por variante
└── templates/
    └── output-template.md
```

---

## Anti-padrões a Evitar

| ❌ Erro | ✅ Correto |
|---------|-----------|
| Explicar o que Claude já sabe | Só o que é específico do domínio |
| Description vaga ("ajuda com X") | Description com frases-gatilho explícitas |
| SKILL.md com 800+ linhas | Mover para references/ acima de 400 |
| Liberdade zero em tarefas criativas | Alta liberdade para outputs subjetivos |
| Liberdade total em migrations/deploys | Baixa liberdade, script exato |
| Só entregar texto | Sempre empacotar ZIP e usar present_files |
