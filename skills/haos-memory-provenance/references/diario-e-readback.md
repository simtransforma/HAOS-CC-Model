# Diario global e readback remoto (adaptado ao HAOS)

Consolida os dois documentos de origem (`diario-global.md` + `readback-remoto.md`
do Codex) porque no HAOS os dois mecanismos convergem no mesmo executor: o
`/haos:evoluir`. Onde o texto original descrevia infraestrutura exclusiva do
Codex (`.codex/haos-automatic-memory.json`, `finish-task-haos.ps1 -Integrator`,
runtime Codex isolado), o item vem marcado `[so no Codex]` com o equivalente
nosso ao lado.

## Diario literal

1. O diario literal (transcript bruto de sessao) pertence somente ao Obsidian
   privado, hoje em `<SEU_VAULT>/01-Sessoes/`.
   Nunca versionar Chat, anexo ou transcript, nem enviar esse conteudo cru ao
   Mnemoverse ou GBrain. So a SINTESE curada (memoria eterna) vai para esses
   destinos.
2. `[so no Codex]` a config `.codex/haos-automatic-memory.json` com
   `mode=local`/`pilot`. Equivalente aqui: o hook `session_start.py` de
   `~/.claude/hooks` decide o que injeta no boot; nao existe modo pilot
   separado, o guard ENFORCE (CLAUDE.md §1) e quem trava mutacao indevida.
3. O primeiro registro de uma sessao nova e prospectivo: nao importar historico
   antigo por presuncao. Fonte de sub-agente, execucao em nuvem ou identidade
   divergente nao recebe cobertura presumida so porque a sessao principal tem.
4. Opt-out por sessao (se configurado) permanece ativo apos qualquer reativacao
   global; desligar e religar nao recupera o intervalo recusado. Nao remover
   vetos individuais em massa.
5. O `/haos:evoluir` fecha tarefas com identidade e revisao persistentes
   (`sessionId`+`taskKey`+`revision`, ver Fase 6/8). `SO FECHA` nao fabrica
   aprendizado; `CAPITALIZA` atualiza conhecimento tematico e usa
   `finish_task.ps1` para commit local seletivo + espelho de memoria.
6. Destinos locais reais do HAOS: repo da sessao (sua raiz canonica), `<SEU_REPO_DE_MEMORIA>`
   (GitHub privado) e Obsidian. `<SEU_REPO_DE_SKILLS>` (master de skills/agentes) **nao** e
   destino deste fluxo de memoria de sessao. Push continua exigindo OK
   explicito do dono.
7. No GBrain, fila de ingestao (dream noturno) nao comprova ingestao concluida.
   Confirmar com `mcp__gbrain__get_page` ou `mcp__gbrain__search` pela mesma
   pagina/termo antes de declarar indexado.
8. No Mnemoverse, uma chamada que falha (timeout, erro, credencial) fica
   pendente. Nao substituir por credencial de outro escopo. Preservar o resumo
   sanitizado local para retomar depois.

## Readback remoto

1. Registrar tarefa e revisao (`sessionId`+`taskKey`+`revision`) antes do
   trabalho de fechamento; nao criar uma tarefa nova por turno se a mesma
   sessao+tema ja estiver aberta no log.
2. Validar fontes e revisao independente antes de capitalizar (Fase 2 do
   evoluir, reconciliacao anti-duplicata).
3. Gravar e reler os destinos locais (repo, Obsidian, `<SEU_REPO_DE_MEMORIA>`) antes de
   qualquer transporte remoto (Mnemoverse/GBrain).
4. Mnemoverse: usar `memory_read` buscando um trecho do conteudo recem-escrito
   como readback (item E4 do evoluir); busca semantica ampla e complemento, nao
   substituto da igualdade textual.
5. Marcar a tentativa de envio com identidade de tarefa, revisao e conteudo.
   Falha ambigua exige readback; nunca reenviar cegamente nem reescrever o
   conteudo so para contornar rejeicao por duplicidade ou baixa relevancia.
6. GBrain: usar a instancia compartilhada real do grupo
   (`<SEU_CAMINHO_DO_GBRAIN>`) e leitura de pagina/termo equivalente a
   `compiled_truth`. Resposta de erro (`isError=true` ou equivalente) nunca
   comprova sucesso.
7. Recibos precisam corresponder a tarefa, revisao e payload. Fila local nao
   equivale a ingestao; somente readback permite declarar o destino concluido.
8. `SO FECHA` exige que a decisao (nenhum aprendizado novo) tambem seja
   verificavel, nunca "nao lembro se tinha algo" sem checar. Se houver tarefa
   conhecida ainda aberta/reaberta no log, pedir uma unica retomada explicita;
   na reentrada informar a pendencia sem criar loop.

O fechamento ocorre DEPOIS da resposta final ser dada ao dono: nao corrige
retroativamente uma afirmacao ja enviada. O comando `/haos:evoluir` roda direto
(sem pedir OK) por decisao do dono; isso nao dispensa o readback
descrito acima.

O diario literal continua privado. Apenas sintese curada vai para os
repositorios, Obsidian, Mnemoverse e GBrain. Commit local nao equivale a push.
`claude-mem` com health OK pode continuar com backlog de indexacao (camada
degradada, CLAUDE.md §0 camada 2); avaliar essa fila separadamente do
fechamento da tarefa.

---

Origem: Codex, 20/09/2026 (`diario-global.md` + `readback-remoto.md`).
Credito: Gian Marco Menegussi Scaglianti.
