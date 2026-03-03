import json
from unittest.mock import patch, MagicMock

from app.consumer import callback_client_deleted, callback_produit_deleted, start_consumer
from app.rabbitmq import (
    get_connection,
    publish_message,
    publish_commande_created,
    publish_commande_updated,
    publish_commande_deleted,
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
            result = publish_message("commande.created", {"event": "test"})

        assert result is True
        mock_channel.exchange_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_publish_message_no_connection(self):
        """Publication sans connexion disponible - retourne False"""
        with patch("app.rabbitmq.get_connection", return_value=None):
            result = publish_message("commande.created", {"event": "test"})
        assert result is False

    def test_publish_message_exception(self):
        """Exception durant la publication - retourne False"""
        with patch("app.rabbitmq.get_connection", side_effect=Exception("Erreur")):
            result = publish_message("commande.created", {"event": "test"})
        assert result is False

    def test_publish_message_body_is_json(self):
        """Le corps du message est du JSON valide"""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        payload = {"event": "commande_created", "commande_id": 1}

        with patch("app.rabbitmq.get_connection", return_value=mock_connection):
            publish_message("commande.created", payload)

        call_kwargs = mock_channel.basic_publish.call_args
        body = call_kwargs.kwargs["body"]
        assert json.loads(body) == payload


class TestPublishCommandeCreated:
    """Tests pour publish_commande_created"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'commande.created'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_commande_created(1, {"client_id": 1, "total": 33.0})
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "commande.created"

    def test_message_contains_event_and_commande_id(self):
        """Le message contient l'événement et le commande_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_commande_created(10, {"client_id": 1, "total": 33.0})
            body = mock_pub.call_args[0][1]
            assert body["event"] == "commande_created"
            assert body["commande_id"] == 10
            assert "timestamp" in body


class TestPublishCommandeUpdated:
    """Tests pour publish_commande_updated"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'commande.updated'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_commande_updated(2, "validee")
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "commande.updated"

    def test_message_contains_statut(self):
        """Le message contient le nouveau statut"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_commande_updated(2, "expediee")
            body = mock_pub.call_args[0][1]
            assert body["event"] == "commande_updated"
            assert body["commande_id"] == 2
            assert body["statut"] == "expediee"


class TestPublishCommandeDeleted:
    """Tests pour publish_commande_deleted"""

    def test_calls_publish_message_with_correct_routing_key(self):
        """Utilise la routing key 'commande.deleted'"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_commande_deleted(3)
            routing_key = mock_pub.call_args[0][0]
            assert routing_key == "commande.deleted"

    def test_message_contains_commande_id(self):
        """Le message contient le commande_id"""
        with patch("app.rabbitmq.publish_message") as mock_pub:
            publish_commande_deleted(99)
            body = mock_pub.call_args[0][1]
            assert body["event"] == "commande_deleted"
            assert body["commande_id"] == 99


class TestCallbackClientDeleted:
    """Tests pour le consumer callback_client_deleted"""

    def test_success_marks_commandes_as_client_supprime(self):
        """Quand un client est supprimé, ses commandes sont marquées client_supprime"""
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        mock_commande = MagicMock()
        mock_commande.id = 10

        body = json.dumps({"client_id": 42}).encode()

        with patch("app.consumer.SessionLocal") as mock_session_local, \
             patch("app.consumer.crud") as mock_crud:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_crud.get_commandes_by_client.return_value = [mock_commande]

            callback_client_deleted(mock_ch, mock_method, None, body)

            mock_crud.get_commandes_by_client.assert_called_once_with(mock_db, 42)
            mock_crud.update_commande_statut.assert_called_once_with(mock_db, 10, "client_supprime")
            mock_db.close.assert_called_once()
            mock_ch.basic_ack.assert_called_once_with(delivery_tag=1)

    def test_no_commandes_for_client(self):
        """Client sans commandes - aucune mise à jour, ack quand même"""
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 2

        body = json.dumps({"client_id": 99}).encode()

        with patch("app.consumer.SessionLocal") as mock_session_local, \
             patch("app.consumer.crud") as mock_crud:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_crud.get_commandes_by_client.return_value = []

            callback_client_deleted(mock_ch, mock_method, None, body)

            mock_crud.update_commande_statut.assert_not_called()
            mock_ch.basic_ack.assert_called_once_with(delivery_tag=2)

    def test_invalid_json_sends_nack(self):
        """JSON invalide dans le body - nack avec requeue"""
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 3

        callback_client_deleted(mock_ch, mock_method, None, b"invalid json")

        mock_ch.basic_nack.assert_called_once_with(delivery_tag=3, requeue=True)


class TestCallbackProduitDeleted:
    """Tests pour le consumer callback_produit_deleted"""

    def test_success_sends_ack(self):
        """Message valide - ack envoyé"""
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        body = json.dumps({"produit_id": 5}).encode()

        callback_produit_deleted(mock_ch, mock_method, None, body)

        mock_ch.basic_ack.assert_called_once_with(delivery_tag=1)

    def test_invalid_json_sends_nack(self):
        """JSON invalide dans le body - nack avec requeue"""
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 2

        callback_produit_deleted(mock_ch, mock_method, None, b"invalid json")

        mock_ch.basic_nack.assert_called_once_with(delivery_tag=2, requeue=True)


class TestStartConsumer:
    """Tests pour start_consumer (avec pika mocké pour éviter le blocage)"""

    def test_start_consumer_configures_queues(self):
        """start_consumer crée les queues et démarre la consommation"""
        with patch("app.consumer.pika.BlockingConnection") as mock_conn_class:
            mock_connection = MagicMock()
            mock_channel = MagicMock()
            mock_conn_class.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            mock_channel.start_consuming.return_value = None

            start_consumer()

            mock_conn_class.assert_called_once()
            mock_channel.exchange_declare.assert_called_once()
            assert mock_channel.queue_declare.call_count == 2
            assert mock_channel.queue_bind.call_count == 2
            mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)
            assert mock_channel.basic_consume.call_count == 2
            mock_channel.start_consuming.assert_called_once()
