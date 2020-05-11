from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from main import *


def agent_portrayal(agent):
    
    if isinstance(agent, Seaweed):
        portrayal = {"Shape": "rect", 
                    "Filled": "true", 
                    "w": 0.8, 
                    "h": 0.8, 
                    "Layer": 0,
                    "Color": "forestgreen"}
        
    else:
        portrayal = {"Shape": "circle",
                    "Filled": "true"}

        if isinstance(agent, Fish):
            portrayal["Color"] = "cornflowerblue"
            portrayal["Layer"] = 2
            portrayal["r"] = 0.4
        if isinstance(agent, Shark):
            portrayal["Color"] = "blueviolet"
            portrayal["Layer"] = 1
            portrayal["r"] = 0.6

    return portrayal

seaweed = {"Label": "Seaweed", "Color": "forestgreen"}
fish = {"Label": "Fish", "Color": "cornflowerblue"}
shark = {"Label": "Shark", "Color": "blueviolet"}

chart = ChartModule([seaweed, fish, shark])

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)
server = ModularServer(OceanModel,
                       [grid, chart],
                       "Ocean Model",
                       {"nseaweed":100, "nfish":40, "nshark":4, "width":20, "height":20})
server.port = 8522 
server.launch()