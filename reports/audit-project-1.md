================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, usuários, pedidos, relatórios de vendas)
Architecture:  Monolítica — 4 arquivos planos (app.py, controllers.py, models.py, database.py); models mistura acesso a dados com regra de negócio; rotas e handlers admin dentro do app.py
Source files:  4 files analyzed (~780 lines)
DB tables:     produtos, usuarios, pedidos, itens_pedido (SQLite, loja.db)
Entry point:   app.py
Endpoints:     18 mapped
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] SQL Injection (concatenação de SQL com input do usuário)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155-166, models.py:174, models.py:188, models.py:192, models.py:206, models.py:220, models.py:224, models.py:279-281, models.py:289-297
Description: Todas as queries são montadas com `"..." + valor + "..."` (ex.: `login_usuario` em models.py:109-111 concatena `email` e `senha`; `buscar_produtos` em models.py:289-297 concatena `termo`, `categoria`, `preco_min`, `preco_max`; `criar_produto` em models.py:47-50 concatena `nome`, `descricao`, `categoria`).
Impact: Permite bypass de login (`' OR '1'='1`), vazamento e destruição de dados em qualquer endpoint que receba parâmetros.
Recommendation: Usar queries parametrizadas (`cursor.execute("... WHERE id = ?", (id,))`) em todo o acesso a dados — Playbook P1.

