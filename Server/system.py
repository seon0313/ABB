from dataclasses import dataclass

@dataclass
class message:
    id: str
    type: str
    message: str
    time: str