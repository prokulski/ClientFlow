import random
import time

from db.mongodb import MongoDB
from streaming.kafka_class import Kafka
from tqdm import trange
from utils.config import load_config

config = load_config("config.yaml")


db = MongoDB()
db.db_connect(config)

customers = db.load_all_customers()
products = db.load_all_products()


kafka_server = Kafka(config["kafka_servers"], config["kafka_topic_name"])
kafka_producer = kafka_server.make_producer()

for i in trange(10):
    rnd_customer = random.choice(customers)
    rnd_product = random.choice(products)

    shopping_event = {
        "event_type": "customer_buys_product",
        "customer_id": rnd_customer.id,
        "product_id": rnd_product.id,
        "quantity": random.randint(1, 10),
    }

    kafka_server.send_message(shopping_event)

    time.sleep(2) # specjalnie spowolnione, żeby było widać że coś się dzieje :)
