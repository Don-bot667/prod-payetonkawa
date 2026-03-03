import pytest
from app import crud


class TestCrudUpdateCommandeStatut:
    """Tests directs pour crud.update_commande_statut"""

    def test_update_statut_success(self, db_session, sample_commande, client):
        """update_commande_statut modifie le statut en base"""
        create_resp = client.post("/orders/", json=sample_commande)
        commande_id = create_resp.json()["id"]

        result = crud.update_commande_statut(db_session, commande_id, "client_supprime")
        assert result is not None
        assert result.statut == "client_supprime"

    def test_update_statut_not_found(self, db_session):
        """update_commande_statut retourne None si commande inexistante"""
        result = crud.update_commande_statut(db_session, 99999, "client_supprime")
        assert result is None


class TestRootEndpoint:
    """Tests pour l'endpoint racine"""

    def test_root(self, client):
        """GET / - Retourne un message de bienvenue"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Bienvenue" in response.json()["message"]


class TestCreateOrder:
    """Tests pour POST /orders/"""

    def test_create_order_success(self, client, sample_commande):
        """Création réussie - retourne 201 avec les données de la commande"""
        response = client.post("/orders/", json=sample_commande)
        assert response.status_code == 201
        data = response.json()
        assert data["client_id"] == sample_commande["client_id"]
        assert data["statut"] == "en_attente"
        assert "id" in data
        assert "date_commande" in data

    def test_create_order_calcul_total(self, client, sample_commande):
        """Le total est calculé automatiquement à partir des lignes"""
        # 2 x 12.50 + 1 x 8.00 = 33.00
        response = client.post("/orders/", json=sample_commande)
        assert response.status_code == 201
        assert response.json()["total"] == pytest.approx(33.00)

    def test_create_order_lignes_incluses(self, client, sample_commande):
        """La réponse inclut les lignes de commande"""
        response = client.post("/orders/", json=sample_commande)
        assert response.status_code == 201
        data = response.json()
        assert len(data["lignes"]) == 2
        assert data["lignes"][0]["produit_id"] == 10
        assert data["lignes"][0]["quantite"] == 2
        assert data["lignes"][1]["produit_id"] == 20

    def test_create_order_single_ligne(self, client):
        """Création avec une seule ligne"""
        response = client.post("/orders/", json={
            "client_id": 1,
            "lignes": [{"produit_id": 5, "quantite": 3, "prix_unitaire": 5.00}]
        })
        assert response.status_code == 201
        assert response.json()["total"] == pytest.approx(15.00)
        assert len(response.json()["lignes"]) == 1

    def test_create_order_missing_client_id(self, client):
        """client_id manquant - retourne 422"""
        response = client.post("/orders/", json={
            "lignes": [{"produit_id": 1, "quantite": 1, "prix_unitaire": 10.00}]
        })
        assert response.status_code == 422

    def test_create_order_missing_lignes(self, client):
        """Champ 'lignes' manquant - retourne 422"""
        response = client.post("/orders/", json={"client_id": 1})
        assert response.status_code == 422

    def test_create_order_ligne_missing_prix(self, client):
        """prix_unitaire manquant dans une ligne - retourne 422"""
        response = client.post("/orders/", json={
            "client_id": 1,
            "lignes": [{"produit_id": 1, "quantite": 1}]
        })
        assert response.status_code == 422

    def test_create_order_ligne_missing_produit_id(self, client):
        """produit_id manquant dans une ligne - retourne 422"""
        response = client.post("/orders/", json={
            "client_id": 1,
            "lignes": [{"quantite": 1, "prix_unitaire": 10.00}]
        })
        assert response.status_code == 422

    def test_create_order_quantite_default(self, client):
        """La quantité est 1 par défaut si non fournie"""
        response = client.post("/orders/", json={
            "client_id": 1,
            "lignes": [{"produit_id": 1, "prix_unitaire": 10.00}]
        })
        assert response.status_code == 201
        assert response.json()["lignes"][0]["quantite"] == 1


class TestReadOrders:
    """Tests pour GET /orders/"""

    def test_get_orders_empty(self, client):
        """Liste vide quand aucune commande n'existe"""
        response = client.get("/orders/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_orders_returns_list(self, client, commande_creee):
        """Liste contient la commande après création"""
        response = client.get("/orders/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_orders_multiple(self, client, sample_commande):
        """Liste contient toutes les commandes créées"""
        client.post("/orders/", json=sample_commande)
        client.post("/orders/", json={"client_id": 2, "lignes": [
            {"produit_id": 1, "quantite": 1, "prix_unitaire": 5.00}
        ]})
        response = client.get("/orders/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestReadOrder:
    """Tests pour GET /orders/{id}"""

    def test_get_order_by_id(self, client, commande_creee):
        """Commande existante - retourne 200 avec ses données"""
        commande_id = commande_creee["id"]
        response = client.get(f"/orders/{commande_id}")
        assert response.status_code == 200
        assert response.json()["id"] == commande_id
        assert response.json()["client_id"] == commande_creee["client_id"]

    def test_get_order_includes_lignes(self, client, commande_creee):
        """La commande récupérée par ID inclut ses lignes"""
        commande_id = commande_creee["id"]
        response = client.get(f"/orders/{commande_id}")
        assert response.status_code == 200
        assert len(response.json()["lignes"]) == 2

    def test_get_order_not_found(self, client):
        """Commande inexistante - retourne 404"""
        response = client.get("/orders/99999")
        assert response.status_code == 404
        assert "non trouvee" in response.json()["detail"]


class TestReadOrdersByClient:
    """Tests pour GET /orders/client/{client_id}"""

    def test_get_orders_by_client(self, client, sample_commande):
        """Retourne les commandes du client demandé"""
        client.post("/orders/", json=sample_commande)  # client_id=1
        client.post("/orders/", json=sample_commande)  # client_id=1 aussi
        client.post("/orders/", json={"client_id": 2, "lignes": [
            {"produit_id": 1, "quantite": 1, "prix_unitaire": 5.00}
        ]})

        response = client.get("/orders/client/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(c["client_id"] == 1 for c in data)

    def test_get_orders_by_client_empty(self, client):
        """Client sans commandes - retourne liste vide"""
        response = client.get("/orders/client/999")
        assert response.status_code == 200
        assert response.json() == []


class TestUpdateOrder:
    """Tests pour PUT /orders/{id}"""

    def test_update_order_statut(self, client, commande_creee):
        """Changement de statut réussi - retourne 200"""
        commande_id = commande_creee["id"]
        response = client.put(f"/orders/{commande_id}", json={"statut": "validee"})
        assert response.status_code == 200
        assert response.json()["statut"] == "validee"

    def test_update_order_statut_progression(self, client, commande_creee):
        """Progression du statut : en_attente -> validee -> expediee -> livree"""
        commande_id = commande_creee["id"]

        for statut in ["validee", "expediee", "livree"]:
            response = client.put(f"/orders/{commande_id}", json={"statut": statut})
            assert response.status_code == 200
            assert response.json()["statut"] == statut

    def test_update_order_lignes_non_modifiees(self, client, commande_creee):
        """Le changement de statut ne modifie pas les lignes"""
        commande_id = commande_creee["id"]
        response = client.put(f"/orders/{commande_id}", json={"statut": "validee"})
        assert response.status_code == 200
        assert len(response.json()["lignes"]) == 2

    def test_update_order_not_found(self, client):
        """Commande inexistante - retourne 404"""
        response = client.put("/orders/99999", json={"statut": "validee"})
        assert response.status_code == 404
        assert "non trouvee" in response.json()["detail"]


class TestHealthEndpoint:
    """Tests pour GET /health"""

    def test_health_check_returns_healthy(self, client):
        """GET /health - DB connectée retourne status=healthy"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-commandes"
        assert data["database"] == "connected"
        assert "timestamp" in data
        assert "version" in data


class TestAuthentication:
    """Tests pour la sécurité API Key"""

    def test_missing_api_key_returns_401(self, raw_client):
        """Requête sans clé API - retourne 401"""
        response = raw_client.get("/orders/")
        assert response.status_code == 401
        assert response.json()["detail"] == "API Key manquante"

    def test_wrong_api_key_returns_403(self, raw_client):
        """Clé API incorrecte - retourne 403"""
        response = raw_client.get("/orders/", headers={"X-API-Key": "mauvaise-cle"})
        assert response.status_code == 403
        assert response.json()["detail"] == "API Key invalide"


class TestDeleteOrder:
    """Tests pour DELETE /orders/{id}"""

    def test_delete_order_success(self, client, commande_creee):
        """Suppression réussie - retourne 204"""
        commande_id = commande_creee["id"]
        response = client.delete(f"/orders/{commande_id}")
        assert response.status_code == 204

    def test_delete_order_no_longer_exists(self, client, commande_creee):
        """Après suppression, la commande n'est plus accessible"""
        commande_id = commande_creee["id"]
        client.delete(f"/orders/{commande_id}")
        response = client.get(f"/orders/{commande_id}")
        assert response.status_code == 404

    def test_delete_order_cascade_lignes(self, client, commande_creee, db_session):
        """La suppression d'une commande supprime aussi ses lignes (CASCADE)"""
        from app.models import LigneCommande
        commande_id = commande_creee["id"]

        lignes_avant = db_session.query(LigneCommande).filter(
            LigneCommande.commande_id == commande_id
        ).count()
        assert lignes_avant == 2

        client.delete(f"/orders/{commande_id}")

        lignes_apres = db_session.query(LigneCommande).filter(
            LigneCommande.commande_id == commande_id
        ).count()
        assert lignes_apres == 0

    def test_delete_order_not_found(self, client):
        """Commande inexistante - retourne 404"""
        response = client.delete("/orders/99999")
        assert response.status_code == 404
        assert "non trouvee" in response.json()["detail"]
