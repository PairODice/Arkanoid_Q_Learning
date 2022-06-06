import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
from math import cos
import math

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


# font = pygame.font.SysFont('arial', 25)


Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLUE3 = (150, 150, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

BLOCK_SIZE = 40
BALL_SIZE = 20
PADDLE_SIZE = 100
SPEED = 1000
COLLISION_SLACK = 3
N_DISCRETE = 14


class Ball:
    def __init__(self):
        self.x = None
        self.y = None

        self.x_speed = None
        self.y_speed = None
        self.size = BALL_SIZE

    def is_touching(self, x, y, size):
        if (self.x + self.size) >= x and self.x <= (x + size):
            if (self.y + self.size) >= y and self.y <= (y + size):
                return True
        return False


class ArkanoidGame:

    def __init__(self, human_player=False, w=680, h=800):
        self.is_human = human_player
        self.w = w
        self.h = h
        self.frame = None
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Arkanoid')

        self.clock = pygame.time.Clock()
        self.score = None

        self.ball = Ball()
        self.blocks = []

        self.paddle_x = None
        self.paddle_y = None

        self.reset()

    def reset(self):

        self.frame = 0
        self.score = 0

        self._reset_bricks()

        self._reset_ball()

        self.paddle_x = 0
        self.paddle_y = self.h - 20

    def play_step(self, decision):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        if not self.is_human:
            self.paddle_x = int((np.argmax(decision) / N_DISCRETE) * self.w)
        else:
            mouse = pygame.mouse.get_pos()
            self.paddle_x = mouse[0] - PADDLE_SIZE//2

        self.ball.x += self.ball.x_speed
        self.ball.y += self.ball.y_speed

        # 4. Check collisions and update bounces
        game_over, fitness = self._bounce()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        self.frame += 1

        return game_over, self.score, fitness

    def _bounce(self):
        # check if the ball hit a wall
        if self.ball.x <= 0:
            self.ball.x_speed = -self.ball.x_speed
            self.ball.x = 0
        elif (self.ball.x + BALL_SIZE) >= self.w:
            self.ball.x_speed = -self.ball.x_speed
            self.ball.x = self.w - BALL_SIZE
        if self.ball.y <= 0:
            self.ball.y_speed = -self.ball.y_speed
        # check if ball hit bottom of screen
        elif self.ball.y + BALL_SIZE >= self.paddle_y + BALL_SIZE:
            return True, -10
        # check if ball hit paddle, calc new x speed
        elif self.ball.y + BALL_SIZE >= self.paddle_y:
            if self.ball.x <= self.paddle_x + PADDLE_SIZE and self.ball.x + BALL_SIZE >= self.paddle_x:
                # Calc new x speed
                # Normalize the position of the ball relative to the paddle to be between 0 and 1
                x = abs((self.ball.x + (BALL_SIZE/2) - self.paddle_x)/PADDLE_SIZE - 1)
                # convert to rough estimation of pi, excluding extremes
                x = x * 2.6 + 0.2
                # multiply by desired vector
                x = cos(x) * 5
                self.ball.x_speed = x
                self.ball.y_speed = -self.ball.y_speed
                return False, 10

        # Check if ball is hitting block
        hit_block = False
        for brick_x, brick_y in self.blocks:
            if self.ball.is_touching(brick_x, brick_y, BLOCK_SIZE):
                if not hit_block:
                    hit_block = True
                    if (self.ball.x + COLLISION_SLACK) >= (brick_x + BLOCK_SIZE) \
                            or (self.ball.x + BALL_SIZE) <= brick_x + COLLISION_SLACK:
                        self.ball.x_speed = -self.ball.x_speed
                    if(self.ball.y + COLLISION_SLACK) >= (brick_y + BLOCK_SIZE) \
                            or (self.ball.y + BALL_SIZE) <= brick_y + COLLISION_SLACK:
                        self.ball.y_speed = -self.ball.y_speed
                self.blocks.remove(Point(brick_x, brick_y))
                self.score += 1

        return False, 0

    def _update_ui(self):
        self.display.fill(BLACK)

        # Draw bricks
        for x, y in self.blocks:
            pygame.draw.rect(self.display, BLUE2, (x, y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE1, (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
            pygame.draw.rect(self.display, BLUE3, (x + 4, y + 4, 4, 2))
            pygame.draw.rect(self.display, BLUE3, (x + 4, y + 6, 2, 2))

        # Draw paddle
        pygame.draw.rect(self.display, WHITE, (self.paddle_x, self.paddle_y, PADDLE_SIZE, 10))

        # Draw ball
        pygame.draw.rect(self.display, GREY, (self.ball.x, self.ball.y, BALL_SIZE, BALL_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        pass

    def _reset_bricks(self):
        self.blocks = []
        # Leave a 2 block cushion on either side of the block
        for x in range((self.w//BLOCK_SIZE) - 4):
            # Only have blocks on the top half of the board with a 2 block cushion at the top
            for y in range(((self.h//BLOCK_SIZE) // 2) - 2):
                self.blocks.append(Point((x + 2) * BLOCK_SIZE, (y + 2) * BLOCK_SIZE))


    def _reset_ball(self):
        self.ball.x = random.randint(1, self.w - BALL_SIZE - 1)
        self.ball.y = self.h - 200
        self.ball.x_speed = 0
        self.ball.y_speed = 4

if __name__ == '__main__':
    game = ArkanoidGame(True)

    # game loop
    while True:
        game_over, score = game.play_step(1)

        if game_over == True:
            break

    print('Final Score')

    pygame.quit()
