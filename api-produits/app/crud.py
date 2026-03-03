from sqlalchemy.orm import Session
from . import models, schemas


# CREATE - Ajouter un nouveau produit
def create_produit(db: Session, produit: schemas.ProduitCreate):
    db_produit = models.Produit(**produit.model_dump())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit


# READ - Recuperer un produit par son ID
def get_produit(db: Session, produit_id: int):
    return db.query(models.Produit).filter(models.Produit.id == produit_id).first()


# READ - Recuperer la liste de tous les produits
def get_produits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Produit).offset(skip).limit(limit).all()


# UPDATE - Modifier un produit existant
def update_produit(db: Session, produit_id: int, produit: schemas.ProduitUpdate):
    db_produit = get_produit(db, produit_id)
    if not db_produit:
        return None
    update_data = produit.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_produit, key, value)
    db.commit()
    db.refresh(db_produit)
    return db_produit


# UPDATE IMAGE - Enregistrer l'URL de l'image d'un produit
def update_produit_image(db: Session, produit_id: int, image_url: str):
    db_produit = get_produit(db, produit_id)
    if not db_produit:
        return None
    db_produit.image_url = image_url
    db.commit()
    db.refresh(db_produit)
    return db_produit


# DELETE - Supprimer un produit
def delete_produit(db: Session, produit_id: int):
    db_produit = get_produit(db, produit_id)
    if db_produit:
        db.delete(db_produit)
        db.commit()
        return True
    return False