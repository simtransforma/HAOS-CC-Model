---
name: haos-project-sanitation
description: >-
  Saneamento medido e conservador de residuo de repositorio (cache, build,
  arquivo orfao), audit-only por padrao, com baseline, classificacao de
  residuo e comparacao antes/depois. Use quando o dono pedir para "limpar o
  repo", "tirar lixo do projeto", "por que essa pasta esta gigante" ou antes
  de preparar um repo para manutencao. Diferente de `haos-structural-refactor`
  (esse refatora CODIGO/arquivo gigante; esta so remove RESIDUO, nunca muda
  logica).
---

# HAOS Project Sanitation

Use para organizar repositorio, reduzir residuo ou preparar uma base para
manutencao. O modo padrao e **auditoria sem remocao**.

## Fluxo

1. Capturar baseline: raiz resolvida, branch, `git status`, tamanho relevante,
   comando de teste/build existente e alteracao preexistente (nao confundir
   mudanca alheia com residuo).
2. Inventariar candidato sem seguir junction/symlink e sem atravessar a raiz
   do repo (nunca varrer outra arvore de projeto irma nem outro repo a partir de uma
   tarefa de sanitation do HAOS).
3. Classificar cada candidato como:
   - `GERADO_RECRIAVEL`: cache/build comprovadamente reproduzivel;
   - `STALE_COM_EVIDENCIA`: sem referencia e com substituto confirmado;
   - `ATIVO_OU_DESCONHECIDO`: preservar;
   - `SENSIVEL`: preservar e redigir do relatorio (segredo, dado pessoal).
4. Mostrar impacto estimado e mecanismo de rollback antes de qualquer remocao.
5. Remocao, movimento recursivo ou limpeza externa exige OK explicito do dono
   no turno (CLAUDE.md §3, item 6; nunca `rm`/`clean`/`reset --hard` como
   atalho, esses comandos ja sao bloqueados por padrao no main, ver §1.c).
6. Quando autorizado, alterar somente o conjunto aprovado.
7. Comparar tamanho, status e verificacao antes/depois.

## Regras bloqueantes

- Worktree sujo nunca autoriza apagar ou reverter mudanca (ver
  `superpowers:using-git-worktrees`: proibido remover worktree de sessao
  de outra ferramenta/IDE apontada pelo seu setup, sao sessoes de terceiro).
- Nao classificar por nome apenas; provar origem e recriabilidade.
- Nao tocar em `.git`, cofre (`_secrets/`), banco, memoria eterna, sessao do
  usuario ou outro runtime sem escopo explicito. Caminho `_secrets/`,
  `.githooks/` e hooks-guard sao ENFORCE TOTAL (CLAUDE.md §1.c): bloqueados
  para o main nos dois regimes, sempre delega.
- Nao instalar formatador/linter novo so para justificar uma limpeza.
- Se a verificacao piorar depois da limpeza, parar e restaurar apenas o que
  esta rotina alterou.

## Evidencia

O relatorio deve listar manifesto de candidato e removido, bytes antes/depois,
checagem executada, falha e risco residual. Nunca registrar valor secreto,
so o nome da variavel quando aplicavel.

---

Origem: portado do Codex (`<toolkit-codex-interno>/.agents/skills/haos-project-sanitation`,
20/09/2026). Adaptado: cruzado com `haos-structural-refactor` (para deixar
claro que sanitation NAO e refatoracao de codigo) e com os gates reais do HAOS
(ENFORCE TOTAL §1.c, worktrees do superpowers, OK explicito do dono §3).
Credito: Gian Marco Menegussi Scaglianti.
