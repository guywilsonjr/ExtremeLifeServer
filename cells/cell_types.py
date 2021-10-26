from dataclasses import dataclass

from cell import Cell, CellGrid, CellEffect, CellEffectType, CellData

specializing_factor = 2


class AttackCell(Cell):
    attack = 1.0

    def __post_init__(self):
        super().__init__(self.x_loc, self.y_loc, self.team_number, self.data_grid)

    def get_target(self) -> CellData:
        return next(self.enemy_neighbors, None).data if self.enemy_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.ATTACK, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND, self.x_loc, self.y_loc)


class DefenseCell(Cell):
    armor = 1.0

    def __post_init__(self):
        super().__init__(self.x_loc, self.y_loc, self.team_number, self.data_grid)

    def get_target(self) -> CellData:
        return self.data

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.DEFEND, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.REPLICATE, self.x_loc, self.y_loc)


class ReplicateCell(Cell):
    replicativity = 1.0

    def __post_init__(self):
        super().__init__(self.x_loc, self.y_loc, self.team_number, self.data_grid)

    def get_target(self) -> CellData:
        return next(self.empty_neighbors, None).data if self.empty_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.ATTACK, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND, self.x_loc, self.y_loc)


@dataclass
class ViralCell(Cell):
    virality = 1.0
    antivirality = 1.0

    def __post_init__(self):
        super().__init__(self.x_loc, self.y_loc, self.team_number, self.data_grid)

    def get_target(self) -> CellData:
        return next(self.enemy_neighbors, None).data if self.enemy_neighbors else None

    def simulate_step(self, grid: CellGrid) -> CellEffect:
        target = self.get_target()
        if target:
            return CellEffect(CellEffectType.INFECT, target.x_loc, target.y_loc)
        else:
            return CellEffect(CellEffectType.DEFEND, self.x_loc, self.y_loc)