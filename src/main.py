import json
import logging

import pika

import resolver
from settings import settings


logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def process_message(ch, method, properties, body):
    resolver.run(json.loads(body)["link"])
    ch.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.MQ_HOST,
            heartbeat=settings.MQ_HEARTBEAT,
            blocked_connection_timeout=settings.MQ_TIMEOUT
        )
    )

    channel = connection.channel()
    channel.exchange_declare(settings.MQ_EXCHANGE, exchange_type="topic")

    queue_declare_result = channel.queue_declare(settings.MQ_QUEUE, exclusive=False)
    queue_name = queue_declare_result.method.queue
   
    for routing_key in settings.MQ_BINDKEYS:
        channel.queue_bind(queue_name, settings.MQ_EXCHANGE, routing_key=routing_key)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue_name, process_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()
