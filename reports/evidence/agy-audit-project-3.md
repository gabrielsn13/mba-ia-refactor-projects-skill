================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 5

## Findings

### [CRITICAL] 1. Credenciais e segredos hardcoded (AP-02)
File: app.py:13, services/notification_service.py:7-10
Description: A chave secreta da aplicação (`app.config['SECRET_KEY'] = 'super-secret-key-123'`) e as credenciais SMTP (`self.email_host = 'smtp.gmail.com'`, `self.email_port = 587`, `self.email_user = 'taskmanager@gmail.com'`, `self.email_password = 'senha123'`) estão chumbadas diretamente no código-fonte.
Impact: Vazamento imediato de segredos no controle de versão, comprometimento de sessões/tokens assinados com a `SECRET_KEY` e exposição de credenciais de e-mail para qualquer pessoa com acesso ao repositório.
Recommendation: Extrair configurações e segredos para um módulo de configuração (`config.py`) lendo variáveis de ambiente via `os.environ` / `python-dotenv` e documentar as chaves esperadas em `.env.example` (sem valores reais).

### [CRITICAL] 2. Endpoints perigosos/administrativos sem autenticação (AP-03)
File: routes/user_routes.py:10-211, routes/task_routes.py:85-238, routes/report_routes.py:12-223
Description: A rota `login` (`routes/user_routes.py:207-211`) emite um token falso previsível (`'fake-jwt-token-' + str(user.id)`), e nenhuma rota da API verifica autenticação, identidade ou permissão. Endpoints sensíveis e destrutivos — como `GET /users`, `POST /users` (permite definir `role='admin'`), `PUT /users/<int:user_id>` (altera `role` e `active`), `DELETE /users/<int:user_id>` (apaga usuário e suas tasks), `POST/PUT/DELETE /tasks`, `POST/PUT/DELETE /categories` e `GET /reports/*` — ficam totalmente abertos.
Impact: Qualquer cliente anônimo pode ler dados de todos os usuários, criar ou promover contas administrativas, modificar ou excluir usuários, tarefas e categorias arbitrariamente.
Recommendation: Implementar autenticação real (ex.: JWT assinado com expiração ou sessão autenticada) e middlewares/decorators de autorização por identidade e role para proteger rotas privadas e administrativas.

### [CRITICAL] 3. Tratamento inseguro de senhas e dados sensíveis (AP-04)
File: models/user.py:16-32, routes/user_routes.py:33-40, routes/user_routes.py:85-86, routes/user_routes.py:129, routes/user_routes.py:209
Description: Os métodos `User.set_password` (`models/user.py:27-29`) e `User.check_password` (`models/user.py:31-32`) utilizam `hashlib.md5(pwd.encode()).hexdigest()` sem salt. Além disso, `User.to_dict()` (`models/user.py:16-25`) inclui `'password': self.password` na linha 21, fazendo com que `get_user`, `create_user`, `update_user` e `login` retornem o hash da senha nas respostas JSON.
Impact: Hashes MD5 sem salt podem ser quebrados em segundos por força bruta ou rainbow tables, e sua exposição direta nas respostas da API facilita a obtenção das senhas dos usuários.
Recommendation: Substituir MD5 por algoritmo seguro com salt (`werkzeug.security.generate_password_hash`/`check_password_hash`, `bcrypt` ou `argon2`) e remover o campo `password` de `User.to_dict()` e de todas as respostas JSON.

### [HIGH] 4. Lógica de negócio em controllers/rotas (sem camada adequada) (AP-06)
File: routes/task_routes.py:11-299, routes/user_routes.py:10-211, routes/report_routes.py:12-223
Description: Embora existam diretórios `models/` e `services/`, todas as rotas executam queries ORM diretamente (`Task.query`, `User.query`, `Category.query`, `db.session`), validam payloads, calculam regras de negócio (atraso `overdue`, taxa de conclusão, contagem de produtividade, autenticação) e montam DTOs inline. Adicionalmente, `routes/report_routes.py` mistura relatórios (`/reports/summary`, `/reports/user/<int:user_id>`) com o CRUD completo de categorias (`/categories`, `/categories/<int:cat_id>`).
Impact: Alto acoplamento entre camada HTTP, regras de domínio e persistência, dificultando testes unitários isolados, reaproveitamento de regras e evolução independente dos módulos.
Recommendation: Separar rotas (apenas roteamento), controllers (parsing HTTP e resposta), services (regras de negócio, cálculos e orquestração) e repositories/models (acesso a dados), movendo também o CRUD de categorias para rotas/controllers próprios (`category_routes.py` / `category_controller.py`).

