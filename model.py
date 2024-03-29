from typing import Optional, List, TYPE_CHECKING
from cells.cell_types import Cell, CellInfo

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass


GRID_LENGTH: int = 5


@dataclass
class PlayerProfile:
    user_id: int
    username: str


@dataclass
class ActionScriptMetaResp:
    action_script_id: int
    script_name: str


@dataclass
class ActionScriptMeta:
    resp: ActionScriptMetaResp
    path: str


@dataclass
class FindMatchRequest:
    user_id: int
    action_script_id: int


@dataclass
class MatchRequestData:
    user_id: int
    username: str
    request_id: int
    action_script_id: int
    is_match_complete: Optional[bool]
    game_id: Optional[int] = None


@dataclass
class CellPlacement:
    cell_type: str
    team_number: int
    x_loc: int
    y_loc: int


@dataclass
class GameState:
    current_turn: int
    player_occupied_cells: List[CellInfo]


@dataclass
class ScoreCard:
    p1_score: float
    p2_score: float


@dataclass
class GameData:
    game_id: int
    max_turns: int
    p1_user_id: int
    p2_user_id: int
    current_state: GameState
    awaiting_p1: bool
    awaiting_p2: bool
    awaiting_placements: bool
    score_card: Optional[ScoreCard]
    grid_length: int = GRID_LENGTH
    is_game_over: bool = False


@dataclass
class InitialPlacementRequest:
    user_id: int
    cell_placements: List[CellPlacement]
