import json
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid1

from models.product import Product, ProductBase


@dataclass
class Customer:
    first_name: str
    last_name: str
    address: str
    products: List[Product] = field(default_factory=list, init=False)
    id: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid1())

    def add_base_product(self, product: ProductBase, quantity: float = 0.0) -> None:
        prod = Product(**product.to_dict(), quantity=quantity)
        self.add_product(prod)

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def __repr__(self) -> str:
        client = f"{self.first_name} {self.last_name} ({self.id})"
        if self.products:
            client = client + " - ma następujące produkty:\n\t* "
            products = "\t* ".join(
                [
                    f"{p.type} (ID: {p.id}) {p.name} ({p.quantity} za {p.price:.2f} zł = {p.value:.2f} zł, kupione {p.timestamp:%Y-%m-%d %H:%M:%S})\n"
                    for p in self.products
                ]
            )
        else:
            products = " - nie ma produktów.\n"

        return client + products

    def to_dict(self) -> dict:
        d = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "id": self.id,
        }
        if self.products:
            d["products"] = [
                {
                    "id": p.id,
                    "type": p.type,
                    "name": p.name,
                    "price": p.price,
                    "quantity": p.quantity,
                    "timestamp_ms": int(1000 * p.timestamp.timestamp()),
                }
                for p in self.products
            ]

        return d

    def to_json(self) -> str:
        d = self.to_dict()
        return json.dumps(d, indent=3)
