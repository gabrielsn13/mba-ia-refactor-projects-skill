================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3.14 + Flask 3.0.0
Files:   25 analyzed | ~1262 lines of code

## Summary
CRITICAL: 0 | HIGH: 1 | MEDIUM: 3 | LOW: 3

## Findings

### 1. [HIGH] Lógica de negócio, regras de acesso e agregações acopladas aos controllers (AP-06)
File: src/controllers/report_controller.py:20-111, src/controllers/task_controller.py:44-173, src/controllers/user_controller.py:35-125, src/controllers/validators.py:13-17,84-102
Description: Embora as views em `src/views/` apenas roteiem requisições, os controllers executam diretamente queries/agregações SQLAlchemy, cálculos de domínio e verificações de contexto HTTP. Em `src/controllers/report_controller.py`, `summary_report()` (`:20-85`) e `user_report()` (`:88-111`) realizam múltiplas consultas (`db.session.query`, `Task.query`, `User.query`, `Category.query`) e cálculos de métricas (`_rate`, `days_overdue`, `overdue`, `high_priority`). Em `src/controllers/task_controller.py`, `task_stats()` (`:158-173`) e os handlers CRUD/busca operam diretamente o ORM e calculam `completion_rate`. Em `src/controllers/user_controller.py`, `create_user()` (`:71-72`) e `update_user()` (`:84-86,101-109`) acessam diretamente `flask.g.current_user` para aplicar regras de autorização RBAC junto da persistência. Adicionalmente, `src/controllers/validators.py` mistura parsing HTTP (`flask.request` / `flask.current_app` em `get_json_body`, `parse_int_arg` e `get_pagination`) com validadores de domínio. Enquanto isso, a camada `src/services/` permanece ociosa com apenas um módulo órfão.
Impact: Acopla regras de negócio, relatórios e autorização ao framework web e à sessão SQLAlchemy nos controllers, dificultando testes unitários isolados e fragmentando a arquitetura MVC entre `controllers/` e `services/`.
Recommendation: Extrair agregações de relatório, estatísticas e casos de uso de negócio para a camada `src/services/` (ou métodos de consulta nos models), passar `actor` explicitamente das views para `user_controller` sem acoplamento a `flask.g`, e separar helpers de request HTTP dos validadores puros de domínio.

### 2. [MEDIUM] Duplicação de código em persistência transacional e cálculo de métricas (AP-10)
File: src/controllers/category_controller.py:21-27, src/controllers/task_controller.py:35-41,172, src/controllers/user_controller.py:22-28, src/controllers/report_controller.py:16-17,63
Description: A função `_commit(error_message)` com tratamento idêntico de `db.session.commit()`, `rollback()`, `logger.exception()` e `raise AppError(error_message, 500)` está copiada literalmente em três arquivos (`category_controller.py:21-27`, `task_controller.py:35-41`, `user_controller.py:22-28`). Além disso, o cálculo `round((done / total) * 100, 2) if total > 0 else 0` em `task_stats()` (`task_controller.py:172`) duplica `_rate(done, total)` (`report_controller.py:16-17`), e `report_controller.py:63` repete a tupla literal `('pending', 'in_progress', 'done', 'cancelled')` já definida como `VALID_STATUSES` em `src/config/settings.py:30`.
Impact: Alterações na política de commit, no cálculo de taxa de conclusão ou na lista de status exigem manutenção sincronizada em múltiplos módulos, aumentando o risco de regressões.
Recommendation: Extrair `commit_or_raise(error_message)` e `completion_rate(done, total)` para módulos compartilhados (ex.: `src/database/db.py` e helper/service de métricas) e importar `VALID_STATUSES` de `src/config/settings.py` em `report_controller.py:63`.

