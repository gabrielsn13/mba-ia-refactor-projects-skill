# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

# Análise Manual

## Projeto 1 — `code-smells-project` (Python/Flask, API de E-commerce)

| # | Sev. | Problema | Local | Por que importa |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection (queries concatenadas, inclusive no login) | `models.py:28, 48-50, 58-61, 92, 109-111, 127-129, 174, 280, 291-297` | Bypass de login, vazamento/alteração de dados |
| 2 | CRITICAL | `/admin/query` executa SQL arbitrário e `/admin/reset-db` apaga tudo, sem autenticação | `app.py:47-78` | Qualquer cliente destrói/lê o banco |
| 3 | CRITICAL | `SECRET_KEY` e `DEBUG` hardcoded; `/health` devolve `secret_key` | `app.py:7-8`, `controllers.py:285-289` | Vazamento de segredo |
| 4 | CRITICAL | Senhas em texto puro, retornadas em `/usuarios` | `database.py:76-78`, `models.py:83, 99`, `controllers.py:130` | Exposição de credenciais |
| 5 | HIGH | Lógica de negócio/validação/notificações em controllers; `app.py` mistura rotas, SQL e admin | `controllers.py:24-62, 188-220`, `app.py:47-78` | Sem camadas, não testável |
| 6 | HIGH | Conexão global mutável (`check_same_thread=False`) | `database.py:4-10` | Race conditions, acoplamento |
| 7 | HIGH | Pedido sem transação/rollback; estoque checado e decrementado separadamente | `models.py:133-169` | Overselling, dados inconsistentes |
| 8 | MEDIUM | N+1 em pedidos (itens e produtos por loop) | `models.py:171-233` | Degrada com volume |
| 9 | MEDIUM | Serialização de produto/pedido e validações duplicadas | `models.py:12-21, 31-40, 304-313`, `controllers.py:24-96` | Manutenção cara |
| 10 | MEDIUM | `try/except` repetido devolvendo `str(e)`; sem handler central | `controllers.py` (todo) | Vaza detalhes internos |
| 11 | MEDIUM | `get_json()` sem checar `None`; tipos não validados | `controllers.py:87-90, 169, 239` | 500 em vez de 400 |
| 12 | LOW | `print` no lugar de logging | `controllers.py:8, 57, 179, 208-210` | Sem níveis/rastreio |
| 13 | LOW | Magic numbers (faixas de desconto) e strings (status/categorias) | `models.py:256-262`, `controllers.py:52, 242` | Regras escondidas |
| 14 | LOW | Imports não usados, `id` sombreando builtin, `cursor2/cursor3` | `models.py:2`, `database.py:2`, `app.py:4` | Legibilidade |

## Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

| # | Sev. | Problema | Local | Por que importa |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais hardcoded (`dbPass`, `paymentGatewayKey pk_live_...`, SMTP) | `utils.js:1-7` | Chave de pagamento live versionada |
| 2 | CRITICAL | Número do cartão logado em texto puro com a chave do gateway | `AppManager.js:45` | Violação PCI-DSS |
| 3 | CRITICAL | God Class `AppManager`: schema, seed, rotas, checkout, relatório | `AppManager.js:4-139` | Zero separação MVC |
| 4 | HIGH | `badCrypto` (base64 repetido, 10 chars), senha default `"123456"`, seed `'123'` em texto puro | `utils.js:17-23`, `AppManager.js:18, 68` | Senhas triviais de quebrar |
| 5 | HIGH | Endpoints admin e `DELETE /api/users/:id` sem autenticação | `AppManager.js:80, 131` | Leitura financeira/remoção abertas |
| 6 | HIGH | Estado global mutável (`globalCache`, `totalRevenue` sem uso) | `utils.js:9-15` | Memory leak, acoplamento |
| 7 | HIGH | Checkout sem transação; DELETE deixa matrículas/pagamentos órfãos | `AppManager.js:50-61, 131-136` | Inconsistência |
| 8 | MEDIUM | N+1 no relatório (courses→enrollments→users→payments) | `AppManager.js:83-127` | Performance |
| 9 | MEDIUM | Callback hell (5 níveis), erro do audit log ignorado | `AppManager.js:37-77` | Difícil manter |
| 10 | MEDIUM | Validação só de presença; erros como strings soltas, sem handler central | `AppManager.js:35-48` | API inconsistente |
| 11 | MEDIUM | `enrollments` pode ser `undefined`; ordem do relatório não determinística | `AppManager.js:92-93, 119` | Crash/inconsistência |
| 12 | LOW | Nomes abreviados (`u, e, p, cid, cc`) | `AppManager.js:29-33` | Legibilidade |
| 13 | LOW | Magic values (`"4"`, `'PAID'`, `10000`, `:memory:`) | `AppManager.js:7, 46`, `utils.js:19-22` | Regras escondidas |
| 14 | LOW | Código morto (`totalRevenue`), `console.log` no lugar de logger | `utils.js:10`, `AppManager.js:45`, `app.js:13` | Ruído |

