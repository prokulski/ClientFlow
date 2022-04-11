from db.mongodb import MongoDB
from utils.config import load_config

config = load_config("config.yaml")

db = MongoDB()
db.db_connect(config)

products = db.load_all_products()

for product in products:
    print(product)
