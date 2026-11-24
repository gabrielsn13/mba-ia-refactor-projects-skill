================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependencies:  flask, flask-sqlalchemy, flask-cors, marshmallow, requests, python-dotenv (as 3 últimas não são usadas no código)
Domain:        Task Manager API (tarefas, usuários, categorias, relatórios)
Architecture:  Parcialmente em camadas — models/, routes/, services/ e utils/ existem, mas as routes concentram validação, regra de negócio e queries (sem camada de controllers); sem app factory
Source files:  10 files analyzed (~740 lines)
DB tables:     users, categories, tasks (SQLite via SQLAlchemy, `sqlite:///tasks.db`)
Entry point:   app.py
Endpoints:     22 mapped (/, /health, tasks x7, users x6, /login, reports x2, categories x3)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   10 analyzed | ~740 lines of code

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 7 | LOW: 4

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.py:13, services/notification_service.py:9-10
Description: `SECRET_KEY = 'super-secret-key-123'` e as credenciais SMTP (`taskmanager@gmail.com` / `senha123`) estão fixas no código-fonte.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de assinatura e a senha da conta de e-mail.
Recommendation: Ler de variáveis de ambiente em um módulo de config, sem defaults sensíveis, e documentar em `.env.example` — Playbook P2.

### [CRITICAL] Hash de senha fraco (MD5 sem salt)
File: models/user.py:3, models/user.py:27-32
Description: `set_password` e `check_password` usam `hashlib.md5(pwd.encode()).hexdigest()` sem salt; o seed (seed.py:19,26,33) grava senhas triviais ('1234', 'abcd', 'pass') com esse hash.
Impact: Hashes quebráveis por rainbow table/força bruta em segundos; senhas iguais geram hashes iguais.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash` (scrypt/pbkdf2 com salt) — Playbook P4.

### [CRITICAL] Hash da senha exposto nas respostas da API
File: models/user.py:21, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict()` inclui o campo `password` e é retornado por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
Impact: Vazamento do hash da senha de qualquer usuário a qualquer cliente anônimo.
Recommendation: Remover `password` da serialização pública — Playbook P3/P4.

### [CRITICAL] Autenticação falsa e endpoints sem proteção
File: routes/user_routes.py:207-211, routes/user_routes.py:134-151, routes/task_routes.py:225-238
Description: O login devolve `'token': 'fake-jwt-token-' + str(user.id)`, token previsível que nenhuma rota valida; todas as rotas (inclusive `DELETE /users/<id>`, `PUT /users/<id>` com `role`, `DELETE /tasks/<id>`) são públicas.
Impact: Qualquer cliente pode listar/alterar/apagar usuários e tarefas e se promover a `admin`.
Recommendation: Emitir token assinado (HMAC com `SECRET_KEY`) e proteger rotas de escrita/administrativas com middleware — Playbook P3.

### [CRITICAL] Servidor com debug ligado exposto em 0.0.0.0
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` ativa o debugger interativo do Werkzeug em todas as interfaces.
Impact: Execução remota de código via console do debugger.
Recommendation: Controlar `debug`/`host` por config/ambiente com default seguro (debug desligado, host 127.0.0.1) — Playbook P2.

### [HIGH] Lógica de negócio, validação e queries dentro das routes
File: routes/task_routes.py:11-63, routes/task_routes.py:85-154, routes/task_routes.py:156-223, routes/report_routes.py:12-101, routes/report_routes.py:103-155
Description: Os handlers validam payload, consultam `Model.query`, agregam métricas, montam dicts de resposta e fazem commit; não há camada de controllers/serviços de domínio.
Impact: Regras não testáveis sem HTTP; routes inchadas e acopladas ao ORM.
Recommendation: Routes só mapeiam URL → controller; controllers orquestram; models concentram persistência e regras do domínio — Playbook P5/P6/P8.

### [HIGH] Sem app factory, estado e efeitos colaterais no import
File: app.py:9-16, app.py:30-31, seed.py:2
Description: `app` é um global de módulo, a config é montada inline (`sqlite:///tasks.db` em app.py:11) e `db.create_all()` roda no import; `seed.py` importa o `app` global.
Impact: Impossível criar instâncias isoladas (testes), config acoplada ao código e efeitos colaterais ao importar o módulo.
Recommendation: `create_app(config)` em `src/app.py` como composition root, config em módulo próprio — Playbook P7/P8.

