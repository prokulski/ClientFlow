from typing import List, Protocol

from models.client import Client
from models.product import ProductBase


class DB(Protocol):
    def db_connect(
        self, db_connection_string: str, db_name: str, client_table_name: str, product_table_name: str
    ) -> None:
        """inicjalizacja połączenia z bazą"""
        raise NotImplementedError()

    def load_all_products(self) -> List[ProductBase]:
        """wczytanie wszystkich produktów z bazy"""
        raise NotImplementedError()

    def load_one_product(self, product_id: str) -> ProductBase:
        """wczytanie wszystkich produktów z bazy"""
        raise NotImplementedError()

    def load_all_clients(self) -> List[Client]:
        """wczytanie wszystkich klientów z bazy"""
        raise NotImplementedError()

    def load_one_client(self, client_id: str) -> Client:
        """wczytanie wszystkich klientów z bazy"""
        raise NotImplementedError()

    def save_product(self, product: ProductBase) -> None:
        """zapisz produkt do bazy"""
        raise NotImplementedError()

    def save_client(self, client: Client) -> None:
        """zapisz klienta do bazy"""
        raise NotImplementedError()
