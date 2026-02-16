from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fast_pr.app import app
from fast_pr.models import table_registry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    # sql object out of metadata

    engine = create_engine('sqlite:///:memory:')

    table_registry.metadata.create_all(engine)
    # --> uses sqlite base to create a map of database in metadata

    with Session(engine) as session:  # log on metadata
        yield session

    table_registry.metadata.drop_all(engine)
    # --> exit from base of database after session
    engine.dispose()


@contextmanager
def _mockdb_in_time(*, model, time=datetime(2025, 1, 1)):

    def fake_data(mapper, connection, target):

        if hasattr(target, 'creation'):  # verify if object has taget atibute
            target.creation = time

        if hasattr(target, 'last_update'):
            target.last_update = time
            # each model atr traks its value with time

    event.listen(model, 'before_insert', fake_data)

    yield time

    event.remove(model, 'before_insert', fake_data)


@pytest.fixture
def mock_db():
    return _mockdb_in_time
