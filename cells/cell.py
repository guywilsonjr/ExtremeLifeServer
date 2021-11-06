from abc import abstractmethod, ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Set, Any
import pydantic
import numpy as np
import numpy.typing as npt


class CellEffectType(Enum):
    REPLICATE = auto()
    ATTACK = auto()
    DEFEND = auto()
    INFECT = auto()


@dataclass
class CellEffect:
    effect_type: CellEffectType
    effect_x_loc: int
    effect_y_loc: int


@dataclass
class CellData(ABC):
    x_loc: int
    y_loc: int
    team_number: int
    grid_length: int
    grid_height: int
    armor: float = 0.1
    attack: float = 0.1
    life: float = 1.0
    replicativity: float = 0.1
    stability: float = 1.0
    virality: float = 0.1
    antivirality: float = 1.0


CellDataGrid = npt.NDArray[CellData]


class Cell:
    def __init__(self, data: CellData):
        self.data = data
        self._set_neighbor_ranges()

    def _set_neighbor_ranges(self) -> None:
        self.x_start = self.data.x_loc - 1 if self.data.x_loc > 0 else self.data.x_loc
        self.x_end = self.data.x_loc + 1 if self.data.x_loc < self.data.grid_length - 1 else self.data.x_loc
        self.y_start = self.data.y_loc - 1 if self.data.y_loc > 0 else self.data.y_loc
        self.y_end = self.data.y_loc + 1 if self.data.y_loc < self.data.grid_height - 1 else self.data.y_loc

    def _set_neighbors(self, grid: CellDataGrid) -> Set[CellData]:
        # Search the 3x3 grid around cell or 3x2 or 2x2 if at an edge or corner
        self.neighbors = {cell for cell_list in grid[self.x_start:self.x_end, self.y_start:self.y_end] for cell in cell_list}
        self.empty_neighbors = {cell for cell in self.neighbors if cell is None}
        self.friendly_neighbors = {cell for cell in self.neighbors if cell.team_number == self.data.team_number}
        self.enemy_neighbors = {cell for cell in self.neighbors if cell.team_number != self.data.team_number}

    @abstractmethod
    def get_target(self) -> CellData:
        pass

    def get_attack_target(self) -> CellData:
        return next(self.enemy_neighbors, None).data if self.enemy_neighbors else None

    def get_defense_target(self) -> CellData:
        return self.data

    def get_empty_target(self) -> CellData:
        return self.empty_neighbors.pop().data if self.empty_neighbors else None

    @abstractmethod
    def simulate_step(self, grid: CellDataGrid) -> CellEffect:
        pass


@pydantic.dataclasses.dataclass
class CellGrid(np.ndarray):
    class Config:
        aribtrary_types_allowed = True
    '''
    def __get_validators__():
        yield

    def __get_schema__():
        yield
    '''
    def validate(cls, input: Any):
        return input
