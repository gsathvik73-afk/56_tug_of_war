import random

import pygame

from game.player import Puller
from game.rope import Rope


class GameEngine:
    MATCH_LENGTH_MS = 45_000
    NORMAL_COMPUTER_COOLDOWN_MS = 180
    SURGE_COMPUTER_COOLDOWN_MS = 95

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)")
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER")
        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)
        self.reset()

    @property
    def surge_threshold(self):
        return self.rope.left_win_x + 0.40 * (self.width // 2 - self.rope.left_win_x)

    @property
    def panic_surge(self):
        return self.rope.marker_x <= self.surge_threshold

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYUP and event.key in (pygame.K_a, pygame.K_d):
            self.held_keys.discard(event.key)
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_a, pygame.K_d):
            # An overlapping press is valid; only a repeated press of a held key is ignored.
            if event.key in self.held_keys:
                return
            self.held_keys.add(event.key)
            if event.key != self.last_key:
                self.sudden_death = (pygame.time.get_ticks() - self.match_start
                                     >= self.MATCH_LENGTH_MS)
                self.rope.pull_left(2.0 if self.sudden_death else 1.0)
                self.last_key = event.key
                self.player_momentum = 1.0
                if self.rope.check_winner() == "PLAYER":
                    self.winner = "PLAYER"
                    self.game_state = "GAME_OVER"

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        elapsed = max(0, now - self.last_update)
        self.last_update = now
        decay = max(0.0, 1.0 - elapsed / 450.0)
        self.player_momentum *= decay
        self.computer_momentum *= decay

        self.sudden_death = now - self.match_start >= self.MATCH_LENGTH_MS
        self.computer_pull_cooldown = (self.SURGE_COMPUTER_COOLDOWN_MS
                                       if self.panic_surge else self.NORMAL_COMPUTER_COOLDOWN_MS)
        if now - self.last_computer_pull >= self.computer_pull_cooldown:
            strength = random.uniform(0.7, 1.2)
            if self.panic_surge:
                strength *= 1.25
            if self.sudden_death:
                strength *= 2.0
            self.rope.pull_right(strength)
            self.computer_momentum = 1.0
            self.last_computer_pull = now

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def reset(self):
        self.rope.reset()
        self.last_key = None
        self.held_keys = set()
        self.winner = None
        self.game_state = "PLAYING"
        self.sudden_death = False
        self.player_momentum = 0.0
        self.computer_momentum = 0.0
        now = pygame.time.get_ticks()
        self.match_start = now
        self.last_update = now
        self.last_computer_pull = now
        self.computer_pull_cooldown = self.NORMAL_COMPUTER_COOLDOWN_MS

    def render(self, screen):
        screen.fill((30, 32, 36))
        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        now = pygame.time.get_ticks()
        self.rope.render(screen, tension=max(self.player_momentum, self.computer_momentum), time_ms=now)
        self.player.render(screen, lean=-15 * self.player_momentum)
        self.computer.render(screen, lean=15 * self.computer_momentum)

        instruction = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(instruction, (self.width // 2 - instruction.get_width() // 2, 40))

        elapsed_seconds = max(0, (now - self.match_start) // 1000)
        timer = self.font_small.render(f"Time {elapsed_seconds:02d}s / 45s", True, (240, 240, 240))
        screen.blit(timer, (16, 13))
        if self.sudden_death:
            mode = self.font_small.render("SUDDEN DEATH  x2 pulls", True, (255, 200, 75))
            screen.blit(mode, (self.width - mode.get_width() - 16, 13))
        elif self.panic_surge:
            mode = self.font_small.render("COMPUTER PANIC SURGE", True, (255, 160, 100))
            screen.blit(mode, (self.width - mode.get_width() - 16, 13))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            color = (80, 220, 80) if self.winner == "PLAYER" else (240, 80, 80)
            title = self.font_big.render(f"{self.winner} WINS!", True, color)
            screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 50))
            restart = self.font_small.render("Press [R] to Play Again", True, (240, 240, 240))
            screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 10))