### [HIGH] 5. Estado global mutável / acoplamento forte sem injeção de dependência (AP-07)
File: services/notification_service.py:4-10, services/notification_service.py:31-36, app.py:9-34, database.py:1-3, seed.py:2
Description: `NotificationService` (`services/notification_service.py:5-10`) mantém estado mutável em memória (`self.notifications = []`) e configura parâmetros SMTP fixos no construtor sem injeção de dependência. No nível da aplicação, `app.py:9-34` instancia a variável global `app = Flask(__name__)` sem Application Factory (`create_app`), e `seed.py:2` importa diretamente `from app import app, db`, disparando inicialização global.
Impact: Dificulta execução de testes isolados em paralelo, causa crescimento ilimitado de estado em memória por instância e acopla scripts/módulos a efeitos colaterais de importação.
Recommendation: Adotar Application Factory (`create_app(config)`) em `app.py`, injetar configurações e dependências via parâmetros/construtores nos serviços e persistir ou remover o histórico em memória de `NotificationService`.

### [HIGH] 6. Operações multi-etapa sem transação / integridade (AP-08)
File: models/task.py:13-14, models/task.py:20-21, routes/user_routes.py:134-151, routes/report_routes.py:211-223, seed.py:11-92
Description: As chaves estrangeiras `Task.user_id` (`models/task.py:13`) e `Task.category_id` (`models/task.py:14`) não possuem política `ondelete` nem `cascade` configurado nos relacionamentos (`models/task.py:20-21`). Em `delete_user` (`routes/user_routes.py:140-151`), a marcação de exclusão das tasks ocorre fora do bloco `try`, e em `delete_category` (`routes/report_routes.py:211-223`) a categoria é deletada sem tratar tasks vinculadas. Em `seed.py:11-92`, há múltiplos commits intermediários sem rollback em falha.
Impact: Pode deixar registros órfãos no SQLite, causar violações de chave estrangeira em bancos relacionais estritos e produzir estado inconsistente em falhas parciais.
Recommendation: Definir política de integridade referencial explícita (`ON DELETE CASCADE` ou `SET NULL` conforme regra de negócio) nos models/relacionamentos e garantir transações atômicas com `try/commit/rollback` cobrindo todas as escritas relacionadas.

### [MEDIUM] 7. Queries N+1 (AP-09)
File: routes/task_routes.py:14-59, routes/user_routes.py:12-24, routes/report_routes.py:53-68, routes/report_routes.py:159-164
Description: Em `get_tasks` (`routes/task_routes.py:16-59`), cada task do loop dispara `User.query.get(t.user_id)` (linha 42) e `Category.query.get(t.category_id)` (linha 51) — 1 + 2N queries. Em `get_users` (`routes/user_routes.py:22`), `len(u.tasks)` força lazy load por usuário. Em `summary_report` (`routes/report_routes.py:56`) e `get_categories` (`routes/report_routes.py:163`), são executadas queries por usuário (`Task.query.filter_by(user_id=u.id).all()`) e por categoria (`Task.query.filter_by(category_id=c.id).count()`) dentro de loops.
Impact: Degradação linear/quadrática de latência e sobrecarga no banco de dados conforme cresce o número de tasks, usuários e categorias.
Recommendation: Utilizar `joinedload`/`selectinload` nos relacionamentos de `Task` e `User`, e substituir contagens em loop por agregações SQL com `GROUP BY` (`db.session.query(..., func.count(...)).group_by(...)`).

### [MEDIUM] 8. Duplicação de código (AP-10)
File: models/task.py:23-60, routes/task_routes.py:17-39, routes/task_routes.py:71-80, routes/task_routes.py:92-214, routes/task_routes.py:284-296, routes/user_routes.py:61-120, routes/user_routes.py:162-180, routes/report_routes.py:34-43, routes/report_routes.py:67, routes/report_routes.py:132-151, utils/helpers.py:14-111
Description: O cálculo de atraso (`overdue`) é copiado em 6 trechos das rotas (`routes/task_routes.py:30-39,71-80,284-287`, `routes/user_routes.py:171-180`, `routes/report_routes.py:34-43,132-135`) ignorando `Task.is_overdue()` (`models/task.py:50-60`). A serialização de `Task` é replicada manualmente em `get_tasks` (`routes/task_routes.py:17-28`) e `get_user_tasks` (`routes/user_routes.py:162-169`) ignorando `Task.to_dict()`. Regras de validação de task, email, roles e cálculo de porcentagem também se repetem entre rotas e `utils/helpers.py`.
Impact: Alta propensão a divergência de regras entre endpoints (ex.: um endpoint corrige a regra de `overdue` ou validação e outros permanecem desatualizados) e maior custo de manutenção.
Recommendation: Centralizar serialização nos models/schemas, reutilizar `Task.is_overdue()` e extrair validadores e helpers de cálculo compartilhados na camada de service/schemas.