## Projeto 3 — `task-manager-api` (Python/Flask + SQLAlchemy, parcialmente em camadas)

| # | Sev. | Problema | Local | Por que importa |
|---|---|---|---|---|
| 1 | CRITICAL | Senha com MD5 sem salt | `models/user.py:27-32` | Quebrável em segundos |
| 2 | CRITICAL | Hash de senha exposto na API (`to_dict` inclui `password`) | `models/user.py:21`, `user_routes.py:33, 85, 129, 209` | Vazamento de credenciais |
| 3 | CRITICAL | Segredos hardcoded (`SECRET_KEY`, senha SMTP) | `app.py:13`, `notification_service.py:9-10` | Credenciais versionadas |
| 4 | HIGH | Token falso (`fake-jwt-token-<id>`), nenhuma rota protegida, qualquer um cria `role=admin` | `user_routes.py:207-211, 52, 134` | Sem authn/authz |
| 5 | HIGH | Lógica de negócio, queries e validação dentro das routes; categorias dentro de `report_routes.py` | `task_routes.py`, `user_routes.py`, `report_routes.py` | Viola MVC |
| 6 | HIGH | `process_task_data` e constantes de `helpers.py` não usados; validações divergentes | `helpers.py:57-116` vs `task_routes.py:85-223` | Código morto, inconsistência |
| 7 | MEDIUM | N+1 (`User.query.get`/`Category.query.get` por task, `len(u.tasks)`, contagens em loop) | `task_routes.py:41-57`, `user_routes.py:22`, `report_routes.py:55-56, 163` | Escala mal |
| 8 | MEDIUM | Regra de overdue copiada 6x; serialização manual repetida; `Task.is_overdue()` ignorado | `task_routes.py:30-39, 71-80, 284-287`, `user_routes.py:171-180`, `report_routes.py:34-43, 132-135` | Duplicação |
| 9 | MEDIUM | `except:` nu, sem handler central | `task_routes.py:62, 137, 204, 236`, `user_routes.py:130, 149` | Esconde bugs |
| 10 | MEDIUM | Validação ausente (`get_json()` None, `int(priority)` sem try, `is_valid_color` não usado) | `report_routes.py:196`, `task_routes.py:113, 182, 261-264` | 500 em vez de 400 |
| 11 | LOW | APIs deprecated: `Model.query.get()`, `datetime.utcnow()` | `task_routes.py:42, 67`, `models/*.py`, `helpers.py:38` | Warnings/remoção futura |
| 12 | LOW | Imports não usados; `NotificationService` nunca usado | `app.py:7`, `task_routes.py:7`, `helpers.py:1-7` | Ruído |
| 13 | LOW | Magic numbers/strings (status, roles, tamanhos) apesar de constantes existentes | `user_routes.py:64`, `task_routes.py:99, 110` | Legibilidade |
| 14 | LOW | `print` no lugar de logging, `debug=True` + `host=0.0.0.0`, `type(x) == list` | `app.py:30-34`, `task_routes.py:149, 141` | Boas práticas |

---

# Construção da Skill

A skill `refactor-arch` fica em `.claude/skills/refactor-arch/` e `.github/skills/refactor-arch/` (conteúdo idêntico) em cada um dos 3 projetos.

**Arquivos**
| Arquivo | Papel |
|---|---|
| `SKILL.md` | Orquestra as 3 fases, define o gate de confirmação e o formato do relatório |
| `project-analysis.md` | Heurísticas agnósticas para detectar linguagem, framework, banco e arquitetura |
| `anti-patterns-catalog.md` | Catálogo AP-01..AP-17 + APIs deprecated, com sinais de detecção e severidade |
| `report-template.md` | Template do relatório (Fase 1 + auditoria) |
| `mvc-guidelines.md` | Camadas-alvo (config, database, models, controllers, views, middlewares, services) |
| `refactoring-playbook.md` | Receitas antes/depois (P1–P14) para cada anti-pattern |

**Decisões de design**
- Três fases com pausa obrigatória antes de qualquer alteração: (1) análise, (2) auditoria com relatório salvo em `reports/audit-project-N.md`, (3) refatoração só após "y".
- Agnóstica de tecnologia: o catálogo descreve sinais por conceito (credencial hardcoded, N+1, God class) com exemplos em Python e Node.js.
- Severidades CRITICAL/HIGH/MEDIUM/LOW com linhas exatas de cada achado.
- Fase 3 inicia com *baseline* de comportamento (chamadas reais) e termina com boot, comparação e grep de anti-patterns.
- Projeto parcialmente em camadas (projeto 3): melhora-se a estrutura existente em vez de recriar do zero.

**Desafios**
- Claude Code não estava disponível (plano Free); a skill foi executada pelo GitHub Copilot seguindo o mesmo `SKILL.md`.
- `sqlite3` nativo bloqueado pelo `allowScripts` do npm (projeto 2): resolvido com `prebuild-install`.
- Preservar contratos de API enquanto se corrige segurança: mudanças de comportamento foram listadas explicitamente em cada PR.

