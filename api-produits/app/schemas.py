from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Ce qu'on envoie pour CREER un produit (POST)
class ProduitCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    prix: float = Field(..., gt=0, description="Le prix doit être supérieur à 0")
    stock: int = Field(0, ge=0, description="Le stock doit être >= 0")
    origine: Optional[str] = Field(None, max_length=100)
    poids_kg: float = Field(1.0, gt=0, description="Le poids doit être supérieur à 0")


# Ce qu'on envoie pour MODIFIER un produit (PUT)
class ProduitUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    prix: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    origine: Optional[str] = Field(None, max_length=100)
    poids_kg: Optional[float] = Field(None, gt=0)
    actif: Optional[bool] = None


# Ce que l'API RENVOIE (la reponse)
class ProduitResponse(BaseModel):
    id: int
    nom: str
    description: Optional[str]
    prix: float
    stock: int
    origine: Optional[str]
    poids_kg: float
    image_url: Optional[str] = None
    actif: bool
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True
