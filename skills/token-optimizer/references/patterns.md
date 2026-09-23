# Padrões de Desperdício de Tokens — Referência

## Como interpretar o JSONL

Cada linha `type: "assistant"` tem `message.usage`:
```json
{
  "input_tokens": 3,
  "cache_creation_input_tokens": 90952,
  "cache_read_input_tokens": 16107,
  "output_tokens": 556
}
```

**Fórmula de custo real:**
```
custo = input + (cache_creation × 1.25) + (cache_read × 0.1) + output
```

## O que cada campo significa

| Campo | Custo | Significa |
|---|---|---|
| `input_tokens` | 1× | Tokens novos neste turno (geralmente pequeno) |
| `cache_creation_input_tokens` | 1.25× | System prompt sendo cacheado pela primeira vez |
| `cache_read_input_tokens` | 0.1× | System prompt lido do cache (barato) |
| `output_tokens` | 1× | Resposta gerada |

## Quando cache_creation dispara?
- Início de sessão (primeira vez)
- A cada 5 minutos se o cache expirou (ephemeral_5m)
- A cada 1 hora se o cache de 1h expirou (ephemeral_1h)
- Quando o system prompt muda (arquivo editado, nova skill carregada)

## Padrões vistos no HAOS Master

### 1. Cluster de 4 turnos idênticos
Timestamp: quatro linhas em ±2s com cache_creation idêntico (~90k)
Causa: chamadas paralelas de subagentes — cada spawn recria o cache
Custo: 4× ao invés de 1× para o mesmo prompt

### 2. Cache creation de 157k tokens
Ocorre quando sessão está "quente" com muitos arquivos carregados
Indica system prompt inflado (hooks + skills ativas + agentes lidos)

### 3. CacheRead de 16.467 tokens consistente
É o "baseline" do system prompt do Claude Code sozinho
Quando HAOS Master está ativo, esse número sobe para 90k–157k
A diferença (~74k–140k tokens) é o custo do HAOS Master

## Onde o HAOS Master adiciona tokens ao system prompt

1. **session_start hook** → até 9.000 chars (~2.250 tokens)
   - MEMORY.md: ~500 tokens (duplicado com auto-memory)
   - Sessões recentes: ~800–1.000 tokens
   - Bootstrap: ~750–1.000 tokens
   
2. **Auto-memory do Claude** → carrega todos os arquivos .md linkados no MEMORY.md
   - Cada arquivo memory: 500–2.000 tokens
   - Total estimado: ~5.000–8.000 tokens

3. **Skills ativas** → frontmatter de todas as skills instaladas
   - 20+ skills × ~100 tokens de description = ~2.000 tokens
   
4. **CLAUDE.md do projeto** → se existir, é carregado inteiro

## Técnicas de otimização por impacto

### Alto impacto (>1.000 tokens/sessão)
- Remover duplicação MEMORY.md no hook
- Reduzir janela de sessões recentes
- Enxugar bootstrap.md

### Médio impacto (200–1.000 tokens/sessão)
- Comprimir descriptions de skills
- Mover seções de referência para references/
- Reduzir max_chars do hook de 9.000 → 5.000

### Baixo impacto (<200 tokens/sessão)
- Remover comentários de código nos agentes
- Usar tabelas ao invés de listas em agentes
- Comprimir exemplos inline
