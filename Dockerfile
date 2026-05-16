FROM python:3.13-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /fast_pr/app/
COPY . .

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi --without dev

EXPOSE 10000
CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn fast_pr.app:app --host 0.0.0.0 --port 10000"]