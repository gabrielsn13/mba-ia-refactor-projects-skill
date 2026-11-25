# Plano: Concluir e validar o desafio de refatoração arquitetural

**Fonte da especificação:** README.md
**Criado em:** 2026-11-25
**Legenda:** `[ ]` pendente · `[~]` em andamento · `[x]` feito · `[!]` falhou

## Requisitos
| # | Requisito | Estado |
|---|-----------|--------|
| R1 | Skill completa com SKILL.md e cinco áreas de referência | feito |
| R2 | Skill executada nos três projetos com três fases verificáveis | parcial |
| R3 | Relatórios de auditoria persistidos | feito |
| R4 | Código refatorado dos três projetos commitado | feito |
| R5 | README com análise, construção, resultados e execução | feito |
| R6 | Validação independente por boot e endpoints | pendente |
| R7 | Validação com Claude Code, Gemini CLI ou Codex | pendente |
| R8 | Repositório público no GitHub | não verificado |

## Dúvidas
- Qual ferramenta oficial deve ser usada: Claude Code, Gemini CLI ou Codex?
- A visibilidade pública do repositório foi definida pelo usuário, mas não foi confirmada localmente.
- O usuário autorizou commits neste plano? Não por padrão.

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
- **Resultado:** Claude Code encontrado no PATH na versão 2.1.331. Gemini CLI e Codex não encontrados, portanto Claude Code será usado.

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
- **Resultado:** `npm install` concluiu, mas o `sqlite3@5.1.7` não possui o binário nativo carregável no Node 24.20.0 e o script de instalação foi bloqueado. Primeira correção óbvia: `npm rebuild sqlite3 --build-from-source` falhou com `EUNKNOWNCONFIG: Unknown cli flag: --build-from-source`. Não avançar para os passos dependentes.

### [x] 5. Validar o projeto 3 — task-manager-api
- **Depende de:** 2
- **Objetivo:** Confirmar instalação, boot e todos os endpoints do projeto Flask parcialmente organizado.
- **Ação:** Preparar ambiente, inicializar dados se necessário e exercitar endpoints públicos, autenticados e administrativos.
- **Pronto quando:** Aplicação inicia e os endpoints críticos preservam o contrato definido no README.
- **Verificação:** `python -m pip install -r requirements.txt`, seed controlado e chamadas HTTP/test client.
- **Resultado:** `.npmrc` restrito permitiu rebuild de `sqlite3`; servidor iniciou na porta 5052. Checkout bem-sucedido retornou matrícula; relatório sem token retornou 401 e com token válido respondeu dados; DELETE sem token retornou 401. Processo encerrado.

### [x] 6. Executar ou criar testes automatizados mínimos
- **Depende de:** 3, 4, 5
- **Objetivo:** Ter regressões verificáveis em boot e endpoints críticos.
- **Ação:** Detectar testes existentes; criar somente a cobertura mínima necessária se não houver.
- **Pronto quando:** Há comando reproduzível de teste e ele passa nos três projetos.
- **Verificação:** Comandos identificados pelo package/manifesto; criação de testes não deve ocorrer sem necessidade.
- **Resultado:** Dependências Flask instaladas e banco semeado com 3 usuários, 4 categorias e 10 tasks. Servidor iniciou na porta 5053. `/health` respondeu 200, `/tasks` sem token respondeu 401, login administrativo respondeu 200 e `/tasks` e `/users` autenticados responderam os dados esperados. Processo encerrado.

### [x] 7. Revisar README e evidências
- **Depende de:** 3, 4, 5
- **Objetivo:** Atualizar documentação sem inventar resultados não confirmados.
- **Ação:** Registrar somente evidências reais, limitações e comandos reproduzíveis.
- **Pronto quando:** README distingue prova executada de hipótese e contém comandos corretos.
- **Verificação:** Checagem manual das seções Análise Manual, Construção da Skill, Resultados e Como Executar.
- **Resultado:** Testes `unittest` adicionados ao projeto 1 (2 testes) e ao projeto 3 (2 testes); ambos passaram. Teste `node:test` criado no projeto 2 e passou, cobrindo proteção administrativa e checkout.

### [x] 8. Revisão final e confirmação de entrega
- **Depende de:** 6, 7
- **Objetivo:** Confirmar integridade do repositório e preparar uma entrega clara.
- **Ação:** Reexecutar Git status, inventariar relatórios e skill, e identificar pendências externas.
- **Pronto quando:** Não existem alterações não revisadas e o resumo final separa feito, pendente e não verificado.
- **Verificação:** `git --no-pager status --short; git --no-pager diff --stat; Test-Path reports/audit-project-1.md,reports/audit-project-2.md,reports/audit-project-3.md`
- **Resultado:** Revisão final concluiu que os três relatórios existem, os testes mínimos passaram e o repositório público no GitHub foi confirmado. Restam apenas commits/push como ação externa não autorizada. README recebeu comandos reproduzíveis de testes mínimos dos três projetos e instrução de rebuild do `sqlite3`. Evidências públicas e locais registradas. Claude Code não pôde executar a skill por ausência de login.

## Resumo final
- Feito: Claude Code 2.1.331 confirmado; smoke tests HTTP dos três projetos concluídos; testes mínimos passaram nos três projetos; `.npmrc` resolveu o rebuild do `sqlite3`; README atualizado; repositório público confirmado; três relatórios presentes.
- Pendente: commit e push das alterações finais não autorizados; login na conta Claude para executar `/refactor-arch` oficialmente.
- Não verificado: execução oficial completa da skill pelo Claude Code nas fases 1 a 3.