### 3. [MEDIUM] Validação ausente ou incompleta na borda da API (AP-12)
File: src/controllers/category_controller.py:43-49,57-62, src/controllers/user_controller.py:54-65,88-89, src/controllers/task_controller.py:70-88,104-125,145-146, src/controllers/validators.py:98-100
Description: Diversos campos não passam por validação de tipo, nulidade ou limites antes de chegar ao SQLAlchemy: `create_category()` (`category_controller.py:43-49`) não valida tipo/comprimento de `name` ou `description`; `update_category()` (`:57-60`) atribui `cat.name = data['name']` e `cat.description = data['description']` sem validar `None`, string vazia ou tipos inválidos; `create_user()` (`user_controller.py:59-60`) e `update_user()` (`:88-89`) não validam tipo/vazio/limite de `name`. Em `task_controller.py`, `create_task()` (`:70-72`) usa `if data.get('title')` antes de `v.validate_title` (tratando `0`/`False` como ausente), `description` (`:83,107`) e `user_id`/`category_id` (`:76-79,112-117`) não têm validação de tipo, e `search_tasks()` (`:145-146`) não valida `status` contra `VALID_STATUSES`. Por fim, `get_pagination()` (`validators.py:98-100`) usa `parse_int_arg(...) or 1` e `or 20`, mascarando `?page=0` ou `?per_page=0` em vez de rejeitar valores `< 1`.
Impact: Entradas malformadas (como `name: null` no `PUT /categories/<id>` ou objetos/listas em campos texto/FK) geram exceções internas de banco/driver (HTTP 500) em vez de HTTP 400 com mensagem clara; paginação com zero comporta-se de forma silenciosa e inconsistente com a guarda `page < 1 or per_page < 1`.
Recommendation: Adicionar validadores dedicados em `src/controllers/validators.py` para nomes (`str` não vazia e tamanho máximo), `description` (`str`), IDs inteiros opcionais (`int` não booleano ou `None`), validar `status` em `search_tasks()`, e em `get_pagination()` verificar `is None` antes de aplicar defaults (`1` e `20`).

### 4. [MEDIUM] Tratamento inconsistente de sessão em falha de login de usuário inativo (AP-11 / AP-08)
File: src/controllers/auth_controller.py:16-22, src/models/user.py:37-45, src/middlewares/error_handler.py:13-15
Description: Em `auth_controller.login()` (`:16-22`), quando um usuário inativo com hash MD5 legado tenta autenticar, `user.check_password(password)` (`src/models/user.py:42`) atualiza `self.password` na sessão antes da checagem `if not user.active: raise ForbiddenError('Usuário inativo')` (`:19-20`). Como `handle_app_error` (`error_handler.py:13-15`) não executa rollback e `login()` só faz rollback em credenciais inválidas (`:17`), a alteração fica pendente na sessão sem commit/rollback. Além disso, o `db.session.commit()` na linha `22` não possui tratamento de exceção/rollback dedicado como os demais controllers.
Impact: Deixa estado sujo na sessão em requisições rejeitadas por usuário inativo e expõe a migração de hash a erro genérico sem rollback explícito no ponto de commit.
Recommendation: Validar `user.active` antes de migrar o hash legado (ou antes de confirmar o login sem mutar estado em conta inativa), executar `db.session.rollback()` no tratamento de erro/rejeição e reutilizar o helper transacional compartilhado para `db.session.commit()`.

### 5. [LOW] Código morto: `NotificationService` e configurações `SMTP_*` sem nenhum chamador (AP-16)
File: src/services/notification_service.py:1-53, src/config/settings.py:22-25, .env.example:9-13
Description: A classe `NotificationService` (`src/services/notification_service.py:8-53`, métodos `enabled`, `send_email`, `notify_task_assigned`, `notify_task_overdue`) não é importada, instanciada ou chamada em nenhum módulo da aplicação ou dos testes. Da mesma forma, `Settings.SMTP_HOST`, `Settings.SMTP_PORT`, `Settings.SMTP_USER` e `Settings.SMTP_PASSWORD` (`src/config/settings.py:22-25`), bem como as variáveis documentadas em `.env.example:9-13`, não possuem nenhum consumidor no código. Trata-se de resquício da aplicação parcial da refatoração anterior sobre `NotificationService`.
Impact: Mantém código e configuração mortos na codebase, passando falsa impressão de que o sistema dispara notificações por e-mail ao atribuir ou atrasar tasks e inflando superfície sem testes.
Recommendation: Aplicar integralmente uma das duas resoluções: (a) **remover** `src/services/notification_service.py`, `src/services/__init__.py` (se não houver outros serviços), `Settings.SMTP_*` (`src/config/settings.py:22-25`) e as chaves `SMTP_*` do `.env.example:9-13`; ou (b) **integrar** efetivamente `NotificationService` instanciando-o no composition root (`src/app.py`) a partir de `Settings` e acionando-o nos fluxos correspondentes em `task_controller.py` (com cobertura de teste).

