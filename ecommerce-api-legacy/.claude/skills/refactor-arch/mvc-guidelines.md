# Guidelines de Arquitetura MVC (Fase 3)

Padrão-alvo para APIs backend. Adapte nomes e extensões à linguagem/framework detectado; **a divisão de responsabilidades é o que importa**.

## Estrutura-alvo

```
<projeto>/
├── src/                      # (ou raiz do pacote, conforme convenção da stack)
│   ├── config/               # settings: env vars, constantes, regras configuráveis
│   ├── models/               # entidades + acesso a dados (queries/ORM)
│   ├── controllers/          # orquestração de cada caso de uso
│   ├── views/ (routes/)      # mapeamento URL → controller, serialização
│   ├── middlewares/          # error handler, auth, validação, logging
│   ├── services/             # (opcional) regras de domínio/integrações externas
│   ├── utils/                # helpers puros e sem estado
│   └── app.{py,js}           # composition root / entry point
├── .env.example
└── <manifesto de dependências>
```

Em Flask é comum `app/` ou a raiz do projeto em vez de `src/`; em Express, `src/`. Mantenha o ponto de entrada original funcionando (ex.: `python app.py`, `npm start`) para não quebrar scripts e READMEs.

## Responsabilidades

### Config
- Única fonte de configuração: lê variáveis de ambiente com defaults seguros (porta, debug, DB path, segredos, chaves de gateway).
- Contém constantes de domínio (status válidos, categorias, faixas de desconto, limites).
- **Proibido**: segredos literais; chamadas de negócio.

### Models
- Representam entidades e encapsulam **todo** acesso a dados (SQL parametrizado ou ORM), incluindo joins para evitar N+1.
- Podem conter regras intrínsecas da entidade (`is_overdue`, hash de senha, `to_dict` sem campos sensíveis).
- **Proibido**: conhecer `request`/`response`, formatar HTTP, chamar controllers.

### Controllers
- Concentram o fluxo de cada caso de uso: recebem dados já extraídos da requisição, validam (ou chamam validadores), invocam models/services, aplicam regra de negócio orquestrada e devolvem um resultado/erro de domínio.
- Gerenciam transações (ou delegam ao model) e disparam notificações via services.
- **Proibido**: SQL direto; montar JSON HTTP detalhado quando o framework permitir separar (aceitável retornar dict + status).

### Views / Routes
- Apenas mapeiam método+URL para controller, extraem parâmetros/body e serializam a resposta HTTP.
- Registradas por blueprint/router agrupadas por domínio.
- **Proibido**: regra de negócio, queries, validação de domínio complexa.

### Middlewares
- Error handler **centralizado** (exceções de domínio → status HTTP + JSON padronizado; erros inesperados → 500 genérico e log).
- Autenticação/autorização para rotas sensíveis; 404 padronizado; CORS; logging de requisições.

### Entry point (composition root)
- Cria a app, carrega config, inicializa o banco, registra middlewares e rotas, inicia o servidor. Nada de regras ou SQL.
- Injeta dependências (conexão/repositórios) nos controllers por parâmetro/construtor.

## Regras de dependência

```
views → controllers → models (e services)
                 ↘ config / utils
```
- Camadas internas não importam camadas externas (models não importam controllers/views).
- Sem estado global mutável; dependências por injeção ou factory.
- Sem ciclos de import.

## Projetos parcialmente organizados

Se já existirem `models/`, `routes/`, `services/`:
1. Mantenha a convenção de nomes existente.
2. Crie `controllers/` e mova para lá a lógica que está em `routes/`; as rotas ficam finas.
3. Mova queries soltas em routes para os models (ou métodos de serviço).
4. Consolide duplicações (ex.: validações em helpers realmente usados) e remova código morto.
5. Separe rotas de domínios diferentes que dividem arquivo (ex.: categorias dentro de reports).
6. Adicione `config/` e `middlewares/` se não existirem.

## Compatibilidade

- Mesmos paths, métodos, códigos de status e chaves JSON.
- Se um campo sensível precisar sair da resposta, registre em "Behavior changes".
- Banco existente: não altere esquema de forma incompatível; migre apenas o necessário (ex.: coluna de senha continua `TEXT`).

## Checklist de saída

- [ ] Config extraída (sem segredos no código) • [ ] Models com acesso a dados parametrizado • [ ] Routes finas
- [ ] Controllers com o fluxo • [ ] Error handler central • [ ] Entry point claro • [ ] App sobe e endpoints respondem
