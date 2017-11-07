# pacmanAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman import Directions
from game import Agent
from heuristics import *
import random
import math

class RandomAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        actions = state.getLegalPacmanActions()
        # returns random action from all the valide actions
        return actions[random.randint(0,len(actions)-1)]

class RandomSequenceAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        self.actionList = [];
        for i in range(0,10):
            self.actionList.append(Directions.STOP);
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        possible = state.getAllPossibleActions();
        for i in range(0,len(self.actionList)):
            self.actionList[i] = possible[random.randint(0,len(possible)-1)];
        tempState = state;
        for i in range(0,len(self.actionList)):
            if tempState.isWin() + tempState.isLose() == 0:
                tempState = tempState.generatePacmanSuccessor(self.actionList[i]);
            else:
                break;
        # returns random action from all the valide actions
        return self.actionList[0];

class GreedyAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        legal = state.getLegalPacmanActions()
        # get all the successor state for these actions
        successors = [(state.generatePacmanSuccessor(action), action) for action in legal]
        # evaluate the successor states using scoreEvaluation heuristic
        scored = [(scoreEvaluation(state), action) for state, action in successors]
        # get best choice
        bestScore = max(scored)[0]
        # get all actions that lead to the highest score
        bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
        # return random action from the list of the best actions
        return random.choice(bestActions)

class HillClimberAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        self.actionList = []
        for i in range(0, 5):
            self.actionList.append(Directions.STOP)
        return

    # GetAction Function: Called with every frame
    def getAction(self, state):
        possible = state.getAllPossibleActions()
        for i in range(0,len(self.actionList)):
            self.actionList[i] = possible[random.randint(0,len(possible)-1)]
        maxScore = -2147483648
        maxActionList = self.actionList[:]
        tempState = state          
        while True:
            tempState = state
            tempScore = -2147483648
            for i in range(0,len(self.actionList)):
                tempScore = scoreEvaluation(tempState)
                if tempState.isWin() + tempState.isLose() == 0:
                    tempState = tempState.generatePacmanSuccessor(self.actionList[i])
                    if not tempState:
                        # generatePacmanSuccessor has been called maximum times
                        break
                else:
                    break               
            if tempScore > maxScore:
                maxScore = tempScore
                maxActionList = self.actionList[:]
            if not tempState:
                # generatePacmanSuccessor has been called maximum times
                break
            self.changeActionList(tempState)
        return maxActionList[0]
        
    def changeActionList(self, state):
        possible = state.getAllPossibleActions()
        for i in range(0,len(self.actionList)):
            if (random.randint(0, 9) < 5):
                self.actionList[i] = possible[random.randint(0,len(possible)-1)]

class GeneticAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        defaultChromosome = []
        for i in range(0, 5):
            defaultChromosome.append(Directions.STOP)
        self.chromosomes = []
        for i in range(0, 8):
            self.chromosomes.append(defaultChromosome[:])
        return
    
    # Using rank selection
    def selectIndex(self):
        if not len(self.fitness):
            return None
        sum = 0
        value = random.randint(0, 35)
        for i in range(0, 8):
            sum += i + 1
            if value < sum:
                return self.fitness[i][0]
        return None
    
    def computeFitness(self, state):
        scoresMap = {}
        for i in range(0, len(self.chromosomes)):
            tempState = state
            tempScore = -2147483648
            for j in range(0,len(self.chromosomes[i])):
                tempScore = scoreEvaluation(tempState)
                if tempState.isWin() + tempState.isLose() == 0:
                    tempState = tempState.generatePacmanSuccessor(self.chromosomes[i][j])
                    if tempState is None:
                        # generatePacmanSuccessor has been called maximum times
                        return False
                else:
                    break
            scoresMap.update({i: tempScore})
        self.fitness = sorted(scoresMap.items(), key = lambda x: x[1])[:]
        return True
    
    def generateChildren(self, indexA, indexB, nextGeneration):
        if random.randint(0, 9) < 7:
            # Crossover (70%)
            for i in range(0, 2):
                # 2 children
                child = []
                for j in range(0, len(self.chromosomes[indexA])):
                    if random.randint(0, 1) < 1:
                        child.append(self.chromosomes[indexA][j])
                    else:
                        child.append(self.chromosomes[indexB][j])
                nextGeneration.append(child[:])
        else:
            # Keep the pair (30%)
            nextGeneration.append(self.chromosomes[indexA][:])
            nextGeneration.append(self.chromosomes[indexB][:])

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # Initialize population
        possible = state.getAllPossibleActions()
        for i in range(0, 8):
            tempChromosome = []
            for j in range(0, 5):
                tempChromosome.append(possible[random.randint(0,len(possible)-1)])
            self.chromosomes[i] = tempChromosome[:]
        # Start evolution
        nextGeneration = self.chromosomes[:]
        while self.computeFitness(state) is True:
            # Replace population
            self.chromosomes = nextGeneration[:]
            nextGeneration = []
            # Generate next generation
            while len(nextGeneration) < len(self.chromosomes):
                # Select parents
                parentAIndex = self.selectIndex()
                parentBIndex = self.selectIndex()
                #while parentBIndex == parentAIndex:
                #    parentBIndex = self.selectIndex()
                # Generate children
                self.generateChildren(parentAIndex, parentBIndex, nextGeneration)
            # Mutate
            for i in range(0, len(nextGeneration)):
                if random.randint(0, 9) < 1:
                    # Mutate this chromosome
                    nextGeneration[i][random.randint(0,len(nextGeneration[i])-1)] = possible[random.randint(0,len(possible)-1)]
        #survivor = self.selectIndex()
        survivor = self.fitness[len(self.fitness)-1][0]
        #print self.fitness
        #print survivor
        return self.chromosomes[survivor][0]

class MCTSAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # TODO: write MCTS Algorithm instead of returning Directions.STOP
        return Directions.STOP
