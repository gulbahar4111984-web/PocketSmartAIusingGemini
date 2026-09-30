import os


# Test database
os.environ["DATABASE_URL"] = (
    "sqlite:///./test_pocketsmart.db"
)

# Test secret
os.environ["SECRET_KEY"] = (
    "test-secret-key-for-pocketsmart-tests-123456789"
)

# Force fallback mode during tests
os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app
from app.db.database import (
    Base,
    engine,
)

import pytest


@pytest.fixture()
def client():

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )

    with TestClient(app) as test_client:

        yield test_client