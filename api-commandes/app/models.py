from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Commande(Base):
    __tablename__ = "commandes"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    statut = Column(String(50), default="en_attente", nullable=False)
    total = Column(Float, default=0.0)
    date_commande = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lignes = relationship("LigneCommande", back_populates="commande", cascade="all, delete-orphan")


class LigneCommande(Base):
    __tablename__ = "lignes_commande"

    id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.id", ondelete="CASCADE"), nullable=False)
    produit_id = Column(Integer, nullable=False)
    quantite = Column(Integer, nullable=False, default=1)
    prix_unitaire = Column(Float, nullable=False)

    commande = relationship("Commande", back_populates="lignes")