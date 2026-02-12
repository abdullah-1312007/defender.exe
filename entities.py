import pygame
import math
import random
from constants import WIDTH, HEIGHT, BULLET_SPEED, RADIUS

pygame.init()


def lerp(start, end, factor):
    diff = (end - start + 180) % 360 - 180
    eased = (1 - math.cos(factor * math.pi)) / 2
    return start + diff * eased


class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.img = pygame.transform.scale2x(pygame.image.load('assets/icons/mouse.png')).convert_alpha()
        self.rect = pygame.Rect(x, y, self.img.get_width(), self.img.get_height())
        self.vel = 5
        self.angle = 0

    def draw(self, win):
        rotated_img = pygame.transform.rotate(self.img, -self.angle)
        rotated_rect = rotated_img.get_rect(center=self.pos)
        win.blit(rotated_img, rotated_rect.topleft)

    def move(self, dirs, width, height):  # r l u p
        direction = pygame.Vector2(0, 0)

        if dirs['right']: direction.x += 1
        if dirs['left']: direction.x -= 1
        if dirs['up']: direction.y -= 1
        if dirs['down']: direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos += direction * self.vel
        self.pos.x = max(0, min(width, self.pos.x))
        self.pos.y = max(0, min(height, self.pos.y))
        self.rect.center = self.pos


class Bullet:
    def __init__(self, x, y, angle, color=(255, 255, 255), radius=RADIUS, speed=BULLET_SPEED):
        self.pos = pygame.Vector2(x, y)
        self.angle = angle
        angle_rad = math.radians(self.angle) + math.pi
        self.vel = pygame.Vector2(-math.sin(angle_rad), math.cos(angle_rad)) * speed
        self.speed = speed
        self.radius = radius
        self.color = color
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

    def draw(self, win):
        pygame.draw.circle(win, self.color, self.pos, self.radius)

    def is_offscreen(self, width, height):
        return (
            self.pos.x < 0 or self.pos.x > width or 
            self.pos.y < 0 or self.pos.y > height
        )

class Enemy:
    def __init__(self, x, y, speed, health, img):
        self.pos = pygame.Vector2(x, y)
        self.speed = speed
        self.health = health
        self.img = img
        self.rect = self.img.get_rect(center=self.pos)
        self.angle = 90
        self.rotation_speed = 0.1

    def update(self, player_pos):
        direction = (player_pos - self.pos)
        player_angle = direction.angle_to(pygame.Vector2(1, 0))
        self.angle = lerp(self.angle, -player_angle, self.rotation_speed)

        if direction.length_squared() != 0:
            direction = direction.normalize()

        self.pos += direction * self.speed
        self.rect.center = self.pos

    def draw(self, win):
        rotated = pygame.transform.rotate(self.img, -(self.angle + 90))
        self.rect = rotated.get_rect(center=self.pos)
        win.blit(rotated, self.rect.topleft)

    def is_dead(self):
        return self.health <= 0


class Bug(Enemy):
    img = None

    def __init__(self, x, y):
        if Bug.img is None:
            Bug.img = pygame.transform.scale(pygame.image.load('assets/enemies/bug.png').convert_alpha(), (32, 32))

        super().__init__(x, y, speed=1.4, health=1, img=Bug.img)


class Virus(Enemy):
    img = None

    def __init__(self, x, y):
        if Virus.img is None:
            Virus.img = pygame.image.load('assets/enemies/virus.png').convert_alpha()

        super().__init__(x, y, speed=1.7, health=1, img=Virus.img)
        self.anim_time = 0

    def draw(self, win):
        transformed = pygame.transform.scale_by(self.img, max(abs(math.sin(self.anim_time) * 1.5), 1.0)).convert_alpha()
        self.rect = transformed.get_rect(center=self.pos)
        win.blit(transformed, self.rect.topleft)

    def update(self, player_pos):
        self.anim_time += 0.015
        direction = (player_pos - self.pos)

        if direction.length_squared() != 0:
            direction = direction.normalize()

        self.pos += direction * self.speed
        self.rect.center = self.pos


class Trojan(Enemy):
    img = None

    def __init__(self, x, y):
        if Trojan.img is None:
            Trojan.img = pygame.transform.scale(pygame.image.load('assets/enemies/trojan.png'), (60, 64)).convert_alpha()

        img = pygame.transform.flip(Trojan.img, True, False) if random.randint(1, 10) % 2 == 0 else Trojan.img
        super().__init__(x, y, speed=1.2, health=2, img=img)
        self.bullets = []
        self.shoot_time = 120
        self.timer = 0

    def update(self, player_pos):
        super().update(player_pos)

        self.timer += 1
        if self.timer >= self.shoot_time:
            self.shoot()
            self.timer = 0

        for bullet in self.bullets:
            bullet.update()

        self.bullets = [b for b in self.bullets if not b.is_offscreen(WIDTH, HEIGHT)]

    def draw(self, win):
        super().draw(win)
        for bullet in self.bullets:
            bullet.draw(win)

    def shoot(self):
        self.bullets.append(Bullet(*self.pos, (self.angle + 90), (255, 0, 0), speed=8))

    def check_bullet_collisions(self, target_rect):
        hits = 0
        for bullet in self.bullets[:]:
            if bullet.rect.colliderect(target_rect):
                self.bullets.remove(bullet)
                hits += 1
        return hits


class Corruptor(Enemy):
    img = None

    def __init__(self, x, y):
        if Corruptor.img is None:
            Corruptor.img = pygame.transform.scale2x(pygame.image.load('assets/icons/folder.png')).convert_alpha()

        super().__init__(x, y, speed=1.0, health=2, img=Corruptor.img)
        self.base_img = Corruptor.img
        self.target = pygame.Vector2(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.phase = "moving"
        self.timer = 120
        self.scale = 1.0

    def update(self, game):
        if self.phase == "moving":
            direction = self.target - self.pos
            if direction.length_squared() < 4:
                self.phase = "waiting"
            else:
                self.pos += direction.normalize() * self.speed
                self.rect.center = self.pos

        elif self.phase == "waiting":
            self.timer -= 1
            self.scale = lerp(self.scale, 1.5, 0.08)

            if self.timer <= 0:
                game.hazards.append(CorruptionZone(self.pos.x, self.pos.y))
                self.health = 0
    
    def draw(self, win):
        scaled_img = pygame.transform.scale_by(self.base_img, self.scale).convert_alpha()
        scaled_rect = scaled_img.get_rect(center=self.pos)
        win.blit(scaled_img, scaled_rect.topleft)


class CorruptionZone:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.img = pygame.transform.scale_by(pygame.image.load(
            random.choice(['assets/enemies/glitch1.png', 'assets/enemies/glitch2.png'])), 1.5).convert_alpha()
        self.rect = self.img.get_rect(center=self.pos)
        self.lifetimer = 400
        self.alive = True
        self.damage_timer = 30

    def update(self, player):
        self.lifetimer -= 1
        
        if self.rect.colliderect(player.rect):
            self.damage_timer -= 1

            if self.damage_timer <= 0:
                self.damage_timer = 30
                
                return True
        
        else:
            self.damage_timer = 30

        if self.lifetimer <= 0:
            self.alive = False

        return False
    
    def draw(self, win):
        win.blit(self.img, self.rect.topleft)


pygame.quit()
