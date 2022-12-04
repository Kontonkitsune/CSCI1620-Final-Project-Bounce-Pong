# PONG pygame

import random
import pygame, sys
import math
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# global constants
WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
GRAVITY = 0.1
SPEED_CONSTANT = 4
PADDLE_SPEED = 8

# global variables
paddle_speed = PADDLE_SPEED
gravity = GRAVITY
ball_speed = SPEED_CONSTANT
ball_pos = [0, 0]
ball_vel = [0, 0]
paddle1_pos = 0
paddle2_pos = 0
l_score = 0
r_score = 0

# canvas declaration
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Hello World')


# helper function that spawns a ball, returns a position vector and a velocity vector
# if right is True, spawn to the right, else spawn to the left
def ball_init(right):
    global ball_pos, ball_vel, ball_speed, gravity  # these are vectors stored as lists
    ball_speed = SPEED_CONSTANT
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    ball_direction = random.random() * math.pi / 4
    horizontal_momentum = ball_speed * math.cos(ball_direction)
    vertical_momentum = ball_speed * math.sin(ball_direction)
    gravity = GRAVITY
    '''horz = random.randrange(2, 4)
    vert = random.randrange(1, 3)'''

    if not right:
        horizontal_momentum = - horizontal_momentum

    ball_vel = [horizontal_momentum, vertical_momentum]


def ante_up():
    global ball_speed, paddle_speed, gravity
    ball_speed += 0.5
    paddle_speed += 0.5
    gravity += 0.02


# define event handlers
def init():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, l_score, r_score  # these are floats
    global score1, score2  # these are ints
    paddle1_pos = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
    paddle2_pos = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT // 2]
    l_score = 0
    r_score = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)


# This is a simplification, even though it's annoying to be out of the main movement loop.
def movement():
    global paddle1_pos, paddle2_pos

    keys = pygame.key.get_pressed()

    if keys[K_UP] and paddle2_pos[1] > HALF_PAD_HEIGHT:
        paddle2_pos[1] -= PADDLE_SPEED
        if paddle2_pos[1] < HALF_PAD_HEIGHT:
            paddle2_pos[1] = HALF_PAD_HEIGHT
    if keys[K_DOWN] and paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle2_pos[1] += PADDLE_SPEED
        if paddle2_pos[1] > HEIGHT - HALF_PAD_HEIGHT:
            paddle2_pos[1] = HEIGHT - HALF_PAD_HEIGHT
    if keys[K_w] and paddle1_pos[1] > HALF_PAD_HEIGHT:
        paddle1_pos[1] -= PADDLE_SPEED
        if paddle1_pos[1] < HALF_PAD_HEIGHT:
            paddle1_pos[1] = HALF_PAD_HEIGHT
    if keys[K_s] and paddle1_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle1_pos[1] += PADDLE_SPEED
        if paddle1_pos[1] > HEIGHT - HALF_PAD_HEIGHT:
            paddle1_pos[1] = HEIGHT - HALF_PAD_HEIGHT


def game_processing():
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, l_score, r_score, ball_speed, gravity



    # update paddle's vertical position, keep paddle on the screen
    movement()
    '''if HALF_PAD_HEIGHT < paddle1_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] == HALF_PAD_HEIGHT and paddle1_vel > 0:
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] == HEIGHT - HALF_PAD_HEIGHT and paddle1_vel < 0:
        paddle1_pos[1] += paddle1_vel

    if HALF_PAD_HEIGHT < paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] == HALF_PAD_HEIGHT and paddle2_vel > 0:
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] == HEIGHT - HALF_PAD_HEIGHT and paddle2_vel < 0:
        paddle2_pos[1] += paddle2_vel'''

    # update ball
    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])
    ball_vel[1] += GRAVITY

    # ball collision check on top and bottom walls
    if int(ball_pos[1]) <= BALL_RADIUS:
        ball_pos[1] = BALL_RADIUS + 1
        ball_vel[1] = abs(ball_vel[1]) - 1
    if int(ball_pos[1]) >= HEIGHT + 1 - BALL_RADIUS:
        ball_pos[1] = HEIGHT - BALL_RADIUS - 1
        ball_vel[1] =  - abs(ball_vel[1])

    # ball collision check on gutters or paddles

    # left collider
    if int(ball_pos[0]) <= 1:
        r_score += 1
        ball_init(True)
    elif int(ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH and int(ball_pos[1]) in range(paddle1_pos[1] - HALF_PAD_HEIGHT,
                                                                                 paddle1_pos[1] + HALF_PAD_HEIGHT, 1):
        # ball_vel[0] = abs(ball_vel[0])
        storageval1 = math.radians(ball_pos[1] - paddle1_pos[1])
        ball_vel[1] = ball_speed * math.sin(storageval1)
        ball_vel[0] = ball_speed * math.cos(storageval1)
        ante_up()

    # right collider
    if int(ball_pos[0]) >= WIDTH - 1:
        l_score += 1
        ball_init(False)
    elif int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball_pos[1]) in range(
            paddle2_pos[1] - HALF_PAD_HEIGHT, paddle2_pos[1] + HALF_PAD_HEIGHT, 1):
        storageval1 = math.radians(ball_pos[1] - paddle2_pos[1])
        ball_vel[1] = ball_speed * math.sin(storageval1)
        ball_vel[0] = - ball_speed * math.cos(storageval1)
        ante_up()


# draw function of canvas
def draw(canvas):
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, l_score, r_score, ball_speed, gravity

    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [WIDTH / 2, 0], [WIDTH / 2, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1)
    pygame.draw.circle(canvas, WHITE, [WIDTH // 2, HEIGHT // 2], 70, 1)

    # draw paddles and ball
    pygame.draw.circle(canvas, RED, ball_pos, 20, 0)
    pygame.draw.polygon(canvas, GREEN, [[paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] - HALF_PAD_HEIGHT],
                                        [paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] - HALF_PAD_HEIGHT]], 0)
    pygame.draw.polygon(canvas, GREEN, [[paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] - HALF_PAD_HEIGHT],
                                        [paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] - HALF_PAD_HEIGHT]], 0)

    # update scores
    myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
    label1 = myfont1.render("Score " + str(l_score), 1, (255, 255, 0))
    canvas.blit(label1, (50, 20))

    myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
    label2 = myfont2.render("Score " + str(r_score), 1, (255, 255, 0))
    canvas.blit(label2, (470, 20))


'''
# keyup handler
def keyup(event):
    global paddle1_vel, paddle2_vel

    if event.key in (K_w, K_s):
        paddle1_vel = 0
    elif event.key in (K_UP, K_DOWN):
        paddle2_vel = 0
'''

init()

# game loop
while True:

    game_processing()
    draw(window)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fps.tick(60)