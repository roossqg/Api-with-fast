from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from fast_pr.settings import Settings

engine = create_engine(Settings().DATABASE_URL)

def get_session(engine):
    with Session(engine) as session:
        yield session