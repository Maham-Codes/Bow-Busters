import pygame
from src.window import Window
from src.game import Game
from src.defence import Defence
from src.enemy import Enemy

pygame.init()

# Create minimal game environment
window = Window(1280, 720)
game = Game(window)

print("\n========== RUNNING AUTOMATED TEST CASES ==========\n")


# ---------------------------------------------------
# TEST CASE 1 — A* Pathfinding Completes Successfully
# ---------------------------------------------------
def test_pathfinding_basic():
    pf = game.level.pathfinding

    # Run enough update cycles for A* to finish generating
    for _ in range(500):
        pf.update()

    path = pf.get_path()

    assert path.done, "Pathfinding failed: path did not complete after update calls"
    assert path.points is not None, "Pathfinding failed: no points returned"

    # Path should reach destination (x < 0)
    assert path.points[-1][0] < 0, "Path does not reach the goal"

    # Path should never pass through blocked tiles
    for (x, y) in path.points:
        assert not game.level.collision.point_blocked(x, y), f"Blocked tile found in path at ({x},{y})"

    print("✓ Test Case 1 Passed — Valid A* Path Generated")

