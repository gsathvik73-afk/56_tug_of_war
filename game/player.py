import pygame


class Puller:
    """A puller whose upper body leans in the direction of their pull."""

    def __init__(self, x, y, color, label):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.font = pygame.font.SysFont(None, 24)

    def render(self, surface, lean=0):
        lean = max(-18, min(18, lean))
        shoulder_x = int(self.x + lean)
        body = [
            (self.x - 20, self.y + 30), (self.x + 20, self.y + 30),
            (shoulder_x + 20, self.y - 34), (shoulder_x - 20, self.y - 34),
        ]
        pygame.draw.polygon(surface, self.color, body)
        pygame.draw.circle(surface, (240, 210, 180), (shoulder_x, self.y - 50), 16)
        hand_x = self.x + (30 if self.x < surface.get_width() // 2 else -30)
        pygame.draw.line(surface, (240, 210, 180),
                         (shoulder_x, self.y - 17), (hand_x, self.y), 7)
        label = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label, (self.x - label.get_width() // 2, self.y + 45))
