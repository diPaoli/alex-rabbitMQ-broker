import ssl
import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel
from retry import retry

from broker import std_info


logging_logger = logging.getLogger(__name__)


class BasicRabbitClient:
    def __init__(self, queue, **kwargs):
        self.queue = queue
        self.exchange: str = queue + '_X'
        self.routing_key: str = queue + '_RK'
        self.username: str = std_info.STD_USER
        self.password: str = std_info.STD_PASS
        self.host: str = std_info.STD_HOST
        self.port: int = 5671
        self.durable: bool = True
        self.message_ttl: int = std_info.STD_MESSAGE_TTL

        # retry optional params
        # self.retry_exchange: str = self.queue + "_RX"
        # self.retry_queue: str = self.queue + "_RQ"
        # self.retry_routing_key: str = self.queue + "_RK"

        # dead_letter optional params
        self.dead_letter_exchange: str = self.queue + "_DLX"
        self.dead_letter_queue: str = self.queue + "_DLQ"
        self.dead_letter_routing_key: str = self.queue + "_DLK"

        self.connection: pika.BlockingConnection
        self.channel: BlockingChannel
        self.args = {}

        # Enable/Disable Retry & Dead_Letter workflow
        self.use_retry: bool = False

        for key, value in kwargs.items():
            if key == 'exchange': self.exchange = value
            elif key == 'host': self.host = value
            elif key == 'port': self.port = int(value)
            elif key == 'routing_key': self.routing_key = value
            elif key == 'username': self.username = value
            elif key == 'password': self.password = value
            elif key == 'durable': self.durable = value
            elif key == 'message_ttl':
                self.message_ttl = int(value)
                self.args['x-message-ttl'] = self.message_ttl

            elif key == 'use_retry': self.use_retry = value

            # dead_letter optional params
            elif key == 'dead_letter_exchange':
                self.dead_letter_exchange = value
                self.args['x-dead-letter-exchange'] = self.dead_letter_exchange
            elif key == 'dead_letter_queue': self.dead_letter_queue = value
            elif key == 'dead_letter_routing_key':
                self.dead_letter_routing_key = value
                self.args['x-dead-letter-routing-key'] = self.dead_letter_routing_key

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_options = pika.SSLOptions(context)
        credentials = pika.PlainCredentials(self.username, self.password)
        self.params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                # virtual_host='/',
                credentials=credentials,
                ssl_options=ssl_options
                )

    @retry(pika.exceptions.AMQPConnectionError, delay=3, tries=5, logger=logging_logger)
    def connect(self):
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()

        # declare & Bind queues for retry behavior
        if self.use_retry:
            # self.channel.exchange_declare(exchange=self.retry_exchange, exchange_type='direct')
            # self.channel.queue_declare(queue=self.retry_queue, durable=True, arguments=self.args)
            # self.channel.queue_bind(exchange=self.retry_exchange, queue=self.retry_queue,
            #     routing_key=self.retry_routing_key)

            # bind dead_letter
            self.channel.exchange_declare(exchange=self.dead_letter_exchange, exchange_type='direct')
            self.channel.queue_declare(queue=self.dead_letter_queue, durable=True)
            self.channel.queue_bind(exchange=self.dead_letter_exchange, queue=self.dead_letter_queue,
                routing_key=self.dead_letter_routing_key)

        # declare & Bind main queue
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')
        self.channel.queue_declare(queue=self.queue, durable=self.durable, arguments=self.args)
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