### [MEDIUM] 9. Tratamento de erro inadequado/repetitivo (AP-11)
File: routes/task_routes.py:13-63, routes/task_routes.py:135-154, routes/task_routes.py:202-238, routes/user_routes.py:80-90, routes/user_routes.py:127-151, routes/report_routes.py:182-223, utils/helpers.py:44-50, utils/helpers.py:82-89
Description: Diversos blocos utilizam `except:` nu (`routes/task_routes.py:62,137,204,236`, `routes/user_routes.py:130,149`, `routes/report_routes.py:186,207,221`, `utils/helpers.py:46,49,88`), capturando inclusive exceções de sistema. Além disso, blocos `try/except` idênticos com rollback e retorno 500 se repetem em cada handler de escrita, enquanto outros endpoints (`search_tasks`, `task_stats`, `summary_report`, `user_report`) não têm tratamento padronizado.
Impact: Mascaramento de bugs reais (como `TypeError` ou `ValueError` silenciados), respostas de erro inconsistentes (JSON vs HTML padrão do Flask em exceções não tratadas) e duplicação de boilerplate.
Recommendation: Remover todos os `except:` nus, introduzir exceções de domínio/HTTP explícitas e registrar `@app.errorhandler` centralizado para formatar respostas JSON e logs de erro de forma uniforme.

### [MEDIUM] 10. Validação ausente/fraca na borda (AP-12)
File: routes/report_routes.py:196-203, routes/task_routes.py:87-214, routes/task_routes.py:260-265, routes/user_routes.py:44-126, requirements.txt:4
Description: Em `update_category` (`routes/report_routes.py:196-197`), `request.get_json()` não é verificado contra `None` antes de `'name' in data`, causando `TypeError` 500 se o corpo for ausente/nulo, além de não validar `name` vazio ou formato de `color`. Em `search_tasks` (`routes/task_routes.py:260-264`), `int(priority)` e `int(user_id)` são convertidos sem tratamento de `ValueError`. Em `create_task`/`update_task` e `create_user`/`update_user`, tipos de campos (`title`, `priority`, `name`, `email`, `password`, `active`) não são validados antes de `len()`, comparações numéricas ou `re.match()`. O pacote `marshmallow==3.20.1` está listado em `requirements.txt:4`, mas não é utilizado.
Impact: Entradas malformadas ou com tipos inesperados geram exceções não tratadas (500 Internal Server Error) em vez de respostas `400 Bad Request` descritivas, além de permitirem gravação de dados inválidos (como nome vazio ou cor inválida).
Recommendation: Adotar uma camada explícita de validação na borda (ex.: schemas `marshmallow` ou validadores dedicados com checagem de tipos, obrigatoriedade e formatos), retornando `400` padronizado para payloads e query params inválidos.

### [LOW] 11. Magic numbers e strings (AP-14)
File: app.py:34, models/category.py:10, models/task.py:11-12, models/task.py:39, models/task.py:46, routes/task_routes.py:96-114, routes/task_routes.py:167-184, routes/user_routes.py:64-71, routes/user_routes.py:115-120, routes/report_routes.py:24-28, routes/report_routes.py:45, routes/report_routes.py:129, routes/report_routes.py:180, services/notification_service.py:8
Description: Literais de regra e infraestrutura estão espalhados pelo código — prioridades (`1` a `5`), limites de título (`3`, `200`), tamanho mínimo de senha (`4`), janela de `7` dias, cor padrão `'#000000'`, listas de status/roles e porta `5000`/`587` — ignorando inclusive as constantes já declaradas em `utils/helpers.py:110-116` (`VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH`, `MIN_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH`, `DEFAULT_PRIORITY`, `DEFAULT_COLOR`).
Impact: Risco de inconsistência entre limites aplicados em diferentes partes da API e menor legibilidade das regras de negócio.
Recommendation: Consolidar constantes de domínio e configuração em módulos dedicados (`constants.py` / `config.py`) e referenciá-las em todos os models, validadores e serviços.

### [LOW] 12. Logging inadequado (AP-15)
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21, services/notification_service.py:24, utils/helpers.py:39-41
Description: Eventos de criação, atualização, deleção e erros de banco/SMTP são registrados via `print(...)` direto em stdout, sem níveis de severidade, formatação estruturada ou controle de saída.
Impact: Dificulta filtragem, correlação e coleta de logs em ambientes de produção ou testes automatizados.
Recommendation: Substituir `print(...)` pelo módulo padrão `logging` configurado no composition root com níveis adequados (`INFO`, `WARNING`, `ERROR`).

