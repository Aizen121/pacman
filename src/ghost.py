"""The ghosts: at each crossing, they take the shortest way to a target."""
from src.mover import OPPOSITE, Mover, can_move, neighbour
from src.pathfinding import distances_from
from src.player import BASE_SPEED, Player

GHOST_SPEED_RATIO = 0.9  # ghosts move at 90 % of Pac-Man's speed
# Order used to break ties between equally good ways, as in the arcade game.
PRIORITY = ("up", "left", "down", "right")


class Ghost(Mover):
    """A ghost: goes towards its target cell along the corridors.

    At each crossing it takes the way whose next cell is the closest to the
    target, distances being counted along the corridors (breadth-first
    search). It never turns back on its own, except in a dead end.
    """

    def __init__(self, name: str, corner: tuple[int, int],
                 speed: float = GHOST_SPEED_RATIO * BASE_SPEED) -> None:
        """Create a ghost waiting in its corner.

        Args:
            name: Name of the ghost, which also selects its color.
            corner: Starting cell (x, y), where it respawns.
            speed: Speed in cells per second.
        """
        super().__init__(corner, speed)
        self.name = name
        self.target = corner

    def chase(self, player: Player) -> None:
        """Aim at the cell of Pac-Man: Blinky's way of chasing."""
        self.target = player.cell

    def choose_direction(self, maze: list[list[int]]) -> str | None:
        """Take the open way whose next cell is the closest to the target."""
        back = OPPOSITE[self.direction] if self.direction else None
        ways = [way for way in PRIORITY
                if way != back and can_move(maze, self.cell, way)]
        if not ways:  # dead end: turning back is the only way out
            ways = [way for way in PRIORITY if can_move(maze, self.cell, way)]
        if not ways:
            return None
        distances = distances_from(maze, self.target)
        too_far = len(maze) * len(maze[0])  # longer than any real path
        return min(ways, key=lambda way: distances.get(
            neighbour(self.cell, way), too_far))
