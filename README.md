# Documentação do Projeto Fast Zero API

## 1. Visão Geral do Projeto

O "Fast Zero" é um projeto de API backend construído com **FastAPI**, projetado para gerenciar usuários e suas respectivas listas de tarefas (To-Do). Ele implementa funcionalidades de CRUD (Criar, Ler, Atualizar, Deletar) para ambos os recursos, com um sistema de autenticação robusto baseado em tokens JWT (JSON Web Tokens).

**Principais Tecnologias e Conceitos:**

* **FastAPI:** Framework web moderno e de alta performance para construir APIs com Python.
* **Pydantic:** Usado para validação de dados, serialização e configurações, garantindo contratos de API claros.
* **SQLAlchemy:** Utilizado como ORM (Object Relacional Mapper) para interagir com o banco de dados de forma orientada a objetos (o arquivo `models.py`, embora não fornecido, é fundamental para definir as tabelas `User` e `Todo`).
* **JWT (JSON Web Tokens):** Para autenticação stateless e segura dos endpoints.
* **Injeção de Dependência:** Amplamente utilizada pelo FastAPI para gerenciar sessões de banco de dados, autenticação e outros recursos.
* **Design Modular:** A API é organizada em routers (`users`, `todos`, `auth`), promovendo a separação de responsabilidades.

---

## 2. Filosofia de Design e Funcionamento

A arquitetura do projeto parece seguir as melhores práticas para desenvolvimento de APIs com FastAPI, visando clareza, testabilidade e manutenibilidade.

* **Separação de Responsabilidades:**
    * **Routers (`users.py`, `todo.py`, `auth.py`):** Cada arquivo define os endpoints para um recurso específico, mantendo a lógica de cada API agrupada.
    * **Schemas (`schemas.py`):** Define a estrutura dos dados de entrada e saída, desacoplando a lógica da API da representação dos dados. Isso é crucial para validação automática e para a documentação interativa do FastAPI (Swagger/OpenAPI).
    * **Segurança (`security.py`):** Centraliza toda a lógica de autenticação, criação e verificação de tokens, e hashing de senhas.
    * **Banco de Dados (`database.py`, `models.py`):** `database.py` configura a engine e a gestão de sessões. O `models.py` (assumido) definiria as tabelas do banco de dados.
* **Segurança em Primeiro Lugar:**
    * Endpoints que manipulam dados sensíveis ou específicos do usuário são protegidos, exigindo um token JWT válido.
    * Senhas são armazenadas com hash (`get_password_hash`, `verify_password`).
    * Permissões são verificadas para garantir que um usuário só possa modificar seus próprios dados (ex: `update_user`, `delete_todo`).
* **Eficiência e Clareza:**
    * Uso de `Annotated` e `Depends` para injeção de dependências de forma explícita.
    * Respostas e status HTTP seguem os padrões RESTful.
    * Validação de dados de entrada e saída é feita automaticamente pelo FastAPI usando os schemas Pydantic.

---

## 3. Fluxo de Autenticação (`auth.py` e `security.py`)

A autenticação é um pilar central do projeto.

1.  **Login (`POST /auth/token`):**
    * **Lógica:** O usuário envia `username` (que é o email, conforme o código) e `password` via `OAuth2PasswordRequestForm`.
    * O sistema busca o usuário pelo email no banco.
    * Se encontrado, a senha fornecida é verificada contra o hash armazenado (`verify_password`).
    * Se as credenciais forem válidas, um `access_token` JWT é gerado (`create_access_token`). O *subject* (`sub`) do token é o email do usuário.
    * **Pensamento:** Este é o fluxo padrão OAuth2 para obtenção de token. A escolha do email como `sub` é comum para identificar o usuário.

2.  **Criação e Verificação de Token (`security.py`):**
    * `create_access_token(data: dict)`: Adiciona um tempo de expiração ao token (configurado em `settings.ACCESS_TOKEN_EXPIRE_MINUTES`) e o assina usando `settings.SECRET_KEY` e `settings.ALGORITHM`.
    * `get_current_user(token: str = Depends(oauth2_scheme))`: Esta é uma dependência crucial usada para proteger rotas.
        * Ela extrai o token JWT do header `Authorization: Bearer`.
        * Decodifica o token usando a `SECRET_KEY` e o `ALGORITHM`.
        * Verifica a assinatura e o tempo de expiração.
        * Extrai o `username` (email) do payload do token (`sub`).
        * Busca o usuário no banco de dados com base nesse email.
        * Se qualquer passo falhar (token inválido, expirado, usuário não encontrado), uma `HTTPException` (401 Unauthorized) é levantada.
    * **Pensamento:** A separação dessas funções em `security.py` torna o código dos routers mais limpo e reutilizável. O uso de `OAuth2PasswordBearer` integra-se perfeitamente com a documentação automática do FastAPI.

