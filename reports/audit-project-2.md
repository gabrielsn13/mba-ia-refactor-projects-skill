================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18 (express ^4.18.2)
Dependencies:  express, sqlite3 ^5.1.6
Domain:        LMS API com fluxo de checkout (cursos, matrículas, pagamentos) e relatório financeiro
Architecture:  Monolítica — classe AppManager concentra banco, rotas, regras de negócio e pagamento; utils.js guarda config e estado global
Source files:  3 files analyzed (~180 lines)
DB tables:     users, courses, enrollments, payments, audit_logs (SQLite em memória)
Entry point:   src/app.js
Endpoints:     3 mapped (POST /api/checkout, GET /api/admin/financial-report, DELETE /api/users/:id)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:2-5
Description: `config` contém `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (chave live do gateway) e `smtpUser` fixos no código-fonte.
Impact: Qualquer pessoa com acesso ao repositório obtém credenciais de banco, chave de pagamento de produção e e-mail do sistema.
Recommendation: Ler tudo de variáveis de ambiente em um módulo de config, sem defaults sensíveis, e documentar em `.env.example` — Playbook P2.

### [CRITICAL] Dados sensíveis de cartão e chave do gateway em log
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` imprime o número completo do cartão e a chave do gateway a cada checkout.
Impact: Violação de PCI-DSS e vazamento de dados financeiros e de segredo via logs.
Recommendation: Nunca logar PAN/segredos; logar apenas identificadores (ex.: últimos 4 dígitos) por um logger central — Playbook P13.

### [CRITICAL] Armazenamento de senha inseguro (hash falso e senha em texto puro)
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68
Description: `badCrypto` concatena 10000 vezes o base64 dos 2 primeiros caracteres e corta em 10 chars (não é hash, é reversível e colide facilmente); a senha padrão `"123456"` é usada quando `pwd` não é enviado (AppManager.js:68); o usuário seed é inserido com senha `'123'` em texto puro (AppManager.js:18).
Impact: Senhas triviais de recuperar e contas criadas com senha previsível.
Recommendation: Usar `bcrypt`/`crypto.scrypt` com salt, exigir senha no checkout e remover o default — Playbook P4.

### [CRITICAL] God Class: AppManager mistura banco, rotas, regra de negócio e pagamento
File: src/AppManager.js:4-139
Description: A classe `AppManager` cria a conexão SQLite (linha 7), define o schema e o seed (10-22), registra as 3 rotas Express (25-138), contém a regra de checkout/pagamento/matrícula (28-78), o relatório financeiro (80-129) e a exclusão de usuário (131-137).
Impact: Impossível testar isoladamente; qualquer mudança afeta tudo; viola completamente a separação MVC e SRP.
Recommendation: Separar em config, database, models (users/courses/enrollments/payments), controllers, routes e error handler — Playbook P5/P6/P8.

### [CRITICAL] Endpoints administrativos e destrutivos sem autenticação
File: src/AppManager.js:80-129, src/AppManager.js:131-137
Description: `GET /api/admin/financial-report` expõe nome de alunos e receita por curso e `DELETE /api/users/:id` apaga qualquer usuário, ambos sem nenhum middleware de autenticação/autorização.
Impact: Qualquer cliente anônimo lê dados financeiros e remove usuários.
Recommendation: Proteger rotas administrativas com middleware de autenticação (ex.: token em variável de ambiente ou JWT) — Playbook P3.

### [HIGH] Lógica de negócio dentro dos handlers de rota
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: O handler de `/api/checkout` valida entrada, consulta curso e usuário, cria usuário, simula pagamento (`cc.startsWith("4")`, linha 46), grava matrícula, pagamento e auditoria; o relatório monta a estrutura de resposta dentro da rota.
Impact: Regras não reutilizáveis nem testáveis sem subir HTTP; controller inchado.
Recommendation: Mover regras para controllers/serviços finos e persistência para models; rotas só mapeiam URL → controller — Playbook P6/P8.

### [HIGH] Estado global mutável
File: src/utils.js:9-10, src/utils.js:12-15, src/utils.js:25, src/AppManager.js:2, src/AppManager.js:59
Description: `globalCache` e `totalRevenue` são variáveis de módulo mutáveis exportadas; `logAndCache` escreve no cache global a cada checkout (AppManager.js:59) e `totalRevenue` é importado sem uso (AppManager.js:2) — e exportado por valor, nunca refletiria alterações.
Impact: Estado compartilhado entre requisições, vazamento de memória (cache sem limite) e comportamento imprevisível em testes.
Recommendation: Remover o cache global ou encapsulá-lo em um serviço injetável com limite; eliminar variáveis sem uso — Playbook P7.

