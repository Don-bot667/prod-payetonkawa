from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Ce qu'on reçoit lors de la CRÉATION
class ClientCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telephone: Optional[str] = Field(None, pattern=r'^0[1-9][0-9]{8}$')
    adresse: Optional[str] = Field(None, max_length=200)
    mot_de_passe: str = Field(..., min_length=4, max_length=100)


# Ce qu'on reçoit lors de la MODIFICATION (tous les champs sont optionnels)
class ClientUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    prenom: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    telephone: Optional[str] = Field(None, pattern=r'^0[1-9][0-9]{8}$')
    adresse: Optional[str] = Field(None, max_length=200)
    mot_de_passe: Optional[str] = Field(None, min_length=4, max_length=100)


# Ce qu'on renvoie au client (RESPONSE) — le mot de passe n'est jamais renvoyé
class ClientResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    actif: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Ce qu'on reçoit pour se connecter
class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str
