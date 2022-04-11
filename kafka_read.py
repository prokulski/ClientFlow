from streaming.kafka import Kafka

KAFKA_SERVER = "127.0.0.1:9093"
KAFKA_TOPIC_NAME = "test_topic_1"

kafka_server = Kafka(KAFKA_SERVER, KAFKA_TOPIC_NAME)
kafka_consumer = kafka_server.make_consumer()

for msg in kafka_consumer:
    print(msg.value)
