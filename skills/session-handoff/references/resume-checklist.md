# Checklist de Retomada

Siga este checklist ao retomar trabalho a partir de um handoff, para
continuar com zero ambiguidade.

## Verificacao pre-retomada

- [ ] Ler o handoff inteiro antes de tomar qualquer acao.
- [ ] Verificar que voce esta no diretorio de projeto correto.
- [ ] Confirmar que a branch git bate (ou entender por que pode divergir).
- [ ] Checar o timestamp do handoff, quao desatualizado esta o contexto.

## Validacao de contexto

- [ ] Revisar a secao "Contexto Importante" com atencao.
- [ ] Entender toda premissa listada, ela ainda vale?
- [ ] Checar se algum bloqueio ja foi resolvido desde o handoff.
- [ ] Revisar "Pegadinhas Potenciais" para evitar armadilha conhecida.

## Verificacao de estado

- [ ] Rodar `git status` para ver o estado atual dos arquivos.
- [ ] Comparar a lista de arquivos modificados do handoff com o estado atual.
- [ ] Checar se alguma variavel de ambiente precisa ser setada.
- [ ] Verificar se servico/processo necessario esta rodando.

## Execucao da retomada

- [ ] Comecar pelo item 1 de "Proximos Passos Imediatos".
- [ ] Usar a tabela "Arquivos Modificados" como contexto de mudanca recente.
- [ ] Aplicar o padrao documentado em "Padroes Descobertos".
- [ ] Seguir o insight de arquitetura de "Visao de Arquitetura".

## Durante o trabalho

- [ ] Atualizar o handoff se surgir contexto novo relevante.
- [ ] Marcar item concluido em "Trabalho Pendente" a medida que terminar.
- [ ] Adicionar bloqueio/pergunta nova conforme surgir.
- [ ] Considerar criar um handoff novo se a sessao ficar longa.

## Sinal de alerta: pare e verifique

Se encontrar qualquer um destes, pause e verifique o contexto antes de
continuar:

1. **Arquivo citado no handoff nao existe**, o codebase pode ter mudado
   significativamente.
2. **Branch divergiu bastante**, checar `git log` por commit recente.
3. **Premissa claramente invalida**, reavaliar a abordagem.
4. **Bloqueio marcado como nao resolvido agora esta travando o trabalho**,
   escalar ao dono.
5. **Arquitetura mudou**, reexplorar antes de continuar.

## Comandos rapidos

Depois de ler o handoff, estes comandos ajudam a verificar o estado
(todos de LEITURA, seguros para o main rodar direto, ver CLAUDE.md §1.a):

```bash
# Checar branch atual e status
git branch --show-current
git status

# Ver commit recente (comparar com o handoff)
git log --oneline -10

# Checar processo em background mencionado no handoff
ps aux | grep [nome-do-processo]

# Verificar variavel de ambiente (so o NOME, nunca o valor)
env | grep [nome-da-variavel] | cut -d= -f1
```

## Avaliacao de qualidade do handoff

Avalie a qualidade do handoff para saber se precisa explorar mais:

| Aspecto | Bom | Precisa explorar mais |
|---|---|---|
| Proximo passo | Claro, acionavel | Vago ou ausente |
| Referencia de arquivo | Caminho/linha especifico | Descricao generica |
| Decisao | Motivo incluido | So o resultado |
| Contexto | Quadro completo | Lacuna ou premissa nao dita |

Se mais de um aspecto cair em "Precisa explorar mais", gaste tempo
reexplorando o codebase antes de continuar a implementacao.

---

Origem: Codex, 20/09/2026 (`references/resume-checklist.md`). Traduzido para
PT-BR; comandos de leitura confirmados contra a allowlist real do guard
(CLAUDE.md §1.a).
Credito: Gian Marco Menegussi Scaglianti.