3.  **Refresh de Token (`POST /auth/refresh_token`):**
    * **Lógica:** Este endpoint requer um token JWT válido no header (pois depende de `get_current_user`).
    * Uma vez que o usuário atual é identificado, um novo `access_token` é gerado para ele.
    * **Pensamento:** Permite que os usuários estendam sua sessão sem precisar reenviar suas credenciais, desde que possuam um token ainda válido (ou recentemente expirado, dependendo da lógica de refresh que poderia ser mais complexa, mas aqui parece ser para um token ativo).

4.  **Hashing de Senhas:**
    * `get_password_hash(password: str)`: Usa `pwdlib` para gerar um hash seguro da senha.
    * `verify_password(plain_password: str, hashed_password: str)`: Verifica se a senha fornecida corresponde ao hash armazenado.
    * **Pensamento:** Essencial para a segurança, nunca armazenando senhas em texto plano.

---

## 4. Gerenciamento de Usuários (`users.py`)

Este router lida com todas as operações relacionadas a usuários.

1.  **Criação de Usuário (`POST /users/`):**
    * **Lógica:** Recebe dados do usuário (`UserSchema`: username, email, password).
    * Verifica se já existe um usuário com o mesmo `username` ou `email`. Se sim, levanta `HTTPException` (400 Bad Request) para evitar duplicidade.
    * O password é transformado em hash.
    * Um novo objeto `User` (modelo SQLAlchemy) é criado e salvo no banco.
    * Retorna os dados públicos do usuário (`UserPublic`, que não inclui o password).
    * **Pensamento:** Validação de unicidade de username/email é crucial. A separação entre `UserSchema` (entrada com senha) e `UserPublic` (saída sem senha) é uma boa prática de segurança.

2.  **Leitura de Usuários (`GET /users/`):**
    * **Lógica:** Lista usuários com paginação (parâmetros `limit` e `offset`).
    * **Observação:** Este endpoint, como está no código fornecido, **não está protegido** pela dependência `get_current_user`. Isso significa que qualquer um pode listar os usuários. Se a intenção era restringir isso, a dependência deveria ser adicionada.
    * **Pensamento:** Paginação é importante para APIs que podem retornar muitos itens.

3.  **Atualização de Usuário (`PUT /users/{user_id}`):**
    * **Lógica:** Protegido por `get_current_user`.
    * Verifica se o `current_user.id` (obtido do token) é o mesmo que o `user_id` na URL. Se não for, levanta `HTTPException` (403 Forbidden), garantindo que um usuário só possa atualizar seu próprio perfil.
    * Atualiza os campos `email`, `username` e `password` (o novo password também é hasheado).
    * Salva as alterações no banco.
    * **Pensamento:** A verificação de permissão é fundamental para a segurança dos dados do usuário.

4.  **Deleção de Usuário (`DELETE /users/{user_id}`):**
    * **Lógica:** Similar à atualização, é protegido e verifica se o `current_user.id` corresponde ao `user_id`.
    * Remove o usuário do banco.
    * Retorna uma mensagem de sucesso.
    * **Pensamento:** Novamente, a checagem de permissão é a chave aqui.

---

## 5. Gerenciamento de Tarefas (To-Do) (`todo.py`)

Este router gerencia as tarefas, que são sempre associadas a um usuário.

1.  **Criação de Tarefa (`POST /todos/`):**
    * **Lógica:** Protegido por `get_current_user`.
    * Recebe dados da tarefa (`TodoSchema`: title, description, state).
    * Cria um novo objeto `Todo` (modelo SQLAlchemy), associando-o ao `user.id` do `current_user`.
    * Salva no banco.
    * **Pensamento:** Garante que toda tarefa criada pertença ao usuário autenticado.

2.  **Listagem de Tarefas (`GET /todos/`):**
    * **Lógica:** Protegido por `get_current_user`.
    * Retorna **apenas as tarefas que pertencem ao `current_user`**.
    * Permite filtragem por `title`, `description` e `state` através do schema `FilterTodo`, que também inclui `offset` e `limit` para paginação. Os filtros são aplicados dinamicamente à query SQLAlchemy se fornecidos.
    * **Pensamento:** Crucial para a privacidade dos dados. A filtragem dinâmica e a paginação tornam a API flexível e eficiente.

3.  **Atualização Parcial de Tarefa (`PATCH /todos/{todo_id}`):**
    * **Lógica:** Protegido por `get_current_user`.
    * Recebe dados para atualização (`TodoUpdate`, que permite que nem todos os campos sejam enviados).
    * Busca a tarefa no banco, garantindo que ela pertença ao `current_user` e que o `todo_id` exista. Se não, `HTTPException` (404 Not Found).
    * Itera sobre os campos fornecidos no `todo.model_dump(exclude_unset=True)` e atualiza apenas eles no objeto `db_todo`.
    * Salva as alterações.
    * **Pensamento:** O uso de `PATCH` e `exclude_unset=True` é ideal para atualizações parciais, evitando a necessidade de enviar o objeto completo. A verificação de propriedade é mantida.

