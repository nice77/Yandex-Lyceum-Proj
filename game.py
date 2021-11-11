from sys import exit
import pygame
from random import choice, randint


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.walk = list(map(lambda x: pygame.image.load(f'assets/images/player/r{x}.png'), range(4)))
        self.walk = list()
        for i in range(4):
            self.walk.append(pygame.image.load(f'assets/images/player/r{i}.png'))
        self.jumper = pygame.image.load('assets/images/player/jumper.png')
        self.index = 0
        self.gravity = 0

        self.image = self.walk[self.index]
        self.rect = self.image.get_rect(bottomleft=(50, 350))

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom == 350:
            self.gravity = -150

    def apply_gravity(self):
        self.gravity += 3.5
        self.rect.bottom += self.gravity
        if self.rect.bottom >= 350:
            self.rect.bottom = 350
        self.gravity = 0

    def animation(self):
        if self.rect.bottom < 350:
            self.image = self.jumper
        else:
            self.index += 0.15
            if self.index > 3:
                self.index = 0
            self.image = self.walk[int(self.index)]

    def update(self):
        self.animation()
        self.input()
        self.apply_gravity()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        if type == 'snail':
            self.walk = list(map(lambda x: pygame.image.load(f'assets/images/enemies/snail/snail{x}.png'), range(1, 3)))
            y_pos = 350
        else:
            self.walk = list(map(lambda x: pygame.image.load(f'assets/images/enemies/Fly/fly{x}.png'), range(1, 3)))
            y_pos = 210
        self.index = 0
        self.image = self.walk[self.index]
        self.rect = self.image.get_rect(bottomleft=(randint(900, 1000), y_pos))

    def animation(self):
        self.index += 0.1
        if self.index > 2:
            self.index = 0
        self.image = self.walk[int(self.index)]

    def update(self):
        self.animation()
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()


def display_score():
    current = pygame.time.get_ticks()
    score = font.render(f'Score: {(current - start_time) // 1000}', False, (70, 70, 70))
    score_rect = score.get_rect(center=(366, 50))
    screen.blit(score, score_rect)


def colliding():
    if pygame.sprite.spritecollide(player.sprite, enemy, False):
        enemy.empty()
        return False
    return True


pygame.init()

WIDTH, HEIGHT = 732, 448

screen = pygame.display.set_mode((WIDTH, HEIGHT))
the_world = pygame.image.load('assets/images/the_world.jpg').convert()
font = pygame.font.Font('assets/Pixeltype.ttf', 50)

game_active = False

clock = pygame.time.Clock()

player = pygame.sprite.GroupSingle()
player.add(Player())

enemy = pygame.sprite.Group()

enemy_timer = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_timer, 1000)
start_time = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == enemy_timer and game_active:
            enemy.add(Enemy(choice(['snail', 'snail', 'fly'])))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and not game_active:
            game_active = True
            start_time = pygame.time.get_ticks()

    if game_active:
        screen.blit(the_world, (0, 0))
        player.draw(screen)
        player.update()
        enemy.draw(screen)
        enemy.update()
        game_active = colliding()
        display_score()

    else:
        screen.fill((163, 83, 151))
        text = font.render('Press "W" to run', False, (0, 0, 0))
        text_rect = text.get_rect(center=(366, 224))
        screen.blit(text, text_rect)

    pygame.display.update()
    clock.tick(60)
