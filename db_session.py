import os
from typing import Optional, Callable

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

PASSWORD = os.environ["db_password"]
DATABASE_URL = os.environ["DATABASE_URL"]
Base = declarative_base()

__factory: Optional[Callable[[], orm.Session]] = None


def global_init():
    global __factory
    if __factory:
        return

    conn_str = DATABASE_URL
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=True)
    __factory = orm.sessionmaker(bind=engine)
    Base.metadata.create_all(engine)


def create_session() -> orm.Session:
    global __factory
    return __factory()
