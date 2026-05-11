from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from fast_pr.app import app
from fast_pr.database import get_session
from fast_pr.models import Users, table_registry
from fast_pr.security import get_hash_password


class UserFactory(factory.Factory):
    class Meta:
        model = Users

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    # sql object out of metadata

    # engine = create_async_engine(
    # 'sqlite+aiosqlite:///:memory:',
    # poolclass=StaticPool,
    # connect_args={'check_same_thread': False},
    # use same tread-connection,same comunnication channel

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    # table_registry.metadata.create_all(engine)
    # --> uses sqlite base to create a map of database in metadata

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # log on metadata
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    # --> exit from base of database after session
    engine.dispose()


@contextmanager
def _mockdb_in_time(*, model, time=datetime(2025, 1, 1)):

    def fake_data(mapper, connection, target):

        if hasattr(target, 'creation'):  # verify if object has taget atibute
            target.creation = time

        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

        if hasattr(target, 'last_update'):
            target.last_update = time
            # each model atr traks its value with time

    event.listen(model, 'before_insert', fake_data)

    yield time

    event.remove(model, 'before_insert', fake_data)


@pytest.fixture
def mock_db():
    return _mockdb_in_time


@pytest_asyncio.fixture
async def user(session):

    password = 'boopass'
    user = UserFactory(password=get_hash_password(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # object to verify:
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def other_user(session):

    password = 'boopass'
    user = UserFactory(password=get_hash_password(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # object to verify:
    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']
