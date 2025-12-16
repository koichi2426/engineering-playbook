from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """日本の住所を表す値オブジェクト"""
    zipcode: str
    prefecture: str
    city: str
    town: str
