---
name: refactor-arch
description: Analisa, audita e refatora uma codebase de backend para o padrão MVC, independente de linguagem/framework. Use quando o usuário pedir /refactor-arch, auditoria de arquitetura, detecção de code smells/anti-patterns ou refatoração para MVC. Executa 3 fases (análise, auditoria com confirmação, refatoração com validação).
---

# refactor-arch — Refatoração Arquitetural Automatizada

Você é um especialista em arquitetura de software. Execute as 3 fases **em ordem**, dentro do diretório do projeto atual (cwd). A skill é agnóstica de tecnologia: nunca assuma nomes de arquivos, linguagem ou framework — descubra-os na Fase 1.

## Arquivos de referência (leia sob demanda)

| Arquivo | Quando ler |
|---|---|
| `project-analysis.md` | Fase 1 — heurísticas de stack, banco, arquitetura |
| `anti-patterns-catalog.md` | Fase 2 — catálogo, sinais de detecção, severidades, APIs deprecated |
| `report-template.md` | Fase 2 — formato obrigatório do relatório |
| `mvc-guidelines.md` | Fase 3 — estrutura-alvo e responsabilidades das camadas |
| `refactoring-playbook.md` | Fase 3 — transformações antes/depois por anti-pattern |

## Regras globais

- Nunca modifique arquivos antes da confirmação da Fase 2. Fases 1 e 2 são **somente leitura** (exceto salvar o relatório).
- Todo finding deve citar **arquivo e linhas exatos** (leia o arquivo com números de linha; não estime).
- Preserve o comportamento externo: mesmas rotas, métodos HTTP, formatos de resposta e status codes. Mudanças inevitáveis (ex.: parar de retornar senha/segredo) devem ser listadas no resumo final.
- Não invente achados: só reporte o que for evidenciado no código.

---

## FASE 1 — Análise do projeto

Leia `project-analysis.md` e execute:

1. Liste os arquivos do projeto (ignore `node_modules`, `.git`, venvs, `__pycache__`, lockfiles, bancos `.db`).
2. Detecte linguagem, framework (+ versão), dependências relevantes, banco de dados e tabelas/entidades.
3. Descreva o domínio da aplicação em uma frase.
4. Mapeie a arquitetura atual: onde estão rotas, regras de negócio, acesso a dados, configuração; classifique como monolítica / parcialmente em camadas / MVC.
5. Conte os arquivos-fonte analisados e as linhas aproximadas.
6. Liste os endpoints existentes (base de validação na Fase 3).
7. Imprima exatamente neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <...>
Framework:     <... versão>
Dependencies:  <...>
Domain:        <...>
Architecture:  <...>
Source files:  <N> files analyzed
DB tables:     <...>
Entry point:   <...>
Endpoints:     <N> mapped
================================
```

## FASE 2 — Auditoria

Leia `anti-patterns-catalog.md` e `report-template.md`.

1. Leia **todos** os arquivos-fonte com números de linha.
2. Cruze o código contra cada anti-pattern do catálogo usando os sinais de detecção; inclua a seção de **APIs deprecated**.
3. Classifique cada achado (CRITICAL, HIGH, MEDIUM, LOW) conforme o catálogo; agrupe ocorrências repetidas em um finding com várias linhas.
4. Gere o relatório no formato de `report-template.md`, **ordenado de CRITICAL → LOW**, e imprima-o.
5. Salve o relatório em `reports/audit-<nome-do-projeto>.md` na raiz do repositório git (crie a pasta se necessário) — única escrita permitida nesta fase. Se o usuário indicar outro caminho (ex.: `reports/audit-project-1.md`), use-o.
6. **PARE** e pergunte: `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`. Aguarde a resposta. Se não for "y"/"sim", encerre sem alterar nada.

## FASE 3 — Refatoração (somente após confirmação)

Leia `mvc-guidelines.md` e `refactoring-playbook.md`.

1. **Baseline**: antes de mexer, suba a aplicação, chame os endpoints mapeados e registre status/formato das respostas.
2. Planeje a estrutura-alvo adaptando ao projeto:
   - Projeto monolítico → crie todas as camadas.
   - Projeto já parcialmente em camadas → mantenha o que está adequado, mova o que está no lugar errado (ex.: regras de negócio de routes para controllers/services), remova código morto; não recrie do zero.
3. Aplique as transformações do playbook, por prioridade (CRITICAL primeiro). Aplique cada **Recommendation** do relatório **por inteiro**: se o finding apontar código morto (classe, função ou arquivo sem chamadores), **remova-o** — ou integre-o de fato ao fluxo da aplicação, justificando a escolha no resumo final; nunca deixe módulos órfãos "limpos porém sem uso". Atualize `requirements.txt`/`package.json` se adicionar dependências e documente variáveis de ambiente em `.env.example`.
4. Mantenha um único entry point claro (composition root): configura, registra rotas e inicia o servidor.
5. **Validação obrigatória**:
   - Instale dependências se necessário e **inicie a aplicação** — deve subir sem erros.
   - Chame **todos** os endpoints do baseline e compare com as respostas originais (status e formato).
   - Reaplique os sinais de detecção do catálogo (grep): nenhum anti-pattern CRITICAL/HIGH deve restar.
   - Revise o relatório **finding por finding** e confirme que cada Recommendation foi aplicada **integralmente** (inclusive remoções de código morto); liste no resumo qualquer item aplicado parcialmente, com justificativa.
   - Se algo falhar, corrija e valide de novo (máx. 3 tentativas); depois reporte o que restou.
   - Encerre o processo do servidor ao final.
6. Imprima o resumo:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore>

## Changes
<anti-pattern → como foi resolvido>

## Behavior changes (se houver)
<ex.: campo senha removido das respostas>

## Validation
  ✓/✗ Application boots without errors
  ✓/✗ All endpoints respond correctly (<N>/<N>)
  ✓/✗ Zero CRITICAL/HIGH anti-patterns remaining
================================
```
