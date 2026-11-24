# Catálogo de Anti-Patterns (Fase 2)

Para cada anti-pattern: **sinais de detecção** (procure por grep/leitura), **severidade** e **recomendação**. Os exemplos de sintaxe são ilustrativos: aplique o mesmo raciocínio a qualquer linguagem.

Escala: CRITICAL (segurança/arquitetura grave) > HIGH (violação forte de MVC/SOLID) > MEDIUM (padronização, duplicação, performance moderada) > LOW (legibilidade).

---

## CRITICAL

### AP-01 — SQL Injection
- **Sinais**: SQL montado por concatenação/interpolação com entrada externa: `"... WHERE id = " + str(id)`, `f"SELECT ... {x}"`, `` `SELECT ... ${x}` ``, `"... LIKE '%" + termo + "%'"`; `execute(` recebendo string concatenada.
- **Recomendação**: queries parametrizadas (`?`, `%s`, `:nome`) ou ORM.

### AP-02 — Credenciais e segredos hardcoded
- **Sinais**: `SECRET_KEY = "..."`, `password`, `pass`, `token`, `api_key`, `pk_live_`, `smtp` literais em código; `DEBUG = True` fixo; segredos devolvidos em respostas (ex.: health check).
- **Recomendação**: módulo de config lendo variáveis de ambiente (+ `.env.example`), nunca devolver segredos.

### AP-03 — Endpoints perigosos/administrativos sem autenticação
- **Sinais**: rotas `/admin/*`, `reset-db`, execução de SQL arbitrário vindo do cliente (`execute(request.json["sql"])`), DELETE/PUT de usuários sem checagem de identidade/role; token falso (`'fake-jwt-token-' + id`).
- **Recomendação**: remover endpoints de execução arbitrária; proteger rotas administrativas com middleware de autenticação/autorização.

### AP-04 — Tratamento inseguro de senhas e dados sensíveis
- **Sinais**: senha em texto puro no banco/seed; hash fraco (`md5`, `sha1`, base64 "cripto" caseira); campo `password/senha` incluído em `to_dict`/respostas JSON; log de número de cartão/senha.
- **Recomendação**: hash com bcrypt/argon2/`werkzeug.security`/`scrypt`; remover campos sensíveis de respostas e logs.

### AP-05 — God Class / God File
- **Sinais**: um arquivo/classe com rotas + SQL/DB init + regras de negócio + formatação (ex.: classe que cria schema, registra rotas e processa checkout; `app.py` com rotas e SQL direto); arquivo com >300 linhas misturando ≥3 responsabilidades.
- **Recomendação**: separar em config, models, controllers, views/routes, middlewares.

---

## HIGH

### AP-06 — Lógica de negócio em controllers/rotas (sem camada adequada)
- **Sinais**: handlers que validam, calculam, consultam o banco e disparam notificações no mesmo corpo; regras de desconto/estoque/overdue dentro de rotas; `Model.query` ou `db.execute` dentro de arquivos de rota.
- **Recomendação**: controllers orquestram; regras no model/service; rotas só roteiam.

### AP-07 — Estado global mutável / acoplamento forte sem injeção de dependência
- **Sinais**: `global db_connection`; módulo-level `cache = {}` ou contadores mutáveis; singletons importados diretamente e instanciados em construtores (`new sqlite3.Database` no `constructor`); `self.email_password` fixo em serviço.
- **Recomendação**: factory/ connection por contexto, injeção via parâmetro/construtor, cache com limite ou removido.

### AP-08 — Operações multi-etapa sem transação / integridade
- **Sinais**: várias escritas dependentes (pedido + itens + estoque; usuário + matrícula + pagamento) sem `BEGIN/commit/rollback` atômico; checagem de estoque separada do decremento; deleção de entidade pai sem remover/tratar filhas; `except` sem rollback.
- **Recomendação**: transação única com rollback em erro; `ON DELETE CASCADE`/remoção explícita dos dependentes.

---

## MEDIUM

### AP-09 — Queries N+1
- **Sinais**: query dentro de `for`/`forEach`/callback iterando resultados (`for pedido in pedidos: cursor.execute("... WHERE pedido_id = ...")`); `Model.query.get(x.fk)` por item; `len(user.tasks)` em loop; contagem por entidade em loop.
- **Recomendação**: JOIN, `IN (...)`, `joinedload`/`selectinload`, `GROUP BY`.

### AP-10 — Duplicação de código
- **Sinais**: mesmo bloco de serialização campo a campo copiado; mesma condicional aninhada (ex.: overdue) em ≥2 lugares; mesma lista de status/categorias/regex repetida; validação idêntica em criar/atualizar.
- **Recomendação**: extrair função/método (ex.: `to_dict`, `is_overdue`), constantes e validadores compartilhados.

