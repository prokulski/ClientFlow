import json
from uuid import uuid1

from kafka import KafkaConsumer, KafkaProducer


class Kafka:
    def __init__(self, bootstrap_server: str, topic_name: str, group_id: str = None) -> None:
        self.bootstrap_server = bootstrap_server
        self.topic_name = topic_name
        if group_id:
            self.group_id = group_id
        else:
            self.group_id = str(uuid1())

    def make_producer(self) -> KafkaProducer:
        return KafkaProducer(
            bootstrap_servers=self.bootstrap_server,
            acks="all",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def make_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(
            self.topic_name,
            group_id=self.group_id,
            bootstrap_servers=self.bootstrap_server,
            auto_offset_reset="earliest",
            value_deserializer=json.loads,
        )
