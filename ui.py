import pygame
from constants import WIDTH, HEIGHT, COLORS


class Taskbar:
    def __init__(self, screen_width, screen_height):
        self.width = screen_height
        self.height = 50
        self.rect = pygame.Rect(0, screen_height - self.height, screen_width, self.height)
        self.icons = {
            'start': pygame.transform.scale(pygame.image.load('assets/ui/start.png'), (83, 33)).convert_alpha(),
            'bullet': pygame.transform.scale(pygame.image.load('assets/icons/bullet.png'), (12, 27)).convert_alpha(),
            'skull': pygame.image.load('assets/icons/skull.png').convert_alpha(),
            'bell': pygame.image.load('assets/icons/bell.png').convert_alpha(),
            'mute': pygame.image.load('assets/icons/bell_mute.png').convert_alpha(),
            'bar': pygame.image.load('assets/ui/volume_bar.png').convert_alpha(),
            'button': pygame.image.load('assets/ui/volume_button.png').convert_alpha()
        }

        self.slider_width = 100
        self.slider_height = 4
        self.slider_x = 890
        self.slider_y = 746
        
        self.volume = 0.6
        self.last_volume = self.volume
        self.muted = False
        self.dragging = False

        self.button_rect = self.icons['button'].get_rect()
        self._update_position()

    def _toggle_mute(self):
        if not self.muted:
           self.last_volume = self.volume
           self.volume = 0
        else:
           self.volume = self.last_volume
        self.muted = not self.muted
        self._update_position()

    def _update_position(self):
        clamped_volume = max(0, min(self.volume, 1))
        x = self.slider_x + clamped_volume * self.slider_width - self.button_rect.width // 2
        y = self.slider_y - 8
        self.button_rect.topleft = (x, y)

    def draw(self, game):
        pygame.draw.rect(game.win, (192, 192, 192), self.rect)

        game.win.blit(self.icons['start'], (15, 727))

        cycle_text = game.end_font.render('Scan Cycle: ' + str(game.wave_manager.wave), True, (0, 0, 0))
        game.win.blit(cycle_text, (140, 735))

        bullet_text = game.end_font.render(': ' + str(game.bullet_amount), True, (0, 0, 0))
        game.win.blit(self.icons['bullet'], (578, 733))
        game.win.blit(bullet_text, (600, 740))

        threat_text = game.end_font.render(': ' + str(game.killed), True, (0, 0, 0))
        game.win.blit(self.icons['skull'], (700, 735))
        game.win.blit(threat_text, (730, 740))

        if self.volume > 0:
            game.win.blit(self.icons['bell'], (840, 735))
        else:
            game.win.blit(self.icons['mute'], (840, 735))
        game.win.blit(self.icons['bar'], (self.slider_x, self.slider_y))
        game.win.blit(self.icons['button'], self.button_rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.dragging = True
            elif pygame.Rect(840, 735, 20, 24).collidepoint(event.pos):
                self._toggle_mute()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                x = max(self.slider_x, min(event.pos[0], self.slider_x + self.slider_width))
                self.volume = (x - self.slider_x) / self.slider_width
                if self.volume > 0:
                    self.last_volume = self.volume
                self.muted = False
                self._update_position()


def draw_icons(self):
        if self.lives >= 1:
            self.win.blit(self.texts[0], (15, 90))
            self.win.blit(self.icons['pc'], (40, 30))
        if self.lives >= 2:
            self.win.blit(self.texts[1], (18, 186))
            self.win.blit(self.icons['bin'], (40, 126))
        if self.lives >= 3:
            self.win.blit(self.texts[2], (25, 282))
            self.win.blit(self.icons['folder'], (40, 222))
        if self.lives >= 4:
            self.win.blit(self.texts[3], (24, 378))
            self.win.blit(self.icons['folder2'], (40, 318))
        if self.lives >= 5:
            self.win.blit(self.texts[4], (21, 480))
            self.win.blit(self.icons['file'], (40, 420))

def draw_bsod(self):
    self.win.fill(COLORS['bsod'])
    line_height = 30
    for i, rendered in enumerate(self.bsod_lines):
        text_rect = rendered.get_rect(center=(WIDTH // 2, 200 + i * line_height))
        self.win.blit(rendered, text_rect)

def draw_pause_overlay(self): 
    pause_text = self.end_font.render("Paused - Press P to Resume", True, (255, 255, 255))
    text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    self.win.blit(self.overlay, (0, 0))
    self.win.blit(pause_text, text_rect)


def draw_main_menu(self):
    self.win.fill((0, 0, 0))

    title_font = pygame.font.Font('assets/fonts/Perfect DOS VGA 437 Win.ttf', 32)
    title_text = title_font.render("INSERT FLOPPY TO START_", True, (0, 255, 0))

    self.win.blit(title_text, (WIDTH // 2 - title_text.get_width()//2, HEIGHT // 2 - 50))


def handle_menu_events(self, event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        self.state = "playing"
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
        pygame.mouse.get_rel()
