import pika
import json
import os
import logging
from .database import SessionLocal
from . import crud

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def callback_client_deleted(ch, method, properties, body):
    """Quand un client est supprimé, marquer ses commandes comme client_supprime"""
    try:
        data = json.loads(body)
        client_id = data.get("client_id")
        logger.info(f"Client supprimé détecté: {client_id}")

        db = SessionLocal()
        try:
            commandes = crud.get_commandes_by_client(db, client_id)
            for commande in commandes:
                crud.update_commande_statut(db, commande.id, "client_supprime")
            logger.info(f"{len(commandes)} commandes marquées comme client_supprime")
        finally:
            db.close()

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Erreur traitement client.deleted: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def callback_produit_deleted(ch, method, properties, body):
    """Quand un produit est supprimé, logger l'information"""
    try:
        data = json.loads(body)
        produit_id = data.get("produit_id")
        logger.info(f"Produit supprimé détecté: {produit_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Erreur traitement produit.deleted: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    """Lance le consumer RabbitMQ"""
    logger.info("Démarrage du consumer RabbitMQ...")

    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    channel.exchange_declare(exchange='payetonkawa', exchange_type='topic', durable=True)

    channel.queue_declare(queue='commandes_client_events', durable=True)
    channel.queue_bind(
        exchange='payetonkawa',
        queue='commandes_client_events',
        routing_key='client.deleted'
    )

    channel.queue_declare(queue='commandes_produit_events', durable=True)
    channel.queue_bind(
        exchange='payetonkawa',
        queue='commandes_produit_events',
        routing_key='produit.deleted'
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='commandes_client_events',
        on_message_callback=callback_client_deleted
    )
    channel.basic_consume(
        queue='commandes_produit_events',
        on_message_callback=callback_produit_deleted
    )

    logger.info("Consumer démarré, en attente de messages...")
    channel.start_consuming()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_consumer()
