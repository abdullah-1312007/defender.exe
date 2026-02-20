import pygame
from entities import *
from ui import *
from constants import WIDTH, HEIGHT, SENS, lines, FPS, COLORS
from waves import WaveManager


class Game:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.win = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)
        pygame.display.set_caption("defender.exe")
        self.clock = pygame.time.Clock()

        self.icons = {
            'pc': pygame.transform.scale(pygame.image.load('assets/icons/pc.png'), (48, 48)).convert_alpha(),
            'bin': pygame.transform.scale(pygame.image.load('assets/icons/bin.png'), (48, 48)).convert_alpha(),
            'folder': pygame.transform.scale(pygame.image.load('assets/icons/folder1.png'), (48, 48)).convert_alpha(),
            'folder2': pygame.transform.scale(pygame.image.load('assets/icons/folder2.png'), (48, 48)).convert_alpha(),
            'file': pygame.transform.scale(pygame.image.load('assets/icons/file.png'), (42, 56)).convert_alpha(),
        }
        self.desk_font = pygame.font.Font('assets/fonts/Perfect DOS VGA 437 Win.ttf', 16)
        self.end_font = pygame.font.Font('assets/fonts/Perfect DOS VGA 437 Win.ttf', 18)
        self.texts = [
            self.desk_font.render("My Computer", False, (255, 255, 255)),
            self.desk_font.render("Recycle Bin", False, (255, 255, 255)),
            self.desk_font.render("Documents", False, (255, 255, 255)),
            self.desk_font.render("Important", False, (255, 255, 255)),
            self.desk_font.render("passwords", False, (255, 255, 255))
        ]
        self.bsod_lines = [self.end_font.render(line, True, (255, 255, 255)) for line in lines]
        self.overlay = pygame.Surface((WIDTH, HEIGHT - 50), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128))
        self.taskbar = Taskbar(WIDTH, HEIGHT)
        self.paused = False
        self.state = "menu"

        self.player = Player(450, 450)
        self.lives = 5
        self.killed = 0
        self.keys = {'right': False, 'left': False, 'up': False, 'down': False, 'rotate_right': False, 'rotate_left': False}
        self.enemies = []
        self.hazards = []
        self.bullets = []
        self.powerups = []
        self.bullet_amount = 5
        self.damage_flash = 10
        
        self.wave_manager = WaveManager()
        self.wave_manager.spawn_wave(self)

    def check_collision(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= 1
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.killed += 1
                        self.bullet_amount += random.randint(0, 3)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
        

    def draw(self):
        self.win.fill(COLORS['bg'])
        self.taskbar.draw(self)
        draw_icons(self)

        for bullet in self.bullets[:]:
            bullet.draw(self.win)

        for hazard in self.hazards[:]:
            hazard.draw(self.win)

        for enemy in self.enemies[:]:
            enemy.draw(self.win)

        for powerup in self.powerups[:]:
            powerup.draw(self.win)

        self.player.draw(self.win)

        if self.damage_flash > 0:
            red_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, self.damage_flash))
            self.win.blit(red_overlay, (0, 0))
            self.damage_flash -= 1

    def update(self):
        self.check_collision()
        self.player.move(self.keys, WIDTH, HEIGHT)
        self.wave_manager.update(self)

        for enemy in self.enemies[:]:
            if isinstance(enemy, Corruptor):
                enemy.update(self)
            else:
                enemy.update(self.player.pos)
            if enemy.rect.colliderect(self.player.rect):
                self.lives = max(0, self.lives - 1)
                enemy.health = 0
                self.enemies.remove(enemy)

            if isinstance(enemy, Trojan):
                self.lives = max(0, self.lives - enemy.check_bullet_collisions(self.player.rect))

            self.enemies = [e for e in self.enemies if not e.is_dead()]

        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_offscreen(WIDTH, HEIGHT):
                self.bullets.remove(bullet)

        max_glow = 0

        for hazard in self.hazards[:]:
            damage, glow_alpha = hazard.update(self.player)

            if damage:
                self.lives = max(0, self.lives - 1)

            if glow_alpha > max_glow:
                max_glow = glow_alpha

        self.damage_flash = max_glow

        self.hazards = [h for h in self.hazards if h.alive]

        for powerup in self.powerups[:]:
            if powerup.rect.colliderect(self.player.rect):
                powerup.apply(self)
                self.powerups.clear()
        

    def run(self):
        run = True
        show_bsod = False

        while run:
            self.clock.tick(FPS)

            if not self.paused and self.lives > 0:
                rel_x, _ = pygame.mouse.get_rel()
                self.player.angle += rel_x * SENS

                mx, _ = pygame.mouse.get_pos()
                if abs(mx - WIDTH // 2) > 100:
                    pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
                    pygame.mouse.get_rel()

                if self.keys['rotate_right']:
                    self.player.angle += 10 * SENS
                if self.keys['rotate_left']:
                    self.player.angle -= 10 * SENS

            for event in pygame.event.get():
                self.taskbar.handle_event(event)

                if event.type == pygame.QUIT:
                    run = False

                if self.state == "menu":
                    handle_menu_events(self, event)
                
                elif self.state == "playing":

                    if event.type == pygame.KEYDOWN:
                        if self.lives <= 0 or self.bullet_amount <= 0:
                            if event.key == pygame.K_ESCAPE:
                                run = False
                            else:
                                self.__init__()
                                self.state = "playing"
                                pygame.mouse.set_visible(False)
                                pygame.event.set_grab(True)
                                pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
                                pygame.mouse.get_rel()
                                continue

                        if event.key == pygame.K_d: self.keys['right'] = True
                        if event.key == pygame.K_a: self.keys['left'] = True
                        if event.key == pygame.K_w: self.keys['up'] = True
                        if event.key == pygame.K_s: self.keys['down'] = True
                        if event.key == pygame.K_RIGHT: self.keys['rotate_right'] = True
                        if event.key == pygame.K_LEFT: self.keys['rotate_left'] = True
                        if event.key == pygame.K_ESCAPE: run = False
                        if event.key == pygame.K_r: self.enemies.append(Corruptor(random.randint(0, WIDTH), -20))
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                            pygame.mouse.set_visible(self.paused)
                            pygame.event.set_grab(not self.paused)

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_d: self.keys['right'] = False
                        if event.key == pygame.K_a: self.keys['left'] = False
                        if event.key == pygame.K_w: self.keys['up'] = False
                        if event.key == pygame.K_s: self.keys['down'] = False
                        if event.key == pygame.K_RIGHT: self.keys['rotate_right'] = False
                        if event.key == pygame.K_LEFT: self.keys['rotate_left'] = False

                    if (event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)) and not self.paused and self.lives > 0 and self.bullet_amount > 0:
                        self.bullets.append(Bullet(*self.player.pos, self.player.angle))
                        self.bullet_amount -= 1


            if self.state == "menu":
                draw_main_menu(self)

            elif self.state == "playing":

                if self.lives > 0 and self.bullet_amount > 0:
                    if not self.paused:
                        self.update()
                    self.draw()
                    if self.paused:
                        draw_pause_overlay(self)
                else:
                    if not show_bsod:
                        pygame.time.delay(300)
                        show_bsod = True
                    draw_bsod(self)

            pygame.display.update()

        pygame.quit()
