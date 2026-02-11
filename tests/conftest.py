import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_pr.app import app
from fast_pr.models import table_registry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():

    engine = create_engine('sqlite:///:memory:')

    table_registry.metadata.create_all(engine)
    # --> uses sqlite base to create a map of database in metadata

    with Session(engine) as session:  # log on metadata
        yield session

    table_registry.metadata.drop_all(engine)
    # --> exit from base of database after session
    engine.dispose()
