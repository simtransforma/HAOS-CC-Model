---
name: haos-auditoria-master
description: >-
  Playbook de auditoria master de um sistema HAOS, aplicavel ao ambiente LOCAL e
  a um servidor com multiplos runtimes de IA. Use quando o pedido for "auditoria
  master", "auditoria completa do sistema", "vasculha tudo, acha buraco e ponta
  solta", "audita o servidor / os runtimes", "caca o que ta quebrado ou fora do
  lugar", ou antes de uma rodada de limpeza, hardening ou governanca geral.
  Cobre diagnostico READ-ONLY em paralelo, consolidacao P0/P1/P2, correcao em
  ondas com OK explicito, conselho de lentes opostas, second-opinion externo com
  triagem critica, docs em modelo fonte-viva e fechamento. Nada e corrigido sem
  aprovacao.
metadata:
  version: "1.0"
  autor: Gian Marco Menegussi Scaglianti
  marca: HAOS
  origem: >-
    Procedimento real executado em 21-23/07/2026 (auditoria geral em 4 frentes,
    correcao em 3 ondas, second-opinion nos hooks criticos, migracao dos docs
    para o modelo fonte-viva).
---

# HAOS Auditoria Master (playbook)

Auditar um sistema HAOS inteiro sem quebrar nada e sem inventar problema. O metodo
tem uma unica lei acima de todas: **Regra #0, verificar antes de afirmar (VBA)**.
Auditor que crava sem evidencia produz correcao errada em cima de premissa falsa,
que e pior do que nao auditar.

> Regra de bolso desta skill: **"nao achei em X" NUNCA e "nao existe".** Metade do
> que parece ponta solta e texto morto, e parte do que parece ponta solta e real
> mas nao esta onde o auditor olhou.

---

## a) Quando usar (gatilhos)

Dispare esta skill quando o pedido soar como:

- "auditoria master" / "auditoria completa do sistema"
- "vasculha tudo, acha buraco e ponta solta"
- "audita o servidor" / "audita os runtimes"
- "caca o que ta quebrado ou fora do lugar"
- "da uma varrida geral antes de eu mexer nisso"
- antes de hardening, limpeza grande, migracao de runtime ou entrega de governanca

**Nao use** para: debug de UM sintoma especifico (isso e troubleshooting pontual),
revisao de codigo de UM PR (isso e code review), inventario de rotina (isso e
heartbeat/monitor).

---

## b) Pre-requisitos

| Item | Por que |
|---|---|
| Leitura ampla (Read / Grep / Glob) | O diagnostico e 100% leitura |
| Ferramenta de sub-agentes (Agent) | O paralelismo e o que torna a auditoria viavel |
| Acesso SSH ao servidor, chave dedicada | Auditoria da camada de infra e runtimes |
| Guard em modo ENFORCE | O main ORQUESTRA, nao executa; o guard e a garantia disso |
| Mapa do ambiente carregado | Ver skill `servidor-compartilhado` (detalhes vivem em runtime privado) |

**Secrets:** a chave SSH, tokens e senhas sao referenciados SEMPRE por NOME de
variavel do arquivo master de secrets (padrao `MASTER.env`), nunca pelo valor.
Valor de segredo nao entra em resposta, log, relatorio, commit nem arquivo
temporario. Se a auditoria ENCONTRAR um segredo exposto, o achado descreve o
arquivo e a natureza do segredo, nunca o conteudo.

---

## c) Passo a passo (o metodo real)

### Passo 1. DIAGNOSTICO: N auditores READ-ONLY em paralelo

Spawnar um sub-agente auditor por frente independente, TODOS ao mesmo tempo.
Frentes que se provaram bem separadas no ambiente local:

