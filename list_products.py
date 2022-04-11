from db.mongodb import MongoDB

MONGO_SERVER = "mongodb://root:rootpass@localhost:27017"
MONGO_DB_NAME = "clients_flow"
MONGO_SERVER_PRODUCT = "products"
MONGO_SERVER_CLIENTS = "clients"

db = MongoDB()
db.db_connect(
    db_connection_string=MONGO_SERVER,
    db_name=MONGO_DB_NAME,
    client_table_name=MONGO_SERVER_CLIENTS,
    product_table_name=MONGO_SERVER_PRODUCT,
)

products = db.load_all_products()

for product in products:
    print(product)
