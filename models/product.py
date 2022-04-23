import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid1


@dataclass
class ProductBase:
    name: str
    type: str
    price: float
    id: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid1())

    def to_dict(self) -> dict:
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
    quantity: float = field(default=0.0)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self.value = self.quantity * self.price