| Frente | Escopo |
|---|---|
| (i) Nucleo | Hooks, gates/guards, arquivos de config, comandos slash, tarefas agendadas |
| (ii) Capacidades | Skills, agentes/SOULs, plugins, playbooks, duplicatas e orfaos |
| (iii) Infra | Servidor, containers, runtimes, cron, systemd, backups, firewall, disco |
| (iv) Memoria/cerebros | Indice x arquivos reais, contradicoes, drenos, espelhos, orfaos |

**Briefing obrigatorio de cada auditor:**

1. **SO LEITURA.** Proibido editar, mover, deletar, reiniciar, instalar. Se achar
   algo grave, ESCREVE no relatorio, nao conserta.
2. **Tag de fonte em todo achado:** `[verifiquei: <comando ou arquivo> -> <o que vi>]`.
   Sem tag com lastro, o achado e HIPOTESE e vai marcado como tal.
3. **Classificacao obrigatoria:**
   - **P0 (critico):** segredo exposto, perda de dado, servico caido, brecha de seguranca.
   - **P1 (importante):** funciona mas errado, fragil, duplicado, desalinhado do dono unico.
   - **P2 (cosmetico):** nomenclatura, doc desatualizado sem impacto, ruido.
4. **Cada achado tem 4 campos:** o que e, evidencia (comando + saida), impacto, fix proposto.
5. **Antes de cravar um NEGATIVO** ("nao existe", "sumiu", "nunca rodou"), checar por
   um SEGUNDO caminho e consultar a memoria. Um caminho so nao fecha negativo.
6. Formato de saida curto: tabela de achados + lista de "confirmados saudaveis"
   (o que foi checado e esta OK importa tanto quanto o que esta quebrado).

**Nesta fase NADA e corrigido.** Nem o "obvio de 1 linha".

### Passo 2. CONSOLIDACAO

O orquestrador junta os relatorios, deduplica (o mesmo problema aparece em 2-3
frentes com nomes diferentes), reclassifica quando a visao cruzada muda a
prioridade, e produz UM relatorio unico:

- Placar: quantos P0, P1, P2.
- Tabela por prioridade com evidencia e fix proposto.
- **Falsos alarmes desmentidos**, com a cadeia de evidencia que os derrubou. Esta
  secao e obrigatoria e e a que mais gera confianca no relatorio.
- Recomendacao de ondas de correcao (o que entra em qual onda e por que).

**Gate:** nada e corrigido sem OK explicito do dono do sistema. Relatorio primeiro,
mao no sistema depois.

### Passo 3. CORRECAO EM ONDAS (so apos o OK)

Executores sub-agentes em paralelo, um por area, **P0 primeiro**. Uma onda so
comeca quando a anterior fecha com evidencia.

**Regras duras da correcao:**

1. **Arquivar, NUNCA deletar.** O que sai de uso vai para `_archive/` (ou
   `_archive-<categoria>/`), FORA do diretorio que o sistema carrega, para nao
   voltar como namespace ativo.
2. **Backup antes de editar**, com sufixo datado, ex.: `arquivo.py.bak_wave1_AAAAMMDD`,
   guardado em pasta de backups do proprio componente.
3. **Segredo nunca em tela.** Mover valor para o arquivo de secrets, referenciar
   por NOME de variavel, destruir o arquivo exposto, confirmar que o consumidor
   continua funcionando. Nao ecoar o valor em nenhum momento.
4. **Regra #0 em tudo:** cada executor tambem verifica antes de afirmar que corrigiu.
5. **Uma mudanca por vez em componente stateful.** Corrigiu, validou, proxima.

**Conselho para decisao polemica.** Quando a correcao envolve trade-off de design
(o que fica no doc, quebrar compatibilidade, mudar contrato), spawnar sub-agentes
com **lentes OPOSTAS**: defensor da opcao A, defensor da opcao B, advogado do
diabo (ataca as duas). O orquestrador sintetiza e leva a decisao ja com os dois
lados escritos. Isso evita que a auditoria vire opiniao unica disfarcada de tecnica.

### Passo 4. SECOND-OPINION no codigo critico alterado

