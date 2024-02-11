import pygame
# from pygame import mixer
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
        self.shoot = False
        self.shoot_cooldown = 0 
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)
        self.rect = self.image.get_rect(center = (400, 400))
        self.health = 500
        self.current_health = 500
        self.maximum_health = 1000
        self.health_bar_length = 400
        self.health_ratio = self.maximum_health / self.health_bar_length

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
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
        if keys[pygame.K_UP]:
            self.velocity_y = -self.speed
        if keys[pygame.K_DOWN]:
            self.velocity_y = self.speed



        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self):
         if self.shoot_cooldown == 0:
             self.shoot_cooldown = SHOOT_COOLDOWN
             spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
             self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
             bullet_group.add(self.bullet)
             all_sprites_group.add(self.bullet)
        
         if self.bullet.rect.left > WIDTH or self.bullet.rect.right < 0 or self.bullet.rect.top > HEIGHT or self.bullet.rect.bottom < 0:
            self.bullet.kill()

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()
        self.basic_health()    
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        

    def get_damage(self, amount):
        if self.current_health > 0:
            self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0 
    
    def get_health(self, amount):
        if self.current_health < self.maximum_health:
            self.current_health += amount
        if self.current_health >= self.maximum_health:
            self.current_health = self.maximum_health

    def basic_health(self):
        pygame.draw.rect(screen, (255,0,0),(10,10,self.current_health/self.health_ratio,25))
        pygame.draw.rect(screen, (255,255,255),(10,10,self.health_bar_length,25),4)


class Bullet(pygame.sprite.Sprite): 
    
    all_bullets =[]    
    
    def __init__(self, x, y, angle): 
        super().__init__()
        self.image = pygame.image.load("1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.pos = pygame.math.Vector2(self.x, self.y)
        self.speed = BULLET_SPEED
        self.angle = angle
        self.x_vel = math.cos(self.angle * (2*math.pi/360)) * self.speed
        self.y_vel = math.sin(self.angle * (2*math.pi/360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks() # gets the specific time that the bullet was created, stays static
        Bullet.all_bullets.append(self)

    def bullet_movement(self): 
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime: 
            Bullet.all_bullets.remove(self)
            self.kill()

    def update(self):
        self.bullet_movement()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Zombie.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, .25)

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = 2

        self.position = pygame.math.Vector2(position)

        self.health = 100
        self.max_health = self.health

    def hunt_player(self):
        player_vector = pygame.math.Vector2(player.hitbox_rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()
        
        self.velocity = self.direction * self.speed
        self.position += self.velocity

        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

        if self.rect.colliderect(player.rect):
            player.health -= 10

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()
    
    def draw_health_bar(self):
        BAR_LENGTH = 50
        BAR_HEIGHT = 5
        fill = (self.health / self.max_health) * BAR_LENGTH
        bar_x = self.rect.centerx - BAR_LENGTH // 2
        outline_rect = pygame.Rect(bar_x, self.rect.y - 10, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(bar_x, self.rect.y - 10, fill, BAR_HEIGHT)
        pygame.draw.rect(screen, RED , outline_rect, 2)
        pygame.draw.rect(screen, GREEN , fill_rect)
    
    def update(self):
        self.hunt_player()
        self.draw_health_bar()

        if self.health <=0:
            self.kill()
    





all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

player = Player()
zombie = Enemy((800, 100))


all_sprites_group.add(player, zombie)




player_alive = True
all_enemies_defeated= False

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    if player_alive:    
        collisions = pygame.sprite.groupcollide(bullet_group, enemy_group, True, False)
        for bullet, enemies_hit in collisions.items():
            for enemy in enemies_hit:
                enemy.health -= 10
                if enemy.health <=0:
                    enemy.kill()
    
        player_enemy_collisions = pygame.sprite.spritecollide(player, enemy_group, False)
        for enemy in player_enemy_collisions:
            player.get_damage(10)

        player.user_input()

    screen.blit(background, (0,0))
   
    if player_alive and len(enemy_group) > 0:
        all_sprites_group.draw(screen)
    elif not player_alive: 
        font = pygame.font.SysFont(None, 100)
        death_text = font.render("You have died!", True, RED)
        screen.blit(death_text, (WIDTH // 2 - death_text.get_width() // 2, HEIGHT // 2 - death_text.get_width() // 2))

    elif len(enemy_group) == 0 and not all_enemies_defeated:
        victory_font = pygame.font.SysFont(None, 100)
        victory_text = victory_font.render("You have survived!", True, GREEN)
        screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - victory_text.get_width() // 2))

    all_sprites_group.update()

    if player.health <= 0:
        player_alive = False
        player.velocity_x = 0
        player.velocity_y = 0


    pygame.display.update()
    clock.tick(FPS)