### [CRITICAL] Hardcoded Credentials / Secret Key exposta
File: app.py:7, controllers.py:285-289, database.py:76-78
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` está fixa no código (app.py:7) e ainda é devolvida em texto puro pelo endpoint `/health` (controllers.py:289, junto com `db_path` e `debug`). As senhas do seed (`admin123`, `123456`, `senha123`) também estão no código (database.py:76-78).
Impact: Qualquer pessoa com acesso ao repositório ou ao endpoint `/health` obtém o segredo usado para assinar sessões; credenciais de admin conhecidas.
Recommendation: Mover para módulo de configuração lendo variáveis de ambiente, remover segredos do `/health` e documentar em `.env.example` — Playbook P2.

### [CRITICAL] Endpoints administrativos sem autenticação (Backdoor)
File: app.py:47-57, app.py:59-78
Description: `POST /admin/reset-db` apaga todas as tabelas (app.py:51-55) e `POST /admin/query` executa SQL arbitrário recebido no corpo (`cursor.execute(query)`, app.py:69) — ambos sem qualquer autenticação/autorização.
Impact: Qualquer cliente pode ler, alterar ou apagar todo o banco remotamente (execução remota de SQL).
Recommendation: Remover `/admin/query` e proteger/remover `/admin/reset-db` (restrito a ambiente de desenvolvimento via config e checagem de papel admin) — Playbook P3.

### [CRITICAL] Senhas armazenadas e expostas em texto puro
File: database.py:76-78, models.py:83, models.py:99, models.py:110, models.py:127-128, controllers.py:155-160
Description: A coluna `senha` guarda o texto original (comparado direto em `WHERE ... senha = '...'`, models.py:110) e `get_todos_usuarios`/`get_usuario_por_id` retornam `"senha": row["senha"]` (models.py:83, 99) em `GET /usuarios` e `GET /usuarios/<id>`.
Impact: Vazamento total das credenciais dos usuários em uma única requisição; sem hash, qualquer comprometimento do banco expõe todas as senhas.
Recommendation: Armazenar hash (`werkzeug.security.generate_password_hash`/`check_password_hash`) e nunca serializar o campo senha — Playbook P4.

### [HIGH] God Module: models.py mistura persistência, regra de negócio e formatação
File: models.py:1-314
Description: Um único arquivo concentra acesso a dados de 4 domínios (produtos, usuários, pedidos, relatórios), serialização manual e regras de negócio: validação de estoque e cálculo de total em `criar_pedido` (models.py:133-169) e cálculo de desconto progressivo em `relatorio_vendas` (models.py:256-262).
Impact: Impossível testar regra de negócio sem banco; qualquer mudança afeta todos os domínios; viola SRP.
Recommendation: Separar um model por entidade (apenas persistência) e mover regras para controllers/serviços — Playbook P5/P6.

### [HIGH] Estado global mutável: conexão de banco singleton
File: database.py:4-5, database.py:7-11, database.py:86
Description: `db_connection` e `db_path` são globais de módulo; `get_db()` usa `global db_connection` e abre a conexão com `check_same_thread=False`, compartilhada por todas as requisições. Schema e seed são criados dentro do próprio `get_db()` (database.py:14-84).
Impact: Conexão compartilhada entre threads sem controle, acoplamento forte (todos os models e controllers importam `get_db`), difícil de testar e de trocar o banco.
Recommendation: Extrair configuração (`DATABASE_PATH`) para config, criar conexão por requisição (`flask.g`/teardown) e separar init do schema/seed — Playbook P7.

### [HIGH] Lógica de negócio e roteamento misturados em controllers e no entry point
File: controllers.py:24-62, controllers.py:64-96, controllers.py:188-220, controllers.py:237-255, controllers.py:264-290, app.py:32-78
Description: Controllers validam payloads, aplicam regras de categoria/status e disparam "notificações" (prints de e-mail/SMS/push, controllers.py:208-210). `health_check` abre cursor e executa SQL direto (controllers.py:266-274). `app.py` define handlers de rota (`index`, `reset_database`, `executar_query`) e acessa o banco diretamente (app.py:47-78) em vez de apenas compor a aplicação.
Impact: Camadas acopladas; `app.py` não é um composition root; regras não reutilizáveis nem testáveis isoladamente.
Recommendation: Controllers apenas orquestram (validação → model → resposta), rotas em módulo de views/routes, entry point só compõe — Playbook P6/P8.

### [HIGH] Debug ativo e vazamento de informação interna
File: app.py:8, app.py:88, controllers.py:286-288
Description: `DEBUG=True` (app.py:8) e `app.run(host="0.0.0.0", debug=True)` (app.py:88) expõem o depurador Werkzeug em todas as interfaces; `/health` devolve `"ambiente": "producao"`, `"db_path"` e `"debug": True` (controllers.py:286-288); controllers retornam `str(e)` ao cliente.
Impact: Execução remota de código via console do debugger e exposição de detalhes internos.
Recommendation: Ler `DEBUG`/`HOST`/`PORT` de variáveis de ambiente com default seguro e retornar mensagens genéricas via error handler — Playbook P2/P9.

### [MEDIUM] N+1 Queries em listagem de pedidos
File: models.py:171-201, models.py:203-233
Description: `get_pedidos_usuario` e `get_todos_pedidos` executam 1 query de pedidos + 1 query de itens por pedido (models.py:187-188, 219-220) + 1 query de produto por item (models.py:191-192, 223-224).
Impact: Número de queries cresce com pedidos × itens; degrada a performance de `/pedidos`.
Recommendation: Usar um único JOIN (`pedidos/itens_pedido/produtos`) e agrupar em memória — Playbook P10.

### [MEDIUM] Duplicação de código (serialização e validação)
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:178-199, models.py:211-232, controllers.py:28-50, controllers.py:74-90
Description: O mapeamento linha→dict de produto aparece 3 vezes e o de usuário 2 vezes; o bloco de listagem de pedidos com itens é copiado entre `get_pedidos_usuario` e `get_todos_pedidos`; a validação de produto se repete (e diverge) entre `criar_produto` e `atualizar_produto`.
Impact: Correção em um ponto não propaga; inconsistência (update não valida tamanho do nome nem categoria, controllers.py:87-90 vs 43-54).
Recommendation: Extrair `to_dict()`/helpers de serialização e validadores compartilhados — Playbook P11.

### [MEDIUM] Validação de entrada ausente ou incompleta
File: controllers.py:39-46, controllers.py:150-158, controllers.py:169-174, controllers.py:195-203, controllers.py:239-243, models.py:275-283
Description: `preco`/`estoque` não têm tipo checado (`preco < 0` quebra com string → 500); e-mail sem formato; `login` e `atualizar_status_pedido` chamam `dados.get` sem verificar `dados is None`; itens do pedido não têm `produto_id`/`quantidade` validados (quantidade negativa/zero); atualizar status não verifica se o pedido existe.
Impact: Dados inválidos chegam ao banco e geram 500 em vez de 400.
Recommendation: Validar tipos/faixas/formatos na camada de controller antes de chamar o model — Playbook P11.

### [MEDIUM] Tratamento de erros repetido e sem handler centralizado
File: controllers.py:6-12, controllers.py:15-22, controllers.py:60-62, controllers.py:95-96, controllers.py:108-109, controllers.py:125-126, controllers.py:133-134, controllers.py:143-144, controllers.py:164-165, controllers.py:185-186, controllers.py:218-220, controllers.py:226-227, controllers.py:234-235, controllers.py:254-255, controllers.py:261-262, controllers.py:291-292
Description: Todos os 16 handlers repetem `try/except Exception` devolvendo `str(e)` com 500; não há `errorhandler` global.
Impact: Respostas de erro inconsistentes, vazamento de mensagens internas e boilerplate repetido.
Recommendation: Criar middleware/error handler centralizado e levantar exceções de domínio — Playbook P9.

### [MEDIUM] Criação de pedido sem transação/atomicidade e regra de estoque incompleta
File: models.py:133-169, controllers.py:249-250
Description: `criar_pedido` faz validação de estoque, inserção do pedido, itens e baixa de estoque em passos separados sem `try/rollback`, com checagem e atualização não atômicas (race condition). Ao cancelar um pedido, apenas imprime "Devolver estoque" (controllers.py:250) sem devolver.
Impact: Pedidos parciais e estoque inconsistente em caso de falha ou concorrência.
Recommendation: Envolver a operação em transação com rollback no erro e implementar a devolução de estoque no cancelamento — Playbook P12.

### [LOW] Logging com print() e notificações simuladas
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:219, controllers.py:248, controllers.py:250, app.py:56, app.py:83-86
Description: Logs e "envio de e-mail/SMS/push" são `print` espalhados pelos controllers e pelo entry point (inclusive e-mail do usuário em login, controllers.py:179).
Impact: Sem níveis, sem formato, difícil de filtrar; dados pessoais em stdout.
Recommendation: Usar o módulo `logging` configurado centralmente — Playbook P13.

### [LOW] Magic numbers e strings soltas
File: controllers.py:47-52, controllers.py:242, models.py:257-262, app.py:88
Description: Limites de nome (2/200), lista de categorias e de status, faixas de desconto (10000/5000/1000 → 10%/5%/2%) e porta 5000 estão inline no código.
Impact: Difícil de entender e alterar regras; duplicação potencial.
Recommendation: Extrair para constantes no módulo de config — Playbook P14.

### [LOW] Nomenclatura e imports não utilizados
File: models.py:2, database.py:2, controllers.py:14, controllers.py:64, controllers.py:98, controllers.py:136, controllers.py:56
Description: `import sqlite3` sem uso em models.py:2 e `import os` sem uso em database.py:2; parâmetro/variável `id` sombreia o builtin (controllers.py:14, 64, 98, 136, 56); mistura de português e inglês nos nomes.
Impact: Ruído e risco de bugs sutis; legibilidade reduzida.
Recommendation: Remover imports mortos e renomear para `produto_id`/`usuario_id` — Playbook P14.

## Deprecated APIs
None detected

================================
Total: 16 findings
================================
