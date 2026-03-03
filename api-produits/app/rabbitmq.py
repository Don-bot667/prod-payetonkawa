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


def publish_produit_created(produit_id: int, produit_data: dict):
    """Publie un événement de création de produit"""
    publish_message("produit.created", {
        "event": "produit_created",
        "produit_id": produit_id,
        "data": produit_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


def publish_produit_updated(produit_id: int, produit_data: dict):
    """Publie un événement de modification de produit"""
    publish_message("produit.updated", {
        "event": "produit_updated",
        "produit_id": produit_id,
        "data": produit_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


def publish_produit_deleted(produit_id: int):
    """Publie un événement de suppression de produit"""
    publish_message("produit.deleted", {
        "event": "produit_deleted",
        "produit_id": produit_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


def publish_produit_stock_low(produit_id: int, produit_nom: str, stock: int):
    """Alerte quand le stock est bas (< 10 unités)"""
    publish_message("produit.stock_low", {
        "event": "produit_stock_low",
        "produit_id": produit_id,
        "produit_nom": produit_nom,
        "stock_actuel": stock,
        "seuil_alerte": 10,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
