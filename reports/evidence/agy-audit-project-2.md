================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 4

## Findings

### 1. [CRITICAL] Credenciais e segredos hardcoded (AP-02)
File: src/utils.js:1-7, src/AppManager.js:18, src/AppManager.js:45
Description: O objeto `config` em `src/utils.js:1-7` armazena credenciais e chaves sensíveis literais no código-fonte (`dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser: "no-reply@fullcycle.com.br"`). Além disso, o seed em `src/AppManager.js:18` insere a senha literal `'123'` e `src/AppManager.js:45` imprime `config.paymentGatewayKey` no console.
Impact: Exposição direta de segredos de banco de dados, gateway de pagamento e SMTP no repositório e em logs de execução, permitindo comprometimento completo de integrações e dados.
Recommendation: Mover configurações sensíveis para variáveis de ambiente (`process.env`) carregadas em módulo isolado `src/config/env.js` e documentadas em `.env.example`, removendo segredos do código e dos logs.

### 2. [CRITICAL] Endpoints perigosos/administrativos sem autenticação (AP-03)
File: src/AppManager.js:80-129, src/AppManager.js:131-137
Description: As rotas `GET /api/admin/financial-report` (`src/AppManager.js:80-129`) e `DELETE /api/users/:id` (`src/AppManager.js:131-137`) não possuem qualquer middleware de autenticação ou verificação de autorização/perfil.
Impact: Qualquer cliente anônimo pode consultar o relatório financeiro completo da plataforma (incluindo nomes de alunos e valores pagos) e excluir contas de usuários arbitrariamente.
Recommendation: Proteger rotas administrativas e destrutivas com middlewares de autenticação e autorização baseados em token/sessão e papel (role) de usuário antes de executar os controllers.

### 3. [CRITICAL] Tratamento inseguro de senhas e dados sensíveis (AP-04)
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:45, src/AppManager.js:68
Description: A função `badCrypto(pwd)` (`src/utils.js:17-23`) usada em `src/AppManager.js:68` implementa um hash caseiro inseguro concatenando 10.000 vezes os 2 primeiros caracteres de `Buffer.from(pwd).toString('base64')` e truncando o resultado para 10 caracteres (preservando apenas o prefixo repetido), além de usar `"123456"` como fallback quando `p` está ausente. O seed em `src/AppManager.js:18` grava a senha `'123'` em texto puro na tabela `users`, e `src/AppManager.js:45` registra o número completo do cartão (`cc`) em `console.log`.
Impact: Senhas podem ser facilmente revertidas ou colidem trivialmente; o log do número completo do cartão viola boas práticas de proteção de dados (PCI-DSS/LGPD) e expõe dados financeiros em texto claro.
Recommendation: Substituir `badCrypto` por algoritmo criptográfico forte para senhas (`crypto.scrypt` com salt aleatório ou `bcrypt`/`argon2`), gerar hash seguro também nos seeds e remover/mascarar dados de cartão e chaves em logs.

### 4. [CRITICAL] God Class / God File (AP-05)
File: src/AppManager.js:4-139
Description: A classe `AppManager` concentra todas as responsabilidades da aplicação em 136 linhas: instanciação da conexão SQLite no construtor (`src/AppManager.js:5-8`), criação de schema e carga de seeds em `initDb()` (`src/AppManager.js:10-23`), registro de rotas Express em `setupRoutes(app)` (`src/AppManager.js:25-138`), validação de entrada, regras de negócio de checkout/relatório, consultas SQL diretas e formatação de respostas HTTP.
Impact: Alto acoplamento e baixa coesão, tornando testes unitários inviáveis, dificultando evolução de regras de negócio e aumentando o risco de regressões a cada alteração.
Recommendation: Separar `AppManager` em camadas MVC: `config` (ambiente e banco), `models`/`repositories` (acesso a dados e schema), `services` (regras de negócio), `controllers` (orquestração HTTP) e `routes` (mapeamento de endpoints).

### 5. [HIGH] Lógica de negócio em controllers/rotas (AP-06)
File: src/AppManager.js:28-78, src/AppManager.js:80-129, src/AppManager.js:131-137
Description: Os handlers registrados diretamente em `setupRoutes` misturam parsing de requisição, regras de domínio (autorização simulada de cartão por prefixo `"4"` em `src/AppManager.js:46`, cálculo de receita em `src/AppManager.js:108-109`), queries SQL diretas (`this.db.get`, `this.db.run`, `this.db.all`) e disparo de cache/auditoria no mesmo corpo de função.
Impact: Regras de negócio não podem ser reutilizadas nem testadas sem subir o servidor Express e o banco de dados, violando o princípio de responsabilidade única e o padrão MVC.
Recommendation: Extrair a lógica de checkout, relatório financeiro e gestão de usuários para services/models dedicados, deixando nas rotas apenas o roteamento e nos controllers a leitura do request e devolução da resposta.

