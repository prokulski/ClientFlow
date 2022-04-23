import random

from db.mongodb import MongoDB
from models.product import ProductBase
from utils.config import load_config

config = load_config("config.yaml")

products = [
    ("mleko", "Mleko Wypasione", "mleko_db_1"),
    ("mleko", "Łaciate", "mleko_db_2"),
    ("cukier", "Cukier w kostkach", "cukier_db_1"),
    ("cukier", "Cukier drobny", "cukier_db_2"),
    ("czekolada", "Milka Mleczna", "czekolada_db_1"),
    ("czekolada", "Wedel Gorzka", "czekolada_db_2"),
    ("czekolada", "Alpengold z orzechami", "czekolada_db_3"),
    ("czekolada", "Alpengold mleczna", "czekolada_db_4"),
    ("chleb", "Chleb staropolski", "chleb_db_1"),
    ("chleb", "Chleb wiejski", "chleb_db_2"),
    ("chleb", "Chleb codzienny", "chleb_db_3"),
    ("masło", "Masło ekstra", "maslo_db_1"),
    ("masło", "Masełko maślane", "maslo_db_2"),
]


db = MongoDB()
db.db_connect(config)


for product in products:
    p = ProductBase(id=product[2], name=product[1], type=product[0], price=round(random.randint(1, 100) / 100, 2))
    db.save_product(p)
