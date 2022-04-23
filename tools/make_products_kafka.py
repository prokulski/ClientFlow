import random

from models.product import ProductBase
from streaming.kafka_class import Kafka
from utils.config import load_config

config = load_config("config.yaml")

products = [
    ("mleko", "Mleko Wypasione"),
    ("mleko", "Łaciate"),
    ("cukier", "Cukier w kostkach"),
    ("cukier", "Cukier drobny"),
    ("czekolada", "Milka Mleczna"),
    ("czekolada", "Wedel Gorzka"),
    ("czekolada", "Alpengold z orzechami"),
    ("czekolada", "Alpengold mleczna"),
    ("chleb", "Chleb staropolski"),
    ("chleb", "Chleb wiejski"),
    ("chleb", "Chleb codzienny"),
    ("masło", "Masło ekstra"),
    ("masło", "Masełko maślane"),
]

kafka_server = Kafka(config["kafka_servers"], config["kafka_topic_name"])
kafka_producer = kafka_server.make_producer()


for product in products:
    p = ProductBase(name=product[1], type=product[0], price=round(random.randint(1, 100) / 100, 2))
    p_dict = p.to_dict()
    p_dict["event_type"] = "new_product"

    kafka_server.send_message(p_dict)
