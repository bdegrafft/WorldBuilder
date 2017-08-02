import numpy as np
from random import choice, randint
from scipy import ndimage


class Agent(object):
    """An agent is an object that wanders the map, under some defined
    constraints"""
    def __init__(self, location, constraints, civilization, scoutingRadius=0, maxradius=50):
        self.location = location
        self.constraints = constraints
        self.scoutingRadius = scoutingRadius
        self.civilization = civilization
        self.path = np.zeros(constraints.shape, dtype=bool)
        self.maxradius = maxradius

    def step(self, iterations=1, settle=False):
        print('stepping for %s'%self.civilization.name)
        for stepNum in range(iterations):
            ###Randomwalk Method###
            # self.path[self.location] = True
            # neighbors, i = [], self.scoutingRadius
            # while len(neighbors) == 0:
            #     neighbors = self.getNeighbors(self.path, self.location, i)
            #     i += 1
            #     if i > self.maxradius:
            #         self.civilization.territory = np.logical_or(ndimage.binary_fill_holes(self.path),self.civilization.territory)
            #         print('Path Ended')
            #         return None
            # self.location = choice(neighbors)

            ####county walk method###
            claimedCounties=None
            if settle is True:
                if randint(0, 100) == 1:
                    self.civilization.cities.append(Settlement('City', self.location, self.cityID))
                    self.cityID += 1
        self.civilization.territory = np.logical_or(ndimage.binary_fill_holes(self.path),self.civilization.territory)

    def getNeighbors(self, array, point, size):
        """Return list of True x,y coordinates within size number of tiles"""
        x, y = point[0], point[1]
        relativeNeighbors = zip(*np.where(array[x-size:x+size+1, y-size:y+size+1] == False))
        neighbors = [(p[0]-size+x, p[1]-size+y) for p in relativeNeighbors]
        relativeConstrained = zip(*np.where(self.constraints[x-size:x+size+1, y-size:y+size+1] == False))
        constrained = [(p[0]-size+x, p[1]-size+y) for p in relativeConstrained]
        for p in constrained:
            if p in neighbors:
                neighbors.remove(p)
        return neighbors


class Settlers(Agent):
    """Agents that create settlements based on criteria"""
    def __init__(self, location, constraints,civilization):
        super(Settlers, self).__init__(location, constraints,civilization)
        self.cities = []
        self.cityID = 240

    def step(self, iterations=1):
        super(Settlers, self).step(iterations,settle=True)


class Settlement(object):
    """docstring for Settlement."""
    def __init__(self, name, pos, ID):
        self.name = name
        self.pos = pos
        self.ID = ID
        self.population = 5

    def addToMap(self, mapName):
        mapName[self.pos] = self.ID


class Civilization(object):
    def __init__(self, name):
        self.name = name
        self.cities = []
        self.territory=np.zeros((2100, 2100),dtype=bool)

    def expand(self,iterations,constraints):
        if self.cities:

            city = choice(self.cities)
            start=city.pos
            print('expanding from %s'%city.ID)
        else:
            #start = choice(list(zip(*np.where(constraints))))
            start=(randint(1000,1300),randint(600,800))
        s = Settlers(start, constraints,self)
        t = s.step(iterations)
        print(np.unique(self.territory))
        return t
