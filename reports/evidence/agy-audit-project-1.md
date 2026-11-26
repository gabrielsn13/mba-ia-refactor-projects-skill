================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 4 | LOW: 5

## Findings

### 1. [CRITICAL] SQL Injection (AP-01)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155, models.py:157-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-299
Description: Todas as consultas SQL em `models.py` constroem instruções `SELECT`, `INSERT`, `UPDATE` e `DELETE` concatenando strings com entradas vindas da requisição (`nome`, `descricao`, `categoria`, `email`, `senha`, `novo_status`, `termo`, `id`, `usuario_id`, `pedido_id`, `produto_id`), incluindo filtros `LIKE '%" + termo + "%'` em `buscar_produtos` e autenticação em `login_usuario`.
Impact: Permite que atacantes leiam, alterem ou apaguem qualquer dado do banco SQLite (`loja.db`) e contornem a autenticação de login via payloads SQL maliciosos.
Recommendation: Substituir todas as concatenações por queries parametrizadas com placeholders `?` do `sqlite3` (ex.: `cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))`) ou adotar ORM/repositórios parametrizados.

### 2. [CRITICAL] Credenciais e segredos hardcoded (AP-02)
File: app.py:7-8, controllers.py:288-289
Description: O segredo da aplicação (`app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`) e a flag `app.config["DEBUG"] = True` estão fixos no código-fonte. Além disso, o endpoint público `GET /health` (`health_check`) retorna `"debug": True` e `"secret_key": "minha-chave-super-secreta-123"` no JSON de resposta.
Impact: Compromete a confidencialidade de sessões/tokens assinados pela `SECRET_KEY` e expõe publicamente segredos e configurações internas para qualquer cliente da API.
Recommendation: Carregar `SECRET_KEY` e demais segredos via variáveis de ambiente em um módulo de configuração dedicado (documentado em `.env.example`) e remover imediatamente `secret_key`, `debug` e `db_path` da resposta de `health_check`.

