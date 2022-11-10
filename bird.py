import time
import os
import random
import pygame
from pygame.locals import *

pygame.init()

#Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
CYAN = (0,255,255)
GREY = (120,120,120)

#Game window
window_x = 720
window_y = 640
fps = 60
clock = pygame.time.Clock()
game_window = pygame.display.set_mode((window_x, window_y))
pygame.display.set_caption("Flappy Bird")

bg = pygame.image.load('asset/bg.png').convert()
ground = pygame.image.load('asset/ground.png').convert()
restart = pygame.image.load('asset/restart.png')

#Fonts
font_30 = pygame.font.SysFont('Costantia', 32)
font_50 = pygame.font.SysFont('Costantia', 50)
font_80 = pygame.font.SysFont('Costantia', 80)
font_100 = pygame.font.SysFont('Oswald', 100)

#Vars
running = True
start = False
game_over = False
pass_pipe = False
score = 0
ground_scroll = 0
scroll_vel = 3
pipe_gap = 150
pipe_frequency = 1600#milisecs
last_pipe = pygame.time.get_ticks() - pipe_frequency

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,4):
            img = pygame.image.load(f'asset/bird{num}.png')
            self.images.append(img)
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.mask = pygame.mask.from_surface(self.image)
        self.vel = 0
        self.clicked = False

    def update(self):
        global game_over
        if start:
            #Gravity
            self.vel += 0.2
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 540:
                self.rect.y += self.vel

        #Jump
        if not game_over:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.clicked == False:
                self.clicked = True
                self.vel = -5
            if not key[pygame.K_SPACE]:
                self.clicked = False


        #Motion
        self.counter += 1
        if self.counter >= 8:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.image = self.images[self.index]
        #Rotate
        self.image = pygame.transform.rotate(self.images[self.index], -2*self.vel)

        if pygame.sprite.spritecollide(self, pipe_group, False, pygame.sprite.collide_mask) or flappy.rect.bottom >= 540:
            game_over = True

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('asset/pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap/2]
        if position == -1:
            self.rect.topleft = [x, y + pipe_gap/2]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if start and not game_over:
            self.rect.x -= scroll_vel
        if self.rect.right < -10:
            self.kill()

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        clicked = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                clicked = True
        return clicked


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()

flappy = Bird(96, window_y/2)
bird_group.add(flappy)

restart_button = Button(window_x/2, window_y/3, restart)
button_group.add(restart_button)

def show_score():
    score_surface = font_50.render(str(score).upper(), True, WHITE)
    game_window.blit(score_surface, (window_x/2 - (score_surface.get_width() - 10)/2, 5))

def reset():
    global score, start
    pipe_group.empty()
    flappy.rect.x = 96
    flappy.rect.y = window_y/2
    score = 0
    start = False

while running:
    #Running background
    game_window.blit(bg, (0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                start = True

    #Updates
    bird_group.update()
    pipe_group.update()
    #Draw
    pipe_group.draw(game_window)
    bird_group.draw(game_window)

    game_window.blit(ground, (ground_scroll,540))

    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    if start and not game_over:
        #Create pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            rand = random.randint(-100, 100)
            btm_pipe = Pipe(window_x + 64, window_y/2 + rand, -1)
            top_pipe = Pipe(window_x + 64, window_y/2 + rand, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = pygame.time.get_ticks()

        ground_scroll -= scroll_vel
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    if game_over:
        if restart_button.update():
            game_over = False
            reset()
        button_group.draw(game_window)
    
    show_score()

    clock.tick(fps)
    pygame.display.update()
pygame.quit()