import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url


def get_database_url(service_name: str) -> str:
    """获取数据库连接URL"""
    base_url = os.getenv("DATABASE_URL", "postgresql+pg8000://postgres:051014ccx@localhost:5432/")
    return f"{base_url}{service_name}"


def create_database_engine(database_url: str):
    """创建数据库引擎"""
    return create_engine(database_url, future=True)


def create_session_factory(engine):
    """创建会话工厂"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session(service_name: str):
    """获取数据库会话"""
    database_url = get_database_url(service_name)
    engine = create_database_engine(database_url)
    SessionLocal = create_session_factory(engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

