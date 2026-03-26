from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./raw_material_agent.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
