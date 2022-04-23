from typing import Dict, List, Protocol

from models.customer import Customer
from models.product import ProductBase


class DB(Protocol):
    def db_connect(self, config: Dict) -> None:
        """inicjalizacja połączenia z bazą"""
        raise NotImplementedError()

    def load_all_products(self) -> List[ProductBase]:
        """wczytanie wszystkich produktów z bazy"""
        raise NotImplementedError()

    def load_one_product(self, product_id: str) -> ProductBase:
        """wczytanie wszystkich produktów z bazy"""
        raise NotImplementedError()

    def load_all_customers(self) -> List[Customer]:
        """wczytanie wszystkich klientów z bazy"""
        raise NotImplementedError()

    def load_one_customer(self, client_id: str) -> Customer:
        """wczytanie wszystkich klientów z bazy"""
        raise NotImplementedError()

    def save_product(self, product: ProductBase) -> None:
        """zapisz produkt do bazy"""
        raise NotImplementedError()

    def save_customer(self, client: Customer) -> None:
        """zapisz klienta do bazy"""
        raise NotImplementedError()
