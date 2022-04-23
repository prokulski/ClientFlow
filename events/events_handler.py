from db.db import DB
from models.customer import Customer
from models.product import ProductBase


class EventHandler:
    def __init__(self, message: dict, db: DB) -> None:
        if not message.get("event_type"):
            raise ValueError("Message has to have 'event_type'!")

        self.__db = db
        self.__message = message

        if message.get("event_type") == "new_customer":
            self.new_customer()
        if message.get("event_type") == "new_product":
            self.new_product()
        if message.get("event_type") == "customer_buys_product":
            self.customer_buys_product()

    def new_customer(self) -> None:
        msg = self.__message
        c = Customer(
            id=msg.get("id"),
            first_name=msg.get("first_name"),
            last_name=msg.get("last_name"),
            address=msg.get("address"),
        )
        self.__db.save_customer(client=c)

    def new_product(self) -> None:
        msg = self.__message
        p = ProductBase(id=msg.get("id"), name=msg.get("name"), type=msg.get("type"), price=msg.get("price"))
        self.__db.save_product(p)

    def customer_buys_product(self) -> None:
        msg = self.__message

        customer = self.__db.load_one_customer(msg.get("customer_id"))
        product = self.__db.load_one_product(msg.get("product_id"))
        customer.add_base_product(product, msg.get("quantity"))
        self.__db.save_customer(customer)
