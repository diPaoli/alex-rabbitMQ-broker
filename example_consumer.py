from broker.consumer import BasicMessage, RabbitConsumer
from broker.retry_publisher import RetryPublisher


def handle_message(message: BasicMessage):
    print("\nMESSAGE RECEIVED: ", message.body)
    print(f'RETRY_COUNT: {message.retry_count}')

    i = input('Type a number: ')
    if int(i) > 0:
        RetryPublisher(consumer, message)
    else: message.channel.basic_nack(delivery_tag=message.method.delivery_tag, requeue=False)


consumer = RabbitConsumer(
    queue = "ERIK_example_queue",
    task=handle_message,
    use_retry = True,
    auto_acknowledge=False
    )
consumer.consume()