Rodar `/second-opinion` (Codex CLI, autenticado por login ChatGPT, sandbox
read-only, **sem gastar API key**) no codigo critico que a auditoria mexeu:
guards, hooks, scripts de backup, qualquer coisa que decida bloqueio/permissao.

**Triagem critica e obrigatoria.** O modelo externo NAO conhece o contexto HAOS.
Ele vai apontar coisa valida e coisa que e decisao deliberada. Separar sempre:

| Categoria | Exemplo real |
|---|---|
| Achado VALIDO | Bypass real da allowlist de leitura do guard (comando mutante passando como leitura) |
| Falso-positivo | Fail-open em JSON invalido, que e DELIBERADO (guard quebrado nunca pode travar a operacao) |
| Fora de modelo de ameaca | Ofuscacao adversarial extrema, quando o "atacante" e o proprio orquestrador COOPERATIVO |

Priorizar o que o operador digitaria SEM QUERER (mutacao natural), nao o que um
adversario faria de proposito. Aplicar em ondas e registrar a onda seguinte como
pendencia explicita, com a lista dos itens que ficaram de fora.

### Passo 5. DOCS EM MODELO FONTE-VIVA

Regra aprovada e nao negociavel: **documentacao de config guarda REGRA e
ROTEAMENTO, NUNCA INVENTARIO.**

| Tipo de informacao | Onde vive |
|---|---|
| Numero volatil (contagem de skills, containers, comandos, roadmap datado) | Vira PONTEIRO para a fonte viva (`docker ps`, heartbeat, manifesto do plugin, memoria, vault) |
| Ancora estavel (Zone ID, IP fixo, ID de container GTM, path canonico) | Fica HARDCODED no doc |

Motivo: numero em doc estatico nasce errado no dia seguinte e vira mentira que o
sistema inteiro repete. Aplicar isso ao arquivo de instrucoes principal e ao
bootstrap na mesma onda.

Complemento util: fechar a **matriz de donos unicos** (quem e fonte da verdade de
que conhecimento: SOULs, skills, regras, diario de sessao, marca, estado vivo,
narrativa, grafo). Espelho que divergir do dono se REGENERA a partir do dono,
nunca se edita no espelho.

### Passo 6. FECHAMENTO

1. Rotina de fechamento de tarefa (`finish_task`): commit + push do repo da sessao,
   espelho da memoria, push do repo privado de memoria.
2. `/haos:evoluir` para capitalizar os aprendizados da auditoria em regra duravel
   (o que quebrou vira memoria, o que se repetiu vira skill).
3. Registrar as pendencias NAO aplicadas de forma explicita e nominal (onda 2,
   itens adiados, decisoes que aguardam OK). Pendencia sem nome apodrece.

---

## d) Verificacao (sem isso a auditoria nao fecha)

Cada correcao entrega EVIDENCIA, nao adjetivo:

| Tipo de mudanca | Evidencia aceita |
|---|---|
| Hook / guard | Suite de teste passando (contagem antes -> depois), compilacao OK, guard nunca ficou quebrado no meio |
| Servico web | Health check com codigo HTTP na tela |
| Container / cron | Comando ao vivo mostrando estado, nao memoria |
| Repo / doc | Hash do commit e push confirmado |
| Segredo movido | Consumidor funcionando + arquivo exposto inexistente, sem exibir valor |
| Arquivamento | Listagem do destino + confirmacao de que a origem nao carrega mais |

**Regra dura:** auditor ou executor NUNCA declara conclusao sem `[verifiquei: ...]`
com lastro de comando no proprio turno. Tag mentirosa (dizer que verificou sem ter
rodado) e pior que chute honesto.

**Frescor:** para estado VIVO (container up/down, processo, porta, saldo), memoria
nao fecha o gate, so o comando ao vivo fecha. Se memoria e servidor divergem, o
servidor ganha e a memoria e atualizada.

---

## e) PEGADINHAS E ANTI-PADROES (secao critica)

