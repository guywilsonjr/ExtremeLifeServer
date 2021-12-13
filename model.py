from typing import Optional, List, TYPE_CHECKING
from cells.cell_types import CellType, Cell, CellInfo

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass


GRID_LENGTH = 10
GRID_WIDTH = 10
EMPTY_CELL: Cell = None


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
    cell_type: CellType
    team_number: int
    x_loc: int
    y_loc: int


@dataclass
class GameState:
    current_turn: int
    player_occupied_cells: List[CellInfo]


@dataclass
class GameData:
    game_id: int
    player1_req: MatchRequestData
    player2_req: MatchRequestData
    current_state: GameState
    grid_length: int = 10
    awaiting_p1_placment: bool = True
    awaiting_p2_placment: bool = True


@dataclass
class InitialPlacementRequest:
    user_id: int
    cell_placements: List[CellPlacement]
