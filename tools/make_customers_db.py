from db.mongodb import MongoDB
from faker import Faker
from models.customer import Customer
from utils.config import load_config

config = load_config("config.yaml")

faker = Faker(locale="pl")

db = MongoDB()
db.db_connect(config)


for i in range(5):
    id_str = f"customer_db_{i:03}"
    c = Customer(id=id_str, first_name=faker.first_name(), last_name=faker.last_name(), address=faker.address())
    db.save_customer(client=c)
