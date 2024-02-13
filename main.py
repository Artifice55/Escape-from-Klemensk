import pygame
from sys import exit
import math
from settings import * 

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape from Klemensk")
clock = pygame.time.Clock()

background = pygame.transform.scale(pygame.image.load("street_background.png").convert(), (WIDTH, HEIGHT))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("0.png").convert_alpha(), 0, 0.35)
        self.base_player_image = self.image
        self.hitbox_rect = self.base_player_image.get_rect(center = self.pos)
        self.rect = self.hitbox_rect.copy()
        self.speed = PLAYER_SPEED 
    
    def player_rotation(self):
        self.mouse_coordinate = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coordinate[0] - self.hitbox_rect.centerx)
        self.y_change_mouse_player = (self.mouse_coordinate[1] - self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center = self.hitbox_rect.center)

    def user_input(self):
        self.velocity_x = 0 
        self.velocity_y = 0 
     
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()


player = Player()

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


    screen.blit(background, (0,0))
    screen.blit(player.image, player.rect)
    player.update()

    pygame.display.update()
    clock.tick(FPS)