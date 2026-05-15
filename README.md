# To-Do List API

A simple api where you can create your tasks and view their status.
after create a login,you can create a task with the structure:

- _title_: str;
- _description_: str;
- _status_: Todostatus;

_status_ consists in four states that you can set you task in create/upgrade. 

There's no limit of task creation. 


## Techs  (icons)
- Fastapi: Python backend api structure
    - Sqlalchemy: Python database interations
    - Postgresql: robust database
    - Pydantic: Python data validation
    - Alembic: database alters (migrations)

-  Jwt:
    Json Web Token Authentication

- Docker: development,Postgresql database and app distribuition.
    - Docker Compose: Deployment e setting env instructions

- Tests:
    Pytest

- Enviroitment
    Poetry: install dependencies

### Arquiteture (tree+docs print)


### Variables
#### User:
- DATABASE_URL: user info and task storage address
- SECRET_KEY: user password
- ALGORITHM: use to create hashs
- TOKEN_EXPIRE_MINUTES: expire jwt token

#### Database:
- POSTGRES_USER
- POSTGRES_DB
- POSTGRES_PASSWORD

## How Use/Examples (install+init+use/example sucess)

+app rotation fluxogram