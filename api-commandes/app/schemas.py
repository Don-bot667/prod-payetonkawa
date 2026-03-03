from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- LIGNES DE COMMANDE ---

# Ce qu'on envoie pour creer une ligne (dans une commande)
class LigneCommandeCreate(BaseModel):
    produit_id: int = Field(..., gt=0)
    quantite: int = Field(1, ge=1, description="La quantité doit être >= 1")
    prix_unitaire: float = Field(..., gt=0, description="Le prix doit être supérieur à 0")


# Ce que l'API renvoie pour une ligne
class LigneCommandeResponse(BaseModel):
    id: int
    commande_id: int
    produit_id: int
    quantite: int
    prix_unitaire: float

    class Config:
        from_attributes = True


# --- COMMANDES ---

# Ce qu'on envoie pour CREER une commande (POST)
class CommandeCreate(BaseModel):
    client_id: int = Field(..., gt=0)
    lignes: List[LigneCommandeCreate] = Field(..., min_length=1, description="Au moins une ligne requise")


# Ce qu'on envoie pour MODIFIER le statut (PUT)
class CommandeUpdate(BaseModel):
    statut: Optional[str] = None


# Ce que l'API RENVOIE (la reponse complete)
class CommandeResponse(BaseModel):
    id: int
    client_id: int
    statut: str
    total: float
    date_commande: datetime
    date_modification: datetime
    lignes: List[LigneCommandeResponse]

    class Config:
        from_attributes = True
