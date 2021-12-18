import random
from abc import ABCMeta
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class CellActionType(Enum):
    REPLICATE_ACTION = auto()
    ATTACK_ACTION = auto()
    DEFEND_ACTION = auto()
    INFECT_ACTION = auto()


@dataclass
class CellStats:
    defense: float = 1.0
    attack: float = 1.0
    replicativity: float = 1.0
    virality: float = 1.0
    antivirality: float = 1.0


@dataclass
class AttackCellStats(CellStats):
    attack = 2.0


@dataclass
class DefenseCellStats(CellStats):
    defense = 2.0


@dataclass
class ReplicateCellStats(CellStats):
    replicativity = 2.0


@dataclass
class ViralCellStats(CellStats):
    virality = 2.0
    antivirality = 2.0


@dataclass
class CellInfo:
    x_loc: int
    y_loc: int
    team_number: int
    cell_type: str
    life: float
    resilience: float


@dataclass
class CellAction:
    cell_info: CellInfo
    effect_type: CellActionType
    effect_x_loc: int
    effect_y_loc: int


class Cell(ABCMeta):
    @staticmethod
    def get_action(cell_info, neighbors: List[CellInfo]) -> CellAction:
        return CellAction(cell_info, CellActionType.DEFEND_ACTION, 0, 0)


class AttackCell(Cell):
    @staticmethod
    def get_action(cell_info: CellInfo, neighbors: List[CellInfo]) -> CellAction:
        for neigh in neighbors:
            if not cell_info.team_number == neigh.team_number:
                return CellAction(cell_info, CellActionType.ATTACK_ACTION, neigh.x_loc, neigh.y_loc)

        for neigh in neighbors:
            return CellAction(cell_info, CellActionType.DEFEND_ACTION, neigh.x_loc, neigh.y_loc)
        return CellAction(cell_info, CellActionType.DEFEND_ACTION, cell_info.x_loc, cell_info.y_loc)

    @staticmethod
    def get_stats() -> AttackCellStats:
        return AttackCellStats()


class DefenseCell(Cell):
    @staticmethod
    def get_action(cell_info: CellInfo, neighbors: List[CellInfo]) -> CellAction:
        for neigh in neighbors:
            if cell_info.team_number == neigh.team_number and random.random() > 0.4:
                return CellAction(cell_info, CellActionType.DEFEND_ACTION, neigh.x_loc, neigh.y_loc)

        for neigh in neighbors:
            if not cell_info.team_number == neigh.team_number:
                return CellAction(cell_info, CellActionType.ATTACK_ACTION, neigh.x_loc, neigh.y_loc)
        return CellAction(cell_info, CellActionType.DEFEND_ACTION, cell_info.x_loc, cell_info.y_loc)


    @staticmethod
    def get_stats() -> DefenseCellStats:
        return DefenseCellStats()

"""
class ReplicateCell(Cell):
    @staticmethod
    def get_action(cell_info: CellInfo, neighbors: List[CellInfo]) -> CellAction:
        return CellAction(cell_info, CellActionType.DEFEND_ACTION, 0, 0)

    @staticmethod
    def get_stats() -> ReplicateCellStats:
        return ReplicateCellStats()


class ViralCell(Cell):
    @staticmethod
    def get_action(cell_info: CellInfo, neighbors: List[CellInfo]) -> CellAction:
        return CellAction(cell_info, CellActionType.DEFEND_ACTION, 0, 0)

    @staticmethod
    def get_stats() -> ViralCellStats:
        return ViralCellStats()
"""

CELL_MAPPINGS = {
    'REPLICATE': AttackCell,
    'ATTACK': AttackCell,
    'DEFEND': DefenseCell,
    'INFECT': DefenseCell
}


