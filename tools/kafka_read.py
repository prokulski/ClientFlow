from streaming.kafka_class import Kafka
from utils.config import load_config

config = load_config("config.yaml")

kafka_server = Kafka(config["kafka_servers"], config["kafka_topic_name"])
kafka_consumer = kafka_server.make_consumer()

for msg in kafka_consumer:
    print(msg.value)
