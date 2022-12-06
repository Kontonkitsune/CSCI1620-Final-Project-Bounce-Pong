"""
Code originally by vinothpandian
Modified by Lucian Reiter, Dec 3, 2022
"""

import random
import pygame, sys
import math
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
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
GRAVITY = 0.1  # How fast the ball falls.
SPEED_CONSTANT = 4  # How fast the ball moves at the beginning of each match.
PADDLE_SPEED = 8
PARTITION_HEIGHT = 100
VERTICAL_SKEW = 2.0  # How high/low the ball is skewed based on the paddle's speed and the distance to its edge.

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
paddle1ai = True  # Dictates that both sides start off as AI players.
paddle2ai = True

game_state = False # true if a game is active.
l_total_score = 0
r_total_score = 0
cursor_pos = 1
cpu_difficulty = 3
game_length = 5
winner = ""
keydown = 0 # this just prevents key stuttering and allows the menu to be navigable.

# canvas declaration
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Pong Pong')


# helper function that spawns a ball, returns a position vector and a velocity vector
# if right is True, spawn to the right, else spawn to the left
def ball_init(right: bool) -> None:
    """
    This function runs every time a match ends. It is used to reset the playing field after a point is scored.

    :right: Boolean. Whether the ball should be served from the left side or the right side.
    """
    global ball_pos, ball_vel, ball_speed, gravity, paddle_speed  # these are vectors stored as lists
    ball_speed = SPEED_CONSTANT
    paddle_speed = PADDLE_SPEED
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    ball_direction = random.random() * math.pi / 4
    horizontal_momentum = ball_speed * math.cos(ball_direction)
    vertical_momentum = ball_speed * math.sin(ball_direction)
    gravity = GRAVITY

    if not right:
        horizontal_momentum = - horizontal_momentum

    ball_vel = [horizontal_momentum, vertical_momentum]


def ante_up() -> None:
    """This function is to be used when the ball hits a paddle. It slightly increases the difficulty and ensures that
    single matches don't extend infinitely."""
    global ball_speed, paddle_speed, gravity
    ball_speed += 0.5
    paddle_speed += 0.5
    gravity += 0.02


# define event handlers
def init() -> None:
    """This function initializes the game."""
    global paddle1_pos, paddle2_pos, l_score, r_score, paddle1ai, paddle2ai

    paddle1_pos = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
    paddle2_pos = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT // 2]
    l_score = 0
    r_score = 0
    paddle1ai = True
    paddle2ai = True
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)


# This is a simplification, even though it's annoying to be out of the main movement loop.
def paddle_movement() -> None:
    """This function controls the movement of the paddles."""
    global paddle1_pos, paddle2_pos, paddle1ai, paddle2ai, keys

    if keys[K_UP] and paddle2_pos[1] > HALF_PAD_HEIGHT:
        if paddle2ai:
            paddle2ai = False
        paddle2_pos[1] -= PADDLE_SPEED
        if paddle2_pos[1] < HALF_PAD_HEIGHT:
            paddle2_pos[1] = HALF_PAD_HEIGHT
    if keys[K_DOWN] and paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        if paddle2ai:
            paddle2ai = False
        paddle2_pos[1] += PADDLE_SPEED
        if paddle2_pos[1] > HEIGHT - HALF_PAD_HEIGHT:
            paddle2_pos[1] = HEIGHT - HALF_PAD_HEIGHT
    if keys[K_w] and paddle1_pos[1] > HALF_PAD_HEIGHT:
        if paddle1ai:
            paddle1ai = False
        paddle1_pos[1] -= PADDLE_SPEED
        if paddle1_pos[1] < HALF_PAD_HEIGHT:
            paddle1_pos[1] = HALF_PAD_HEIGHT
    if keys[K_s] and paddle1_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        if paddle1ai:
            paddle1ai = False
        paddle1_pos[1] += PADDLE_SPEED
        if paddle1_pos[1] > HEIGHT - HALF_PAD_HEIGHT:
            paddle1_pos[1] = HEIGHT - HALF_PAD_HEIGHT

    # if the AI is controlling the paddle.
    if paddle2ai:
        simple_ai_paddle(True)
    if paddle1ai:
        simple_ai_paddle(False)


def simple_ai_paddle(rightpong: bool) -> None:
    """
    This function controls the movement of the AI players.

    :rightpong: Boolean. Whether the AI in question is for Paddle 1 or Paddle 2
    """
    global paddle1_pos, paddle2_pos, ball_pos
    ai_paddle_speed = int(
        min(paddle_speed * (cpu_difficulty / 10) * (1 + abs(paddle1_pos[1] - ball_pos[1]) / 100), paddle_speed))
    if rightpong:
        if abs(paddle2_pos[1] - ball_pos[1]) > HALF_PAD_HEIGHT / 2:
            if paddle2_pos[1] > ball_pos[1]:
                paddle2_pos[1] -= ai_paddle_speed
            else:
                paddle2_pos[1] += ai_paddle_speed
    else:
        if abs(paddle1_pos[1] - ball_pos[1]) > HALF_PAD_HEIGHT / 2:
            if paddle1_pos[1] > ball_pos[1]:
                paddle1_pos[1] -= ai_paddle_speed
            else:
                paddle1_pos[1] += ai_paddle_speed


