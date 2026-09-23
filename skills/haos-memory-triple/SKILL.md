---
name: haos-memory-triple
description: "Rotina de memória tripla HAOS: local, Obsidian/OneDrive e GitHub privado, com claude-mem opcional isolado."
---

# HAOS Memory Triple

Use ao salvar, consultar, fechar ou sincronizar memória.

## Camadas

1. `memory/` no projeto — fonte operacional local.
2. Obsidian/OneDrive — leitura humana e espelho diário/manual.
3. GitHub privado de memória — backup versionado sanitizado.

## Regras

- Nunca salvar segredos.
- Sanitizar dados sensíveis.
- Separar fatos duráveis de logs de sessão.
- `memory/durable/`: fatos permanentes.
- `memory/sessions/`: histórico de sessões.
- `memory/episodic/`: aprendizados por projeto.
- `memory/claude-mem/`: dados do claude-mem isolado, não misturar com Claude Code.

## Fechamento

Executar `scripts/finish-task-haos.ps1`.