# Resultados

## Achados por projeto

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 4 | 4 | 5 | 3 | 16 |
| 2 — ecommerce-api-legacy | Node/Express | 5 | 3 | 5 | 3 | 16 |
| 3 — task-manager-api | Python/Flask + SQLAlchemy | 5 | 4 | 7 | 4 | 20 |

Relatórios completos: `reports/audit-project-1.md`, `-2.md`, `-3.md`.

## Antes / depois da estrutura

| Projeto | Antes | Depois |
|---|---|---|
| 1 | Poucos arquivos monolíticos (app/controllers/models/database misturados) | `src/{config,database,models,controllers,views,middlewares,...}` |
| 2 | `AppManager.js` (God class), `utils.js`, rotas e SQL misturados | `src/{config,database,models,controllers,views,middlewares,services,utils}` + `createApp(db)` |
| 3 | `app.py` global, `routes/` com lógica e queries, `models/`, `utils/helpers.py` não usado | `src/{config,database,models,controllers,views,middlewares,services,utils}` + `create_app()`; `app.py` raiz fino |

## Principais correções
- Credenciais/segredos hardcoded → variáveis de ambiente (`.env.example` em cada projeto).
- MD5/criptografia fraca → scrypt (P2) e hash werkzeug com migração do legado (P3).
- Tokens falsos/sem autorização → token assinado + controle por role (P3), `X-Admin-Token` (P2).
- N+1 → `joinedload`/queries agrupadas; SQL injection → queries parametrizadas.
- `except:` nus e `print` → handler de erro central e `logging`.
- APIs deprecated (`utcnow`, `Query.get`) → `datetime.now(timezone.utc)`, `db.session.get`.

## Checklist de validação (executado, por projeto)

| Item | P1 Flask | P2 Express | P3 Flask |
|---|---|---|---|
| Fase 1: linguagem, framework, banco, arquitetura e domínio corretos | [x] | [x] | [x] |
| Fase 2: achados com arquivo/linhas, por severidade, relatório salvo | [x] | [x] | [x] |
| Fase 2: pausa para confirmação antes de alterar código | [x] | [x] | [x] |
| Fase 3: estrutura MVC criada | [x] | [x] | [x] |
| Fase 3: aplicação sobe sem erros | [x] | [x] | [x] |
| Fase 3: endpoints respondem como antes (exceto mudanças intencionais) | [x] | [x] | [x] |
| Fase 3: grep de anti-patterns limpo | [x] | [x] | [x] |

## Logs de execução após a refatoração (exemplo, projeto 3, boot real)
```
GET  /health                              -> 200
GET  /tasks (sem token)                   -> 401 {"error":"Token ausente ou inválido"}
POST /users (role admin sem ser admin)    -> 403
POST /login                               -> 200 (token assinado)
GET  /tasks (com Bearer)                  -> 200
DELETE /users/1 (não admin)               -> 403
```
Nos projetos 1 e 2 a verificação foi equivalente: servidor iniciado como processo real e chamadas HTTP comparadas com o baseline anterior à refatoração (P2: 401 sem `X-Admin-Token`, 403 com token errado).

## Observações sobre a skill em stacks diferentes
- **Python/Flask (P1, P3):** a detecção por `requirements.txt` e imports funcionou bem; os anti-patterns de SQL injection, N+1 e `except:` nus foram encontrados de forma direta. APIs deprecated (`utcnow`, `Query.get`) só aparecem em P3.
- **Node/Express (P2):** os mesmos conceitos do catálogo (God class, callback hell, credenciais, criptografia fraca) foram mapeados para JS; a refatoração exigiu promisificar o sqlite e extrair um composition root.
- **Projeto parcialmente em camadas (P3):** a skill melhorou as camadas existentes em vez de recriar tudo, movendo lógica das rotas para controllers e extraindo categorias de `report_routes`.
- Limitação: a execução foi feita pelo GitHub Copilot lendo o `SKILL.md`, não pelo Claude Code.

## Evidências
Baseline e verificação pós-refatoração por projeto: chamadas reais (HTTP/test client) antes e depois, com diff contendo apenas as mudanças intencionais documentadas em cada PR (#3, #5, #7).

# Como Executar

**Skill**: no Claude Code, dentro do projeto, `claude` e depois `/refactor-arch`. Com GitHub Copilot, a skill é lida de `.github/skills/refactor-arch/`. A skill pausa após a auditoria; responda `y` para refatorar.

**Projetos**
```bash
# Projeto 1 e 3 (Python/Flask)
cd code-smells-project   # ou task-manager-api
pip install -r requirements.txt
cp .env.example .env     # e exporte as variáveis
python app.py            # (P3: python seed.py para dados iniciais)

# Projeto 2 (Node/Express)
cd ecommerce-api-legacy
npm install
cp .env.example .env
npm start
```
No projeto 3, envie `Authorization: Bearer <token>` (obtido em `POST /login`); no projeto 2, `X-Admin-Token` para relatório e DELETE.