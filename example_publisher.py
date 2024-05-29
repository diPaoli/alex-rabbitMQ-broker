from broker.publisher import RabbitPublisher

msg = "Message example using ERIK!"

publisher = RabbitPublisher(queue="ERIK_example_queue", message=msg)
publisher.publish()
print('Message published.')