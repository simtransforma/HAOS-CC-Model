# Checklist de Qualidade — Antes de Empacotar

Execute este checklist mentalmente após escrever o SKILL.md.

---

## Frontmatter

- [ ] `name` em kebab-case, 1-64 caracteres
- [ ] `description` contém: o que faz + frases-gatilho + contextos implícitos + instrução pushy
- [ ] `compatibility` definido (claude.ai / claude-code / ambos)
- [ ] `allowed-tools` definido se a skill usar ferramentas específicas (só Claude Code)

## Corpo do SKILL.md

- [ ] Tem menos de 400 linhas (idealmente < 300)
- [ ] Referencia `references/` se existir conteúdo detalhado
- [ ] Primeira linha após frontmatter explica o papel da skill em 1 frase
- [ ] Fluxo é sequencial e claro (numerado quando há ordem obrigatória)
- [ ] Grau de liberdade correto para cada seção (alta/média/baixa)
- [ ] Não explica coisas que Claude já sabe
- [ ] Inclui contexto específico do usuário se relevante

## Description (o mais crítico)

- [ ] Contém pelo menos 3 frases-gatilho explícitas
- [ ] Contém pelo menos 1 contexto implícito (quando usuário não usa as palavras exatas)
- [ ] Usa linguagem "pushy" ("Use esta skill sempre que...", "Nunca pule...")
- [ ] É suficientemente específica para não disparar em situações erradas

## Arquivos de Referência

- [ ] Arquivos em `references/` têm nomes descritivos
- [ ] SKILL.md instrui explicitamente quando ler cada referência
- [ ] Templates em `templates/` são completos e usáveis sem modificação

## Entrega

- [ ] ZIP criado corretamente (`zip -r nome.zip nome/`)
- [ ] ZIP copiado para `/mnt/user-data/outputs/`
- [ ] `present_files` chamado com o ZIP
- [ ] Preview do SKILL.md mostrado ao usuário (primeiras 30 linhas)
- [ ] Instruções de instalação fornecidas (Claude.ai e Claude Code)