### [HIGH] Acoplamento forte e ausência de injeção de dependência
File: src/AppManager.js:7, src/app.js:8-10, src/AppManager.js:2
Description: `AppManager` instancia `new sqlite3.Database(':memory:')` no construtor (caminho do banco fixo) e importa `config`/`utils` diretamente; `app.js` cria o manager e chama `initDb()`/`setupRoutes()` manualmente.
Impact: Não é possível trocar banco/configuração nem testar com um banco isolado; todos os dados são perdidos ao reiniciar.
Recommendation: Criar a conexão em módulo de database configurável e injetar nos models; `app.js` como composition root — Playbook P7/P8.

### [MEDIUM] N+1 Queries no relatório financeiro
File: src/AppManager.js:83-128
Description: Para cada curso executa uma query de matrículas (linha 92) e, para cada matrícula, duas queries adicionais: usuário (104) e pagamento (106).
Impact: Número de queries cresce com cursos × matrículas; degrada rapidamente o endpoint.
Recommendation: Substituir por um único JOIN (`courses/enrollments/users/payments`) e agrupar em memória — Playbook P10.

### [MEDIUM] Callback hell
File: src/AppManager.js:37-77, src/AppManager.js:83-128
Description: Callbacks aninhados em até 7 níveis no checkout e no relatório, com contadores manuais (`coursesPending`, `enrPending`) para detectar término.
Impact: Difícil de ler e propenso a bugs de concorrência (ex.: relatório pode responder fora de ordem).
Recommendation: Promisificar o acesso ao banco e usar `async/await` — Playbook P12.

### [MEDIUM] Validação e tratamento de erros ausentes ou inconsistentes
File: src/AppManager.js:29-35, src/AppManager.js:41, src/AppManager.js:57-61, src/AppManager.js:93, src/AppManager.js:104-106, src/AppManager.js:133-136
Description: Só testa presença de campos (35); não valida formato de e-mail, número do cartão ou tipo do curso; erros respondem texto puro variado ("Bad Request", "Erro DB"); o `err` do audit log é ignorado (57), `enrollments` é usado sem checar `err` (93), e o DELETE sempre responde sucesso mesmo com erro (133-136).
Impact: Falhas silenciosas, possíveis exceções não tratadas e contrato de erro inconsistente.
Recommendation: Validar entrada no controller e centralizar erros em um middleware que responde JSON padronizado — Playbook P9/P11.

### [MEDIUM] Exclusão de usuário deixa dados órfãos
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` remove só a linha de `users`; a própria resposta admite "as matrículas e pagamentos ficaram sujos no banco".
Impact: Matrículas e pagamentos órfãos corrompem o relatório financeiro (aparece "Unknown").
Recommendation: Remover/anonimizar em cascata dentro de uma transação (pagamentos → matrículas → usuário) — Playbook P12.

### [MEDIUM] Checkout sem transação
File: src/AppManager.js:50-63
Description: Matrícula, pagamento e audit log são inseridos em comandos independentes; falha no meio deixa matrícula sem pagamento.
Impact: Inconsistência de dados em falhas parciais.
Recommendation: Executar a sequência em uma transação (`BEGIN`/`COMMIT`/`ROLLBACK`) — Playbook P12.

### [LOW] Nomes pouco descritivos
File: src/AppManager.js:26, src/AppManager.js:29-33, src/AppManager.js:43
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`, `self`, `processPaymentAndEnroll` e campos do body `usr`, `eml`, `pwd`, `c_id`.
Impact: Legibilidade reduzida e maior risco de erro.
Recommendation: Renomear internamente (`userName`, `email`, `password`, `courseId`, `cardNumber`) mantendo o contrato externo do body — Playbook P14.

### [LOW] Magic numbers e strings soltas
File: src/utils.js:19-22, src/AppManager.js:46, src/AppManager.js:48, src/utils.js:6
Description: Loop de `10000` iterações e `substring(0, 2)`/`substring(0, 10)` em `badCrypto`, prefixo de cartão `"4"` e status `"PAID"`/`"DENIED"` inline, porta `3000`.
Impact: Regras implícitas difíceis de entender e alterar.
Recommendation: Extrair para constantes nomeadas na config — Playbook P14.

### [LOW] Logging com console.log e configuração morta
File: src/utils.js:13, src/AppManager.js:45, src/app.js:13, src/utils.js:2-5
Description: Logs via `console.log` sem nível/formato; `dbUser`, `dbPass` e `smtpUser` nunca são usados (o banco é `:memory:`).
Impact: Ruído, sem controle de nível, e configuração morta que sugere credenciais reais.
Recommendation: Usar um logger central e remover configuração não utilizada — Playbook P13/P14.

## Deprecated APIs
None detected

================================
Total: 16 findings
================================
