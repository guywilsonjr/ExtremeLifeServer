from cell import Cell

specializing_factor = 2


class AttackCell(Cell):
    attack = 1.0


class DefenseCell(Cell):
    armor = 1.0


class ReplicateCell(Cell):
    replicativity = 1.0


class ViralCell(Cell):
    virality = 1.0
