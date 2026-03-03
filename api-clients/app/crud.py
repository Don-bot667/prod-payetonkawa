from sqlalchemy.orm import Session
import bcrypt
from . import models, schemas


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# CREATE - Créer un client en base
def create_client(db: Session, client: schemas.ClientCreate):
    data = client.model_dump()
    data["mot_de_passe"] = hash_password(data["mot_de_passe"])
    db_client = models.Client(**data)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


# READ - Récupérer un client par son ID unique
def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()


# READ - Récupérer un client par son email
def get_client_by_email(db: Session, email: str):
    return db.query(models.Client).filter(models.Client.email == email).first()


# READ - Récupérer la liste de tous les clients
def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()


# UPDATE - Modifier un client existant
def update_client(db: Session, client_id: int, client: schemas.ClientUpdate):
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    update_data = client.model_dump(exclude_unset=True)
    if "mot_de_passe" in update_data:
        update_data["mot_de_passe"] = hash_password(update_data["mot_de_passe"])
    for key, value in update_data.items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client


# DELETE - Supprimer un client
def delete_client(db: Session, client_id: int):
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False
