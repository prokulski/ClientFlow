import json
import re
from uuid import uuid1

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError


class NoProducerError(KafkaError):
    message = "No producer error"
    description = "No producer available in Kafka class."


class NoConsumerError(KafkaError):
    message = "No consumer error"
    description = "No consumer available in Kafka class."


class Kafka:
    def __init__(self, bootstrap_server: str, topic_name: str, group_id: str = None) -> None:
        self.bootstrap_server = bootstrap_server
        self.topic_name = topic_name
        if group_id:
            self.group_id = group_id
        else:
            self.group_id = str(uuid1())
        self.consumer = None
        self.producer = None

    def make_producer(self) -> KafkaProducer:
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_server,
            acks="all",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        return self.producer

    def make_consumer(self) -> KafkaConsumer:
        self.consumer = KafkaConsumer(
            self.topic_name,
            group_id=self.group_id,
            bootstrap_servers=self.bootstrap_server,
            auto_offset_reset="earliest",
            value_deserializer=json.loads,
        )
        return self.consumer

    def send_message(self, message: dict) -> bool:
        if not self.producer:
            raise NoProducerError()

        future = self.producer.send(self.topic_name, message)
        try:
            _ = future.get(timeout=3)
            return True
        except Exception as e:
            print("Error", e)
            return False
