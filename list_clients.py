from db.mongodb import MongoDB
from utils.config import load_config

config = load_config("config.yaml")

db = MongoDB()
db.db_connect(config)

clients = db.load_all_clients()

for client in clients:
    print(client)
