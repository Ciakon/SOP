import keyboard as kb
import numpy as np
import random

from wall_crasher_v1 import Wall_crasher

class Q_table:
    def __init__(self, observation_amount, action_amount, size):

        states = [size for i in range(observation_amount)] # fx: [20, 20], with 2 observations of size 20.
        actions = [action_amount]

        self.table = np.zeros(states + actions) # Q-values for state can be found with self.table[state_info[0], state_info[1]...]
    

class Q_learning:
    def __init__(self, env = Wall_crasher(), learning_rate = 0.5, discount_factor = 0.7, size = 5, exploration_factor = 0.01):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_factor = exploration_factor
        self.lowest = env.observation_space[0] 
        self.highest = env.observation_space[1] # highest observable values
        self.action_amount = len(env.action_space)
        self.observation_amount = len(self.lowest)
        self.size = size # amount of possible observation between lowest and highest

        self.Q_table = Q_table(self.observation_amount, self.action_amount, self.size).table

        # convert continous space to discrete space.
        self.discrete_space = np.linspace(self.lowest[0], self.highest[0], self.size)

        self.state = None

    def map_observations(self, observations):
        observations = np.array(observations)

        observation_indexes = []

        for observation in observations:
            distances = [abs(possible_observation - observation) for possible_observation in self.discrete_space]
            index = np.array(distances).argmin()

            observation_indexes.append(
                index
            )

            # discrete_observation = self.discrete_space[index]
        return observation_indexes

    def calculate_Q_value(self, Q_value_old, Q_value_new, reward):
        return (1 - self.learning_rate) * Q_value_old + self.learning_rate * (reward + self.discount_factor * Q_value_new)
    
    def train(self, episodes):
        
        for episode in range(episodes):
            state = self.env.reset()
            observations, reward, crashed, timeout = state
            observations = tuple(self.map_observations(observations))

            while (not crashed and not timeout):

                if random.random() >= self.exploration_factor:
                    action = np.argmax(self.Q_table[observations])
                    Q_value = np.max(self.Q_table[observations])
                else:
                    action = random.choice(self.env.action_space)
                    Q_value = self.Q_table[observations][action]

                new_state = self.env.step(action)
                new_observations, reward, crashed, timeout = new_state
                new_observations = tuple(self.map_observations(new_observations))

                Q_value_new = np.max(self.Q_table[new_observations]) # Q-value for the new state (value of state)

                Q_value = self.calculate_Q_value(Q_value, Q_value_new, reward)
                
                # update Q-table
                self.Q_table[observations][action] = Q_value

                state = new_state
                observations, reward, crashed, timeout = state
                observations = tuple(self.map_observations(observations))

            if kb.is_pressed('i'): # show information
                    print("Episode:", episode)
                    print("Exploration factor:", self.exploration_factor)

            if kb.is_pressed('space'): # stop training
                break

            if timeout:
                    print("timeout, episode:", episode)

    def test(self):
        self.env.render = True
        state = self.env.reset()
        observations, reward, crashed, timeout = state
        observations = tuple(self.map_observations(observations))

        while (not crashed and not timeout):   
            action = np.argmax(self.Q_table[observations])

            new_state = self.env.step(action)
            new_observations, reward, crashed, timeout = new_state
            new_observations = tuple(self.map_observations(new_observations))

            state = new_state
            observations, reward, crashed, timeout = state
            observations = tuple(self.map_observations(observations))

        self.env.render = False
        self.env.close()
    
    def save(self, filename):
        np.save(filename, self.Q_table)

    def load(self, filename):
        self.Q_table = np.load(filename)


stage1 = Wall_crasher(wall_filename="stage 1.txt", car_position=[100, 100])
stage2 = Wall_crasher(wall_filename="stage 2.txt", timeout_time=350)
stage3 = Wall_crasher(wall_filename="stage 3.txt", timeout_time=500)
stage4 = Wall_crasher(wall_filename="stage 4.txt", timeout_time=700)
test_stage = Wall_crasher(wall_filename="test.txt", timeout_time=400)

Benson = Q_learning(env=test_stage, learning_rate=0.5, discount_factor=0.9, size=20, exploration_factor=0.01)

Benson.load("Benson.npy")

Benson.train(50000)
input("training done")
Benson.test()