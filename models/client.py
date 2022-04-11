import json
from dataclasses import dataclass, field
from typing import Dict, List
from uuid import uuid1

from models.product import Product


@dataclass
class Customer:
    first_name: str
    last_name: str
    address: str
    id: str = field(default_factory=lambda: str(uuid1()))
    products: List[Product] = field(default_factory=list, init=False)

    def add_product(self, product):
        self.products.append(product)

    def __repr__(self) -> str:
        client = f"{self.first_name} {self.last_name} ({self.id})"
        if self.products:
            client = client + " - ma następujące produkty:\n\t* "
            products = "\t* ".join(
                [
                    f"{p.type} {p.name} ({p.quantity} za {p.price:.2f} zł = {p.value:.2f} zł, kupione {p.timestamp:%Y-%m-%d %H:%M:%S})\n"
                    for p in self.products
                ]
            )
        else:
            products = " - nie ma produktów.\n"

        return client + products

    def to_dict(self) -> Dict:
        d = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "id": self.id,
        }
        if self.products:
            d["products"] = [
                {
                    "color": p.type,
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