def game_processing() -> None:
    """
    This function does most of the game's calculations.
    These have to do with the ball's movement, momentum, and collision.
    """
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, l_score, r_score, ball_speed, gravity, keys
    global winner, game_state, l_total_score, r_total_score
    keys = pygame.key.get_pressed()
    if keys[K_ESCAPE]:
        game_state = False
    # draw the game
    draw_game(window)

    # update paddle's vertical position, keep paddle on the screen
    paddle_movement()

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
        ball_vel[1] = - abs(ball_vel[1])

    # left collider
    if int(ball_pos[0]) <= 1:
        r_score += 1
        ball_init(True)
    elif int(ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH and int(ball_pos[1]) in range(paddle1_pos[1] - HALF_PAD_HEIGHT,
                                                                                   paddle1_pos[1] + HALF_PAD_HEIGHT, 1):
        storageval1 = math.radians(ball_pos[1] - paddle1_pos[1])
        ball_vel[1] = VERTICAL_SKEW * ball_speed * math.sin(storageval1)
        if keys[K_w]:
            ball_vel[1] -= 2 * VERTICAL_SKEW
        elif keys[K_s]:
            ball_vel[1] += 2 * VERTICAL_SKEW
        ball_vel[0] = ball_speed * math.cos(storageval1)
        ante_up()

    # right collider
    if int(ball_pos[0]) >= WIDTH - 1:
        l_score += 1
        ball_init(False)
    elif int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball_pos[1]) in range(
            paddle2_pos[1] - HALF_PAD_HEIGHT, paddle2_pos[1] + HALF_PAD_HEIGHT, 1):
        storageval1 = math.radians(ball_pos[1] - paddle2_pos[1])
        ball_vel[1] = VERTICAL_SKEW * ball_speed * math.sin(storageval1)
        if keys[K_UP]:
            ball_vel[1] -= 2 * VERTICAL_SKEW
        elif keys[K_DOWN]:
            ball_vel[1] += 2 * VERTICAL_SKEW
        ball_vel[0] = - ball_speed * math.cos(storageval1)
        ante_up()

    # central collider
    if abs(int(ball_pos[0]) - (WIDTH // 2)) < BALL_RADIUS and int(ball_pos[1]) > HEIGHT - PARTITION_HEIGHT:
        if abs(ball_vel[1]) < 4 + (5 * gravity):
            ball_vel[1] = - 4 - (5 * gravity)
        if ball_pos[0] < WIDTH // 2:
            ball_pos[0] = (WIDTH // 2) - BALL_RADIUS
            ball_vel[0] = - abs(ball_vel[0])
        else:
            ball_pos[0] = (WIDTH // 2) + BALL_RADIUS
            ball_vel[0] = abs(ball_vel[0])

    if l_score > game_length // 2:
        winner = "Left"
        game_state = False
        l_total_score += 1
        init()
    elif r_score > game_length // 2:
        winner = "Right"
        r_total_score += 1
        game_state = False
        init()


# draw function of canvas
def draw_game(canvas) -> None:
    global paddle1_pos, paddle2_pos, ball_pos, l_score, r_score

    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(canvas, RED, [WIDTH // 2, HEIGHT - PARTITION_HEIGHT], [WIDTH // 2, HEIGHT], 5)
    pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1)

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
    if game_state:
        # update scores
        myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
        canvas.blit(myfont1.render("Score " + str(l_score), True, WHITE), (50, 20))
        canvas.blit(myfont1.render("Score " + str(r_score), True, WHITE), (470, 20))


def menu_processing():
    global cursor_pos, keys, keydown, cpu_difficulty, game_length, game_state
    draw_menu(window)
    keys = pygame.key.get_pressed()
    if keydown == 0:
        cancursormove = True
    else:
        cancursormove = False

    # move cursor
    if (keys[K_UP] or keys[K_w]) and cancursormove:
        cursor_pos -= 1
        if cursor_pos < 1:
            cursor_pos = 3
    if (keys[K_DOWN] or keys[K_s]) and cancursormove:
        cursor_pos += 1
        if cursor_pos > 3:
            cursor_pos = 1

    # change settings
    if (keys[K_RIGHT] or keys[K_d]) and cancursormove:
        if cursor_pos == 1:
            game_state = True
        elif cursor_pos == 2:
            cpu_difficulty += 1
            if cpu_difficulty > 10:
                cpu_difficulty = 10
        elif cursor_pos == 3:
            game_length += 2
            if game_length > 9:
                game_length = 9
    if (keys[K_LEFT] or keys[K_a]) and cancursormove:
        if cursor_pos == 1:
            game_state = True
        elif cursor_pos == 2:
            cpu_difficulty -= 1
            if cpu_difficulty < -1:
                cpu_difficulty = -1
        elif cursor_pos == 3:
            game_length -= 2
            if game_length < 1:
                game_length = 1

    if keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT] or keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d]:
        keydown += 1
    else:
        keydown = 0


def draw_menu(canvas) -> None:

    draw_game(canvas)

    myfont = pygame.font.SysFont("Comic Sans MS", 20)
    canvas.blit(myfont.render("Wins: " + str(l_total_score), True, YELLOW), (50, 20))
    canvas.blit(myfont.render("Wins: " + str(r_total_score), True, YELLOW), (470, 20))
    if winner != "":
        canvas.blit(myfont.render("Winner: " + winner, True, YELLOW), (240, 20))
    myfontbig = pygame.font.SysFont("Comic Sans MS", 30)
    canvas.blit(myfontbig.render("Pong Pong", True, (0, 255, 0)),
                (PAD_WIDTH + 20, 50))
    canvas.blit(myfontbig.render("Play game", True, YELLOW if cursor_pos == 1 else WHITE),
                (PAD_WIDTH + 20, 100))
    canvas.blit(myfontbig.render("CPU Difficulty: " + str(cpu_difficulty), True, YELLOW if cursor_pos == 2 else WHITE),
                (PAD_WIDTH + 20, 150))
    canvas.blit(myfontbig.render("Best of: " + str(game_length), True, YELLOW if cursor_pos == 3 else WHITE),
                (PAD_WIDTH + 20, 200))

init()

# game loop
while True:

    if game_state:
        game_processing()
    else:
        menu_processing()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fps.tick(60)