### 6. [HIGH] Estado global mutável / acoplamento forte sem injeção de dependência (AP-07)
File: src/AppManager.js:5-8, src/utils.js:9-15, src/utils.js:25
Description: `AppManager` instancia `new sqlite3.Database(':memory:')` diretamente dentro de `constructor()` (`src/AppManager.js:7`), impedindo injeção de outra conexão ou mock. Em `src/utils.js:9-15,25`, `globalCache` e `totalRevenue` são declarados como estado global mutável no nível de módulo, e `logAndCache` insere chaves em `globalCache` indefinidamente sem limite ou expiração.
Impact: Acoplamento rígido dificulta testes isolados e escalabilidade horizontal; o crescimento ilimitado de `globalCache` gera risco de vazamento de memória (memory leak).
Recommendation: Criar factory/injeção da conexão SQLite via construtor/parâmetro a partir do composition root (`src/app.js`), remover variáveis globais mutáveis ou encapsular cache com política de expiração/limite se necessário.

### 7. [HIGH] Operações multi-etapa sem transação / integridade (AP-08)
File: src/AppManager.js:12-16, src/AppManager.js:50-75, src/AppManager.js:131-137
Description: No endpoint `POST /api/checkout`, a criação opcional de usuário (`src/AppManager.js:69`), inserção de matrícula (`src/AppManager.js:50`), inserção de pagamento (`src/AppManager.js:54`) e registro de auditoria (`src/AppManager.js:57`) são executadas em comandos independentes sem `BEGIN TRANSACTION`/`COMMIT`/`ROLLBACK`. Além disso, as tabelas (`src/AppManager.js:12-16`) não definem `FOREIGN KEY ... ON DELETE CASCADE` e `DELETE /api/users/:id` (`src/AppManager.js:131-137`) remove apenas o usuário, deixando registros órfãos em `enrollments` e `payments`.
Impact: Falhas parciais no checkout produzem estado inconsistente (ex.: usuário criado e matrícula gravada sem pagamento), e a remoção de usuários corrompe a integridade referencial do banco e dos relatórios financeiros.
Recommendation: Envolver as escritas do checkout em uma transação SQL atômica com `ROLLBACK` em caso de erro, habilitar `PRAGMA foreign_keys = ON`, definir chaves estrangeiras com `ON DELETE CASCADE` (ou exclusão ordenada em transação) ao remover usuários.

### 8. [MEDIUM] Queries N+1 (AP-09)
File: src/AppManager.js:83-128
Description: Em `GET /api/admin/financial-report`, o código consulta todos os cursos (`src/AppManager.js:83`), depois executa uma query de matrículas por curso dentro de `courses.forEach` (`src/AppManager.js:92`) e, dentro de `enrollments.forEach` (`src/AppManager.js:102`), dispara mais duas queries individuais por matrícula para buscar usuário (`src/AppManager.js:104`) e pagamento (`src/AppManager.js:106`).
Impact: O número de consultas cresce linearmente com a quantidade de cursos e matrículas (`1 + C + 2*E`), degradando rapidamente a latência e sobrecarregando o banco com o aumento de dados.
Recommendation: Substituir o encadeamento de queries em loop por uma única consulta SQL com `LEFT JOIN` entre `courses`, `enrollments`, `users` e `payments` e agregar os resultados em memória no service/model.

### 9. [MEDIUM] Tratamento de erro inadequado/repetitivo (AP-11)
File: src/AppManager.js:35, src/AppManager.js:38, src/AppManager.js:41, src/AppManager.js:48, src/AppManager.js:51, src/AppManager.js:55, src/AppManager.js:57, src/AppManager.js:70, src/AppManager.js:84, src/AppManager.js:92, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133-136
Description: Cada callback repete verificações manuais `if (err) return res.status(500).send(...)` retornando texto puro inconsistente com o formato JSON de sucesso (`src/AppManager.js:60`). Em diversos callbacks (`src/AppManager.js:57,92,104,106,133`), o parâmetro `err` é completamente ignorado/engolido — podendo até lançar exceção não tratada ao acessar `enrollments.length` se `enrollments` for `undefined` na linha 93, ou retornar sucesso no `DELETE` mesmo em falha.
Impact: Erros silenciosos mascaram falhas de banco, derrubam a resposta por exceções em callbacks e entregam formatos inconsistentes aos consumidores da API.
Recommendation: Promisificar o acesso ao banco com `async/await`, usar classes de erro de domínio e centralizar o tratamento em um error middleware do Express com payload JSON padronizado.

### 10. [MEDIUM] Validação ausente/fraca na borda (AP-12)
File: src/AppManager.js:29-35, src/AppManager.js:46, src/AppManager.js:68, src/AppManager.js:132-133
Description: Em `POST /api/checkout`, a validação verifica apenas truthiness de `u`, `e`, `cid` e `cc` (`src/AppManager.js:35`), sem validar se `req.body` existe, se `e` é um e-mail válido, se `c_id` é inteiro positivo ou se `card` é uma string válida (um número em JSON fará `cc.startsWith("4")` lançar `TypeError` na linha 46). Além disso, `pwd` é opcional com fallback `"123456"` (`src/AppManager.js:68`). Em `DELETE /api/users/:id` (`src/AppManager.js:132-133`), `req.params.id` não é validado nem se verifica se algum registro foi afetado.
Impact: Payloads malformados causam falhas 500 não tratadas ou cadastros com dados inválidos e senhas fracas padrão.
Recommendation: Criar camada de validação na borda (validators/schemas) que valide tipos, formatos e obrigatoriedade de campos, retornando `400 Bad Request` estruturado antes de acionar os services.

