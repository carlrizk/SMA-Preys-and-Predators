from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import Checkbox, Slider

from prey_predator.agents import Animal, GrassPatch, Sheep, Wolf
from prey_predator.model import WORLD_SIZE, WolfSheep


def wolf_sheep_portrayal(agent):
    if agent is None:
        return
    if type(agent) is GrassPatch:
        return {
            "Shape": "rect",
            "w": 1,
            "h": agent.progress / 100,
            "yAlign": 1,
            "Layer": 0,
            "Color": "#42f55d" if agent.is_fully_grown else "#e5ff00",
            "Filled": "true",
        }

    if isinstance(agent, Animal):
        protrayal = {
            "Shape": "rect",
            "w": agent.energy / 100,
            "h": 0.1,
            "xAlign": 0,
            "yAlign": 1,
            "Layer": 1,
            "Color": "#ff0000",
            "Filled": "true",
        }
        if type(agent) is Sheep:
            protrayal["text"] = "🐏"
        if type(agent) is Wolf:
            protrayal["text"] = "🐺"
        return protrayal
    return {}


server = ModularServer(
    WolfSheep,
    # Visualisation
    [
        CanvasGrid(wolf_sheep_portrayal, WORLD_SIZE[0], WORLD_SIZE[1], 500, 500),
        ChartModule(
            [
                {"Label": "Average Grass Growth", "Color": "red"},
            ]
        ),
        ChartModule(
            [
                {"Label": "Average Sheep Energy", "Color": "red"},
                {"Label": "Max Sheep Energy", "Color": "green"},
            ]
        ),
        ChartModule(
            [
                {"Label": "Average Wolf Energy", "Color": "red"},
                {"Label": "Max Wolf Energy", "Color": "green"},
            ]
        ),
        ChartModule(
            [
                {"Label": "# Sheeps", "Color": "red"},
                {"Label": "# Wolves", "Color": "green"},
            ]
        ),
    ],
    "Prey Predator Model",
    # Model Params
    {
        # Simulation World
        "moore": Checkbox("Moore grid ?", True),
        # Grass
        "grass_progress_per_step": Slider("Grass: growth % per step", 5, 0, 100),
        # Sheep
        "sheep_initial_count": Slider("Sheep: Initial count", 100, 0, 200),
        "sheep_energy_step_expenditure": Slider(
            "Sheep: Energy expenditure each step", 5, 0, 100
        ),
        "sheep_energy_gain_from_food": Slider(
            "Sheep: Energy gain from food", 35, 0, 100
        ),
        "sheep_reproduction_energy_cost": Slider(
            "Sheep: Reproduction cost", 30, 0, 100
        ),
        "sheep_reproduction_chance": Slider(
            "Sheep: Reproduction chance", 0.05, 0, 1, 0.001
        ),
        # Wolf
        "wolf_initial_count": Slider("Wolf: Initial count", 15, 0, 200),
        "wolf_energy_step_expenditure": Slider(
            "Wolf: Energy expenditure each step", 2, 0, 100
        ),
        "wolf_energy_gain_from_food": Slider("Wolf: Energy gain from food", 50, 0, 100),
        "wolf_reproduction_energy_cost": Slider("Wolf: Reproduction cost", 30, 0, 100),
        "wolf_reproduction_chance": Slider(
            "Wolf: Reproduction chance", 0.201, 0, 0.5, 0.001
        ),
    },
)
server.port = 8521
