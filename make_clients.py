import random
import time

from faker import Faker

from db.mongodb import MongoDB
from models.client import Client
from models.product import Product
from streaming.kafka_class import Kafka
from utils.config import load_config

config = load_config("config.yaml")
print(config)

product_colors = ["biały", "czerwony", "zielony", "niebieski", "czarny"]
product_names = ["mleko", "cukier", "czekolada", "chleb", "masło"]


faker = Faker(locale="pl")
db = MongoDB()
db.db_connect(config)


kafka_server = Kafka(config["kafka_servers"], config["kafka_topic_name"])
kafka_producer = kafka_server.make_producer()


for i in range(5):
    c = Client(first_name=faker.first_name(), last_name=faker.last_name(), adress=faker.address())
    for j in range(random.randint(0, 4)):
        p = Product(
            name=random.choice(product_names),
            color=random.choice(product_colors),
            price=round(random.randint(1, 100) / 100, 2),
            quantity=random.randint(1, 10),
        )

        db.save_product(p)

        c.add_product(p)
        time.sleep(0.15)
    print(c.to_json())
    print("=" * 60)

    # wysłanie na kafkę
    future = kafka_producer.send(config["kafka_topic_name"], c.to_dict())
    record_metadata = future.get(timeout=1)

    # zapis do Mongo
    db.save_client(client=c)

    onec = db.load_one_client(client_id=c.id)
    print(onec.to_json())
