from mazegenerator.mazegenerator import MazeGenerator
from src.player import Player
from src.parser import Config, LevelSize
import sys

# The maze package draws a random maze for any seed <= 0.
RANDOM_SEED = 0


class Level:

    def __init__(self, size: LevelSize, config: Config, seed: int) -> None:

        self.dimensions = (size.width, size.height)
        self.seed = seed
        self.generator = self._generate()
        self.maze = self.generator.maze
        self.corners = [(0, 0), (self.dimensions[0] - 1, 0), (0, self.dimensions[1] - 1), (self.dimensions[0] - 1, self.dimensions[1] - 1)]
        self.logo = [(x, y) for y, row in enumerate(self.maze) for x, cell in enumerate(row) if cell == 15]
        self.pacgums = self._place_pacgums(config.pacgum)
        self.available_pacgums = self.pacgums
        self.super_pacgums = set(self.corners)
        self.available_super_pacgums = self.super_pacgums
        self.player_start = self._find_maze_center()
        self.player = Player(self.player_start)

    # def _place_player(self)

    def _generate(self) -> MazeGenerator:
        """Run the external maze package, stopping cleanly if it fails."""
        try:
            return MazeGenerator(size=self.dimensions, seed=self.seed)
        except Exception as error:  # external code: any failure is possible
            print(f"Error: the maze generator failed for a "
                  f"{self.dimensions[0]}x{self.dimensions[1]} maze ({error}).",
                  file=sys.stderr)
            sys.exit(1)

    def _place_pacgums(self, pacgums: int) -> set[tuple[int, int]]:

        excluded = {*self.corners, *self.logo}
        
        candidates = [
            (x, y)
            for y in range(self.dimensions[1])
            for x in range(self.dimensions[0])
            if (x, y) not in excluded
        ]
        count = min(pacgums, len(candidates))
        if count == 0:
            return set()
        step = len(candidates) / count
        return {candidates[int(i * step)] for i in range(count)}

    def _find_maze_center(self) -> tuple[int, int]:
        """Return the free cell closest to the middle of the maze.

        The exact middle can be a cell of the "42" pattern, which is closed.
        """
        middle_x, middle_y = self.dimensions[0] // 2, self.dimensions[1] // 2
        free = [(x, y) for y in range(self.dimensions[1])
                for x in range(self.dimensions[0]) if (x, y) not in self.logo]
        return min(free, key=lambda cell: abs(cell[0] - middle_x)
                   + abs(cell[1] - middle_y))
