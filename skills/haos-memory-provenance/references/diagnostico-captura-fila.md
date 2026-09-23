# Diagnostico de captura e filas de memoria (adaptado ao HAOS)

O original e quase todo `[so no Codex]`: descreve o runtime isolado do Codex
(processo, bundle, banco SQLite proprio, CLI `haos_journal/diagnostics.py`).
O HAOS nao tem esse runtime; o equivalente funcional aqui e o `claude-mem`
(camada degradada, ver CLAUDE.md §0 camada 2) e os hooks de sessao em
`~/.claude/hooks`. Os PRINCIPIOS gerais (o que abaixo NAO e Codex-especifico)
continuam validos e sao a parte reaproveitavel desta skill.

## Preflight (adaptado)

1. `[so no Codex]` "confirmar o runtime Codex isolado, processo, bundle e
   banco antes de reiniciar". Equivalente HAOS: antes de mexer no `claude-mem`,
   confirmar o worker (`health` HTTP) sem tocar no servico `mnemoverse`/GBrain
   compartilhado; nao reiniciar servico alheio para diagnosticar o proprio.
2. Verificar saude/readiness do worker em snapshot consistente. Esse resultado
   NAO comprova que toda mensagem foi processada (health 200 != captura
   vetorial funcionando; caso real de 04/09/2026: worker saudavel, `/api/search`
   500).
3. Separar fila pendente/em processamento de itens concluidos antes de comparar
   snapshots no tempo. Fila menor pode ser exclusao, nao apenas sucesso;
   inspecionar o caminho de finalizacao antes de inferir "processou tudo".

## Provider e fila operacional (generico, reaproveitavel)

1. Diferenciar autenticacao (chave valida), limite individual da chave, saldo e
   limite upstream do provider (ex.: OpenRouter, usado hoje pelo `claude-mem`
   desde a migracao Gemini->OpenRouter de 17/05/2026). Uma chave aceita sem
   erro de auth nao prova saldo nem capacidade disponivel.
2. HTTP 429 exige serializacao, backoff e respeito a `Retry-After`; HTTP 402
   indica restricao de credito/orcamento. Nao trocar chave ou modelo, nem
   ampliar gasto, so para "testar se agora funciona".
3. Diagnostico usa somente categorias de erro permitidas para log. Nunca
   imprimir corpo bruto de excecao que contenha credencial. Resolver o
   segredo pelo NOME da variavel no MASTER.env antes de alegar "chave ausente"
   (gate anti-desistencia do CLAUDE.md de usuario, item 3).
4. Antes de retomar um backlog de fila, auditar os caminhos de abort, quota e
   finalizacao. Nao remover pendencia sem confirmar processamento duravel.
5. Qualquer correcao aplicada ao worker de memoria deve ser isolada (testes com
   dado sintetico, nao dado pessoal real de cliente/comprador), com plano de
   rollback. Nao aplicar a mesma correcao ao runtime principal do Claude Code
   sem validar separadamente.
6. Endpoint que so devolve contador nao equivale a endpoint de recuperacao.
   Reprocessar historico exige escopo limitado, deduplicacao e controle de
   custo; nao iniciar drenagem ilimitada de fila antiga sem OK do dono se isso
   implicar gasto de API.

## Aceite

Separar evidencia de: codigo corrigido, ativacao viva confirmada, captura indo
para frente a partir de agora, e historico (que pode continuar com lacuna).
Timeout ou exit code zero de um script de diagnostico nao substitui leitura do
resultado. Fechar o `/haos:evoluir` com o readback por destino descrito em
`references/diario-e-readback.md` e registrar qualquer pendencia real; nunca
declarar "memoria totalmente recuperada" havendo lacuna nao verificada.

---

Origem: Codex, 20/09/2026 (`diagnostico-captura-fila.md`). Adaptado: removida a
CLI exclusiva do Codex, mantidos so os principios de diagnostico de fila/rate
limit que se aplicam ao `claude-mem` e a qualquer provider de LLM do HAOS.
Credito: Gian Marco Menegussi Scaglianti.
