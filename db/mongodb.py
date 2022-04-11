from datetime import datetime
from typing import Dict, List

from models.client import Customer
from models.product import Product, ProductBase
from pymongo import MongoClient

from db.db import DB


class MongoDB(DB):
    __mongo_client = None
    __mongo_database = None
    __customers_collection = None
    __products_collection = None

    def db_connect(self, config: Dict) -> None:
        """inicjalizacja połączenia z bazą"""
        self.__mongo_client = MongoClient(config["db_uri"])
        self.__mongo_database = self.__mongo_client[config["db_name"]]
        self.__customers_collection = self.__mongo_database[config["customers_table"]]
        self.__products_collection = self.__mongo_database[config["products_table"]]

    def __preproces_product(self, product: Dict) -> ProductBase:
        """Zrób z dicta obiekt typu Product"""
        return ProductBase(name=product.get("name"), type=product.get("type"), price=product.get("price"))

    def __preproces_customers_product(self, product: Dict) -> Product:
        """Zrób z dicta obiekt typu Produkt który klient kupił"""
        return Product(
            name=product.get("name"),
            type=product.get("type"),
            price=product.get("price"),
            quantity=product.get("quantity"),
            timestamp=datetime.fromtimestamp(product.get("timestamp_ms", 0) / 1000),
        )

    def load_all_products(self) -> List[ProductBase]:
        """wczytanie wszystkich produktów z bazy"""
        product_list = [self.__preproces_product(product) for product in self.__products_collection.find()]
        return product_list

    def load_one_product(self, product_id: str) -> ProductBase:
        """wczytanie wszystkich produktów z bazy"""
        product = self.__products_collection.find({"id": product_id})
        product = list(product)[0]
        product_obj = self.__preproces_product(product)
        return product_obj

    def __preproces_customer(self, client: Dict) -> Customer:
        """Zbuduj klienta z dicta"""
        client_obj = Customer(
            first_name=client.get("first_name"),
            last_name=client.get("last_name"),
            address=client.get("address"),
            id=client.get("id"),
        )
        if client.get("products"):
            for product in client.get("products"):
                p = self.__preproces_customers_product(product)
                client_obj.add_product(product=p)
        return client_obj

    def load_all_customers(self) -> List[Customer]:
        """wczytanie wszystkich klientów z bazy"""
        client_lists = [self.__preproces_customer(client) for client in self.__customers_collection.find()]
        return client_lists

    def load_one_customer(self, client_id: str) -> Customer:
        """wczytanie wszystkich klientów z bazy"""
        client = self.__customers_collection.find({"id": client_id})
        client = list(client)[0]
        client_obj = self.__preproces_customer(client)
        return client_obj

    def save_product(self, product: ProductBase) -> None:
        """zapisz produkt do bazy"""
        self.__products_collection.delete_one({"id": product.id})
        self.__products_collection.insert_one(product.to_dict())

    def save_customer(self, client: Customer) -> None:
        """zapisz klienta do bazy"""
        self.__customers_collection.delete_one({"id": client.id})
        self.__customers_collection.insert_one(client.to_dict())
