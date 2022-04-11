import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict
from uuid import uuid1


@dataclass
class ProductBase:
    name: str
    type: str
    price: float
    id: str = field(default_factory=lambda: str(uuid1()), init=False)

    def to_dict(self) -> Dict:
        d = {
            "name": self.name,
            "type": self.type,
            "price": self.price,
            "id": self.id,
        }
        return d

    def to_json(self) -> str:
        d = self.to_dict()
        return json.dumps(d, indent=3)

    def __repr__(self) -> str:
        return f'Produkt: "{self.name}" ({self.type}, cena {self.price:.2f} zł, ID {self.id})'


@dataclass
class Product(ProductBase):
    quantity: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self.value = self.quantity * self.price