### 11. [MEDIUM] Callback hell / fluxo assíncrono ingovernável (AP-13)
File: src/AppManager.js:26, src/AppManager.js:37-77, src/AppManager.js:83-128
Description: O handler `POST /api/checkout` (`src/AppManager.js:37-77`) encadeia 5 níveis de callbacks aninhados exigindo o alias `const self = this` (`src/AppManager.js:26`) para preservar contexto dentro de `function(err)`. Já `GET /api/admin/financial-report` (`src/AppManager.js:83-128`) utiliza 4 níveis de callbacks sincronizados manualmente pelos contadores `coursesPending` e `enrPending`, enviando `res.json(report)` de dentro do callback mais interno.
Impact: Código frágil, difícil de ler e depurar, sujeito a race conditions e respostas duplicadas ou travadas caso algum callback falhe antes de decrementar os contadores.
Recommendation: Envolver os métodos de `sqlite3` (`run`, `get`, `all`) em helpers baseados em `Promise` e reescrever os fluxos com `async/await`.

### 12. [LOW] Magic numbers e strings (AP-14)
File: src/AppManager.js:21, src/AppManager.js:46, src/AppManager.js:68, src/AppManager.js:108, src/utils.js:6, src/utils.js:19-22
Description: Valores literais de regra de negócio e configuração aparecem espalhados pelo código sem constantes nomeadas: prefixo de cartão `"4"` e status `"PAID"`/`"DENIED"` (`src/AppManager.js:21,46,108`), senha padrão `"123456"` (`src/AppManager.js:68`), porta `3000` (`src/utils.js:6`) e parâmetros `10000`, `2`, `10` em `badCrypto` (`src/utils.js:19-22`).
Impact: Dificulta manutenção, leitura e alteração centralizada de regras de negócio e status do sistema.
Recommendation: Extrair status de pagamento, prefixos/regras de validação e configurações padrão para constantes nomeadas em módulo dedicado de configuração/constantes.

### 13. [LOW] Logging inadequado (AP-15)
File: src/app.js:13, src/AppManager.js:45, src/utils.js:13
Description: A aplicação utiliza `console.log` diretamente para inicialização (`src/app.js:13`), processamento de pagamento com dados sensíveis (`src/AppManager.js:45`) e operações de cache (`src/utils.js:13`), sem níveis de severidade, timestamps padronizados ou formato estruturado.
Impact: Dificulta observabilidade e filtragem de logs em produção, além de agravar o vazamento de dados sensíveis em stdout.
Recommendation: Adotar um utilitário de logger estruturado com níveis (`info`, `warn`, `error`) e garantir sanitização de campos sensíveis antes de registrar eventos.

### 14. [LOW] Nomenclatura ruim e código morto (AP-16)
File: src/AppManager.js:2, src/AppManager.js:26, src/AppManager.js:29-33, src/AppManager.js:43, src/AppManager.js:52, src/AppManager.js:89, src/AppManager.js:102, src/AppManager.js:104, src/utils.js:10, src/utils.js:25
Description: Identificadores abreviados ou pouco expressivos prejudicam a legibilidade (`u`, `e`, `p`, `cid`, `cc` em `src/AppManager.js:29-33`; `enrId` na linha 52; `c` na linha 89; `enr` na linha 102; `self` na linha 26). Há também código morto: `totalRevenue` é definido e exportado em `src/utils.js:10,25` e importado em `src/AppManager.js:2`, mas nunca utilizado; e `email` é selecionado em `SELECT name, email FROM users` (`src/AppManager.js:104`) sem ser usado na resposta.
Impact: Reduz clareza semântica do código e mantém símbolos/consultas desnecessários ativos na base.
Recommendation: Adotar nomes descritivos nas variáveis internas (mantendo o contrato JSON externo dos endpoints), remover `totalRevenue` e colunas não utilizadas nas queries.

### 15. [LOW] Configuração de execução insegura (AP-17)
File: src/utils.js:6, src/app.js:8-14
Description: A porta do servidor está fixa em `port: 3000` (`src/utils.js:6`) sem suporte a `process.env.PORT`, e `src/app.js:8-10` executa efeitos colaterais de inicialização do banco (`initDb()`) e binding de porta diretamente no escopo principal sem fábrica de app exportável ou tratamento de encerramento.
Impact: Impede configuração flexível por ambiente (dev/test/prod) e dificulta testes de integração sem iniciar o servidor na porta fixa 3000.
Recommendation: Ler porta e variáveis de ambiente via `process.env` com fallback documentado, e separar a criação da instância Express (`createApp`) da inicialização do servidor (`app.listen`) no composition root.

## Deprecated APIs
None detected

================================
Total: 15 findings
================================
