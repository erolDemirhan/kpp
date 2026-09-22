import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DEMO_AUTH"] = "true"
import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.seed import seed


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(engine); seed(); yield; Base.metadata.drop_all(engine)
@pytest.fixture
def db():
    with SessionLocal() as value: yield value
@pytest.fixture
def client(): return TestClient(app)
