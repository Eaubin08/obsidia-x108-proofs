
from dataclasses import dataclass

@dataclass
class Event:
    id: str
    label: str
    date: str
    narrative: str