### [LOW] 13. Nomenclatura ruim e código morto (AP-16)
File: app.py:7, models/category.py:14, models/task.py:3, models/task.py:38-60, models/user.py:34-38, routes/task_routes.py:7, routes/task_routes.py:16, routes/task_routes.py:141, routes/task_routes.py:210, routes/task_routes.py:268, routes/task_routes.py:283, routes/user_routes.py:6, routes/user_routes.py:14, routes/user_routes.py:37, routes/user_routes.py:141, routes/user_routes.py:161, routes/report_routes.py:7-8, routes/report_routes.py:33, routes/report_routes.py:55-59, routes/report_routes.py:119, routes/report_routes.py:161, services/notification_service.py:4-48, utils/helpers.py:3-116, requirements.txt:4-6
Description: Há múltiplos imports não utilizados (`os`, `sys`, `json`, `time`, `hashlib`, `math`, `format_date`, `calculate_percentage`), dependências não usadas (`marshmallow`, `requests`, `python-dotenv`), código morto nunca chamado (`NotificationService`, `Task.validate_status`, `Task.validate_priority`, `Task.is_overdue`, `User.is_admin`, todas as funções de `utils/helpers.py`), variáveis abreviadas de uma letra (`t`, `u`, `c`, `d`, `p`, `s`, `n`) e checagem de tipo com `type(...) == list` (`routes/task_routes.py:141,210`, `utils/helpers.py:103`).
Impact: Aumenta ruído cognitivo, confunde sobre qual implementação está ativa e mantém dependências desnecessárias no projeto.
Recommendation: Remover imports/código morto ou integrá-los à arquitetura alvo, usar nomes descritivos para variáveis de iteração e substituir `type(x) == list` por `isinstance(x, list)`.

### [LOW] 14. Configuração de execução insegura (AP-17)
File: app.py:11, app.py:15, app.py:30-31, app.py:34
Description: `app.py:30-31` executa `db.create_all()` como side effect durante o import do módulo; `app.py:11,15` fixa `SQLALCHEMY_DATABASE_URI` e `CORS(app)` irrestrito; e `app.py:34` executa `app.run(debug=True, host='0.0.0.0', port=5000)` com `debug=True`, host público e porta fixos.
Impact: O modo debug do Werkzeug em `0.0.0.0` expõe o console interativo em caso de erro (risco crítico em produção) e efeitos colaterais de importação dificultam testes e CLI.
Recommendation: Mover inicialização do banco para função explícita no composition root/CLI, parametrizar `DEBUG`, `HOST`, `PORT`, `DATABASE_URI` e `CORS_ORIGINS` via variáveis de ambiente e usar WSGI em produção.

### [LOW] 15. Deprecated APIs — `Model.query.get()` e `datetime.utcnow()` (Deprecated API)
File: routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/task_routes.py:117, routes/task_routes.py:122, routes/task_routes.py:158, routes/task_routes.py:188, routes/task_routes.py:195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155, routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:213, models/category.py:11, models/task.py:15-16, models/task.py:52, models/user.py:14, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:71, routes/report_routes.py:133, services/notification_service.py:35, utils/helpers.py:38, seed.py:66-67, seed.py:69-70, seed.py:74
Description: O projeto usa intensivamente `Model.query.get(...)` (16 ocorrências), marcado como legado no SQLAlchemy 2.x / Flask-SQLAlchemy 3.1.1, e `datetime.utcnow()` (21 ocorrências), obsoleto desde o Python 3.12+ (ambiente atual Python 3.14.7), além de `hashlib.md5` para senhas e `app.run(debug=True)`.
Impact: Emissão de `LegacyAPIWarning` / `DeprecationWarning` em runtime e risco de quebra em atualizações futuras de Python e SQLAlchemy.
Recommendation: Substituir `Model.query.get(id)` por `db.session.get(Model, id)` e `datetime.utcnow()` por `datetime.now(timezone.utc)` (ou helper compatível com SQLite timezone-aware/naive consistente).

## Deprecated APIs
- `routes/task_routes.py:42,51,67,117,122,158,188,195,227` — `Model.query.get(id)` → `db.session.get(Model, id)`
- `routes/user_routes.py:29,94,136,155` — `Model.query.get(id)` → `db.session.get(Model, id)`
- `routes/report_routes.py:105,192,213` — `Model.query.get(id)` → `db.session.get(Model, id)`
- `models/category.py:11` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `models/task.py:15,16,52` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `models/user.py:14` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `routes/task_routes.py:31,72,215,285` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `routes/user_routes.py:172` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `routes/report_routes.py:35,42,45,71,133` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `services/notification_service.py:35` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `utils/helpers.py:38` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `seed.py:66,67,69,70,74` — `datetime.utcnow()` → `datetime.now(timezone.utc)`
- `models/user.py:29,32` — `hashlib.md5()` para senhas → `werkzeug.security.generate_password_hash` / `bcrypt` / `argon2`
- `app.py:34` — `app.run(debug=True)` fixo → `flask run` com variáveis de ambiente / servidor WSGI

================================
Total: 15 findings
================================
