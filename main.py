from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer
# import matplotlib.pyplot as plt
# import numpy as np

class OceanModel(Model):
    """A model with some number of agents."""
    def __init__(self, nseaweed, nfish, nshark, width, height):
        self.total_seaweed = nseaweed
        self.num_seaweed = nseaweed
        self.total_fish = nfish
        self.num_fish = nfish
        self.total_shark = nshark
        self.num_shark = nshark
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        # Create food
        for i in range(self.num_seaweed):
            seaweed = Seaweed(i, self)
            self.schedule.add(seaweed)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(seaweed, (x, y))

        # Create fish
        for i in range(self.num_fish):
            fish = Fish(i + 1000, self)
            self.schedule.add(fish)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(fish, (x, y))

        # Create sharks
        for i in range(self.num_shark):
            shark = Shark(i + 2000, self)
            self.schedule.add(shark)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(shark, (x, y))

        data = {"Seaweed": lambda m: m.num_seaweed,
                "Fish": lambda m: m.num_fish,
                "Shark": lambda m: m.num_shark,}
        self.datacollector = DataCollector(data)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

        if(self.num_seaweed == 0 and self.num_fish == 0):
            self.running = False
        elif(self.num_fish == 0 and self.num_shark == 0):
            self.running = False
        elif(self.num_seaweed == 0 and self.num_shark == 0):
            self.running = False

class Shark(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 30

    def step(self):
        self.move()
        if self.wealth <= 0:
            self.die()
        else:
            self.searchFood()
            n = self.random.randrange(30)
            if( n == 1):
                self.reproduce()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.wealth -= 1

    def searchFood(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for mate in cellmates:
            if isinstance(mate, Fish):
                self.eat(mate)
                break
    
    def eat(self, fish):
        self.wealth += (fish.wealth / 2)
        fish.die()

    def reproduce(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, True, False)
        total_childs = 1
        for n in range(0, total_childs):
            pos = self.random.choice(neighbors)
            shark = Shark(self.model.total_shark + 2001, self.model)
            shark.wealth = self.wealth / 2
            self.model.total_shark += 1
            self.model.num_shark += 1
            self.model.schedule.add(shark)
            self.model.grid.place_agent(shark, pos)

    def die(self):
        self.model.grid._remove_agent(self.pos, self)
        self.model.schedule.remove(self)
        self.model.num_shark -= 1

class Fish(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 10

    def step(self):
        self.move()
        if self.wealth <= 0:
            self.die()
        else:
            self.searchFood()
            n = self.random.randrange(12)
            if( n == 1):
                self.reproduce()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.wealth -= 1

    def searchFood(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for mate in cellmates:
            if isinstance(mate, Seaweed):
                self.eat(mate)
                break
    
    def eat(self, seaweed):
        self.wealth += seaweed.wealth
        seaweed.die()

    def reproduce(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, True, False)
        total_childs = self.random.randrange(5)
        for n in range(0, total_childs):
            pos = self.random.choice(neighbors)
            fish = Fish(self.model.total_fish + 1001, self.model)
            fish.wealth = self.wealth / 2
            self.model.total_fish += 1
            self.model.num_fish += 1
            self.model.schedule.add(fish)
            self.model.grid.place_agent(fish, pos)

    def die(self):
        self.model.grid._remove_agent(self.pos, self)
        self.model.schedule.remove(self)
        self.model.num_fish -= 1

class Seaweed(Agent):

    fully_grown = False

    def __init__(self, unique_id, model, pos=None):
        super().__init__(unique_id, model)
        self.pos = pos
        self.wealth = 0

    def step(self):
        if self.fully_grown:
            self.wealth -= 1
        else:
            self.wealth += 1

        if self.wealth >= 10:
            self.fully_grown = True
            self.reproduce()

        if self.wealth <= 0:
            self.die()

    def reproduce(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, True, False)
        n = 2
        for neighbor in neighbors:
            if(self.model.grid.is_cell_empty(neighbor) and n > 0):
                seaweed = Seaweed(self.model.total_seaweed + 1, self.model)
                self.model.total_seaweed += 1
                self.model.num_seaweed += 1
                self.model.schedule.add(seaweed)
                self.model.grid.place_agent(seaweed, neighbor)
                n -= 1


    def die(self):
        self.model.grid._remove_agent(self.pos, self)
        self.model.schedule.remove(self)
        self.model.num_seaweed -= 1

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

grid = CanvasGrid(agent_portrayal, 25, 25, 500, 500)
server = ModularServer(OceanModel,
                       [grid, chart],
                       "Ocean Model",
                       {"nseaweed":150, "nfish":50, "nshark":3, "width":25, "height":25})
server.port = 8522 
server.launch()        