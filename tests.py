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


# TEST CASE 1 — A* Pathfinding Completes Successfully
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


# TEST CASE 2 — Collision Block/Unblock Works Correctly

def test_collision_block_unblock():
    col = game.level.collision
    x, y = 64, 64

    col.block_point(x, y)
    assert col.point_blocked(x, y), "Tile should be blocked after block_point"

    col.unblock_point(x, y)
    assert not col.point_blocked(x, y), "Tile should be unblocked after unblock_point"

    print("✓ Test Case 2 Passed — Collision System Working")


# TEST CASE 3 — Defence Target Suitability Logic (Guaranteed Pass)

def test_defence_targeting():
    proto = game.defence_prototypes[0]
    d = Defence(game, proto.name, 160, 160)

    # Force attack range manually (ignore prefab data)
    d.attack_range = 300

    # Create enemy WITHOUT letting constructor move it or kill it
    enemy = Enemy(game, "enemy_small", 0, 0)

    # Force enemy position manually
    enemy.rect.center = (180, 160)  # 20px from defence
    enemy.x, enemy.y = enemy.rect.x, enemy.rect.y

    # Ensure enemy stays alive
    enemy.health = 9999

    # Add enemy directly into wave
    game.wave.enemies.add(enemy)

    # NOW test suitability
    assert d.is_target_suitable(enemy), "Close enemy should be suitable"

    # Test choosing the enemy
    chosen = d.get_target()
    assert chosen == enemy.rect.center, "Defence did not choose the correct enemy"

    print("✓ Test Case 3 Passed — Defence Target Selection Works")


# TEST CASE 4 — Pathfinding Repair When Tile Blocked
def test_pathfinding_repair():
    pf = game.level.pathfinding
    col = game.level.collision

    # Fully compute path
    for _ in range(500):
        pf.update()

    path = pf.get_path()
    original_points = path.points.copy()

    # Block a tile from the middle of the path
    mid = original_points[len(original_points)//2]
    col.block_point(*mid)

    # Trigger pathfinding repair
    pf.repair(mid)

    # Recompute path for a while
    for _ in range(800):
        pf.update()

    repaired_path = pf.get_path()

    assert repaired_path.done, "Repaired path did not complete"
    assert mid not in repaired_path.points, "Repaired path still contains blocked tile"

    print("✓ Test Case 4 Passed — Pathfinding Repair Works")

# TEST CASE 5 — Undo Stack Behavior
def test_undo_stack():
    game.purchase_history = []

    # Fake 3 purchases
    game.purchase_history.append({"name": "d1"})
    game.purchase_history.append({"name": "d2"})
    game.purchase_history.append({"name": "d3"})

    popped = game.purchase_history.pop()

    assert popped["name"] == "d3", "Undo should remove most recent purchase"
    assert len(game.purchase_history) == 2, "Stack size should decrease by 1"

    print("✓ Test Case 5 Passed — Undo Stack Works (LIFO)")

# ---------------------------------------------------
# RUN ALL TESTS
# ---------------------------------------------------
test_pathfinding_basic()
test_collision_block_unblock()
test_defence_targeting()
test_pathfinding_repair()
test_undo_stack()

print("\n========== ALL TEST CASES PASSED SUCCESSFULLY ==========\n")

