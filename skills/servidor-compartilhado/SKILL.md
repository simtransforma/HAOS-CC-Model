---
name: servidor-compartilhado
description: >-
  Padrao "leia antes de agir" para o servidor unico de producao HAOS.
  Esta skill descreve um PADRAO GENERICO de operacao em servidor compartilhado
  com varios stacks (automacao, multi-agente, dashboards, landing pages) atras de
  reverse-proxy com TLS. Detalhes especificos do ambiente (IPs, dominios, nomes
  de containers, paths absolutos, regras de cron, credenciais) sao mantidos em
  runtime privado fora deste repositorio publico. Use antes de qualquer tarefa
  de deploy, troubleshooting, scaling, reconfiguracao ou auditoria.
metadata:
  version: "1.1"
  autor: Gian Marco Menegussi Scaglianti
  marca: HAOS
  nota: |
    Esta skill descreve um padrao generico. Detalhes de infra especificos do
    ambiente sao mantidos em runtime privado.
---

# HAOS Server Map (padrao "leia antes de agir")

> Esta skill descreve um **padrao generico** de operacao em servidor unico de
> producao. Os valores reais (IPs, hostnames, paths absolutos, credenciais,
> nomes de container, regras de firewall) ficam em runtime privado fora deste
> repositorio publico. O texto abaixo descreve a ESTRUTURA do mapa, nao o
> conteudo dele.

---

## Padrao de acesso

Acesso administrativo se da por SSH com chave dedicada, referenciada por NOME
de variavel de ambiente (nunca valor) num arquivo de secrets local. O servidor
fica atras de um reverse-proxy com TLS, e apenas as portas estritamente
necessarias sao publicas. Tudo o mais escuta em loopback.

**Regras universais:**
- Nunca expor valores de secrets em resposta, log ou commit; so NOMES de variavel.
- Comandos curtos e individuais; pipelines longos numa unica sessao SSH sao
  fragilizados por instabilidade de rede.
- `df -h` antes de qualquer operacao pesada (pull grande, dump, build).

---

## Estrutura do mapa real (mantido em runtime privado)

O mapa real do ambiente segue este indice — **carregue do runtime privado, nao
deste repositorio**:

1. **Host** — hostname, provedor, regiao, OS/kernel, dimensoes (CPU/RAM/swap/disco), uptime.
2. **Containers por stack** — automacao, multi-agente, painel/admin, email marketing, mensageria, fluxos conversacionais, object storage, gerenciador de tarefas, dashboards/sites publicos, RAG, monitoramento e infra base. Para cada container: imagem, porta interna, proposito.
3. **Runtimes de IA** — agente CLI no host, runtimes em container, runtime via harness. Para cada um: tipo (CLI vs container), onde mora, autenticacao, diretorio de skills.
4. **Rede / exposicao** — quais portas sao publicas; demais em loopback; caminhos de entrada (reverse-proxy direto vs tunnel para servicos internos).
5. **Dominios -> destino** — tabela de roteamento (host rule -> container:porta) para cada caminho de entrada.
6. **Bancos de dados** — engines, propositos, usuarios. Nenhum exposto publicamente. Backup verificado antes de qualquer mudanca.
7. **Paths-chave** — diretorio de secrets, clone canonico de skills, broker de secrets, sandbox auditada, ops por servico, backups, scripts de manutencao, configs de proxy/tunnel/WAF.
8. **systemd** — services e timers (proxy, fail2ban, auditoria, refresh, dashboards internos, coleta de metricas).
9. **cron** — jobs agendados (backup geral, backup do orquestrador de fluxos, self-heal/health check, sync de vault, ETLs, snapshots de memoria, sync de skills, monitores de seguranca, alertas de saldo).
10. **Firewall** — UFW (allow do estritamente necessario), iptables owner-match para sandbox, fail2ban (jail SSH).
11. **Backups** — geral diario, n8n/orquestrador semanal off-site, snapshots semanais, retencao curta local + copia segura off-site, DR testado.
12. **Seguranca / sandbox** — broker de secrets (agentes chamam APIs sem ver chaves), sandbox auditada de funcionario, WAF, fail2ban, regras de owner-match.

---

## Regras operacionais (vale em qualquer ambiente HAOS)

1. **NAO reiniciar em cascata** servicos com sessao stateful (ex.: integrador de mensageria). Self-heal + monitor cuidam; um restart por vez e validar antes do proximo.
2. **Backup verificado ANTES de mexer** em banco, volume ou stack critica. Backup nao testado nao conta.
3. **Distinguir CLI de container** ao inventariar runtimes; nao procurar container para CLI no host.
4. **Cap de concorrencia em agentes de IA** quando dividirem o mesmo plano/rate-limit upstream.
5. **Tunnel/proxy: alterar ingress = editar config + restart do servico do tunnel.** NAO mexer no DNS dos hostnames roteados pelo tunnel sem coordenar.
6. **Skills: fonte unica = repo canonico.** Editar no repo -> `git pull` no clone local do servidor -> rodar o script de sync. Editar dentro de container = perda garantida.
7. **Secrets: so via broker ou arquivo `.env` perm 600.** Nunca colocar chave em codigo/compose/repo. Nunca printar valores; so NOMES.
8. **Monitorar disco.** Retencao local de backup curta; copia segura off-site diaria. Pruning de imagens com cuidado.
9. **Sandbox de funcionario e auditada.** Nao desabilitar guard/audit/alerts/owner-match sem aprovacao explicita + revisor de seguranca na call.
10. **SSH instavel: comandos curtos e individuais.**
11. **Auth de runtime privilegiado (ex.: Max OAuth) e root-only.** Usar fluxo interativo, nao token-setup.
12. **Producao e sagrada.** Mudanca em prod = rollback planejado + janela + registro. Staging antes de prod sempre que houver.

---

## Specialist Routing

| Demanda | Agente |
|---|---|
| Infra, deploy, containers, proxy, tunnel, DNS, backup, scaling, troubleshooting de servidor | **@devops** |
| Apps, APIs, scripts, codigo dos servicos | **@dev-backend** (ou **@dev-frontend** para UI) |
| Auditoria, seguranca, vulnerabilidades, WAF, revisao de broker/sandbox, hardening | **@chuck-norris** (em par com @devops em mudanca de WAF/firewall) |

> Mudanca em WAF/CDN/firewall = revisao obrigatoria com @chuck-norris. Acesso SSH novo = aprovacao @chuck-norris.