Tudo aqui quebrou de verdade. Ler antes de comecar, nao depois.

### 1. Metade das "pontas soltas" e TEXTO MORTO

Doc, SOUL e config descrevem coisas que **nao existem mais**. Exemplo real: um SOUL
citava um espelho de sincronismo de arquivos (lsyncd) que nao existe no servidor.
O auditor tratou como "sistema quebrado" quando o quebrado era o TEXTO.

> **"achei no doc" NAO significa "existe no vivo".** Antes de abrir achado sobre um
> mecanismo, confirmar ao vivo que o mecanismo existe. Se nao existe, o achado e
> "documentacao descreve componente inexistente" (P2/P1 de doc), nao "componente
> falhando" (P0 de infra). A prioridade muda inteira.

### 2. O guard bloqueia o proprio auditor

Com o guard em ENFORCE, o orquestrador nao executa. Se o auditor tentar EXECUTAR
correcao, ele bate no guard e a auditoria trava.

> Auditor roda READ-ONLY. Correcao vai por sub-agente executor, que o guard libera.
> Isso nao e limitacao, e o desenho: separar quem OLHA de quem MEXE.

### 3. `git add -A` morre atomico em nome de DEVICE do Windows

Arquivo chamado `nul`, `con`, `aux`, `prn`, `com1`, `lpt1` no repo faz o `git add -A`
FALHAR INTEIRO (nao parcialmente). O commit da auditoria nao sai e a mensagem de
erro nao aponta o culpado com clareza.

> Sintoma: fechamento de tarefa falha sem motivo aparente. Checar `git status` por
> arquivo de nome de device. Isso ja causou falha de commit em auditoria real.

### 4. Rotina agendada travada quase nunca e a agenda

Rotina que dispara (lastRun confirmado) mas nao produz resultado costuma estar
apontando para um **PATH LEGADO** (por exemplo um diretorio de memoria congelado),
por causa da SKILL ou do config que ela carrega, nao da agenda.

> Antes de culpar o agendador, a UI ou "watermark", checar o PATH que a rotina
> escreve. Caso real: o digest semanal disparava certo e escrevia num diretorio
> congelado ha meses.

### 5. O Codex do second-opinion DERAILA em workdir do HAOS

Se o `/second-opinion` rodar dentro do diretorio de trabalho do HAOS, o Codex
carrega o bootstrap, se comporta como orquestrador (tenta delegar, tenta agir) e
ainda bate no guard.

> Rodar o second-opinion em **workdir NEUTRO**, modo texto, passando o diff ou o
> arquivo como conteudo. O revisor externo precisa ser burro de contexto de
> proposito, e por isso a triagem do passo 4 e obrigatoria.

### 6. Diagnostico ANTERIOR pode estar errado

Achado herdado de sessao passada NAO e verdade estabelecida. Caso real: "digest
travado por watermark/UI" era falso, a causa era path legado. Se a auditoria
comeca aceitando o diagnostico velho, ela conserta o problema errado.

> Reconfirmar ao vivo TODA premissa herdada antes de agir sobre ela.

### 7. Falso alarme e o subproduto natural da auditoria

Dois exemplos reais que quase viraram correcao desnecessaria:

- **Backup "vazio" de 210 bytes:** o tar era pequeno porque o volume esta
  genuinamente vazio (o proprio script documenta isso); os dados vivem no dump do
  Postgres, integro e com as tabelas certas.
- **Arquivo de hooks "ausente":** o auditor olhou so a subpasta `hooks/`; o
  instalador poe o arquivo na RAIZ do diretorio de dados, e ele existia, com log
  provando execucao.

> Todo achado NEGATIVO passa por segunda checagem por outro caminho antes de entrar
> no relatorio. A secao "falsos alarmes desmentidos" existe justamente para isso.

### 8. Auditoria generica quando o pedido era especifico

