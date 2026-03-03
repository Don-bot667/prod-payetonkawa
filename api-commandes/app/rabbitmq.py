import pika
import json
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "payetonkawa"


def get_connection():
    """Établit une connexion à RabbitMQ"""
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        return pika.BlockingConnection(parameters)
    except Exception as e:
        logger.error(f"Erreur connexion RabbitMQ: {e}")
        return None


def publish_message(routing_key: str, message: dict):
    """Publie un message sur RabbitMQ"""
    try:
        connection = get_connection()
        if not connection:
            return False

        channel = connection.channel()

        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type='topic',
            durable=True
        )

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        connection.close()
        logger.info(f"Message publié: {routing_key}")
        return True
    except Exception as e:
        logger.error(f"Erreur publication RabbitMQ: {e}")
        return False


def publish_commande_created(commande_id: int, commande_data: dict):
    """Publie un événement de création de commande"""
    publish_message("commande.created", {
        "event": "commande_created",
        "commande_id": commande_id,
        "data": commande_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


def publish_commande_updated(commande_id: int, statut: str):
    """Publie un événement de modification de commande"""
    publish_message("commande.updated", {
        "event": "commande_updated",
        "commande_id": commande_id,
        "statut": statut,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


def publish_commande_deleted(commande_id: int):
    """Publie un événement de suppression de commande"""
    publish_message("commande.deleted", {
        "event": "commande_deleted",
        "commande_id": commande_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
