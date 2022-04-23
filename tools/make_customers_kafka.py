from faker import Faker
from models.client import Customer
from streaming.kafka_class import Kafka
from utils.config import load_config

config = load_config("config.yaml")

faker = Faker(locale="pl")

kafka_server = Kafka(config["kafka_servers"], config["kafka_topic_name"])
kafka_producer = kafka_server.make_producer()


for i in range(5):
    c = Customer(first_name=faker.first_name(), last_name=faker.last_name(), address=faker.address())
    c_dict = c.to_dict()
    c_dict["event_type"] = "new_customer"

    kafka_server.send_message(c_dict)
