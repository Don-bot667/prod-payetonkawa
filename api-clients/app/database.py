from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# On charge les variables d'environnement du fichier .env 
load_dotenv()

# On récupère l'URL de connexion configurée précédemment 
DATABASE_URL = os.getenv("DATABASE_URL")

# Création du moteur (Engine) qui communique avec PostgreSQL [cite: 282, 283]
engine = create_engine(DATABASE_URL)

# Création d'une usine à sessions pour exécuter nos futures requêtes [cite: 282, 283]
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base dont hériteront tous nos modèles (tables) [cite: 282, 283]
Base = declarative_base()

# Dépendance FastAPI pour ouvrir/fermer la session proprement à chaque appel API [cite: 282, 283]
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()