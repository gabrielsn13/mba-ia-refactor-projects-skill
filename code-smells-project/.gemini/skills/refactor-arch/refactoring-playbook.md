# Playbook de Refatoração (Fase 3)

Padrões concretos de transformação. Cada um mapeia anti-patterns do catálogo (AP-xx). Exemplos em Python e JavaScript; aplique o equivalente na stack do projeto.

---

## P1 — Queries parametrizadas (AP-01)

**Antes (Python/sqlite)**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**Depois**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```
Busca com LIKE: `cursor.execute("... WHERE nome LIKE ?", (f"%{termo}%",))`. Filtros dinâmicos: monte a lista de condições e de parâmetros separadamente; nunca concatene valores.

**Antes (JS)** `` db.get(`SELECT * FROM users WHERE id = ${id}`) `` → **Depois** `db.get("SELECT * FROM users WHERE id = ?", [id])`.

---

## P2 — Extrair configuração e segredos (AP-02, AP-17)

**Antes**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.run(host="0.0.0.0", port=5000, debug=True)
```
**Depois** — `config/settings.py`
```python
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 5000))
DB_PATH = os.environ.get("DB_PATH", "loja.db")
```
```js
// config/index.js
module.exports = {
  port: Number(process.env.PORT) || 3000,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  dbPath: process.env.DB_PATH || ':memory:',
};
```
Crie `.env.example` com as chaves (sem valores reais). Remova segredos de respostas (ex.: `/health`).

---

## P3 — Remover/proteger endpoints administrativos (AP-03)

**Antes**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    cursor.execute(request.get_json()["sql"])
```
**Depois**: remova a execução de SQL arbitrário. Para operações administrativas legítimas (reset de banco), proteja com middleware e habilite só fora de produção:
```python
def require_admin(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if request.headers.get("X-Admin-Token") != settings.ADMIN_TOKEN:
            return jsonify({"erro": "Não autorizado"}), 401
        return fn(*a, **kw)
    return wrapper
```
```js
const requireAdmin = (req, res, next) =>
  req.get('x-admin-token') === config.adminToken ? next() : res.status(401).json({ error: 'Unauthorized' });
router.get('/admin/financial-report', requireAdmin, reportController.financial);
```

---

## P3b — Senhas e dados sensíveis (AP-04)

**Antes**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
def to_dict(self): return {..., "password": self.password}
```
**Depois**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd): self.password = generate_password_hash(pwd)
def check_password(self, pwd): return check_password_hash(self.password, pwd)
def to_dict(self): return {"id": self.id, "name": self.name, "email": self.email}  # sem password
```
```js
const bcrypt = require('bcryptjs');
const hash = await bcrypt.hash(password, 10);   // substitui badCrypto
```
Nunca logue cartão/senha: `logger.info('Processando pagamento', { last4: card.slice(-4) })`. Para dados legados (senha em texto puro/MD5), aceite o formato antigo no login e rehash na primeira autenticação bem-sucedida; seeds devem gerar hash.

---

## P4 — Quebrar God Class/File em camadas (AP-05, AP-06)

**Antes** — um arquivo com schema, rotas, regras e SQL (`AppManager.setupRoutes` com `app.post('/api/checkout', ...)` fazendo tudo).

**Depois**
```
config/settings.js
models/{userModel,courseModel,enrollmentModel,paymentModel}.js
controllers/{checkoutController,reportController,userController}.js
routes/index.js            # só mapeia
middlewares/errorHandler.js
app.js                     # composition root
```
```js
// routes/index.js
router.post('/api/checkout', checkoutController.checkout);
// controllers/checkoutController.js
exports.checkout = async (req, res, next) => {
  try { res.status(200).json(await checkoutService.process(req.body)); } catch (e) { next(e); }
};
```
Regra: cada arquivo novo tem uma responsabilidade; o entry point só compõe.

---

## P5 — Mover lógica de negócio do controller/route para model/service (AP-06, AP-10)

**Antes** (rota com regra de overdue repetida)
```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
```
**Depois**
```python
# models/task.py
def is_overdue(self):
    return bool(self.due_date and self.due_date < utcnow()
                and self.status not in ("done", "cancelled"))
# controllers/task_controller.py
data = task.to_dict(); data["overdue"] = task.is_overdue()
```
Regras de desconto: mova para o model/service e leia faixas de `config` (veja P9). Notificações viram `services/notification_service`.

---

## P6 — Eliminar estado global; injetar dependências (AP-07)

**Antes**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None: db_connection = sqlite3.connect(db_path, check_same_thread=False)
```
**Depois**
```python
# database.py
def get_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()
```
```js
class UserModel { constructor(db) { this.db = db; } }      // injeção
const userModel = new UserModel(db);                       // composition root
```
Caches globais: remova ou encapsule em objeto com limite/TTL injetado.

---

## P7 — Transações e integridade (AP-08)

**Antes**: checa estoque em um loop e escreve pedido/itens/estoque sem rollback.

**Depois**
```python
def criar_pedido(usuario_id, itens):
    with transaction() as conn:
        total = 0
        for item in itens:
            row = conn.execute("SELECT preco, estoque, nome FROM produtos WHERE id = ?", (item["produto_id"],)).fetchone()
            if row is None: raise NotFoundError(...)
            if row["estoque"] < item["quantidade"]: raise ValidationError(...)
            total += row["preco"] * item["quantidade"]
        pedido_id = conn.execute("INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)", (usuario_id, total)).lastrowid
        ...  # itens + UPDATE estoque dentro da mesma transação
    return {"pedido_id": pedido_id, "total": total}
```
Em JS, use `BEGIN`/`COMMIT`/`ROLLBACK` ou a transação do ORM. Ao deletar pai, remova dependentes na mesma transação (`DELETE FROM enrollments WHERE user_id = ?`).

