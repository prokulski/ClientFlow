import yaml


def load_config(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf8") as fp:
        config = yaml.safe_load(fp)

    database_type = config.get("database_type")
    db_data = {
        "db_uri": f"{database_type}://",
        "db_server": config.get(database_type).get("db_server"),
        "db_port": config.get(database_type).get("db_port"),
        "db_login": config.get(database_type).get("db_login"),
        "db_pass": config.get(database_type).get("db_pass"),
        "db_name": config.get(database_type).get("db_name"),
        "product_table": config.get(database_type).get("product_table"),
        "customers_table": config.get(database_type).get("customers_table"),
    }

    config_obj = {
        "kafka_servers": config.get("kafka_servers"),
        "kafka_topic_name": config.get("kafka_topic_name"),
        "db_uri": f"{db_data.get('db_uri')}{db_data.get('db_login')}:{db_data.get('db_pass')}@{db_data.get('db_server')}:{db_data.get('db_port')}",
        "db_name": db_data.get("db_name"),
        "products_table": db_data.get("product_table"),
        "customers_table": db_data.get("customers_table"),
    }

    return config_obj
