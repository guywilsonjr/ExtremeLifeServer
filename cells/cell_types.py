from dataclasses import dataclass

from cells.cell import Cell, CellGrid, CellEffect, CellEffectType, CellData

specializing_factor = 2


@dataclass
class AttackCellData(CellData):
    def __post_init__(self):
        self.attack = 1.0


@dataclass
class DefenseCellData(CellData):
    def __post_init__(self):
        self.armor = 1.0


@dataclass
class ReplicateCellData(CellData):
    def __post_init__(self):
        self.replicativity = 1.0


@dataclass
class ViralCellData(CellData):
    def __post_init__(self):
        self.virality = 1.0
        self.antivirality = 1.0


class AttackCell(Cell):
    def get_target(self) -> CellData:
        return next(self.enemy_neighbors, None).data if self.enemy_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.ATTACK, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND, self.data.x_loc, self.data.y_loc)


class DefenseCell(Cell):
    def __post_init__(self):
        super().__init__(self.data)

    def get_target(self) -> CellData:
        return self.data

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.DEFEND, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.REPLICATE, self.data.x_loc, self.data.y_loc)


class ReplicateCell(Cell):

    def get_target(self) -> CellData:
        return next(self.empty_neighbors, None).data if self.empty_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.ATTACK, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND, self.data.x_loc, self.data.y_loc)


@dataclass
class ViralCell(Cell):
    def __post_init__(self):
        super().__init__(self.data)

    def get_target(self) -> CellData:
        return next(self.enemy_neighbors, None).data if self.enemy_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.INFECT, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND, self.data.x_loc, self.data.y_loc)
