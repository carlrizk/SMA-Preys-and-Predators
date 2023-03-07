"""
Prey-Predator Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

from typing import List

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.space import Coordinate, MultiGrid

from prey_predator.agents import Animal, GrassPatch, Sheep, Wolf
from prey_predator.schedule import RandomActivationByBreed

WORLD_SIZE = (20, 20)


class WolfSheep(Model):
    """
    Wolf-Sheep Predation Model
    """

    def __init__(
        self,
        # Simulation World
        moore: bool,
        # Grass
        grass_progress_per_step: float,
        # Sheep
        sheep_initial_count: int,
        sheep_energy_step_expenditure: float,
        sheep_energy_gain_from_food: float,
        sheep_reproduction_energy_cost: float,
        sheep_reproduction_chance: float,
        # Wolf
        wolf_initial_count: int,
        wolf_energy_step_expenditure: float,
        wolf_energy_gain_from_food: float,
        wolf_reproduction_energy_cost: float,
        wolf_reproduction_chance: float,
    ):
        """
        Create a new Wolf-Sheep model with the given parameters.
        """
        super().__init__()

        # Simulation World
        self.width = WORLD_SIZE[0]
        self.height = WORLD_SIZE[1]
        self.moore = moore

        # Grass
        self.grass_progress_per_step = grass_progress_per_step

        # Sheep
        self.sheep_initial_count = sheep_initial_count
        self.sheep_energy_step_expenditure = sheep_energy_step_expenditure
        self.sheep_energy_gain_from_food = sheep_energy_gain_from_food
        self.sheep_reproduction_energy_cost = sheep_reproduction_energy_cost
        self.sheep_reproduction_chance = sheep_reproduction_chance

        # Wolf
        self.wolf_initial_count = wolf_initial_count
        self.wolf_energy_step_expenditure = wolf_energy_step_expenditure
        self.wolf_energy_gain_from_food = wolf_energy_gain_from_food
        self.wolf_reproduction_energy_cost = wolf_reproduction_energy_cost
        self.wolf_reproduction_chance = wolf_reproduction_chance

        ############
        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {
                "Average Grass Growth": lambda x: x.__get_average_metric_for(
                    GrassPatch, lambda g: g.progress
                ),
                "Average Sheep Energy": lambda x: x.__get_average_metric_for(
                    Sheep, lambda s: s.energy
                ),
                "Max Sheep Energy": lambda x: x.__get_max_metric_for(
                    Sheep, lambda s: s.energy
                ),
                "Average Wolf Energy": lambda x: x.__get_average_metric_for(
                    Wolf, lambda w: w.energy
                ),
                "Max Wolf Energy": lambda x: x.__get_max_metric_for(
                    Wolf, lambda w: w.energy
                ),
                "# Sheeps": self.__get_number_of(Sheep),
                "# Wolves": self.__get_number_of(Wolf),
            }
        )

        # Create sheep_initial_count sheeps in empty cells with random energy
        for i in range(self.sheep_initial_count):
            cell = self.grid.find_empty()
            if cell == None:
                raise "No empy cells left to create sheep"
            sheep = self.create_sheep(cell, self.random.randrange(1, 101))
            self.add_agent(sheep, cell)

        # Create wolf_initial_count wolves in empty cells with random energy
        for i in range(self.wolf_initial_count):
            cell = self.grid.find_empty()
            if cell == None:
                raise "No empy cells left to create wolf"
            wolf = self.create_wolf(cell, self.random.randrange(1, 101))
            self.add_agent(wolf, cell)

        # Create grass patches in every cell with random starting progress
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                grass = GrassPatch(
                    self.next_id(),
                    self,
                    self.random.randrange(0, 101),
                    self.grass_progress_per_step,
                )
                self.add_agent(grass, (x, y))

    def create_sheep(self, pos: Coordinate, energy: float):
        return Sheep(
            self.next_id(),
            self,
            self.grid,
            pos,
            self.moore,
            energy,
            self.sheep_energy_step_expenditure,
            self.sheep_energy_gain_from_food,
            self.sheep_reproduction_chance,
            self.sheep_reproduction_chance,
        )

    def create_wolf(self, pos: Coordinate, energy: float):
        return Wolf(
            self.next_id(),
            self,
            self.grid,
            pos,
            self.moore,
            energy,
            self.sheep_energy_step_expenditure,
            self.wolf_energy_gain_from_food,
            self.sheep_reproduction_chance,
            self.sheep_reproduction_chance,
        )

    def step(self):
        self.schedule.step()

        self.kill_animals()
        self.feed_animals()
        self.reproduce_animals()

        # Collect data
        self.datacollector.collect(self)

    def reproduce_animals(self):
        # Filter to animals
        animals_to_reproduce: List[Animal] = filter(
            lambda a: isinstance(a, Animal), self.schedule.agents
        )
        # Filter to animals that can reproduce
        animals_to_reproduce = filter(lambda a: a.can_reproduce, animals_to_reproduce)
        # Iterate over animals that can reproduce
        for animal in animals_to_reproduce:
            # Check if the animal is lucky and will reproduce
            chance = self.random.random()
            if chance <= animal.reproduction_chance:
                # Create a new animal of the same breed as his parent in the same cell as his parent
                if type(animal) is Sheep:
                    to_create = self.create_sheep(
                        animal.pos, 2 * animal.energy_step_expenditure + 1
                    )
                if type(animal) is Wolf:
                    to_create = self.create_wolf(
                        animal.pos, 2 * animal.energy_step_expenditure + 1
                    )
                self.add_agent(to_create, animal.pos)
                # Reduce the parent's energy by the reproduction cost
                animal.energy -= animal.reproduction_energy_cost

    def feed_wolves(self):
        # Filter to wolves
        wolves_to_feed: List[Wolf] = filter(
            lambda a: isinstance(a, Wolf), self.schedule.agents
        )

        # Filter to wolves that are hungry
        wolves_to_feed = filter(lambda w: w.is_hungry, wolves_to_feed)

        # Iterate over the wolves that are hungry
        for wolf in wolves_to_feed:
            # Check if there is a sheep in the same cell as the wolf
            cell_content = self.grid.get_cell_list_contents(wolf.pos)
            sheeps_in_cell = list(filter(lambda a: isinstance(a, Sheep), cell_content))
            if len(sheeps_in_cell) == 0:
                # If there is no sheep, the wolf can't eat
                continue
            # Choose a random sheep to kill
            sheep_to_kill = self.random.choice(sheeps_in_cell)
            # Kill the chosen sheep and increase the wolf's energy
            self.kill_agent(sheep_to_kill)
            wolf.energy += wolf.energy_gain_from_food

    def feed_sheeps(self):
        # Filter to sheeps
        sheeps_to_feed: List[Sheep] = filter(
            lambda a: isinstance(a, Sheep), self.schedule.agents
        )
        # Filter to sheeps that are hungry
        sheeps_to_feed = filter(lambda s: s.is_hungry, sheeps_to_feed)

        # Iterate over the sheeps that are hungry
        for sheep in sheeps_to_feed:
            # Find the GrassPatch in the same cell as the sheep
            cell_content = self.grid.get_cell_list_contents(sheep.pos)
            grass_in_cell: GrassPatch = list(
                filter(lambda a: isinstance(a, GrassPatch), cell_content)
            )[0]
            # Check if the GrassPatch is fully grown, reset it's state and increase the sheep's energy
            if grass_in_cell.is_fully_grown:
                grass_in_cell.reset()
                sheep.energy += sheep.energy_gain_from_food

    def feed_animals(self):
        self.feed_wolves()
        self.feed_sheeps()

    def kill_animals(self):
        # Filter to animals
        animals_to_kill: List[Animal] = filter(
            lambda a: isinstance(a, Animal), self.schedule.agents
        )

        # Filter this animals with 0 energy
        animals_to_kill = filter(lambda a: a.energy == 0, animals_to_kill)

        # Kill those animals
        for animal in animals_to_kill:
            self.kill_agent(animal)

    def get_grass_in_cell(self, pos: Coordinate) -> GrassPatch:
        content = self.grid.get_cell_list_contents(pos)
        grass = list(filter(lambda a: type(a) is GrassPatch, content))[0]
        return grass

    def add_agent(self, agent: Agent, pos: Coordinate):
        self.schedule.add(agent)
        self.grid.place_agent(agent, pos)

    def kill_agent(self, agent: Agent):
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)

    def run_model(self, step_count=200):
        for i in range(step_count):
            self.step()

    ################### Functions to calculate statistics to be displayed in the mesa interface

    def __get_average_metric_for(self, type, mapping_function):
        agents = self.schedule.get_breed(type)
        agents_metrics = map(mapping_function, agents)
        number_agents = len(agents)
        if number_agents == 0:
            return 0
        return sum(agents_metrics) / number_agents

    def __get_max_metric_for(self, type, mapping_function):
        agents = self.schedule.get_breed(type)
        agents_metrics = list(map(mapping_function, agents))
        if len(agents_metrics) == 0:
            return 0
        return max(agents_metrics)

    def __get_number_of(self, type):
        return lambda x: len(self.schedule.get_breed(type))
