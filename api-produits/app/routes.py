import os
import glob
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas, rabbitmq
from .database import get_db
from .auth import verify_api_key
from .logging_config import logger

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(verify_api_key)]
)


# POST /products : Creer un produit
@router.post("/", response_model=schemas.ProduitResponse, status_code=201)
def create_product(produit: schemas.ProduitCreate, db: Session = Depends(get_db)):
    db_produit = crud.create_produit(db=db, produit=produit)
    logger.info(f"Produit cree: id={db_produit.id} nom={db_produit.nom}")
    rabbitmq.publish_produit_created(db_produit.id, {
        "nom": db_produit.nom,
        "prix": db_produit.prix,
        "stock": db_produit.stock
    })
    return db_produit


# GET /products : Lister tous les produits
@router.get("/", response_model=List[schemas.ProduitResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_produits(db, skip=skip, limit=limit)


# GET /products/{id} : Recuperer un produit par son ID
@router.get("/{produit_id}", response_model=schemas.ProduitResponse)
def read_product(produit_id: int, db: Session = Depends(get_db)):
    db_produit = crud.get_produit(db, produit_id=produit_id)
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    return db_produit


# PUT /products/{id} : Modifier un produit
@router.put("/{produit_id}", response_model=schemas.ProduitResponse)
def update_product(produit_id: int, produit: schemas.ProduitUpdate, db: Session = Depends(get_db)):
    db_produit = crud.update_produit(db, produit_id=produit_id, produit=produit)
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    logger.info(f"Produit modifie: id={db_produit.id} stock={db_produit.stock}")
    rabbitmq.publish_produit_updated(db_produit.id, {
        "nom": db_produit.nom,
        "prix": db_produit.prix,
        "stock": db_produit.stock
    })
    if db_produit.stock < 10:
        rabbitmq.publish_produit_stock_low(db_produit.id, db_produit.nom, db_produit.stock)
    return db_produit


# DELETE /products/{id} : Supprimer un produit
@router.delete("/{produit_id}", status_code=204)
def delete_product(produit_id: int, db: Session = Depends(get_db)):
    success = crud.delete_produit(db, produit_id=produit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    logger.info(f"Produit supprime: id={produit_id}")
    rabbitmq.publish_produit_deleted(produit_id)


# POST /products/{id}/image : Uploader une image pour un produit
@router.post("/{produit_id}/image", response_model=schemas.ProduitResponse)
async def upload_product_image(
    produit_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    db_produit = crud.get_produit(db, produit_id=produit_id)
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouve")

    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Format invalide. Formats acceptes : jpg, jpeg, png, webp"
        )

    # Supprimer l'ancienne image du produit s'il en a une
    for old_file in glob.glob(os.path.join(UPLOAD_DIR, f"produit_{produit_id}.*")):
        os.remove(old_file)

    filename = f"produit_{produit_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    image_url = f"/uploads/{filename}"
    return crud.update_produit_image(db, produit_id=produit_id, image_url=image_url)


# GET /products/uploads/{filename} : Servir les images
@router.get("/uploads/{filename}")
async def get_image(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image non trouvee")
    return FileResponse(filepath)