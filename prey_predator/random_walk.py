"""
Generalized behavior for random walking, one grid cell at a time.
"""

from mesa import Agent, Model
from mesa.space import Coordinate, MultiGrid


class RandomWalker(Agent):
    """
    Class implementing random walker methods in a generalized manner.

    Not indended to be used on its own, but to inherit its methods to multiple
    other agents.

    """

    def __init__(self, unique_id: int, model: Model,
                grid: MultiGrid, pos: Coordinate, moore: bool
                ):
        """
        Args:
        - `grid` (MultiGrid): The grid in which the agent lives.
        - `pos` (int, int): The agents current position in the grid.
        - `moore` (bool): If True, may move in all 8 directions. Otherwise, only up, down, left, right.
        """
        super().__init__(unique_id, model)
        self.grid = grid
        self.pos = pos
        self.moore = moore

    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent cells.
        next_moves = self.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.grid.move_agent(self, next_move)