### 3. [CRITICAL] Endpoints perigosos/administrativos sem autenticação (AP-03)
File: app.py:47-57, app.py:59-78, app.py:14-28
Description: O arquivo `app.py` expõe `POST /admin/reset-db` (`reset_database`), que apaga todos os registros de `itens_pedido`, `pedidos`, `produtos` e `usuarios`, e `POST /admin/query` (`executar_query`), que executa diretamente qualquer comando SQL enviado no campo `"sql"` do JSON, ambos sem autenticação ou autorização. Ademais, nenhuma rota de escrita ou leitura sensível (`POST/PUT/DELETE /produtos`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<int:pedido_id>/status`, `GET /relatorios/vendas`) exige autenticação.
Impact: Qualquer usuário anônimo na rede pode apagar toda a base de dados, executar SQL arbitrário, consultar dados de usuários ou modificar catálogo e status de pedidos.
Recommendation: Remover o endpoint `POST /admin/query` (execução de SQL arbitrário), remover ou proteger `POST /admin/reset-db` atrás de autenticação/autorização estrita de administrador, e adicionar middleware de autenticação e controle de acesso por perfil (`admin`/`cliente`) nas rotas protegidas.

### 4. [CRITICAL] Tratamento inseguro de senhas e dados sensíveis (AP-04)
File: database.py:75-83, models.py:79-86, models.py:95-102, models.py:109-111, models.py:126-129
Description: As senhas dos usuários iniciais em `database.py` (`"admin123"`, `"123456"`, `"senha123"`) e dos novos usuários em `criar_usuario` são gravadas em texto puro na coluna `senha`; `login_usuario` compara a senha em texto puro na query; e `get_todos_usuarios` / `get_usuario_por_id` incluem `"senha": row["senha"]` nos dicionários retornados pelos endpoints `GET /usuarios` e `GET /usuarios/<int:id>` (`controllers.py:128-144`).
Impact: Exposição direta das senhas de todos os usuários pela API HTTP e comprometimento imediato de todas as contas em caso de vazamento do banco `loja.db`.
Recommendation: Armazenar apenas hashes seguros gerados com `werkzeug.security.generate_password_hash` / `bcrypt` / `argon2`, verificar com `check_password_hash` e remover o campo `senha` de todos os retornos e serializadores de usuário.

### 5. [CRITICAL] God Class / God File (AP-05)
File: models.py:1-314, controllers.py:1-292, app.py:1-88
Description: Os arquivos centrais acumulam múltiplas responsabilidades distintas: `models.py` (314 linhas) mistura queries SQL diretas de 4 entidades, serialização manual, lógica de negócio (`criar_pedido`, `relatorio_vendas`) e mensagens de erro; `controllers.py` (292 linhas) mistura parsing HTTP, validação de domínio, simulação de notificações e queries SQL diretas (`health_check`); `app.py` mistura configuração hardcoded, registro de rotas, endpoints administrativos com SQL direto e boot do servidor.
Impact: Alto acoplamento entre infraestrutura, domínio e transporte HTTP, dificultando testes unitários isolados, manutenção e evolução para o padrão MVC.
Recommendation: Separar responsabilidades em camadas distintas: `config` (variáveis de ambiente e setup), `models`/`repositories` (entidades e acesso a dados), `services` (regras de negócio e notificações), `controllers` (orquestração HTTP) e `routes`/`blueprints` (roteamento).

### 6. [HIGH] Lógica de negócio em controllers/rotas (sem camada adequada) (AP-06)
File: app.py:47-78, controllers.py:208-210, controllers.py:247-250, controllers.py:266-274, models.py:133-169, models.py:235-273
Description: As rotas `reset_database` e `executar_query` em `app.py` e o controller `health_check` em `controllers.py` importam `get_db()` e executam SQL diretamente. Em `controllers.py`, `criar_pedido` e `atualizar_status_pedido` disparam notificações diretamente no fluxo HTTP, enquanto regras de negócio como validação de estoque, cálculo de total, baixa de estoque e faixas de desconto (`relatorio_vendas`) residem acopladas a queries SQL em `models.py`, sem camada de serviço.
Impact: Impede reutilização de regras de negócio fora do contexto HTTP/SQL e obriga alterações de domínio a modificar diretamente rotas, controllers ou queries.
Recommendation: Introduzir uma camada `services/` para encapsular regras de pedidos, estoque, relatórios e notificações, mantendo rotas apenas para roteamento, controllers para entrada/saída HTTP e models/repositórios exclusivamente para persistência.

### 7. [HIGH] Estado global mutável / acoplamento forte sem injeção de dependência (AP-07)
File: database.py:4-11, app.py:4, controllers.py:3, models.py:1
Description: `database.py` mantém uma variável global mutável `db_connection = None` modificada por `global db_connection` dentro de `get_db()` com `sqlite3.connect(db_path, check_same_thread=False)`. Todos os módulos (`app.py`, `controllers.py`, `models.py`) importam e invocam diretamente esse singleton global sem injeção de dependência.
Impact: Risco de corrupção/concorrência em acesso simultâneo à mesma conexão SQLite entre threads, vazamento de estado entre testes e impossibilidade de injetar bancos de teste isolados.
Recommendation: Gerenciar conexões por requisição usando contexto da aplicação (`flask.g` + `teardown_appcontext`) ou factory de conexão/sessão injetada nos repositórios/serviços.

### 8. [HIGH] Operações multi-etapa sem transação / integridade (AP-08)
File: models.py:133-169, models.py:65-70, models.py:275-283, database.py:14-53
Description: `criar_pedido` verifica estoque em um loop, insere o pedido, relê preços, insere itens e atualiza estoque em outro loop sem bloco transacional com `rollback` em caso de exceção nem controle contra condições de corrida. O schema em `database.py` não define `FOREIGN KEY` entre `pedidos`/`usuarios` e `itens_pedido`/`pedidos`/`produtos`, permitindo exclusão de produtos referenciados (`deletar_produto`) e criação de pedidos para usuários inexistentes. Além disso, `atualizar_status_pedido` não valida se `pedido_id` existe nem estorna estoque ao cancelar.
Impact: Risco de inconsistência de dados (pedidos sem itens, estoque negativado ou divergente, registros órfãos no banco).
Recommendation: Envolver operações multi-etapa em transação atômica com `commit`/`rollback` explícito (e `PRAGMA foreign_keys = ON` + `FOREIGN KEY` no schema), validar existência dos registros e implementar estorno de estoque em cancelamentos dentro da camada de serviço.

### 9. [MEDIUM] Queries N+1 (AP-09)
File: models.py:171-201, models.py:203-233, models.py:239-254, controllers.py:268-274
Description: Tanto `get_pedidos_usuario` quanto `get_todos_pedidos` executam uma query para buscar pedidos e, dentro de dois loops aninhados, executam queries individuais em `itens_pedido` (por pedido) e em `produtos` (por item). Adicionalmente, `relatorio_vendas` dispara 5 queries separadas na tabela `pedidos` e `health_check` executa 4 queries sequenciais.
Impact: Degradação severa de latência e I/O no banco conforme cresce o número de pedidos e itens listados.
Recommendation: Substituir os loops de queries em `get_pedidos_usuario` e `get_todos_pedidos` por `JOIN` único entre `pedidos`, `itens_pedido` e `produtos` (ou busca em lote com `IN (...)`) e consolidar as métricas de `relatorio_vendas` em uma única query SQL agregada.

### 10. [MEDIUM] Duplicação de código (AP-10)
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:177-200, models.py:209-232, controllers.py:28-50, controllers.py:72-90
Description: A serialização campo a campo de `produto` está duplicada em `get_todos_produtos`, `get_produto_por_id` e `buscar_produtos`; a serialização de `usuario` está duplicada em `get_todos_usuarios` e `get_usuario_por_id`; a montagem de pedido com seus itens está duplicada entre `get_pedidos_usuario` e `get_todos_pedidos`; e as regras de validação de produto estão duplicadas (de forma inconsistente) entre `criar_produto` e `atualizar_produto`.
Impact: Aumenta o custo de manutenção e gera divergências de comportamento (como `atualizar_produto` não validar tamanho do nome nem `categorias_validas`).
Recommendation: Extrair funções/métodos serializadores (`to_dict` / mappers por entidade), unificar a listagem de pedidos com filtro opcional por `usuario_id` e centralizar a validação de produto em um validador compartilhado.

### 11. [MEDIUM] Tratamento de erro inadequado/repetitivo (AP-11)
File: controllers.py:5-292, app.py:68-78
Description: Todos os 16 handlers em `controllers.py` (linhas 6-12, 15-22, 25-62, 65-96, 99-109, 112-126, 129-134, 137-144, 147-165, 168-186, 189-220, 223-227, 230-235, 238-255, 258-262, 265-292) e `executar_query` em `app.py` replicam blocos `try ... except Exception as e` retornando `str(e)` com status 500. O formato das respostas de erro também varia entre `{"erro": ...}`, `{"erro": ..., "sucesso": False}` e `{"status": "erro", "detalhes": str(e)}`.
Impact: Vazamento de mensagens internas de exceção/SQL para o cliente, poluição visual nos controllers e contrato de erro inconsistente.
Recommendation: Implementar exceções de domínio específicas e um error handler centralizado no Flask (`@app.errorhandler`) que registre o detalhe no logger e devolva um formato JSON padronizado e seguro.

### 12. [MEDIUM] Validação ausente/fraca na borda (AP-12)
File: controllers.py:43-54, controllers.py:87-90, controllers.py:118-121, controllers.py:153-160, controllers.py:169-171, controllers.py:196-204, controllers.py:239-243, app.py:61-62
Description: `login` (`controllers.py:169`), `atualizar_status_pedido` (`controllers.py:239`) e `executar_query` (`app.py:61`) chamam `request.get_json()` sem verificar `None` antes de acessar `.get(...)`. `buscar_produtos` converte `preco_min`/`preco_max` com `float(...)` sem tratar `ValueError`. `criar_produto` e `atualizar_produto` comparam `preco < 0` e `estoque < 0` sem checar tipo numérico, e `atualizar_produto` ignora validação de `len(nome)` e `categoria`. Em `criar_pedido`, os objetos de `itens` não validam presença/tipo de `produto_id` nem `quantidade > 0` (permitindo quantidades negativas que aumentariam o estoque).
Impact: Entradas malformadas provocam exceções não tratadas (HTTP 500) ou corrompem regras de negócio (como incremento indevido de estoque via quantidade negativa).
Recommendation: Criar validadores/schemas explícitos na borda da API validando JSON obrigatório, tipos, faixas numéricas (ex.: `quantidade > 0`) e retornando HTTP 400 padronizado.

### 13. [LOW] Magic numbers e strings (AP-14)
File: models.py:150, models.py:247-262, controllers.py:47-54, controllers.py:242, controllers.py:285-287, database.py:5, database.py:32, database.py:40, database.py:76-78, app.py:36, app.py:88
Description: Limiares e alíquotas de desconto (`10000`, `0.1`, `5000`, `0.05`, `1000`, `0.02`) em `relatorio_vendas`, limites de tamanho de nome (`2`, `200`), lista de categorias válidas, status de pedidos (`"pendente"`, `"aprovado"`, `"enviado"`, `"entregue"`, `"cancelado"`), papéis (`"cliente"`, `"admin"`), porta `5000`, host `"0.0.0.0"`, versão `"1.0.0"` e `"loja.db"` aparecem como literais espalhados no código.
Impact: Dificulta alteração de regras e aumenta o risco de erros de digitação entre camadas.
Recommendation: Extrair constantes nomeadas e enums para módulos `config.py` / `constants.py` compartilhados.

### 14. [LOW] Logging inadequado (AP-15)
File: app.py:56, app.py:83-86, controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:219, controllers.py:248, controllers.py:250
Description: A aplicação utiliza chamadas `print(...)` diretamente para registrar inicialização, reset de banco, listagens, erros críticos, tentativas de login com e-mail do usuário e simulações de envio de e-mail, SMS e push.
Impact: Ausência de níveis de log (`INFO`, `WARNING`, `ERROR`), timestamps e formatação estruturada, além de exposição de dados de usuários no stdout.
Recommendation: Substituir todos os `print(...)` por `logging` padrão do Python configurado centralmente e mover notificações para um serviço dedicado.

### 15. [LOW] Nomenclatura ruim e código morto (AP-16)
File: app.py:13, app.py:15-16, app.py:19, controllers.py:14, controllers.py:56, controllers.py:64, controllers.py:98, controllers.py:136, controllers.py:160, models.py:2, models.py:24, models.py:54, models.py:65, models.py:89, models.py:187, models.py:191, models.py:219, models.py:223, database.py:2
Description: Uso repetido do identificador `id` sombreando a função builtin `id()` do Python em rotas, controllers e models; variáveis pouco descritivas como `cursor2`, `cursor3` e `prod` em `models.py`; e imports não utilizados (`import os` em `database.py:2` e `import sqlite3` em `models.py:2`).
Impact: Reduz a legibilidade do código e pode causar bugs sutis pelo sombreamento do builtin `id()`.
Recommendation: Renomear `id` para nomes semânticos (`produto_id`, `usuario_id`), eliminar variáveis numeradas (`cursor2`/`cursor3`) e remover os imports não utilizados.

### 16. [LOW] Configuração de execução insegura (AP-17)
File: app.py:8, app.py:82, app.py:88, database.py:5, database.py:10
Description: `app.py` fixa `app.config["DEBUG"] = True`, `host="0.0.0.0"` e `port=5000` diretamente no código e inicializa o banco dentro do bloco `if __name__ == "__main__"`. `database.py` fixa `db_path = "loja.db"` sem leitura de variáveis de ambiente.
Impact: Impede configuração segura por ambiente (desenvolvimento vs produção) e dificulta empacotamento/testes com factory de aplicação.
Recommendation: Criar application factory (`create_app`), ler host, porta, debug e `DB_PATH` de variáveis de ambiente com valores padrão seguros e documentá-los em `.env.example`.

### 17. [LOW] Uso de servidor de desenvolvimento Flask com debug=True em produção (Deprecated API)
File: app.py:88, controllers.py:286, controllers.py:288
Description: `app.py` executa `app.run(host="0.0.0.0", port=5000, debug=True)` enquanto a própria API se declara em produção (`"ambiente": "producao"` e `"debug": True` em `health_check`), padrão obsoleto/desencorajado pelo Flask para ambientes produtivos por expor o debugger interativo Werkzeug e utilizar o servidor de desenvolvimento single-process.
Impact: Exposição crítica de execução remota de código caso o modo debug fique ativo em rede acessível e baixa resiliência/concorrência em produção.
Recommendation: Remover `debug=True` hardcoded de `app.run`, utilizar `flask run` controlado por variáveis de ambiente (`FLASK_DEBUG`) em desenvolvimento e servidor WSGI (como `gunicorn` ou `waitress`) em produção.

## Deprecated APIs
app.py:88 — `app.run(host="0.0.0.0", port=5000, debug=True)` em produção → `flask run` com variável de ambiente / servidor WSGI (`gunicorn`/`waitress`)

================================
Total: 17 findings
================================
