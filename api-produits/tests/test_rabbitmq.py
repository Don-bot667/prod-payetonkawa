import json
from unittest.mock import patch, MagicMock

from app.rabbitmq import (
    get_connection,
    publish_message,
    publish_produit_created,
    publish_produit_updated,
    publish_produit_deleted,
    publish_produit_stock_low,
)


class TestGetConnection:
    """Tests pour la fonction get_connection"""

    def test_get_connection_success(self):
        """Connexion RabbitMQ réussie - retourne l'objet connexion"""
        with patch("app.rabbitmq.pika.BlockingConnection") as mock_conn:
            mock_conn.return_value = MagicMock()
            result = get_connection()
            assert result is not None
            mock_conn.assert_called_once()

    def test_get_connection_failure_returns_none(self):
        """Connexion RabbitMQ échouée - retourne None"""
        with patch("app.rabbitmq.pika.BlockingConnection", side_effect=Exception("Connexion refusée")):
            result = get_connection()
            assert result is None


class TestPublishMessage:
    """Tests pour la fonction publish_message"""

    def test_publish_message_success(self):
        """Publication réussie - retourne True"""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel

        with patch("app.rabbitmq.get_connection", return_value=mock_connection):
            result = publish_message("produit.created", {"event": "test"})

        assert result is True
        mock_channel.exchange_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_publish_message_no_connection(self):
        """Publication sans connexion disponible - retourne False"""
        with patch("app.rabbitmq.get_connection", return_value=None):
            result = publish_message("produit.created", {"event": "test"})
        assert result is False

    def test_publish_message_exception(self):
        """Exception durant la publication - retourne False"""
        with patch("app.rabbitmq.get_connection", side_effect=Exception("Erreur")):
            result = publish_message("produit.created", {"event": "test"})
        assert result is False

    def test_publish_message_body_is_json(self):
        """Le corps du message est du JSON valide"""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        payload = {"event": "produit_created", "produit_id": 1}

        with patch("app.rabbitmq.get_connection", return_value=mock_connection):
            publish_message("produit.created", payload)

        call_kwargs = mock_channel.basic_publish.call_args
        body = call_kwargs.kwargs["body"]
        assert json.loads(body) == payload


class TestPublishProduitCreated:
    """Tests pour publish_produit_created"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'produit.created'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_created(1, {"nom": "Café"})
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "produit.created"

    def test_message_contains_event_and_produit_id(self):
        """Le message contient l'événement et le produit_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_created(5, {"nom": "Café"})
            body = mock_pub.call_args[0][1]
            assert body["event"] == "produit_created"
            assert body["produit_id"] == 5
            assert "timestamp" in body


class TestPublishProduitUpdated:
    """Tests pour publish_produit_updated"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'produit.updated'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_updated(2, {"stock": 50})
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "produit.updated"

    def test_message_contains_event_and_produit_id(self):
        """Le message contient l'événement et le produit_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_updated(8, {"stock": 50})
            body = mock_pub.call_args[0][1]
            assert body["event"] == "produit_updated"
            assert body["produit_id"] == 8


class TestPublishProduitDeleted:
    """Tests pour publish_produit_deleted"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'produit.deleted'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_deleted(3)
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "produit.deleted"

    def test_message_contains_event_and_produit_id(self):
        """Le message contient l'événement et le produit_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_deleted(12)
            body = mock_pub.call_args[0][1]
            assert body["event"] == "produit_deleted"
            assert body["produit_id"] == 12


class TestPublishProduitStockLow:
    """Tests pour publish_produit_stock_low"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'produit.stock_low'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_stock_low(4, "Café Burkina", 3)
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "produit.stock_low"

    def test_message_contains_stock_info(self):
        """Le message contient les infos de stock"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_produit_stock_low(4, "Café Burkina", 3)
            body = mock_pub.call_args[0][1]
            assert body["event"] == "produit_stock_low"
            assert body["produit_id"] == 4
            assert body["produit_nom"] == "Café Burkina"
            assert body["stock_actuel"] == 3
            assert body["seuil_alerte"] == 10
