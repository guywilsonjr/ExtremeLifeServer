from dataclasses import dataclass
from enum import Enum
from cells.cell import Cell, CellGrid, CellEffect, CellEffectType, CellData, CellStats


specializing_factor = 2


@dataclass
class AttackCellStats(CellStats):
    attack = 2.0


@dataclass
class DefenseCellStats(CellStats):
    armor = 2.0


@dataclass
class ReplicateCellStats(CellStats):
    replicativity = 2.0


@dataclass
class ViralCellStats(CellStats):
    virality = 2.0
    antivirality = 2.0


class AttackCell(Cell):
    def get_target(self) -> CellData:
        return next(self.enemy_neighbors, None).data if self.enemy_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.ATTACK_EFFECT, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND_EFFECT, self.data.x_loc, self.data.y_loc)


class DefenseCell(Cell):
    def __post_init__(self):
        super().__init__(self.data)

    def get_target(self) -> CellData:
        return self.data

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.DEFEND_EFFECT, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.REPLICATE_EFFECT, self.data.x_loc, self.data.y_loc)


class ReplicateCell(Cell):
    def get_target(self) -> CellData:
        return next(self.empty_neighbors, None).data if self.empty_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.ATTACK_EFFECT, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND_EFFECT, self.data.x_loc, self.data.y_loc)


@dataclass
class ViralCell(Cell):
    def __post_init__(self):
        super().__init__(self.data)

    def get_target(self) -> CellData:
        return next(self.enemy_neighbors, None).data if self.enemy_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.INFECT_EFFECT, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND_EFFECT, self.data.x_loc, self.data.y_loc)


class CellType(Enum):
    REPLICATE = 'REPLICATE'
    ATTACK = 'ATTACK'
    DEFEND = 'DEFEND'
    INFECT = 'INFECT'
