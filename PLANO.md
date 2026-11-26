# Plano: Concluir e validar o desafio de refatoração arquitetural

**Fonte da especificação:** README.md
**Criado em:** 2026-11-25
**Legenda:** `[ ]` pendente · `[~]` em andamento · `[x]` feito · `[!]` falhou

## Requisitos
| # | Requisito | Estado |
|---|-----------|--------|
| R1 | Skill completa com SKILL.md e cinco áreas de referência | feito |
| R2 | Skill executada nos três projetos com três fases verificáveis | feito: Antigravity CLI em cópias do código original |
| R3 | Relatórios de auditoria persistidos | feito |
| R4 | Código refatorado dos três projetos commitado | feito |
| R5 | README com análise, construção, resultados e execução | feito |
| R6 | Validação independente por boot e endpoints | feito: boot + endpoints nas duas execuções |
| R7 | Validação com Claude Code, Gemini CLI ou Codex | feito: Antigravity CLI 1.5.17, sucessor oficial do Gemini CLI (descontinuado para contas individuais em 06/2026) |
| R8 | Repositório público no GitHub | confirmado |

## Dúvidas
- ~~Gemini CLI foi selecionado; a execução das três fases depende de conexão funcional e confirmação do usuário.~~ Resolvido: o Gemini CLI foi descontinuado para contas individuais; a execução foi feita pelo Antigravity CLI (sucessor oficial) — ver Resumo final.
- ~~Os testes existentes são parciais e não comprovam todos os endpoints.~~ Mitigado: a Fase 3 da execução oficial validou todos os endpoints mapeados por baseline (22/22, 10 cenários e 22/22); os testes automatizados mínimos continuam como regressão de boot.

## Passos

### [x] 1. Confirmar estado base e ferramentas disponíveis
- **Objetivo:** Registrar uma linha de base real antes de alterar ou validar o projeto.
- **Ação:** Ler estado Git, remotes e disponibilidade dos executáveis das ferramentas permitidas.
- **Pronto quando:** Estado do trabalho, remotos e ferramentas ficam registrados sem erro.
- **Verificação:** `git --no-pager status --short; git remote -v; Get-Command claude,gemini,codex -ErrorAction SilentlyContinue`
- **Resultado:** Git limpo exceto por `PLANO.md` (não rastreado). Remotes `origin` e `upstream` confirmados. Claude encontrado em `C:\Program Files\nodejs\claude.ps1`; Gemini/Codex não encontrados.

### [x] 2. Decidir a ferramenta oficial de execução
- **Depende de:** 1
- **Objetivo:** Resolver a tecnologia obrigatória antes de executar a skill.
- **Ação:** Aguardar escolha do usuário se nenhuma das ferramentas estiver disponível ou se mais de uma estiver disponível.
- **Pronto quando:** Há uma ferramenta oficial escolhida ou o bloqueio foi explicitamente registrado.
- **Verificação:** Comando da ferramenta selecionada exibindo sua versão.
- **Resultado:** Claude Code 2.1.331 foi encontrado, mas o login não estava disponível. Em seguida, o usuário selecionou Gemini CLI; `npx --yes @google/gemini-cli --version` retornou 0.71.1.

### [x] 3. Validar o projeto 1 — code-smells-project
- **Depende de:** 2
- **Objetivo:** Confirmar instalação, boot e endpoints do projeto Flask refatorado.
- **Ação:** Preparar ambiente somente conforme dependências existentes; usar o entry point do projeto e exercitar os endpoints documentados.
- **Pronto quando:** Aplicação inicia, endpoint principal responde e a evidência é registrada.
- **Verificação:** `python -m pip install -r requirements.txt` e comando de smoke test HTTP ou test client do projeto.
- **Resultado:** Dependências Flask instaladas. Servidor iniciado na porta 5051 e `/`, `/health`, `/produtos`, `/usuarios`, `/pedidos` e `/relatorios/vendas` retornaram HTTP 200. Processo encerrado.

### [x] 4. Validar o projeto 2 — ecommerce-api-legacy
- **Depende de:** 2
- **Objetivo:** Confirmar instalação, boot e endpoints do projeto Express refatorado.
- **Ação:** Instalar dependências existentes, iniciar o servidor e exercitar os endpoints documentados.
- **Pronto quando:** Aplicação inicia e os endpoints críticos retornam respostas compatíveis.
- **Verificação:** `npm install` e `npm start` com chamadas HTTP ao servidor.
- **Resultado:** Após falha inicial do binário nativo, `.npmrc` permitiu rebuild de `sqlite3`; servidor iniciou na porta 5052. Checkout retornou sucesso, relatório sem token retornou 401 e com token válido respondeu dados; DELETE sem token retornou 401.