### 6. [LOW] Magic numbers/strings e atribuição de `lambda` remanescentes (AP-14, AP-16)
File: src/controllers/report_controller.py:13,31,96,108, src/controllers/validators.py:99, src/controllers/task_controller.py:74-75, src/config/settings.py:20
Description: Persistem alguns literais e convenções isoladas: `PRIORITY_LABELS` (`report_controller.py:13`), janela de `7` dias (`:31`), corte `t.priority <= 2` (`:108`), tamanho padrão de página `20` (`validators.py:99`), defaults `'pending'`/`3` (`task_controller.py:74-75`) e `CORS_ORIGINS` com default permissivo `'*'` (`settings.py:20`). Adicionalmente, `report_controller.py:96` atribui uma `lambda` a uma variável local (`count = lambda status: ... # noqa: E731`).
Impact: Reduz levemente a centralização de constantes de domínio/configuração e a conformidade com PEP 8 em `report_controller.py`.
Recommendation: Centralizar `PRIORITY_LABELS`, `DEFAULT_PAGE_SIZE`, `RECENT_ACTIVITY_DAYS` e `HIGH_PRIORITY_THRESHOLD` em `src/config/settings.py`, substituir `count = lambda ...` por `collections.Counter` ou função `def` local em `report_controller.py:96`, e avaliar default mais restritivo para `CORS_ORIGINS`.

### 7. [LOW] Uso da API legada `Query` do SQLAlchemy 1.x e fallback MD5 legado (Deprecated API)
File: src/controllers/auth_controller.py:15, src/controllers/category_controller.py:32,35,69, src/controllers/report_controller.py:22,24,27,32-33,40,45,59-60,93, src/controllers/task_controller.py:46,140,159,162, src/controllers/user_controller.py:36,38,48,68,92,124, seed.py:13-15,96-98, src/models/user.py:1,10,38-44
Description: Embora chamadas pontuais por PK já utilizem `db.session.get()`, os controllers e `seed.py` continuam usando extensivamente a interface legada `Model.query` e `db.session.query(...)` do SQLAlchemy 1.x em um projeto com `flask-sqlalchemy==3.1.1` (SQLAlchemy 2.x). Em `src/models/user.py:38-44`, `check_password()` ainda mantém `hashlib.md5` como fallback de migração de senhas antigas.
Impact: Mistura dois estilos de consulta do SQLAlchemy (`db.session.get` 2.x com `Model.query` / `Session.query` 1.x), dificultando migração futura ao SQLAlchemy 2.x estrito; o shim MD5 mantém código dependente de hash obsoleto enquanto não for aposentado.
Recommendation: Migrar consultas `Model.query` e `db.session.query(...)` para `db.session.execute(db.select(...))` / `db.session.scalar(db.select(...))`, e planejar a remoção do fallback `hashlib.md5` em `User.check_password()` após conclusão da migração das contas legadas.

## Deprecated APIs
- src/controllers/*.py & seed.py — `Model.query` / `db.session.query(...)` (SQLAlchemy 1.x Query API em Flask-SQLAlchemy 3.1.1) → `db.session.execute(db.select(...))` / `db.session.scalars(db.select(...))`
- src/models/user.py:40 — `hashlib.md5` (shim de migração legado em `check_password`) → `werkzeug.security.generate_password_hash` / `check_password_hash` (já usado em `set_password`, remover shim após migração)

================================
Total: 7 findings
================================
