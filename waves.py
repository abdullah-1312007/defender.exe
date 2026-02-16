import random
from constants import WIDTH, WAVE_WAIT_TIME, ENEMY_WAIT_TIME
from entities import Bug, Virus, Trojan, Corruptor

class WaveManager:
    def __init__(self):
        self.wave = 1
        self.timer = 0
        self.waiting = False
        self.spawn_timer = 0
        self.spawn_delay = ENEMY_WAIT_TIME
        
        self.spawned = 0
        self.count = 5

        self.weights = {
            1: {"bug": 10, "corruptor": 90},
            2: {"corruptor": 70, "virus": 30},
            3: {"bug": 50, "virus": 50},
            5: {"bug": 40, "virus": 40, "trojan": 20},
            7: {"bug": 20, "virus": 40, "trojan": 40},
            10: {"virus": 40, "trojan": 60}
        }
        self.types = []
        self.chances = []

    def update(self, game):
        if not game.enemies and self.spawned >= self.count and not self.waiting:
            self.waiting = True
            self.timer = WAVE_WAIT_TIME

        if self.waiting:
            self.timer -= 1
            if self.timer <= 0:
                self.wave += 1
                self.spawn_wave(game)
                self.waiting = False

        if self.spawned < self.count:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.spawn_enemy(game)
                self.spawned += 1
                self.spawn_timer = self.spawn_delay

    def get_weights(self):
        weight = sorted([w for w in self.weights if w <= self.wave])[-1]
        return self.weights[weight]

    def spawn_wave(self, game):
        weight = self.get_weights()
        self.types = list(weight.keys())
        self.chances = list(weight.values())

        self.count = int(5 + self.wave * 1.5)
        self.spawned = 0
        self.spawn_timer = 0

    def spawn_enemy(self, game):
        enemy = random.choices(self.types, self.chances)[0]
        x, y = random.randint(0, WIDTH), -20

        if enemy == "bug":
            game.enemies.append(Bug(x, y))
        elif enemy == "virus":
            game.enemies.append(Virus(x, y))
        elif enemy == "trojan":
            game.enemies.append(Trojan(x, y))
        elif enemy == "corruptor":
            game.enemies.append(Corruptor(x, y))
