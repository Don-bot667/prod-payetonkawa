import sys
import os

# Ajouter api-commandes/ en tête de sys.path pour que "from app..." trouve le bon module
_API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _API_DIR)

# Vider le cache des modules 'app' pour éviter les conflits entre les 3 APIs
for _key in list(sys.modules.keys()):
    if _key == "app" or _key.startswith("app."):
        del sys.modules[_key]

# Doit être défini AVANT tout import des modules de l'app
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("API_KEY", "test-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crée les tables, ouvre une session, puis nettoie après chaque test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Client HTTP de test branché sur la base SQLite."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, headers={"X-API-Key": "test-key"}) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def raw_client(db_session):
    """Client HTTP sans clé API (pour tester l'authentification)."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_commande():
    """Payload valide pour créer une commande avec deux lignes."""
    return {
        "client_id": 1,
        "lignes": [
            {"produit_id": 10, "quantite": 2, "prix_unitaire": 12.50},
            {"produit_id": 20, "quantite": 1, "prix_unitaire": 8.00}
        ]
    }


@pytest.fixture
def commande_creee(client, sample_commande):
    """Crée une commande en base et retourne la réponse JSON."""
    response = client.post("/orders/", json=sample_commande)
    assert response.status_code == 201
    return response.json()