### [HIGH] Categorias implementadas dentro de report_routes
File: routes/report_routes.py:157-223
Description: O CRUD de categorias vive no Blueprint de relatórios (`reports`), misturando dois domínios e sem model/controller próprio.
Impact: Violação de SRP/MVC: routes de relatório respondendo por outro recurso, difícil de localizar e evoluir.
Recommendation: Extrair `category_routes` + `category_controller` — Playbook P5/P6.

### [HIGH] Serviço de notificação com credenciais embutidas e estado em memória, nunca usado
File: services/notification_service.py:4-48
Description: `NotificationService` guarda `self.notifications` em memória, abre SMTP com credenciais fixas e não é importado por nenhuma rota.
Impact: Código morto que carrega segredos e, se ligado, perderia estado a cada reinício e seria acoplado ao envio de e-mail.
Recommendation: Receber configuração por injeção (settings), remover estado em memória ou persistir, e remover se não usado — Playbook P2/P7.

### [MEDIUM] N+1 Queries
File: routes/task_routes.py:41-57, routes/user_routes.py:22, routes/report_routes.py:53-68, routes/report_routes.py:163
Description: `GET /tasks` faz `User.query.get` e `Category.query.get` por tarefa; `GET /users` acessa `len(u.tasks)` (lazy load por usuário); o relatório faz uma query de tasks por usuário; `GET /categories` faz um `count()` por categoria.
Impact: Número de queries cresce linearmente com os dados.
Recommendation: `joinedload`/`GROUP BY` e agregações em uma única query — Playbook P10.

### [MEDIUM] Lógica de "atrasada" duplicada 6 vezes (e método do model ignorado)
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:283-287, routes/report_routes.py:33-43, routes/report_routes.py:132-135, routes/user_routes.py:171-180
Description: O mesmo aninhamento `due_date < utcnow` + status ≠ done/cancelled é copiado nas routes, embora `Task.is_overdue()` (models/task.py:50-60) já exista e não seja usado.
Impact: Correção de regra exige alterar 6 pontos; risco de divergência.
Recommendation: Centralizar em `Task.is_overdue` e reutilizar — Playbook P11.

### [MEDIUM] Validação duplicada e helpers de validação sem uso
File: routes/task_routes.py:92-114, routes/task_routes.py:166-184, routes/user_routes.py:61-72, routes/user_routes.py:106-121, utils/helpers.py:19-23, utils/helpers.py:57-108, utils/helpers.py:110-116
Description: Status válidos, papéis, regex de e-mail e limites de título aparecem em routes, no model (task.py:38-48) e em `helpers`; `process_task_data`, `validate_email` e as constantes `VALID_*`/`MIN_*` existem mas nenhuma rota os usa.
Impact: Regras divergentes entre criar e atualizar; código morto confunde a manutenção.
Recommendation: Um único módulo de validação/constantes consumido pelos controllers — Playbook P9/P11.

### [MEDIUM] Validação de tipos ausente (500 em entrada inválida)
File: routes/task_routes.py:113, routes/task_routes.py:182, routes/task_routes.py:261, routes/task_routes.py:264, routes/report_routes.py:196-197, routes/user_routes.py:125
Description: `priority < 1` com valor não numérico levanta `TypeError`; `int(priority)`/`int(user_id)` na busca levantam `ValueError`; `PUT /categories/<id>` com corpo vazio faz `'name' in None`; `active` aceita qualquer valor; `color` de categoria não é validada (`helpers.is_valid_color` não é usado).
Impact: Entradas inválidas geram 500 em vez de 400.
Recommendation: Validar tipo/intervalo no controller e responder 400 — Playbook P9.

