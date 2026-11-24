# Heurísticas de Análise de Projeto (Fase 1)

## 1. Detecção de linguagem

| Evidência | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `*.py` | Python |
| `package.json`, `*.js`, `*.ts`, `node_modules/` | JavaScript / TypeScript (TS se houver `tsconfig.json`) |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `go.mod`, `*.go` | Go |
| `composer.json`, `*.php` | PHP |
| `Gemfile`, `*.rb` | Ruby |
| `*.csproj`, `*.cs` | C# |

Em caso de mistura, use a linguagem da maioria dos arquivos de backend.

## 2. Detecção de framework (e versão)

Procure primeiro no manifesto de dependências (versão), depois nos imports.

| Sinal | Framework |
|---|---|
| `from flask import`, `Flask(__name__)` | Flask |
| `fastapi`, `FastAPI()` | FastAPI |
| `django`, `manage.py`, `settings.py` | Django |
| `require('express')`, `express()` | Express |
| `@nestjs/core` | NestJS |
| `fastify`, `koa`, `hapi` | respectivos |
| `spring-boot-starter-web`, `@RestController` | Spring Boot |
| `gin-gonic/gin`, `net/http` | Gin / stdlib Go |

Registre também bibliotecas relevantes (flask-cors, flask-sqlalchemy, marshmallow, sqlite3...).

## 3. Banco de dados

| Sinal | Banco / camada de acesso |
|---|---|
| `sqlite3.connect`, `new sqlite3.Database`, `*.db`, `sqlite:///` | SQLite |
| `psycopg2`, `pg`, `postgres://` | PostgreSQL |
| `mysql`, `pymysql`, `mysql2` | MySQL |
| `mongoose`, `pymongo`, `mongodb://` | MongoDB |
| `SQLAlchemy`, `db.Model`, `db.Column` | ORM SQLAlchemy |
| `sequelize`, `typeorm`, `prisma` | ORM Node |

Extraia tabelas/entidades de `CREATE TABLE`, classes `db.Model` ou schemas ORM. Anote se o banco é em memória (`:memory:`) ou arquivo.

## 4. Domínio

Deduza pelos nomes de rotas, tabelas e entidades (ex.: `produtos/pedidos` → e-commerce; `courses/enrollments/payments` → LMS com checkout; `tasks/users/categories` → gerenciador de tarefas). Descreva em uma frase.

## 5. Mapeamento de arquitetura

Para cada arquivo-fonte, classifique suas responsabilidades:

- **Rotas / View**: registro de URLs (`@app.route`, `add_url_rule`, `app.get/post`, `Blueprint`, `Router`).
- **Controller**: lê `request`, chama a lógica e devolve a resposta.
- **Regra de negócio / Service**: cálculos, validações de domínio, orquestração.
- **Model / Acesso a dados**: SQL, queries ORM, tabelas, seeds.
- **Config**: segredos, portas, flags, paths.
- **Utils / helpers**: funções auxiliares.

Classificação final:

| Padrão observado | Arquitetura |
|---|---|
| Poucos arquivos; um arquivo mistura ≥3 responsabilidades (rotas + SQL + regras) | **Monolítica / sem camadas** |
| Existem pastas `models/ routes/ services/`, mas routes/controllers fazem queries e regras | **Parcialmente em camadas** |
| Rotas só roteiam, controllers orquestram, models acessam dados, config isolada | **MVC adequado** |

## 6. Contagem e endpoints

- Conte arquivos-fonte e linhas, ignorando dependências e artefatos.
- Enumere endpoints (método + path) buscando `route(`, `add_url_rule`, `app.get|post|put|delete|patch`, `@Get`, `router.`. A lista é o contrato a preservar na Fase 3.

## 7. Como executar o projeto (baseline)

Descubra o comando de start: README, `scripts.start` do `package.json`, `app.run`, `flask run`, `manage.py runserver`. Anote a porta. Se faltar dependência, instale (`pip install -r requirements.txt`, `npm install`).
