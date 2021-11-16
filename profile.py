from pydantic.dataclasses import dataclass
from typing import List, Optional


@dataclass
class Profile:
    username: str
    userid: int
    games: Optional[List[int]] = None
