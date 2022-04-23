import random

from models.product import ProductBase
from streaming.kafka_class import Kafka
from utils.config import load_config

config = load_config("config.yaml")

products = [
    ("mleko", "Mleko Wypasione", "mleko_k_1"),
    ("mleko", "Łaciate", "mleko_k_2"),
    ("cukier", "Cukier w kostkach", "cukier_k_1"),
    ("cukier", "Cukier drobny", "cukier_k_2"),
    ("czekolada", "Milka Mleczna", "czekolada_k_1"),
    ("czekolada", "Wedel Gorzka", "czekolada_k_2"),
    ("czekolada", "Alpengold z orzechami", "czekolada_k_3"),
    ("czekolada", "Alpengold mleczna", "czekolada_k_4"),
    ("chleb", "Chleb staropolski", "chleb_k_1"),
    ("chleb", "Chleb wiejski", "chleb_k_2"),
    ("chleb", "Chleb codzienny", "chleb_k_3"),
    ("masło", "Masło ekstra", "maslo_k_1"),
    ("masło", "Masełko maślane", "maslo_k_2"),
]

kafka_server = Kafka(config["kafka_servers"], config["kafka_topic_name"])
kafka_producer = kafka_server.make_producer()


for product in products:
    p = ProductBase(id=product[2], name=product[1], type=product[0], price=round(random.randint(1, 100) / 100, 2))
    p_dict = p.to_dict()
    p_dict["event_type"] = "new_product"

    kafka_server.send_message(p_dict)
