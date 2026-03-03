from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas, rabbitmq
from .database import get_db
from .auth import verify_api_key
from .logging_config import logger

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(verify_api_key)]
)


# POST /orders : Creer une commande
@router.post("/", response_model=schemas.CommandeResponse, status_code=201)
def create_order(commande: schemas.CommandeCreate, db: Session = Depends(get_db)):
    db_commande = crud.create_commande(db=db, commande=commande)
    logger.info(f"Commande creee: id={db_commande.id} client_id={db_commande.client_id} total={db_commande.total}")
    rabbitmq.publish_commande_created(db_commande.id, {
        "client_id": db_commande.client_id,
        "total": db_commande.total,
        "statut": db_commande.statut
    })
    return db_commande


# GET /orders : Lister toutes les commandes
@router.get("/", response_model=List[schemas.CommandeResponse])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_commandes(db, skip=skip, limit=limit)


# GET /orders/{id} : Recuperer une commande par son ID
@router.get("/{commande_id}", response_model=schemas.CommandeResponse)
def read_order(commande_id: int, db: Session = Depends(get_db)):
    db_commande = crud.get_commande(db, commande_id=commande_id)
    if db_commande is None:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    return db_commande


# GET /orders/client/{client_id} : Commandes d'un client
@router.get("/client/{client_id}", response_model=List[schemas.CommandeResponse])
def read_orders_by_client(client_id: int, db: Session = Depends(get_db)):
    return crud.get_commandes_by_client(db, client_id=client_id)


# PUT /orders/{id} : Modifier le statut d'une commande
@router.put("/{commande_id}", response_model=schemas.CommandeResponse)
def update_order(commande_id: int, commande: schemas.CommandeUpdate, db: Session = Depends(get_db)):
    db_commande = crud.update_commande(db, commande_id=commande_id, commande=commande)
    if db_commande is None:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    logger.info(f"Commande modifiee: id={db_commande.id} statut={db_commande.statut}")
    rabbitmq.publish_commande_updated(db_commande.id, db_commande.statut)
    return db_commande


# DELETE /orders/{id} : Supprimer une commande
@router.delete("/{commande_id}", status_code=204)
def delete_order(commande_id: int, db: Session = Depends(get_db)):
    success = crud.delete_commande(db, commande_id=commande_id)
    if not success:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    logger.info(f"Commande supprimee: id={commande_id}")
    rabbitmq.publish_commande_deleted(commande_id)