import random as rd
import yaml
import ABM as abm
import visualisations as vis
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

with open("simconfig.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

Agents = dict() # initialize empty agent dictionary
newborn = dict() # initialize empty newborn dictionary

# fixed seed for reproducability
np.random.seed(12345678)

# grid
w = cfg['Grid']['NX']
h = cfg['Grid']['NY']

# general
food_res = 4

# initialize grid
grid = abm.Grid(w,h)

# initialize number of prey and predators
rhoPrey = cfg['Sim']['RhoPrey']
rhoPred = cfg['Sim']['RhoPred']
CarryingCapacity = grid.get_cc()
nprey = int(CarryingCapacity * rhoPrey)
npred = int(CarryingCapacity * rhoPred)
num_agents = npred + nprey

# initialize starting positinos for agents
ipos = grid.initialPositions(num_agents)

# init constants
pFlee = cfg['Prey']['Pflee']
pBreedPrey = cfg['Prey']['Pbreed']
pBreedPred = cfg['Pred']['Pbreed']

# init preds
for _ in range(npred):
    abm.Predator(Agents, food_res, ipos[_], MaxFoodReserve=8)

# init preys
for _ in range(npred, num_agents):
    abm.Prey(Agents, food_res, ipos[_], MaxFoodReserve=8)


################# actual simulation below here ##############################

if(__name__ == '__main__'):
    print(":: Simulation start", dt.datetime.now())
    fig, ax = vis.show_agents(grid, Agents, savefig=True, title="Init")
    plt.close(fig)
    for _ in range(cfg['Sim']['NEpoch']):
        start = dt.datetime.now().replace(microsecond=0)  
        print("::: Step: ", _)
        print(":::: Mean food reserve: ", vis.mean_food(Agents))
        agentkeys = list(Agents.keys())
        np.random.shuffle(agentkeys)
        for ID in agentkeys:
            a = Agents[ID]
            if(a.get_kin() is not None):
                Nbh, NbhAgents, currentPos = grid.get_NbhAgents(a, Agents)
                roll = np.random.rand()
                if(roll < a.get_pBreed()):
                    a.createOffspring(Nbh, NbhAgents, currentPos, Agents, newborn)
                else:
                    a.Eat(grid, Nbh, NbhAgents, currentPos, Agents, pFlee)
        abm.lifecycle(grid, Agents, newborn)  # cleanup all the dead Agents

        fig, ax = vis.show_agents(grid, Agents, savefig=True, title="timestep " + str(_))
        plt.close(fig)
        print("::: Elapsed time: ", dt.datetime.now().replace(microsecond=0) - start)  
    print(":: Simulation stop", dt.datetime.now())