### [MEDIUM] Tratamento de erro genérico e não centralizado
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:204, routes/task_routes.py:236, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221, utils/helpers.py:47-49, utils/helpers.py:88
Description: `except:` sem tipo e try/except repetido em cada handler, retornando mensagens ad hoc e engolindo a causa do erro.
Impact: Falhas silenciosas, impossibilidade de diferenciar erros, resposta de erro inconsistente.
Recommendation: Erros de domínio + error handler global — Playbook P11.

### [MEDIUM] Remoções em cascata silenciosas e dados órfãos
File: routes/user_routes.py:140-142, routes/report_routes.py:211-223
Description: `DELETE /users/<id>` apaga todas as tasks do usuário sem aviso; `DELETE /categories/<id>` mantém `category_id` apontando para uma categoria inexistente nas tasks.
Impact: Perda de dados inesperada e referências quebradas.
Recommendation: Definir política explícita (limpar `category_id`/cascade documentado) em transação — Playbook P12.

### [MEDIUM] Listagens sem paginação
File: routes/task_routes.py:14, routes/user_routes.py:12, routes/report_routes.py:159
Description: `GET /tasks`, `/users` e `/categories` carregam todos os registros (o próprio seed lista "Adicionar paginação na API").
Impact: Respostas e consumo de memória crescem sem limite.
Recommendation: Aceitar `page`/`per_page` opcionais com limites — Playbook P10.

### [LOW] Imports não utilizados
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:5-6, routes/report_routes.py:5, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:3-7
Description: `os, sys, json, time, hashlib, re, math` e outros importados e nunca usados; `requests`, `marshmallow` e `python-dotenv` constam em requirements.txt:4-6 sem uso.
Impact: Ruído e dependências desnecessárias.
Recommendation: Remover imports e dependências mortas — Playbook P14.

### [LOW] Magic numbers e strings espalhados
File: routes/user_routes.py:64, routes/user_routes.py:115, routes/report_routes.py:45, routes/report_routes.py:83-89, routes/task_routes.py:99-114, models/task.py:12
Description: Tamanho mínimo de senha (4), janela de 7 dias, limites de título (3/200), faixa de prioridade (1-5) e rótulos de prioridade soltos no código, apesar de constantes existirem em `helpers.py:110-116`.
Impact: Regras implícitas, difíceis de alterar de forma consistente.
Recommendation: Constantes nomeadas em um módulo único — Playbook P14.

### [LOW] Logging com print()
File: routes/task_routes.py:149,153,219,234, routes/user_routes.py:83,89,147, utils/helpers.py:36-41, services/notification_service.py:21,24
Description: Mensagens de log via `print` sem nível, formato ou destino configurável.
Impact: Sem controle de verbosidade e sem timestamps consistentes.
Recommendation: Usar `logging` com logger por módulo — Playbook P13.

### [LOW] Nomes pouco descritivos e serialização duplicada
File: routes/report_routes.py:24-28, routes/task_routes.py:17-28, routes/user_routes.py:162-169
Description: Variáveis `p1..p5`, `t`, `u`, `cat`; a montagem manual do dict da task repete `Task.to_dict` (models/task.py:23-36).
Impact: Legibilidade reduzida e divergência de campos entre rotas.
Recommendation: Nomes descritivos e reuso de `to_dict` — Playbook P14.

## Deprecated APIs
- `Model.query.get(id)` (legado no SQLAlchemy 2.x) — routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227; routes/user_routes.py:29, 94, 136, 155; routes/report_routes.py:105, 192, 213. Substituir por `db.session.get(Model, id)`.
- `datetime.utcnow()` (deprecated desde o Python 3.12) — models/task.py:15-16, 52; models/user.py:14; models/category.py:11; routes/task_routes.py:31, 72, 215, 285; routes/user_routes.py:172; routes/report_routes.py:35, 42, 45, 71, 133; utils/helpers.py:38; services/notification_service.py:35; seed.py:66-74. Substituir por `datetime.now(timezone.utc)`.

================================
Total: 20 findings
================================
