import math

import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12
        self.reset()

    def pull_left(self, strength=1.0):
        self.marker_x -= round(self.pull_step * strength)

    def pull_right(self, strength=1.0):
        self.marker_x += round(self.pull_step * strength)

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"
        if self.marker_x >= self.right_win_x:
            return "COMPUTER"
        return None

    def reset(self):
        self.marker_x = float(self.screen_width // 2)

    def render(self, surface, tension=0.0, time_ms=0):
        # A pull straightens the sagging rope and briefly makes it vibrate.
        tension = max(0.0, min(1.0, tension))
        points = []
        left, right = 60, self.screen_width - 60
        phase = time_ms / 75.0
        for index in range(33):
            position = index / 32
            x = left + (right - left) * position
            envelope = math.sin(math.pi * position)
            sag = (10 - 7 * tension) * envelope
            vibration = 3 * tension * envelope * math.sin(5 * math.pi * position + phase)
            points.append((round(x), round(self.center_y + sag + vibration)))
        pygame.draw.lines(surface, (180, 140, 90), False, points, 10)

        pygame.draw.line(surface, (50, 200, 50),
                         (self.left_win_x, self.center_y - 40),
                         (self.left_win_x, self.center_y + 40), 4)
        pygame.draw.line(surface, (200, 50, 50),
                         (self.right_win_x, self.center_y - 40),
                         (self.right_win_x, self.center_y + 40), 4)
        pygame.draw.line(surface, (120, 120, 120),
                         (self.screen_width // 2, self.center_y - 20),
                         (self.screen_width // 2, self.center_y + 20), 2)
        flag = pygame.Rect(round(self.marker_x) - 12, self.center_y - 24, 24, 48)
        pygame.draw.rect(surface, (230, 40, 40), flag, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), flag, width=2, border_radius=4)
