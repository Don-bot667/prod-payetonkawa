import json
from unittest.mock import patch, MagicMock

from app.rabbitmq import (
    get_connection,
    publish_message,
    publish_client_created,
    publish_client_updated,
    publish_client_deleted,
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
            result = publish_message("client.created", {"event": "test"})

        assert result is True
        mock_channel.exchange_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_publish_message_no_connection(self):
        """Publication sans connexion disponible - retourne False"""
        with patch("app.rabbitmq.get_connection", return_value=None):
            result = publish_message("client.created", {"event": "test"})
        assert result is False

    def test_publish_message_exception(self):
        """Exception durant la publication - retourne False"""
        with patch("app.rabbitmq.get_connection", side_effect=Exception("Erreur inattendue")):
            result = publish_message("client.created", {"event": "test"})
        assert result is False

    def test_publish_message_correct_routing_key(self):
        """La routing key est transmise correctement à basic_publish"""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel

        with patch("app.rabbitmq.get_connection", return_value=mock_connection):
            publish_message("client.created", {"event": "test"})

        call_kwargs = mock_channel.basic_publish.call_args
        assert call_kwargs.kwargs["routing_key"] == "client.created"

    def test_publish_message_body_is_json(self):
        """Le corps du message est du JSON valide"""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        payload = {"event": "client_created", "client_id": 1}

        with patch("app.rabbitmq.get_connection", return_value=mock_connection):
            publish_message("client.created", payload)

        call_kwargs = mock_channel.basic_publish.call_args
        body = call_kwargs.kwargs["body"]
        assert json.loads(body) == payload


class TestPublishClientCreated:
    """Tests pour publish_client_created"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'client.created'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_client_created(1, {"nom": "Test"})
            mock_pub.assert_called_once()
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "client.created"

    def test_message_contains_event_and_client_id(self):
        """Le message contient l'événement et le client_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_client_created(42, {"nom": "Test"})
            body = mock_pub.call_args[0][1]
            assert body["event"] == "client_created"
            assert body["client_id"] == 42
            assert "timestamp" in body


class TestPublishClientUpdated:
    """Tests pour publish_client_updated"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'client.updated'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_client_updated(2, {"nom": "Modifié"})
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "client.updated"

    def test_message_contains_event_and_client_id(self):
        """Le message contient l'événement et le client_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_client_updated(7, {"nom": "Modifié"})
            body = mock_pub.call_args[0][1]
            assert body["event"] == "client_updated"
            assert body["client_id"] == 7


class TestPublishClientDeleted:
    """Tests pour publish_client_deleted"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'client.deleted'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_client_deleted(3)
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "client.deleted"

    def test_message_contains_event_and_client_id(self):
        """Le message contient l'événement et le client_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_client_deleted(99)
            body = mock_pub.call_args[0][1]
            assert body["event"] == "client_deleted"
            assert body["client_id"] == 99
