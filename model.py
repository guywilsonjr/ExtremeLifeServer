from typing import Optional, List, Set, TYPE_CHECKING
import dataclasses
from fastapi import File
from cells.cell import Cell, EMPTY_CELL_DATA, CellGridData
if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass


GRID_LENGTH = 10
GRID_WIDTH = 10
EMPTY_CELL: Cell = None


@dataclass
class Profile:
    userid: int
    username: str
    games: Optional[List[int]] = None


@dataclass
class ActionScriptMetaResp:
    script_id: int
    script_name: str


@dataclass
class ActionScriptMeta:
    resp: ActionScriptMetaResp
    path: str


@dataclass
class FindMatchRequest:
    player_id: int
    action_script_id: int


@dataclass
class MatchRequestData:
    player_id: int
    request_id: int
    action_script_id: int
    match_is_complete: Optional[bool]
    game_id: Optional[int] = None


@dataclass
class GameState:
    current_turn: int
    cell_grid: CellGridData

    def __init__(self):
        # Initialize a GRID_LENGTH x GRID_LENGTH grid of empty cells
        self.cell_grid = [[EMPTY_CELL_DATA] * GRID_LENGTH] * GRID_WIDTH
        self.current_turn = 0

    def get_cell_grid(self) -> CellGridData:
        return self.cell_grid


@dataclass
class NewGameRequest:
    player1_id: int
    player2_id: int
    player1_actionscript_name: str
    player2_actionscript_name: str


@dataclass
class GameData:
    game_id: int
    player1_req: MatchRequestData
    player2_req: MatchRequestData
    current_state: GameState
    awaiting_p1_placment: bool = True
    awaiting_p2_placment: bool = True


@dataclass
class CellPlacement:
    cell_type: str
    team_number: int
    x_loc: int
    y_loc: int


@dataclass
class InitialPlacementRequest:
    player_id: int
    cell_placements: Set[CellPlacement]
