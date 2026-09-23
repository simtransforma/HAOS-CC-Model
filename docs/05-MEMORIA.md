# 05 Memoria

O mecanismo que faz a sessao de amanha saber o que a de hoje aprendeu.

---

## 1. As quatro fontes, da mais barata para a mais cara

A consulta para na primeira fonte que responde. Isso nao e auditoria, e uma escada.

| Nivel | Fonte | Para que serve | Custo |
|---|---|---|---|
| 1 | **Memoria duravel** | Decisao, erro ja cometido, procedimento, pegadinha. Arquivos markdown em disco | Quase zero |
| 2 | **Memoria de sessao** | "Ja resolvemos isso antes?" Busca semantica no historico | Baixo |
| 3 | **Fonte viva** | O codigo, o servidor, a API de verdade | Medio |
| 4 | **Base de conhecimento** | Documento longo, historico de material, contexto de dominio | Medio |

### A regra de frescor

**Para estado que muda sozinho, a memoria nunca fecha a questao.**

Servico no ar, porta aberta, processo rodando, saldo, contagem: so o comando ao vivo responde.
Memoria sem confirmacao ao vivo e declaracao de **incerteza**, nao de fato. Se memoria e servidor
divergem, o servidor ganha e a memoria e corrigida no mesmo instante.

### A regra de camada degradada

Toda camada de memoria um dia falha. Quando a busca semantica cai, o comportamento certo nao e
concluir que nao existe: e **cair para a camada de baixo e declarar no relatorio que pulou a camada**.

> Tempo esgotado numa ferramenta **nunca** e prova de ausencia de conhecimento.
> Ausencia num indice desatualizado **nunca** e prova de inexistencia.

Essa e a mesma lei de verificar antes de afirmar, aplicada a propria memoria.

---

## 2. Como marcar a fonte

Toda afirmacao de fato sai com uma etiqueta que diz de onde veio. Isso permite a quem le caçar
premissa fraca sem esforco.

| Situacao | Etiqueta |
|---|---|
| Verifiquei ao vivo agora | `[verifiquei: <comando> -> <o que vi>]` |
| A memoria diz, nao confirmei | `[memoria: <arquivo>, <N dias> -> a confirmar]` |
| Deducao nao testada | `[hipotese]` ou `[a confirmar]` |

Duas regras sobre isso.

1. **Etiqueta de verificacao exige rastro.** Se voce diz que verificou, a chamada da ferramenta tem
   que estar visivel na conversa. Etiqueta sem rastro e teatro, e teatro e proibido.
2. **Etiqueta mentirosa e pior que palpite honesto.** Dizer que verificou sem ter rodado nada destroi
   a confianca em todas as outras etiquetas.

---

## 3. O que vira memoria e o que nao vira

A memoria mais util e a menor. Poluir custa mais do que esquecer trivialidade.

### Vira memoria

| Tipo | Exemplo |
|---|---|
| **Pegadinha** | O parametro que parece opcional e derruba o servico se faltar |
| **Decisao** | Escolhemos A em vez de B por este motivo, nesta data |
| **Erro cometido** | Concluimos errado por olhar so uma fonte. O certo era checar tambem em X |
| **Procedimento novo** | O jeito certo de fazer isso, passo a passo |
| **Contradicao** | O que estava registrado nao vale mais, e por que |

### Nao vira memoria

Tarefa rotineira que deu certo, sem nada novo. Status momentaneo. Numero que muda sozinho. Resumo do
que ja esta no codigo.

**Na duvida, nao registre.** Nao poluir vale mais que capturar trivialidade.

---

## 4. O anatomia de um registro

```markdown
# <tipo>_<assunto_curto>

**Data:** AAAA-MM-DD
**Tipo:** pegadinha | decisao | erro | procedimento | referencia
**Vale para:** <onde se aplica>

## O que aconteceu
Duas a cinco linhas. Fato, sem narrativa.

## Por que importa
O que quebra se a proxima pessoa nao souber disso.

## A regra que fica
Uma frase imperativa. E isso que a pessoa vai lembrar.

## Evidencia
[verifiquei: <comando> -> <o que vi>]
```

O tipo vai no nome do arquivo porque busca por texto no disco e a camada mais barata, e prefixo bom
faz a busca funcionar.

---

## 5. O ritual de fechamento

> **Nao incluido nesta versao publica.** O comando de fechamento (`/haos:evoluir` no sistema de
> origem) nao vem neste pacote: nenhum arquivo em `commands/` implementa as cinco fases abaixo. O
> que existe aqui e o conceito e o hook `session_end.py`, que so captura o que aconteceu no turno
> (ver `docs/04-HOOKS.md`). Escrever o comando de fechamento completo — com o portao de valor, o
> commit seletivo e o versionamento da memoria num repositorio separado — fica por sua conta; a
> descricao abaixo e o roteiro para voce construir o seu.

Toda tarefa termina com o mesmo comando. Ele faz cinco coisas, nesta ordem.

```
  FASE 0  Portao de valor
          Houve pegadinha, falha, decisao, correcao, procedimento novo ou contradicao?
             sim -> CAPITALIZAR      nao -> SO FECHAR
                |
  FASE 1  Escrever o registro duravel
                |
  FASE 2  Espelhar para o formato legivel (notas com links)
                |
  FASE 3  Versionar: commit da tarefa no repositorio do projeto
                |
  FASE 4  Versionar a memoria num repositorio proprio e privado
```

Tres decisoes de projeto que valem copiar.

**Uma. O portao de valor vem antes de tudo.** Sem ele a memoria vira diario e perde a utilidade.

**Duas. O repositorio e detectado pela sessao, nunca fixado.** Fixar o repositorio faz o fechamento
commitar no lugar errado quando voce troca de projeto. E, se a sessao estiver num diretorio que nao e
projeto, o fechamento bloqueia o commit e faz so o backup da memoria.

**Tres. A memoria mora num repositorio separado e privado.** Ela contem decisao interna, nome de
pessoa e detalhe de operacao. Nunca deve estar no mesmo lugar que o codigo que voce publica. **Este
modelo traz o mecanismo vazio, de proposito.**

---

## 6. O portao anti desistencia

Antes de escrever "bloqueado", "nao tenho acesso", "nao e possivel", "nao existe" ou "nao encontrei",
e obrigatorio esgotar quatro fontes, nesta ordem.

1. **Memoria duravel**: busca por texto pelo tema **e** pelo nome do servico.
2. **Skills**: a resposta muitas vezes esta numa skill que voce ainda nao leu. Procure pelo nome do
   servico.
3. **Credencial pelo nome da variavel** no seu arquivo de segredos. Nunca concluir "sem credencial"
   sem ter procurado o nome certo. Nunca reproduzir o valor.
4. **A fonte viva por outro caminho** alem do primeiro que voce tentou. Outro comando, outro host,
   outra instancia, o registro no banco em vez da pasta.

Se depois disso ainda estiver bloqueado, o relatorio diz **explicitamente o que foi tentado em cada
uma das quatro**. "Tentei de tudo" sem a lista quer dizer que nao esgotou.

Isso nasceu de um caso real: um agente declarou que nao tinha acesso a um servico depois de procurar
credencial em um unico lugar. O acesso existia, documentado numa skill que ele nunca abriu.
