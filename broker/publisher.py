import logging

from pika import BasicProperties

from broker.basic_rabbit_client import BasicRabbitClient


logging_logger = logging.getLogger(__name__)


class RabbitPublisher(BasicRabbitClient):
    """
    The Publisher class.

    * queue: the queue name to publish in.
    * exchange: exchange name to publish in. Default = "queue" + "_X"
    * retry_count: number of times the message has been requeued.
    * routing_key: the key that binds exchange, queue and messages. Default = "queue" + "_RK"
    * host: default = staging host.
    * port: default = 5671
    * username: default to staging username.
    * password: default to staging password.
    """
    def __init__(self, queue, message, **kwargs):
        super().__init__(queue, **kwargs)
        self.body = message
        self.retry_count: int = 0

        for key, value in kwargs.items():
            if key == 'retry_count': self.retry_count = int(value)


    def publish(self):
        try:
            self.connect()
            properties = BasicProperties(delivery_mode = 2, headers = {"x-retry-count": self.retry_count})
            self.channel.basic_publish(
                exchange = self.exchange,
                routing_key = self.routing_key,
                body = self.body,
                properties = properties
                )
            self.connection.close()
        except (ValueError, AttributeError, TypeError) as ex:
            logging.error(ex)
            print(f'[ERROR]: {ex}')
