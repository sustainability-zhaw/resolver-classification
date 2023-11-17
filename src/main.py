import json
import logging

import pika

import resolver
from settings import settings

settings.load([
    # "defaults.json", 
    "/etc/app/config.json", 
    "/etc/app/secrets.json"
])

logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def process_message(ch, method, properties, body):
    resolver.run(json.loads(body)["link"])
    ch.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    while True:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.MQ_HOST,
                heartbeat=settings.MQ_HEARTBEAT,
                blocked_connection_timeout=settings.MQ_TIMEOUT,
                credentials=pika.PlainCredentials(settings.MQ_USER, settings.MQ_PASS)
            )
        )

        channel = connection.channel()

        for routing_key in settings.MQ_BINDKEYS:
            channel.queue_bind(settings.MQ_QUEUE, settings.MQ_EXCHANGE, routing_key=routing_key)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(settings.MQ_QUEUE, process_message)

        try:
            channel.start_consuming()
        # Don't recover if connection was closed by broker
        except pika.exceptions.ConnectionClosedByBroker:
            break
        # Don't recover on channel errors
        except pika.exceptions.AMQPChannelError:
            break
        # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            continue

    connection.close()
