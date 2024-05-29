from rabbit_broker.publisher import RabbitPublisher
from rabbit_broker.consumer import BasicMessage, RabbitConsumer
from rabbit_broker import std_info


class RetryPublisher():
    max_retry_count: int = 3
    """
    The Retry class.

    This is a simple publisher that requeues the message or sends it to
the dead_letter_queue specified in the consumer.dead_letter_queue parameter.

    * consumer: the same RabbitConsumer used to start the original queue. This
class will publish using the same parameters. If may also create a new consumer
object for retry purposes only, as needed.
    * message: the BasicMessage object received by the callback function which
contains the attributes to count retrys and handle acknowledgements.
    """
    def __init__(self, consumer: RabbitConsumer, message: BasicMessage, **kwargs):
        self.max_retry_count: int = std_info.STD_MAX_RETRY_COUNT

        for key, value in kwargs.items():
            if key == 'max_retry_count': self.max_retry_count = value

        if message.retry_count < self.max_retry_count:
            retry_publisher = RabbitPublisher(
                exchange=consumer.exchange,
                queue=consumer.queue,
                routing_key=consumer.routing_key,
                host=consumer.host,
                port=consumer.port,
                username=consumer.username,
                password=consumer.password,
                message=message.body,
                retry_count=message.retry_count + 1
            )
            retry_publisher.publish()
        else:
            dead_letter_publisher = RabbitPublisher(
                exchange=consumer.dead_letter_exchange,
                queue=consumer.dead_letter_queue,
                routing_key=consumer.dead_letter_routing_key,
                host=consumer.host,
                port=consumer.port,
                username=consumer.username,
                password=consumer.password,
                message=message.body,
                retry_count=message.retry_count
            )
            dead_letter_publisher.publish()
        message.channel.basic_nack(delivery_tag=message.method.delivery_tag, requeue=False)
