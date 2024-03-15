from typing import TypedDict

class Person(TypedDict):
    address: PersonAddress
    age: int
    email: str
    name: str

class PersonAddress(TypedDict):
    city: str
    state: str
    street: str
    zip: str