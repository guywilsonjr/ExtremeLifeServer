from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Set


@dataclass
class CellData:
    x_loc: int
    y_loc: int
    grid_length: int
    grid_height: int
    team_number: int


@dataclass
class CellData:
    x_loc: int
    y_loc: int
    grid_length: int
    grid_height: int
    team_number: int


CellGrid = List[List[CellData]]


@dataclass
class Cell:
    data: CellData

    def __init__(self, x_loc, y_loc, team_number, grid_length, grid_height):
        self.x_loc = x_loc
        self.y_loc = y_loc
        self.grid_length = grid_length
        self.grid_height = grid_height
        self.team_number = team_number

    def get_neighbors(self, grid: CellGrid) -> Set[CellData]:
        # Search the 3x3 grid around cell or 3x2 or 2x2 if at an edge or corner
        x_start = self.x_loc - 1 if self.x_loc > 0 else self.x_loc
        x_end = self.x_loc + 1 if self.x_loc < self.grid_length - 1 else self.x_loc
        y_start = self.y_loc - 1 if self.y_loc > 0 else self.y_loc
        y_end = self.y_loc + 1 if self.y_loc < self.grid_height - 1 else self.y_loc

        neighbors: Set[CellData] = set([cell for cell_list in grid[x_start:x_end, y_start:y_end] for cell in cell_list])
        # Remove self
        neighbors.remove(self.data)
        return neighbors

    @abstractmethod
    def simulate_step(self, grid: CellGrid) -> int:
        neighbors = self.get_neighbors(grid)
        num_neighbors = len(neighbors)

