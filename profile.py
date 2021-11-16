from pydantic.dataclasses import dataclass
from typing import List, Optional


@dataclass
class Profile:
    userid: int
    username: str
    games: Optional[List[int]] = None

