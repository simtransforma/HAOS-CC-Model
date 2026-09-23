# Seguranca

O que este sistema protege, o que ele **nao** protege, e como reportar problema.

---

## 1. O modelo de ameaca

Um sistema de agentes com acesso a shell, disco e rede tem quatro superficies. Este modelo trata as
quatro de jeitos diferentes, e e importante saber qual e qual.

| Superficie | Ameaca | O que o sistema faz |
|---|---|---|
| **Acao destrutiva do proprio agente** | O modelo executa algo irreversivel por engano ou por instrucao ambigua | Trava por hook antes da ferramenta rodar. Falha fechada |
| **Vazamento de segredo** | Chave aparece em log, relatorio, commit ou resposta | Redacao antes da escrita em disco (automatica, pelo `redact.py`) e regra de citar so o nome da variavel. A varredura de segredo antes do commit e no historico **voce liga** (gitleaks + gancho local, ver secao 4) — este pacote traz a config, nao a automacao pronta |
| **Cadeia de suprimentos** | Skill ou plugin de terceiro traz codigo malicioso | Triagem de quatro etapas antes de instalar. Permissao critica bloqueia sem negociacao |
| **Injecao por conteudo** | Um arquivo, pagina ou resposta de API carrega instrucao disfarcada | Conteudo lido e **dado**, nunca comando. Acao externa exige autorizacao humana |

---

## 2. O que o sistema protege

- **Mutacao nao revisada.** O orquestrador nao escreve, nao apaga e nao envia. Isso e travado, nao
  combinado.
- **Caminho sensivel.** Os proprios arquivos de guarda e o arquivo de configuracao dos hooks sao
  inacessiveis para escrita pelo orquestrador, fixo no codigo. Sem isso a trava se desarma sozinha.
  A pasta de segredo do SEU projeto **nao** entra nessa lista fixa por padrao: declare-a em
  `HAOS_GUARD_PROTECTED` (ver `docs/04-HOOKS.md`) para que ela receba a mesma protecao.
- **Comando encadeado.** Uma cadeia so passa se **todas** as partes forem leitura.
- **Envelopador opaco.** Comando do tipo "roda esse script" e bloqueado por natureza, sem tentar ler o
  conteudo. Lista de proibicao por texto falha aberta.
- **Segredo em log.** A redacao acontece antes da escrita, preservando o nome do campo e removendo o
  valor.
- **Acao externa.** Publicar, enviar, gastar e ativar exigem autorizacao humana explicita, sempre.

---

## 3. O que o sistema NAO protege

Seja honesto sobre isto antes de confiar demais.

- **Nao e caixa de areia.** Um agente com permissao de shell pode fazer o que a conta do sistema
  operacional permitir. A trava reduz a superficie, nao elimina. Para isolamento de verdade, rode em
  container ou maquina dedicada.
- **Nao substitui permissao do sistema operacional.** Rode com a conta de menor privilegio possivel.
- **Nao valida o conteudo das skills que voce escreve.** A triagem cobre skill de terceiro. O que voce
  escreve e responsabilidade sua.
- **Nao impede voce de desligar a trava.** O guard so desliga se um humano remover o hook do
  `settings.json` ou apagar o arquivo. O modelo nunca deveria fazer isso, e nao tem permissao de
  editar o proprio guard nem o arquivo de configuracao dos hooks, mas a decisao final e humana.
- **Nao protege o que voce colocou em repositorio publico por engano.** Depois de publicado, considere
  vazado. Rotacione.

---

## 4. Boas praticas de quem instala

1. **Nunca ponha segredo em arquivo versionado.** Nem em exemplo, nem em comentario, nem em teste.
2. **Ligue a varredura de segredo antes do commit.** Em gancho local e tambem na sua esteira.
3. **Varra o historico, nao so o estado atual.** Repositorio que ja foi privado carrega tudo que
   entrou enquanto era privado. Abrir a visibilidade expoe o historico inteiro.
4. **Rode com a conta de menor privilegio.** Se o agente nao precisa de elevacao, nao de elevacao.
5. **Revise skill de terceiro antes de instalar.** Permissao de leitura em diretorio de chave de
   acesso ou de credencial de nuvem e bloqueio imediato.
6. **Preserve evidencia antes de consertar.** Se algo suspeito acontecer, salve o registro antes de
   mexer no sistema. Consertar primeiro apaga a prova.
7. **Rotacione ao menor sinal.** Segredo que pode ter vazado ja vazou, para efeito de decisao.

---

## 5. Reportando uma vulnerabilidade

Se voce encontrar um problema de seguranca neste modelo, **nao abra uma issue publica**.

Use o canal privado de reporte de vulnerabilidade do repositorio, na aba de seguranca do GitHub.
Descreva o que voce encontrou, como reproduzir, e qual o impacto. A resposta sai em ate cinco dias
uteis.

Se o problema for no Claude Code, e nao neste modelo, reporte a Anthropic pelos canais oficiais.

---

## 6. Escopo

| Dentro do escopo | Fora do escopo |
|---|---|
| Falha que permite ao orquestrador burlar a trava | Falha do proprio Claude Code |
| Caminho que expoe segredo em log ou commit | Configuracao errada da sua instalacao |
| Defeito na triagem de skill de terceiro | Skill maliciosa que voce instalou ignorando a triagem |
| Exemplo neste repositorio que contenha dado real | Problema no seu servidor |
