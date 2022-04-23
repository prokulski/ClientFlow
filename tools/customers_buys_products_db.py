import random
import time

from db.mongodb import MongoDB
from tqdm import trange
from utils.config import load_config

config = load_config("config.yaml")

db = MongoDB()
db.db_connect(config)

customers = db.load_all_customers()
products = db.load_all_products()

for i in trange(10):
    rnd_customer = random.choice(customers)
    rnd_product = random.choice(products)
    rnd_customer.add_base_product(rnd_product, random.randint(1, 10))
    db.save_customer(rnd_customer)

    time.sleep(2)  # specjalnie spowolnione, żeby było widać że coś się dzieje :)
