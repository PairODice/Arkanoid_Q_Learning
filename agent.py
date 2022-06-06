from collections import deque
import numpy as np
from arkanoid_game import ArkanoidGame, Ball
from model import QTrainer, Linear_QNet
import torch
import random



BATCH_SIZE = 1000
LR = 0.003
N_DISCRETE = 14


class Agent:
    def __init__(self):

        self.gamma = 0                          # Discount rate
        self.memory = deque(maxlen=100_000)     # max memory
        self.model = Linear_QNet(3, 512, N_DISCRETE)    # Model Size
        self.trainer = QTrainer(self.model, LR, self.gamma) # Training parameters
        self.n_games = 0                        # number of games played
        self.epsilon = 100                      # randomness element, explore vs exploit

    def get_state(self, board):

        ball = board.ball

        state = [
            2 * ball.x/board.w - 1,
            2 * ball.y/board.h - 1,
            ball.x_speed
        ]

        return np.array(state, dtype=float)

    def remember(self, action, old_state, reward, new_state, game_over):
        self.memory.append((action, old_state, reward, new_state, game_over))

    def make_decision(self, state):
        decision = np.zeros((N_DISCRETE))
        state = torch.tensor(state, dtype=torch.float)
        if random.randint(0, 200) < self.epsilon - self.n_games:
            # TODO REMOVE DEBUG TEXT
            # print('rand')
            decision[random.randint(0, N_DISCRETE-1)] = 1
        else:
            # TODO REMOVE DEBUG TEXT
            # print('intnt', self.model(state))
            # print(torch.argmax(self.model(state)))
            ai_decision = torch.argmax(self.model(state)).item()
            decision[ai_decision] = 1

        return decision

    def train_short_memory(self, action, old_state, reward, new_state, game_over):
        self.trainer.train_step(action, old_state, reward, new_state, game_over)

    def train_long_memory(self):
        if BATCH_SIZE < len(self.memory):
            mini_batch = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_batch = self.memory
        actions, old_states, rewards, new_states, game_overs = zip(*mini_batch)
        self.trainer.train_step(actions, old_states, rewards, new_states, game_overs)


if __name__ == '__main__':
    agent = Agent()
    game = ArkanoidGame()
    high_score = 0
    game_over = None
    fitness = None
    new_state = None
    old_state = None
    decision = np.array([1])
    score = 0
    made_decision = False

    counter = 0
    while True:
        if counter % 5 is 0:
            old_state = agent.get_state(game)
            decision = agent.make_decision(old_state)
            # print(np.argmax(decision))
            game_over, score, fitness = game.play_step(decision)
            new_state = agent.get_state(game)
            agent.remember(decision, old_state, fitness, new_state, game_over)

            agent.train_short_memory(decision, old_state, fitness, new_state, game_over)

            if game_over:
                if score > high_score:
                    high_score = score
                print("Game:", agent.n_games, "Score:", score, "Record:", high_score)
                game.reset()
                agent.n_games += 1
                agent.train_long_memory()
            counter += 1
        else:
            if game_over:
                _, score, fitness = game.play_step(decision)
            else:
                game_over, score, fitness = game.play_step(decision)
            counter += 1
