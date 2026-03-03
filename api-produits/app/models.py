from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from .database import Base


class Produit(Base):
    __tablename__ = "produits"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    prix = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    origine = Column(String(100), nullable=True)
    poids_kg = Column(Float, default=1.0)
    image_url = Column(String(500), nullable=True)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())