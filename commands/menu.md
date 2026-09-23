---
description: Menu principal do HAOS — escolha departamento, agente, modo de operação ou rito
---

# /haos:menu — Menu Principal

Apresente ao usuário o menu interativo do HAOS de forma limpa e organizada. Após mostrar, aguarde a escolha e roteie para o comando/agente apropriado.

## Formato a apresentar

```
🧠 HAOS — HAU Autonomous Operations Squad
─────────────────────────────────────────

🎛️  OPERAÇÃO
  /haos:rito             Pipeline Rito v2 (13 fases — marketing/lançamento)
  /haos:setup            Wizard de configuração / reconfiguração
  /haos:agentes          Listar todos os 30 agentes
  /haos:departamentos    Listar os 8 departamentos
  /haos:base             Visão geral do sistema (versão, contagem, status)

🏛️  DEPARTAMENTOS (8) — broadcast pro entry-point
  /haos:conselho         Estratégia + decisões críticas
  /haos:criativo         Copy, design, vídeo, social
  /haos:trafego          Mídia paga, tracking
  /haos:dados            Análise, BI, pesquisa
  /haos:funnel           Funis, automação, CRM, email
  /haos:produto          PM, UX, dev frontend/backend
  /haos:orquestracao     QA, PM, compliance, devops
  /haos:seguranca        Chuck Norris + concierge

👤 AGENTES DIRETOS (30) — delegação 1:1
  Use /haos:agentes para a lista completa, ou invoque direto:
  /haos:cmo  /haos:estrategista-chefe  /haos:diretor-criativo  /haos:dev-backend  ...

❓ Como prosseguir?
  Digite o comando desejado, OU descreva sua demanda em linguagem natural
  que eu classifico e roteio (modo Concierge, padrão).
```

## Regras
- **Tom:** direto, sem floreio. O HAOS é técnico.
- **Após apresentar:** aguarde input. Se o usuário descrever uma demanda em vez de escolher comando, atue como Concierge (classificar intenção → rotear).
- **Idioma:** PT-BR sempre.
- **Não auto-executar nada** sem o usuário pedir.
