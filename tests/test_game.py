import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.game_engine import GameEngine


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((800, 450))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.now = 0
        self.ticks = patch.object(pygame.time, "get_ticks", side_effect=lambda: self.now)
        self.ticks.start()
        self.addCleanup(self.ticks.stop)
        self.game = GameEngine(800, 450)

    def key(self, kind, key):
        self.game.handle_event(pygame.event.Event(kind, key=key))

    def test_overlapping_alternation_counts_both_presses(self):
        self.key(pygame.KEYDOWN, pygame.K_a)
        self.key(pygame.KEYDOWN, pygame.K_d)
        self.assertEqual(self.game.rope.marker_x, 376)
        self.key(pygame.KEYUP, pygame.K_a)
        self.key(pygame.KEYUP, pygame.K_d)
        self.key(pygame.KEYDOWN, pygame.K_a)
        self.assertEqual(self.game.rope.marker_x, 364)

    def test_key_repeat_does_not_add_pulls(self):
        self.key(pygame.KEYDOWN, pygame.K_a)
        self.key(pygame.KEYDOWN, pygame.K_a)
        self.key(pygame.KEYUP, pygame.K_a)
        self.key(pygame.KEYDOWN, pygame.K_a)
        self.assertEqual(self.game.rope.marker_x, 388)

    def test_panic_surge_accelerates_computer(self):
        self.game.rope.marker_x = self.game.surge_threshold - 1
        self.now = 100
        with patch("game.game_engine.random.uniform", return_value=1.0):
            self.game.update()
        self.assertEqual(self.game.computer_pull_cooldown, 95)
        self.assertEqual(self.game.rope.marker_x, self.game.surge_threshold - 1 + 15)

    def test_sudden_death_doubles_both_sides_and_reset_clears_state(self):
        self.now = 45_000
        self.key(pygame.KEYDOWN, pygame.K_a)
        self.assertTrue(self.game.sudden_death)
        self.assertEqual(self.game.rope.marker_x, 376)
        with patch("game.game_engine.random.uniform", return_value=1.0):
            self.game.update()
        self.assertEqual(self.game.rope.marker_x, 400)
        self.game.rope.marker_x = self.game.rope.left_win_x
        self.game.update()
        self.assertEqual(self.game.winner, "PLAYER")
        self.key(pygame.KEYDOWN, pygame.K_r)
        self.assertEqual(self.game.rope.marker_x, 400)
        self.assertFalse(self.game.sudden_death)
        self.assertIsNone(self.game.last_key)
        self.assertEqual(self.game.held_keys, set())
        self.assertEqual(self.game.match_start, self.now)

    def test_render_draws_without_error(self):
        self.game.player_momentum = 1.0
        self.game.computer_momentum = 1.0
        self.game.render(self.screen)
        self.assertEqual(self.screen.get_size(), (800, 450))

    def test_player_win_is_immediate_at_boundary(self):
        self.game.rope.marker_x = self.game.rope.left_win_x + 10
        self.key(pygame.KEYDOWN, pygame.K_a)
        self.assertEqual(self.game.winner, "PLAYER")
        self.assertEqual(self.game.game_state, "GAME_OVER")


if __name__ == "__main__":
    unittest.main()