Pedido sobre UM subsistema nao autoriza varredura de tudo. Reler o pedido, nomear
o alvo exato e confirmar escopo antes de spawnar 4 auditores.

---

## f) Rollback

Nao existe passo sem volta nesta auditoria:

| Mudanca | Volta por |
|---|---|
| Edicao de arquivo | Backup datado gerado ANTES da edicao |
| Remocao de item | `_archive/`, que preserva o arquivo intacto |
| Qualquer coisa em repo | `git revert` / `git checkout` do commit anterior |
| Config de servico | Copia `.bak` do config + restart do servico |
| Segredo movido | Consumidor volta a ler do nome de variavel antigo (o valor nunca foi perdido, so mudou de casa) |

Se uma correcao NAO tem caminho de volta, ela nao entra na onda: vira item de
decisao para o dono do sistema, com o risco escrito.

---

## g) Aplicacao ao servidor multi-runtime

Auditoria no servidor segue o mesmo desenho, com dois cuidados a mais.

**1. SSH READ-ONLY, comandos curtos e individuais.** SSH instavel quebra pipeline
longo no meio e o auditor conclui coisa errada a partir de saida truncada. Nada de
`&&` encadeando dez comandos. Detalhes do ambiente (IPs, hosts, containers, paths,
cron) vem da skill `servidor-compartilhado` e do runtime privado, nunca hardcoded aqui.

**2. Cobrir TODOS os runtimes, sem tratar dois como um.** Inventario de runtimes de
IA tem no minimo 5 entradas:

| Runtime (exemplo) | Onde vive | Como checar (padrao) |
|---|---|---|
| Orquestrador principal | No host | Binario/config no host |
| Runtime A | Container | `docker ps` + health do endpoint |
| **Runtime B via-Runtime-A** | Harness/plugin do Runtime A | Versao via `docker exec` no container |
| **Runtime B standalone** | Diretorio de dados proprio, separado do container | Existencia e integridade do proprio diretorio/auth |
| Runtime C | CLI on-demand, NAO tem container | `--version` do binario + listar o diretorio |
| Runtime D | Container, com registry proprio | Estado do container + registry, nao so a pasta |

> **Regra anti-recorrencia (ja corrigido 2x em producao):** sempre que a tarefa
> disser "cobrir / travar / atualizar / inventariar runtimes", o checklist do
> Runtime B tem **DUAS entradas OBRIGATORIAS E INDEPENDENTES**: (a) via container
> do Runtime A e (b) standalone. Tratar como UM item e o erro classico: aconteceu
> duas vezes na producao real que originou esta skill.

**Pegadinhas especificas do servidor:**

- CLI on-demand nao aparece em `docker ps`. Nao achar container nao prova que o
  runtime nao existe (caso do Runtime C).
- Binario vendorizado nao aparece em `which`. Checar por dentro do container.
- "Copiar a pasta" quase nunca replica um runtime: pode haver registry em banco.
  Confirmar COMO o componente funciona antes de briefar qualquer sincronismo.
- Nao rodar CLI que disputa refresh token com um servico vivo (token rotativo de
  uso unico gera erro de reuso). Auditar leitura de estado, nao invocar o motor.
- `df -h` antes de qualquer operacao pesada; disco cheio transforma auditoria em
  incidente.

---

## Resumo operacional (cola rapida)

1. Spawnar auditores READ-ONLY em paralelo, um por frente. Nada e corrigido.
2. Consolidar em P0/P1/P2 com evidencia, fix proposto e falsos alarmes desmentidos.
3. Esperar OK. So entao corrigir, em ondas, P0 primeiro, com backup e `_archive/`.
4. Second-opinion no codigo critico alterado, com triagem de falso-positivo.
5. Docs viram regra e roteamento, numero volatil vira ponteiro.
6. Fechar com evidencia, `finish_task` e `/haos:evoluir`, pendencias nomeadas.

---

**Creditos:** Gian Marco Menegussi Scaglianti.