---

## P8 — Eliminar N+1 (AP-09)

**Antes**
```python
for row in pedidos:
    itens = cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens: cursor3.execute("SELECT nome FROM produtos WHERE id = ...")
```
**Depois**
```python
rows = conn.execute("""
  SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
         i.produto_id, pr.nome AS produto_nome, i.quantidade, i.preco_unitario
  FROM pedidos p
  LEFT JOIN itens_pedido i ON i.pedido_id = p.id
  LEFT JOIN produtos pr ON pr.id = i.produto_id
""").fetchall()
# agrupar por p.id em um dict
```
ORM: `Task.query.options(joinedload(Task.user), joinedload(Task.category))`; contagens: `GROUP BY` único em vez de um `count()` por entidade. Preserve a ordem e as chaves originais do JSON.

---

## P9 — Constantes e magic numbers (AP-14)

**Antes** `if faturamento > 10000: desconto = faturamento * 0.1`

**Depois**
```python
# config/constants.py
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
ORDER_STATUSES = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
def calcular_desconto(total):
    return next((total * rate for limit, rate in DISCOUNT_TIERS if total > limit), 0)
```

---

## P10 — Error handler centralizado (AP-11)

**Antes**: `try/except Exception as e: return jsonify({"erro": str(e)}), 500` em cada handler.

**Depois**
```python
class AppError(Exception):
    status = 500
class NotFoundError(AppError): status = 404
class ValidationError(AppError): status = 400

@app.errorhandler(AppError)
def handle_app_error(e): return jsonify({"erro": str(e), "sucesso": False}), e.status

@app.errorhandler(Exception)
def handle_unexpected(e):
    logger.exception("Erro inesperado")
    return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```
```js
app.use((err, req, res, next) => {
  logger.error(err);
  res.status(err.status || 500).json({ error: err.status ? err.message : 'Internal server error' });
});
```
Controllers lançam exceções de domínio e removem os try/except repetidos.

---

## P11 — Validação na borda (AP-12)

**Antes**: `dados = request.get_json(); dados["preco"] < 0` sem checar `None`/tipo.

**Depois**
```python
def validate_product(data):
    if not isinstance(data, dict): raise ValidationError("Dados inválidos")
    for field in ("nome", "preco", "estoque"):
        if field not in data: raise ValidationError(f"{field} é obrigatório")
    if not isinstance(data["preco"], (int, float)) or data["preco"] < 0:
        raise ValidationError("Preço inválido")
```
Use `request.get_json(silent=True)`; envolva `int()/float()` em validação que devolve 400. Reuse o mesmo validador em criar e atualizar.

---

## P12 — Async/await no lugar de callback hell (AP-13)

**Antes**: 5 níveis de `db.get(..., (err, row) => { db.run(..., () => {...}) })`.

**Depois**
```js
const run = (sql, p = []) => new Promise((ok, ko) => db.run(sql, p, function (e) { e ? ko(e) : ok(this); }));
const get = (sql, p = []) => new Promise((ok, ko) => db.get(sql, p, (e, r) => e ? ko(e) : ok(r)));
const all = (sql, p = []) => new Promise((ok, ko) => db.all(sql, p, (e, r) => e ? ko(e) : ok(r)));

async function checkout(body) {
  const course = await get("SELECT * FROM courses WHERE id = ? AND active = 1", [body.courseId]);
  if (!course) throw new NotFoundError("Curso não encontrado");
  const user = await findOrCreateUser(body);
  const { lastID } = await run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [user.id, course.id]);
  ...
}
```

---

## P13 — Logging e limpeza (AP-15, AP-16)

**Antes** `print("ENVIANDO EMAIL: ...")`, `cursor2`, `u/e/p`, imports não usados.

**Depois**
```python
logger = logging.getLogger(__name__)
logger.info("Pedido %s criado para usuário %s", pedido_id, usuario_id)
```
Renomeie para nomes descritivos (aceitando os mesmos nomes de campos no payload externo para não quebrar clientes), remova imports/exports/funções sem uso, troque `type(x) == list` por `isinstance(x, list)`.

---

## P14 — Substituir APIs deprecated

| Antes | Depois |
|---|---|
| `User.query.get(id)` | `db.session.get(User, id)` |
| `datetime.utcnow()` | `datetime.now(timezone.utc)` (mantenha naive se o schema/comparações exigirem: `datetime.now(timezone.utc).replace(tzinfo=None)`) |
| `new Buffer(x)` | `Buffer.from(x)` |
| `md5` para senha | P3b |

Teste após cada troca: a semântica de datas naive/aware pode quebrar comparações.

---

## Ordem de aplicação recomendada

1. P2 (config) → 2. P1 (SQL parametrizado) → 3. P3/P3b (segurança) → 4. P6 (conexão/DI) → 5. P4/P5 (camadas) → 6. P7, P8 (transações, N+1) → 7. P10, P11 (erros, validação) → 8. P12 (async) → 9. P9, P13, P14 (limpeza).
Valide (boot + endpoints) ao fim de cada bloco grande, não só no final.
