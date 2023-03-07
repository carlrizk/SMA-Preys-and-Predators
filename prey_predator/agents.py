from mesa import Agent, Model
from mesa.space import Coordinate, MultiGrid

from prey_predator.random_walk import RandomWalker


class GrassPatch(Agent):
    """
    A patch of grass that grows at a fixed rate

    Each simulation step:
    - The patch growth percentage `progress` increases by `progress_per_step`.
    - If `progress` is `100`, the patch is considered `fully_grown`.
    """

    def __init__(self, unique_id: int, model: Model, progress: int, progress_per_step: int):
        """
        Creates a new patch of grass
        """
        super().__init__(unique_id, model)
        self.progress = progress
        self.progress_per_step = progress_per_step
        self.__update_internal_state()


    def step(self):
        self.progress += self.progress_per_step
        self.progress = min(self.progress, 100)
        self.__update_internal_state()

    def reset(self):
        self.progress = 0
        self.__update_internal_state()


    def __update_internal_state(self):
        self.is_fully_grown = self.progress == 100

class Animal(RandomWalker):
    """
    An animal that walks around.
    """

    def __init__(
            self,
            unique_id: int, model: Model, # <- For Agent
            grid: MultiGrid, pos: Coordinate, moore: bool, # <- For RandomWalker
            energy: int, energy_step_expenditure: int, energy_gain_from_food: int,
            reproduction_energy_cost: int, reproduction_chance: float
            ):
        """
        Creates a new Animal
        """
        super().__init__(unique_id, model, grid, pos, moore)
        self.energy = energy
        self.energy_step_expenditure = energy_step_expenditure
        self.energy_gain_from_food = energy_gain_from_food
        self.reproduction_energy_cost = reproduction_energy_cost
        self.reproduction_chance = reproduction_chance
        self.__update_state()

    def step(self):
        self.random_move()
        self.energy -= self.energy_step_expenditure
        self.energy = max(self.energy, 0)
        self.__update_state()

    def __update_state(self):
        self.is_hungry = (self.energy <= 100 - self.energy_gain_from_food)
        self.can_reproduce = (self.energy >= 10 + self.reproduction_energy_cost)
        

class Sheep(Animal):
    """
    A sheep that walks around, reproduces (asexually) and gets eaten.
    """

    def __init__(
            self,
            unique_id: int, model: Model, # <- For Agent
            grid: MultiGrid, pos: Coordinate, moore: bool, # <- For RandomWalker
            energy: int, step_energy_expenditure: int, energy_gain_from_food: int, # <- For Animal
            reproduction_energy_cost: int, reproduction_chance: float # <- For Animal
            ):
        """
        Creates a new sheep
        """
        super().__init__(
            unique_id, model,
            grid, pos, moore,
            energy, step_energy_expenditure, energy_gain_from_food, reproduction_energy_cost, reproduction_chance)
        


class Wolf(Animal):
    """
    A wolf that walks around, reproduces (asexually) and eats sheeps.
    """

    def __init__(
            self,
            unique_id: int, model: Model, # <- For Agent
            grid: MultiGrid, pos: Coordinate, moore: bool, # <- For RandomWalker
            energy: int, step_energy_expenditure: int, energy_gain_from_food: int, # <- For Animal
            reproduction_energy_cost: int, reproduction_chance: float # <- For Animal
            ):
        """
        Creates a new sheep
        
        Args:
        - `energy` (float [0 - 100]): The percentage of energy the sheep has
        - `step_energy_expenditure` (float): The percentage of energy the sheep uses each step
        """
        super().__init__(
            unique_id, model,
            grid, pos, moore,
            energy, step_energy_expenditure, energy_gain_from_food, reproduction_energy_cost, reproduction_chance)
        