### AP-11 — Tratamento de erro inadequado/repetitivo
- **Sinais**: `try/except Exception` com `str(e)` devolvido ao cliente; `except:` nu; try/except idêntico em cada handler; erros engolidos; mensagens/formatos de erro inconsistentes (string solta vs JSON).
- **Recomendação**: error handler centralizado + exceções de domínio; log do detalhe, mensagem genérica ao cliente.

### AP-12 — Validação ausente/fraca na borda
- **Sinais**: `request.get_json()` usado sem checar `None`; conversões `int(...)`/`float(...)` sem tratamento; tipos não validados (`preco < 0` com string); validar só presença; funções de validação definidas e não usadas.
- **Recomendação**: camada de validação (schema/validators) que devolve 400 com mensagem clara.

### AP-13 — Callback hell / fluxo assíncrono ingovernável
- **Sinais**: callbacks aninhados ≥3 níveis; contadores manuais (`pending--`) para sincronizar respostas; resposta enviada de dentro de callbacks profundos.
- **Recomendação**: Promises/`async-await`, helpers que promisificam a API do driver, queries agregadas.

---

## LOW

### AP-14 — Magic numbers e strings
- **Sinais**: literais numéricos de regra (`10000`, `0.1`, `4`, `3`, `200`), prefixos de cartão `"4"`, status/roles/categorias como strings soltas, constantes definidas mas ignoradas.
- **Recomendação**: constantes nomeadas em módulo de config/constants.

### AP-15 — Logging inadequado
- **Sinais**: `print(...)`/`console.log(...)` para eventos de negócio, erros, "ENVIANDO EMAIL" simulados; log de dados sensíveis.
- **Recomendação**: `logging`/logger estruturado com níveis.

### AP-16 — Nomenclatura ruim e código morto
- **Sinais**: variáveis abreviadas (`u`, `e`, `p`, `cc`, `cid`, `cursor2/3`); `id` sombreando builtin; imports não usados; funções/exports/constantes nunca referenciados; `type(x) == list` em vez de `isinstance`.
- **Recomendação**: nomes descritivos; remover código morto e imports não usados.

### AP-17 — Configuração de execução insegura
- **Sinais**: `debug=True` fixo no `app.run`, `host="0.0.0.0"` fixo, `db.create_all()`/init com side effects em import, porta fixa.
- **Recomendação**: ler de config/env; init em função do composition root.

---

## APIs Deprecated / Obsoletas (severidade LOW, MEDIUM se quebrar em versão atual)

Verifique manifestos de dependência e o código. Reporte como finding "Deprecated API" com o equivalente moderno.

| Ecossistema | Obsoleto (sinal) | Equivalente moderno |
|---|---|---|
| SQLAlchemy 2.x / Flask-SQLAlchemy 3.x | `Model.query.get(id)` | `db.session.get(Model, id)` |
| Python 3.12+ | `datetime.utcnow()`, `utcfromtimestamp()` | `datetime.now(timezone.utc)` |
| Flask | `@app.before_first_request`, `flask.json.JSONEncoder` | init no factory / `app.json` provider |
| Flask | `app.run(debug=True)` em produção | `flask run` + variável de ambiente / WSGI |
| Python | `collections.Mapping` etc., `imp`, `distutils`, `asyncio.get_event_loop()` solto | `collections.abc`, `importlib`, `asyncio.run` |
| Node.js | `new Buffer(x)` / `Buffer(x)` | `Buffer.from(x)` / `Buffer.alloc(n)` |
| Node.js | `require('crypto').createCipher` | `createCipheriv` |
| Node.js | `url.parse()`, `fs.exists`, `util.isArray` | `new URL()`, `fs.existsSync`/`access`, `Array.isArray` |
| Express 4+ | `bodyParser` externo, `app.del()`, `res.send(status)` numérico | `express.json()`, `app.delete()`, `res.sendStatus()` |
| Node (qualquer) | `request` (pacote) | `fetch` nativo/`axios`/`undici` |
| Geral | hashes `md5`/`sha1` para senha | `bcrypt`/`argon2`/`scrypt` |

Cheque também versões fixadas no manifesto com avisos de EOL conhecidos.

---

## Regra de classificação (resumo)

- Entrada do usuário chegando a SQL/comando, segredo exposto, acesso administrativo aberto, senha insegura, God Class → **CRITICAL**.
- Regras de negócio na camada errada, estado global, falta de transação → **HIGH**.
- N+1, duplicação, erros genéricos, validação ausente, callback hell → **MEDIUM**.
- Magic numbers, logging, nomes, código morto, deprecated sem quebra → **LOW**.