4.  **Deleção de Tarefa (`DELETE /todos/{todo_id}`):**
    * **Lógica:** Protegido por `get_current_user`.
    * Busca a tarefa, verificando a propriedade e existência, similar à atualização.
    * Remove a tarefa do banco.
    * **Pensamento:** Operação direta, mas segura pela verificação de propriedade.

---

## 6. Schemas e Validação de Dados (`schemas.py`)

Os schemas Pydantic são a espinha dorsal da validação e serialização de dados.

* **`UserSchema` vs `UserPublic`:** `UserSchema` é usado para entrada (criação/atualização) e inclui o campo `password`. `UserPublic` é usado para saída e omite o `password` por segurança, incluindo o `id` do usuário. `model_config = ConfigDict(from_attributes=True)` permite que os modelos Pydantic sejam criados a partir de objetos ORM.
* **`TodoSchema` vs `TodoPublic`:** Similarmente, `TodoSchema` para entrada e `TodoPublic` para saída (incluindo `id`).
* **`TodoUpdate`:** Permite que `title`, `description` e `state` sejam opcionais (`None`), facilitando atualizações parciais com `PATCH`.
* **`Token`:** Define a estrutura da resposta de login.
* **`Message`:** Um schema genérico para respostas simples com uma mensagem.
* **`UserList`, `TodoList`:** Usados para encapsular listas de usuários/tarefas, facilitando a estruturação da resposta JSON.
* **`FilterPage`, `FilterTodo`:** `FilterPage` define a base para paginação (`offset`, `limit`). `FilterTodo` herda dela e adiciona campos específicos para filtrar tarefas.
* **`TodoState` (importado de `fast_zero.models`):** Assumindo que seja um Enum (ex: `PENDING`, `IN_PROGRESS`, `DONE`) para o estado da tarefa, provendo tipos de dados mais ricos e validação.
* **Pensamento:** O uso de schemas Pydantic:
    * Fornece validação de dados automática para todas as requisições.
    * Serializa automaticamente os dados de resposta no formato correto.
    * Gera automaticamente a documentação da API (Swagger UI / OpenAPI) com os modelos de dados esperados.
    * Cria um contrato claro entre o frontend e o backend.

---

## 7. Interação com Banco de Dados (`database.py` e uso nos routers)

* **`database.py`:**
    * Cria uma `engine` SQLAlchemy usando a `DATABASE_URL` das configurações (`Settings`).
    * A função `get_session()` é um gerador que fornece uma `Session` SQLAlchemy. O uso de `with Session(engine) as session: yield session` garante que a sessão seja fechada corretamente após a requisição, mesmo em caso de erros. O `# pragma: no cover` sugere que esta parte pode ser difícil de testar unitariamente de forma isolada e é comumente excluída da análise de cobertura de testes diretos, confiando em testes de integração.
* **Uso nos Routers:**
    * A dependência `T_Session = Annotated[Session, Depends(get_session)]` injeta uma sessão de banco de dados em cada endpoint que a necessita.
    * As operações utilizam SQLAlchemy Core/ORM para construir queries (ex: `select(User).where(...)`, `session.scalars(...)`, `session.scalar(...)`).
    * `session.add(objeto)`, `session.commit()`, `session.refresh(objeto)`, `session.delete(objeto)` são usados para persistir as mudanças.
* **Pensamento:** A gestão de sessão por requisição é uma prática padrão para evitar problemas de concorrência e garantir que os recursos sejam liberados. O uso do ORM abstrai a complexidade do SQL direto, embora ainda permita queries customizadas e eficientes.

---

## 8. Configurações (Inferido de `settings.py`)

Embora o arquivo `settings.py` não tenha sido fornecido, seu uso é evidente em `security.py` e `database.py` através da classe `Settings`. Este arquivo provavelmente contém:

* `DATABASE_URL`: String de conexão com o banco de dados.
* `SECRET_KEY`: Chave secreta para assinar os JWTs.
* `ALGORITHM`: Algoritmo usado para assinar os JWTs (ex: `HS256`).
* `ACCESS_TOKEN_EXPIRE_MINUTES`: Tempo de validade dos tokens de acesso.
* **Pensamento:** Usar uma classe de configurações (possivelmente Pydantic `BaseSettings`) é uma boa prática para carregar configurações de variáveis de ambiente ou arquivos `.env`, mantendo-as centralizadas e fáceis de gerenciar.

---
