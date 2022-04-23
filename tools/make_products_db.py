import random

from db.mongodb import MongoDB
from models.product import ProductBase
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


db = MongoDB()
db.db_connect(config)


for product in products:
    p = ProductBase(name=product[1], type=product[0], price=round(random.randint(1, 100) / 100, 2))
    db.save_product(p)
