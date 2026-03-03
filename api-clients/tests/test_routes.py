import pytest


class TestRootEndpoint:
    """Tests pour l'endpoint racine"""

    def test_root(self, client):
        """GET / - Retourne un message de bienvenue"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Bienvenue" in response.json()["message"]


class TestCreateCustomer:
    """Tests pour POST /customers/"""

    def test_create_customer_success(self, client, sample_client):
        """Création réussie - retourne 201 avec les données du client"""
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == sample_client["nom"]
        assert data["prenom"] == sample_client["prenom"]
        assert data["email"] == sample_client["email"]
        assert data["actif"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_customer_invalid_email(self, client, sample_client):
        """Email invalide - retourne 422"""
        sample_client["email"] = "ceci-nest-pas-un-email"
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 422

    def test_create_customer_missing_nom(self, client, sample_client):
        """Champ 'nom' manquant - retourne 422"""
        del sample_client["nom"]
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 422

    def test_create_customer_missing_prenom(self, client, sample_client):
        """Champ 'prenom' manquant - retourne 422"""
        del sample_client["prenom"]
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 422

    def test_create_customer_missing_email(self, client, sample_client):
        """Champ 'email' manquant - retourne 422"""
        del sample_client["email"]
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 422

    def test_create_customer_without_optional_fields(self, client):
        """Création sans les champs optionnels (telephone, adresse) - retourne 201"""
        response = client.post("/customers/", json={
            "nom": "Martin",
            "prenom": "Sophie",
            "email": "sophie.martin@example.com",
            "mot_de_passe": "testpass"
        })
        assert response.status_code == 201
        assert response.json()["nom"] == "Martin"

    def test_create_customer_missing_password(self, client, sample_client):
        """Champ 'mot_de_passe' manquant - retourne 422"""
        del sample_client["mot_de_passe"]
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 422

    def test_create_customer_password_too_short(self, client, sample_client):
        """Mot de passe trop court (moins de 4 caractères) - retourne 422"""
        sample_client["mot_de_passe"] = "abc"
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 422

    def test_create_customer_password_not_returned(self, client, sample_client):
        """Le mot de passe ne doit jamais apparaître dans la réponse"""
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 201
        assert "mot_de_passe" not in response.json()


class TestReadCustomers:
    """Tests pour GET /customers/"""

    def test_get_customers_empty(self, client):
        """Liste vide quand aucun client n'existe"""
        response = client.get("/customers/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_customers_returns_list(self, client, sample_client):
        """Liste contient le client après création"""
        client.post("/customers/", json=sample_client)
        response = client.get("/customers/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_customers_multiple(self, client, sample_client):
        """Liste contient tous les clients créés"""
        client.post("/customers/", json=sample_client)
        client.post("/customers/", json={
            "nom": "Martin",
            "prenom": "Sophie",
            "email": "sophie.martin@example.com",
            "mot_de_passe": "testpass"
        })
        response = client.get("/customers/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestReadCustomer:
    """Tests pour GET /customers/{id}"""

    def test_get_customer_by_id(self, client, sample_client):
        """Client existant - retourne 200 avec ses données"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]

        response = client.get(f"/customers/{customer_id}")
        assert response.status_code == 200
        assert response.json()["id"] == customer_id
        assert response.json()["email"] == sample_client["email"]

    def test_get_customer_not_found(self, client):
        """Client inexistant - retourne 404"""
        response = client.get("/customers/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Client non trouvé"


class TestUpdateCustomer:
    """Tests pour PUT /customers/{id}"""

    def test_update_customer_nom(self, client, sample_client):
        """Modification du nom uniquement - retourne 200"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]

        response = client.put(f"/customers/{customer_id}", json={"nom": "Nouveau Nom"})
        assert response.status_code == 200
        assert response.json()["nom"] == "Nouveau Nom"
        # Les autres champs ne doivent pas avoir changé
        assert response.json()["email"] == sample_client["email"]
        assert response.json()["prenom"] == sample_client["prenom"]

    def test_update_customer_email(self, client, sample_client):
        """Modification de l'email - retourne 200"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]

        response = client.put(f"/customers/{customer_id}", json={"email": "nouveau@example.com"})
        assert response.status_code == 200
        assert response.json()["email"] == "nouveau@example.com"

    def test_update_customer_multiple_fields(self, client, sample_client):
        """Modification de plusieurs champs à la fois - retourne 200"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]

        response = client.put(f"/customers/{customer_id}", json={
            "nom": "Durand",
            "prenom": "Pierre"
        })
        assert response.status_code == 200
        assert response.json()["nom"] == "Durand"
        assert response.json()["prenom"] == "Pierre"

    def test_update_customer_not_found(self, client):
        """Client inexistant - retourne 404"""
        response = client.put("/customers/99999", json={"nom": "Test"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Client non trouvé"

    def test_update_customer_invalid_email(self, client, sample_client):
        """Email invalide lors de la modification - retourne 422"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]

        response = client.put(f"/customers/{customer_id}", json={"email": "pas-un-email"})
        assert response.status_code == 422


class TestDeleteCustomer:
    """Tests pour DELETE /customers/{id}"""

    def test_delete_customer_success(self, client, sample_client):
        """Suppression réussie - retourne 204"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]

        response = client.delete(f"/customers/{customer_id}")
        assert response.status_code == 204

    def test_delete_customer_no_longer_exists(self, client, sample_client):
        """Après suppression, le client n'est plus accessible"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]

        client.delete(f"/customers/{customer_id}")

        get_response = client.get(f"/customers/{customer_id}")
        assert get_response.status_code == 404

    def test_delete_customer_not_found(self, client):
        """Client inexistant - retourne 404"""
        response = client.delete("/customers/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Client non trouvé"


class TestHealthEndpoint:
    """Tests pour GET /health"""

    def test_health_check_returns_healthy(self, client):
        """GET /health - DB connectée retourne status=healthy"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-clients"
        assert data["database"] == "connected"
        assert "timestamp" in data
        assert "version" in data


class TestAuthentication:
    """Tests pour la sécurité API Key"""

    def test_missing_api_key_returns_401(self, raw_client):
        """Requête sans clé API - retourne 401"""
        response = raw_client.get("/customers/")
        assert response.status_code == 401
        assert response.json()["detail"] == "API Key manquante"

    def test_wrong_api_key_returns_403(self, raw_client):
        """Clé API incorrecte - retourne 403"""
        response = raw_client.get("/customers/", headers={"X-API-Key": "mauvaise-cle"})
        assert response.status_code == 403
        assert response.json()["detail"] == "API Key invalide"


class TestPagination:
    """Tests pour la pagination des clients"""

    def test_get_customers_skip(self, client, sample_client):
        """skip=1 saute le premier client et retourne le reste"""
        client.post("/customers/", json=sample_client)
        client.post("/customers/", json={
            "nom": "Martin",
            "prenom": "Sophie",
            "email": "sophie.martin@example.com",
            "mot_de_passe": "testpass"
        })
        response = client.get("/customers/?skip=1")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_customers_limit(self, client, sample_client):
        """limit=1 retourne au maximum 1 client"""
        client.post("/customers/", json=sample_client)
        client.post("/customers/", json={
            "nom": "Martin",
            "prenom": "Sophie",
            "email": "sophie.martin@example.com",
            "mot_de_passe": "testpass"
        })
        response = client.get("/customers/?limit=1")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestLoginCustomer:
    """Tests pour POST /customers/login"""

    def test_login_success(self, client, sample_client):
        """Connexion réussie avec email + mot de passe corrects"""
        client.post("/customers/", json=sample_client)
        response = client.post("/customers/login", json={
            "email": sample_client["email"],
            "mot_de_passe": sample_client["mot_de_passe"]
        })
        assert response.status_code == 200
        assert response.json()["email"] == sample_client["email"]

    def test_login_wrong_password(self, client, sample_client):
        """Mauvais mot de passe - retourne 401"""
        client.post("/customers/", json=sample_client)
        response = client.post("/customers/login", json={
            "email": sample_client["email"],
            "mot_de_passe": "mauvais_mdp"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Email ou mot de passe incorrect"

    def test_login_unknown_email(self, client):
        """Email inexistant - retourne 401"""
        response = client.post("/customers/login", json={
            "email": "inconnu@example.com",
            "mot_de_passe": "testpass"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Email ou mot de passe incorrect"

    def test_login_password_not_returned(self, client, sample_client):
        """Le mot de passe ne doit jamais apparaître dans la réponse de login"""
        client.post("/customers/", json=sample_client)
        response = client.post("/customers/login", json={
            "email": sample_client["email"],
            "mot_de_passe": sample_client["mot_de_passe"]
        })
        assert response.status_code == 200
        assert "mot_de_passe" not in response.json()
