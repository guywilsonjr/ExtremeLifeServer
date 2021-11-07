from dataclasses import dataclass
from typing import List


@dataclass
class Profile:
    username: str
    userid: int
    games: List[str]

