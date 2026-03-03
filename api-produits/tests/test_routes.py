import io
import pytest
from unittest.mock import patch


class TestRootEndpoint:
    """Tests pour l'endpoint racine"""

    def test_root(self, client):
        """GET / - Retourne un message de bienvenue"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Bienvenue" in response.json()["message"]


class TestCreateProduct:
    """Tests pour POST /products/"""

    def test_create_product_success(self, client, sample_produit):
        """Création réussie - retourne 201 avec les données du produit"""
        response = client.post("/products/", json=sample_produit)
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == sample_produit["nom"]
        assert data["prix"] == sample_produit["prix"]
        assert data["stock"] == sample_produit["stock"]
        assert data["actif"] is True
        assert "id" in data
        assert "date_creation" in data

    def test_create_product_missing_nom(self, client, sample_produit):
        """Champ 'nom' manquant - retourne 422"""
        del sample_produit["nom"]
        response = client.post("/products/", json=sample_produit)
        assert response.status_code == 422

    def test_create_product_missing_prix(self, client, sample_produit):
        """Champ 'prix' manquant - retourne 422"""
        del sample_produit["prix"]
        response = client.post("/products/", json=sample_produit)
        assert response.status_code == 422

    def test_create_product_without_optional_fields(self, client):
        """Création avec uniquement les champs obligatoires - retourne 201"""
        response = client.post("/products/", json={
            "nom": "Café Brasil",
            "prix": 8.99
        })
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == "Café Brasil"
        assert data["stock"] == 0
        assert data["poids_kg"] == 1.0

    def test_create_product_stock_zero_by_default(self, client):
        """Le stock est 0 par défaut si non fourni"""
        response = client.post("/products/", json={
            "nom": "Café Colombie",
            "prix": 10.00
        })
        assert response.status_code == 201
        assert response.json()["stock"] == 0

    def test_create_product_invalid_prix_type(self, client, sample_produit):
        """Prix de type invalide (texte) - retourne 422"""
        sample_produit["prix"] = "pas-un-prix"
        response = client.post("/products/", json=sample_produit)
        assert response.status_code == 422


class TestReadProducts:
    """Tests pour GET /products/"""

    def test_get_products_empty(self, client):
        """Liste vide quand aucun produit n'existe"""
        response = client.get("/products/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_products_returns_list(self, client, sample_produit):
        """Liste contient le produit après création"""
        client.post("/products/", json=sample_produit)
        response = client.get("/products/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_products_multiple(self, client, sample_produit):
        """Liste contient tous les produits créés"""
        client.post("/products/", json=sample_produit)
        client.post("/products/", json={
            "nom": "Café Brasil",
            "prix": 8.99
        })
        response = client.get("/products/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestReadProduct:
    """Tests pour GET /products/{id}"""

    def test_get_product_by_id(self, client, sample_produit):
        """Produit existant - retourne 200 avec ses données"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        response = client.get(f"/products/{produit_id}")
        assert response.status_code == 200
        assert response.json()["id"] == produit_id
        assert response.json()["nom"] == sample_produit["nom"]

    def test_get_product_not_found(self, client):
        """Produit inexistant - retourne 404"""
        response = client.get("/products/99999")
        assert response.status_code == 404
        assert "non trouve" in response.json()["detail"]


class TestUpdateProduct:
    """Tests pour PUT /products/{id}"""

    def test_update_product_prix(self, client, sample_produit):
        """Modification du prix uniquement - retourne 200"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        response = client.put(f"/products/{produit_id}", json={"prix": 15.00})
        assert response.status_code == 200
        assert response.json()["prix"] == 15.00
        # Les autres champs ne doivent pas avoir changé
        assert response.json()["nom"] == sample_produit["nom"]
        assert response.json()["stock"] == sample_produit["stock"]

    def test_update_product_stock(self, client, sample_produit):
        """Modification du stock - retourne 200"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        response = client.put(f"/products/{produit_id}", json={"stock": 50})
        assert response.status_code == 200
        assert response.json()["stock"] == 50

    def test_update_product_stock_to_zero(self, client, sample_produit):
        """Stock peut être mis à 0 (rupture)"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        response = client.put(f"/products/{produit_id}", json={"stock": 0})
        assert response.status_code == 200
        assert response.json()["stock"] == 0

    def test_update_product_desactiver(self, client, sample_produit):
        """Désactivation du produit (actif=False)"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        response = client.put(f"/products/{produit_id}", json={"actif": False})
        assert response.status_code == 200
        assert response.json()["actif"] is False

    def test_update_product_multiple_fields(self, client, sample_produit):
        """Modification de plusieurs champs à la fois"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        response = client.put(f"/products/{produit_id}", json={
            "nom": "Café Kenya",
            "prix": 14.00,
            "stock": 75
        })
        assert response.status_code == 200
        assert response.json()["nom"] == "Café Kenya"
        assert response.json()["prix"] == 14.00
        assert response.json()["stock"] == 75

    def test_update_product_not_found(self, client):
        """Produit inexistant - retourne 404"""
        response = client.put("/products/99999", json={"prix": 10.00})
        assert response.status_code == 404
        assert "non trouve" in response.json()["detail"]


class TestHealthEndpoint:
    """Tests pour GET /health"""

    def test_health_check_returns_healthy(self, client):
        """GET /health - DB connectée retourne status=healthy"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-produits"
        assert data["database"] == "connected"
        assert "timestamp" in data
        assert "version" in data


class TestAuthentication:
    """Tests pour la sécurité API Key"""

    def test_missing_api_key_returns_401(self, raw_client):
        """Requête sans clé API - retourne 401"""
        response = raw_client.get("/products/")
        assert response.status_code == 401
        assert response.json()["detail"] == "API Key manquante"

    def test_wrong_api_key_returns_403(self, raw_client):
        """Clé API incorrecte - retourne 403"""
        response = raw_client.get("/products/", headers={"X-API-Key": "mauvaise-cle"})
        assert response.status_code == 403
        assert response.json()["detail"] == "API Key invalide"


class TestValidation:
    """Tests de validation des contraintes Pydantic sur les produits"""

    def test_create_product_prix_zero(self, client):
        """Prix à 0 - retourne 422 (prix doit être > 0)"""
        response = client.post("/products/", json={"nom": "Test", "prix": 0})
        assert response.status_code == 422

    def test_create_product_prix_negatif(self, client):
        """Prix négatif - retourne 422"""
        response = client.post("/products/", json={"nom": "Test", "prix": -5.00})
        assert response.status_code == 422

    def test_create_product_stock_negatif(self, client):
        """Stock négatif - retourne 422"""
        response = client.post("/products/", json={
            "nom": "Test",
            "prix": 10.00,
            "stock": -1
        })
        assert response.status_code == 422


class TestDeleteProduct:
    """Tests pour DELETE /products/{id}"""

    def test_delete_product_success(self, client, sample_produit):
        """Suppression réussie - retourne 204"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        response = client.delete(f"/products/{produit_id}")
        assert response.status_code == 204

    def test_delete_product_no_longer_exists(self, client, sample_produit):
        """Après suppression, le produit n'est plus accessible"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        client.delete(f"/products/{produit_id}")

        get_response = client.get(f"/products/{produit_id}")
        assert get_response.status_code == 404

    def test_delete_product_not_found(self, client):
        """Produit inexistant - retourne 404"""
        response = client.delete("/products/99999")
        assert response.status_code == 404
        assert "non trouve" in response.json()["detail"]


class TestStockLowAlert:
    """Tests pour l'alerte stock bas (< 10 unités)"""

    def test_update_stock_below_10_triggers_alert(self, client, sample_produit):
        """Stock mis à < 10 déclenche l'alerte publish_produit_stock_low"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        with patch("app.routes.rabbitmq.publish_produit_stock_low") as mock_alert:
            response = client.put(f"/products/{produit_id}", json={"stock": 5})
            assert response.status_code == 200
            mock_alert.assert_called_once_with(produit_id, sample_produit["nom"], 5)

    def test_update_stock_at_10_no_alert(self, client, sample_produit):
        """Stock mis à 10 ne déclenche pas l'alerte"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        with patch("app.routes.rabbitmq.publish_produit_stock_low") as mock_alert:
            response = client.put(f"/products/{produit_id}", json={"stock": 10})
            assert response.status_code == 200
            mock_alert.assert_not_called()


class TestImageUpload:
    """Tests pour POST /products/{id}/image"""

    def test_upload_image_product_not_found(self, client):
        """Produit inexistant - retourne 404"""
        file_data = io.BytesIO(b"fake image content")
        response = client.post(
            "/products/99999/image",
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )
        assert response.status_code == 404

    def test_upload_image_invalid_extension(self, client, sample_produit):
        """Extension non autorisée (.pdf) - retourne 400"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        file_data = io.BytesIO(b"fake content")
        response = client.post(
            f"/products/{produit_id}/image",
            files={"file": ("doc.pdf", file_data, "application/pdf")}
        )
        assert response.status_code == 400
        assert "Format invalide" in response.json()["detail"]

    def test_upload_image_success(self, client, sample_produit, tmp_path):
        """Upload d'un JPG valide - retourne 200 avec image_url"""
        create_response = client.post("/products/", json=sample_produit)
        produit_id = create_response.json()["id"]

        file_data = io.BytesIO(b"fake image content")
        with patch("app.routes.UPLOAD_DIR", str(tmp_path)), \
             patch("app.routes.glob.glob", return_value=[]):
            response = client.post(
                f"/products/{produit_id}/image",
                files={"file": ("test.jpg", file_data, "image/jpeg")}
            )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert data["image_url"].endswith(".jpg")