### [x] 5. Validar o projeto 3 — task-manager-api
- **Depende de:** 2
- **Objetivo:** Confirmar instalação, boot e todos os endpoints do projeto Flask parcialmente organizado.
- **Ação:** Preparar ambiente, inicializar dados se necessário e exercitar endpoints públicos, autenticados e administrativos.
- **Pronto quando:** Aplicação inicia e os endpoints críticos preservam o contrato definido no README.
- **Verificação:** `python -m pip install -r requirements.txt`, seed controlado e chamadas HTTP/test client.
- **Resultado:** Servidor iniciou na porta 5053. `/health` respondeu 200, `/tasks` sem token respondeu 401, login administrativo respondeu 200 e `/tasks` e `/users` autenticados responderam. Estes testes não cobrem todos os endpoints.

### [x] 6. Executar ou criar testes automatizados mínimos
- **Depende de:** 3, 4, 5
- **Objetivo:** Ter regressões verificáveis em boot e endpoints críticos.
- **Ação:** Detectar testes existentes; criar somente a cobertura mínima necessária se não houver.
- **Pronto quando:** Há comando reproduzível de teste e ele passa nos três projetos.
- **Verificação:** Comandos identificados pelo package/manifesto; criação de testes não deve ocorrer sem necessidade.
- **Resultado:** Testes `unittest` dos projetos 1 e 3 passaram com 2 testes cada; teste `node:test` do projeto 2 passou com 1 teste.

### [x] 7. Revisar README e evidências
- **Depende de:** 3, 4, 5
- **Objetivo:** Atualizar documentação sem inventar resultados não confirmados.
- **Ação:** Registrar somente evidências reais, limitações e comandos reproduzíveis.
- **Pronto quando:** README distingue prova executada de hipótese e contém comandos corretos.
- **Verificação:** Checagem manual das seções Análise Manual, Construção da Skill, Resultados e Como Executar.
- **Resultado:** README recebeu comandos de testes mínimos e de execução pelo Gemini CLI; a execução anterior pelo Copilot continua identificada como tal.

### [x] 8. Revisão final e confirmação de entrega
- **Depende de:** 6, 7
- **Objetivo:** Confirmar integridade do repositório e preparar uma entrega clara.
- **Ação:** Reexecutar Git status, inventariar relatórios e skill, e identificar pendências externas.
- **Pronto quando:** Não existem alterações não revisadas e o resumo final separa feito, pendente e não verificado.
- **Verificação:** `git --no-pager status --short; git --no-pager diff --stat; Test-Path reports/audit-project-1.md,reports/audit-project-2.md,reports/audit-project-3.md`
- **Resultado:** Os três relatórios existem, os testes mínimos passaram e a página pública do GitHub foi confirmada. O commit `6357f7e` foi enviado. A adaptação posterior para Gemini foi revisada e commitada em `21ee916`; a execução oficial pelo Antigravity CLI foi commitada em `c19fad0`.

## Resumo final
- Feito: skill executada de ponta a ponta pelo Antigravity CLI 1.5.17 (`agy`) em 25/11/2026 sobre cópias isoladas do código original (commit `6d1ce62`), com as 3 fases verificadas nos 3 projetos (17/15/15 findings; boot + endpoints validados na Fase 3). Evidências e relatórios do `agy` commitados em `reports/evidence/`; skill adicionada em `.agents/skills/` nos 3 projetos; README atualizado (Desafios, Resultados e Como Executar).
- Decisões do usuário: manter em `reports/audit-project-N.md` os relatórios da primeira execução (Copilot) e manter o código refatorado já commitado; a execução oficial fica documentada via `reports/evidence/`.
- Contexto: o Gemini CLI foi descontinuado para contas individuais em 18/06/2026; a execução pelo login pessoal retornava "This client is no longer supported for Gemini Code Assist for individuals". O Antigravity CLI é o sucessor oficial (skills em `.agents/skills/`), autenticado com conta Google pessoal.

## Retomada em outra máquina (histórico)
- O usuário informou que a autenticação no Gemini CLI foi bem-sucedida e que `refactor-arch` aparece em `/skills list`.
- Ao solicitar a execução, o Gemini retornou `API Error: exception TypeError: fetch failed sending request`. Um teste local ao endpoint `generativelanguage.googleapis.com` falhou com `UNABLE_TO_VERIFY_LEAF_SIGNATURE`; a causa exata do erro do Gemini não foi confirmada.
- Na outra máquina, testar a conexão e executar a skill em cópias isoladas dos projetos originais. (Correção: a revisão `560697e` não existe neste clone; o baseline pré-refatoração é o commit inicial `6d1ce62`.) Preservar o código refatorado e os relatórios existentes.
- Validar boot e endpoints, guardar evidências reais e atualizar o README sem atribuir ao Gemini a execução anterior pelo Copilot.
