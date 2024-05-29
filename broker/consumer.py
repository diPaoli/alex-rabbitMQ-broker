import logging
import time
from threading import Thread

import pika

from broker.basic_rabbit_client import BasicRabbitClient
from broker import std_info

logging_logger = logging.getLogger(__name__)


class BasicMessage():
    """
    Class to carry message and channel info/configs through the retry workflow.

    * channel: exposes the callback ch parameter for you to handle it as needed.
    * method: exposes the callback method parameter. It can be used to call manually to handle
acknowledgements as needed.
    * properties: exposes the callback properties parameter. (for further customization)
    * body: the callback body parameter. This is the message content it self.
    """
    def __init__(self, channel, method, properties, body) -> None:
        self.channel = channel
        self.method = method
        # self.properties = properties
        self.retry_count = properties.headers['x-retry-count']
        self.body = body


class RabbitConsumer(BasicRabbitClient):
    """
    The Consumer class.

    * exchange: exchange name to publish in. Default = "queue" + "_X"
    * queue: queue name to be consumed.
    * routing_key: the key that binds exchange, queue and messages. Default = "queue" + "_RK"
    * host: default = staging host.
    * port: default = 5671
    * username: default to staging username.
    * password: default to staging password.

    * durable: sets if server should be persiste messages. Default=True.
    * message_ttl: Message Time to Live. Default=10000.
    * use_retry: Enable/Disable Retry & Dead_Letter workflow. Default=False.
    * max_retry_count: Default: 3
    * dead_letter_exchange: Default = queue + "_DLX"
    * dead_letter_queue: Default = queue + "_DLQ"
    * dead_letter_routing_key: Default = queue + "_DLK"

    * prefetch_count: number of acknowledgements to send before
receiving more messages. Default value = 20. (for each consumer).
    * param task: method for handle received messages. If use_retry=True, this method
must expect channel, method, properties and body parameters.
    * param auto_acknowledge: whenever received messages should be automatically acknowledged. Default = True
    """
    def __init__(self, queue, task, **kwargs):
        super().__init__(queue, **kwargs)
        self.queue = queue
        self.task = task
        self.prefetch_count: int = std_info.STD_PREFETCH_COUNT
        self.auto_acknowledge: bool = True

        for key, value in kwargs.items():
            if key == 'prefetch_count': self.prefetch_count = int(value)
            elif key == 'auto_acknowledge': self.auto_acknowledge = value


    def consume(self):
        try:
            self.connect()
            self.channel.basic_qos(prefetch_count=self.prefetch_count, global_qos=False)
            self.channel.basic_consume(queue=self.queue, auto_ack=self.auto_acknowledge,
                on_message_callback=self.__callback)

            try:
                consumer_thread = Thread(target = self.channel.start_consuming)
                consumer_thread.start()
                logging.info('CONSUMER Thread launched! Consuming...')
                print('CONSUMER Thread launched! Consuming...')
            except KeyboardInterrupt:
                logging.info("Interrupted by user.")
                self.connection.close()

            reconection_thread = Thread(target = self.check_connection)
            reconection_thread.start()
        except (ValueError, AttributeError, TypeError) as ex:
            logging.error(ex)
            print(f'[ERROR]: {ex}')
            self.connection.close()

    # pylint: disable=C0103, W0718
    def __callback(self, ch, method, properties, body):
        try:
            if self.use_retry:
                message = BasicMessage(ch, method, properties, body)
                self.task(message)
            else: self.task(body)
        except Exception as ex:
            logging.error(ex)
            print(f'[ERROR]: {ex}')


    def check_connection(self):
        logging.info('Connection check loop started.')
        while True:
            if not self.connection or self.connection.is_closed:
                logging.warning('Connection lost! Starting reconnection routine...')
                self.reconnect()


    def reconnect(self):
        try:
            self.consume()
        except pika.exceptions.AMQPConnectionError as err:
            logging.error("Error in reconnection routine: %s", err)
            logging.info("Retrying in 5 seconds...")
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            time.sleep(5)
            logging.info('Retrying to connect...')
