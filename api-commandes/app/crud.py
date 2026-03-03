from sqlalchemy.orm import Session
from . import models, schemas


# CREATE - Creer une commande avec ses lignes
def create_commande(db: Session, commande: schemas.CommandeCreate):
    # Calculer le total a partir des lignes
    total = sum(ligne.prix_unitaire * ligne.quantite for ligne in commande.lignes)

    # Creer la commande
    db_commande = models.Commande(
        client_id=commande.client_id,
        total=total
    )
    db.add(db_commande)
    db.flush()  # Pour obtenir l'ID de la commande avant de creer les lignes

    # Creer les lignes de commande
    for ligne in commande.lignes:
        db_ligne = models.LigneCommande(
            commande_id=db_commande.id,
            produit_id=ligne.produit_id,
            quantite=ligne.quantite,
            prix_unitaire=ligne.prix_unitaire
        )
        db.add(db_ligne)

    db.commit()
    db.refresh(db_commande)
    return db_commande


# READ - Recuperer une commande par son ID
def get_commande(db: Session, commande_id: int):
    return db.query(models.Commande).filter(models.Commande.id == commande_id).first()


# READ - Recuperer toutes les commandes
def get_commandes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Commande).offset(skip).limit(limit).all()


# READ - Recuperer les commandes d'un client specifique
def get_commandes_by_client(db: Session, client_id: int):
    return db.query(models.Commande).filter(models.Commande.client_id == client_id).all()


# UPDATE - Modifier le statut d'une commande
def update_commande(db: Session, commande_id: int, commande: schemas.CommandeUpdate):
    db_commande = get_commande(db, commande_id)
    if not db_commande:
        return None
    update_data = commande.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_commande, key, value)
    db.commit()
    db.refresh(db_commande)
    return db_commande


# UPDATE STATUT - Modifier uniquement le statut d'une commande (utilisé par le consumer)
def update_commande_statut(db: Session, commande_id: int, statut: str):
    db_commande = get_commande(db, commande_id)
    if not db_commande:
        return None
    db_commande.statut = statut
    db.commit()
    db.refresh(db_commande)
    return db_commande


# DELETE - Supprimer une commande (et ses lignes grace au CASCADE)
def delete_commande(db: Session, commande_id: int):
    db_commande = get_commande(db, commande_id)
    if db_commande:
        db.delete(db_commande)
        db.commit()
        return True
    return False