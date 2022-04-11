import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict
from uuid import uuid1


@dataclass
class ProductBase:
    name: str
    color: str
    price: float
    id: str = field(default_factory=lambda: str(uuid1()), init=False)

    def to_dict(self) -> Dict:
        d = {
            "name": self.name,
            "color": self.color,
            "price": self.price,
            "id": self.id,
        }
        return d

    def to_json(self) -> str:
        d = self.to_dict()
        return json.dumps(d, indent=3)


@dataclass
class Product(ProductBase):
    quantity: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self.value = self.quantity * self.price
