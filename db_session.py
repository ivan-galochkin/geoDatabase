import os
from typing import Optional, Callable
import platform
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

if platform.system() != "Windows":
    db_name = os.environ['POSTGRES_DB']
    db_password = os.environ['POSTGRES_PASSWORD']
    db_host = os.environ['DB_HOST']
    db_port = os.environ['DB_PORT']
    db_user = os.environ['POSTGRES_USER']

Base = declarative_base()

__factory: Optional[Callable[[], orm.Session]] = None


def global_init():
    global __factory
    if __factory:
        return

    if platform.system() == "Windows":
        db_conn_str = f'sqlite:///database.sqlite?check_same_thread=False'
    else:
        db_conn_str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    print(f"Подключение к базе данных по адресу {db_conn_str}")

    engine = sa.create_engine(db_conn_str, echo=True)
    __factory = orm.sessionmaker(bind=engine)
    Base.metadata.create_all(engine)


def create_session() -> orm.Session:
    global __factory
    return __factory()
