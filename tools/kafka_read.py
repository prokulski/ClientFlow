from db.mongodb import MongoDB
from events.events_handler import EventHandler
from streaming.kafka_class import Kafka
from utils.config import load_config

# konfiguracja
config = load_config("config.yaml")

# connector do bazy danych
db = MongoDB()
db.db_connect(config)

# connector do Kafki
kafka_server = Kafka(config["kafka_servers"], config["kafka_topic_name"])
kafka_consumer = kafka_server.make_consumer()

for msg in kafka_consumer:
    try:
        eh = EventHandler(msg.value, db)
    except Exception as e:
        print(f"Exception: {e}")
        print(msg)
