import random
import time

from faker import Faker

from db.mongodb import MongoDB
from models.client import Client
from models.product import Product
from streaming.kafka import Kafka

product_colors = ["biały", "czerwony", "zielony", "niebieski", "czarny"]
product_names = ["mleko", "cukier", "czekolada", "chleb", "masło"]
KAFKA_SERVER = "127.0.0.1:9093"
KAFKA_TOPIC_NAME = "test_topic_1"
MONGO_SERVER = "mongodb://root:rootpass@localhost:27017"
MONGO_DB_NAME = "clients_flow"
MONGO_SERVER_PRODUCT = "products"
MONGO_SERVER_CLIENTS = "clients"

faker = Faker(locale="pl")
db = MongoDB()
db.db_connect(
    db_connection_string=MONGO_SERVER,
    db_name=MONGO_DB_NAME,
    client_table_name=MONGO_SERVER_CLIENTS,
    product_table_name=MONGO_SERVER_PRODUCT,
)


kafka_server = Kafka(KAFKA_SERVER, KAFKA_TOPIC_NAME)
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
        #     print("Product dict:")
        #     print(p.to_dict())
        #     print("\nProduct json:")
        #     print(p.to_json())
        c.add_product(p)
        time.sleep(0.15)
    #     print("=" * 20)

    # print("Client:")
    # print(c)
    # print("\nclient dict:")
    # print(c.to_dict())
    # print("\nclient json:")
    print(c.to_json())
    print("=" * 60)

    # wysłanie na kafkę
    future = kafka_producer.send(KAFKA_TOPIC_NAME, c.to_dict())
    record_metadata = future.get(timeout=1)

    # zapis do Mongo
    db.save_client(client=c)

    onec = db.load_one_client(client_id=c.id)
    print(onec.to_json())
