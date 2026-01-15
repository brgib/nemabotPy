"""screen_movement.py

Worm world (movement sandbox).

Shows the "triangle worm" that moves based on motor neuron activity.
The user can place:
- Green circles = food (left click)
- Red squares   = obstacles (right click)

The module updates `sim.food` based on distance to food items and `sim.touch`
when the triangle collides with obstacles.
"""


import pygame
import math
import random

# Screen boundary (solid red frame)
FRAME_THICKNESS = 10

# Triangle collision radius (approximate)
TRIANGLE_RADIUS = 12


def draw(sim, surface, rect):
    init_world_if_needed(sim, rect)
    surface.fill(sim.BLACK)

    # Save previous position (used to prevent passing through walls/obstacles)
    if not hasattr(sim, '_prev_triangle_pos'):
        sim._prev_triangle_pos = (sim.triangle_pos[0], sim.triangle_pos[1])
    prev_pos = (sim.triangle_pos[0], sim.triangle_pos[1])

    # Keep the worm inside the visible arena (solid red frame)
    constrain_triangle_position(sim, rect)

    # Prevent the worm from entering any red obstacle: revert to previous position
    in_obstacle = False
    for obstacle in sim.obstacles:
        if pygame.Rect(obstacle).collidepoint(sim.triangle_pos):
            in_obstacle = True
            break
    if in_obstacle:
        # Restore previous position
        tp = sim.triangle_pos
        if hasattr(tp, 'x') and hasattr(tp, 'y'):
            tp.x, tp.y = prev_pos[0], prev_pos[1]
            sim.triangle_pos = tp
        elif isinstance(tp, list):
            tp[0], tp[1] = prev_pos[0], prev_pos[1]
            sim.triangle_pos = tp
        else:
            sim.triangle_pos = prev_pos

    sim._prev_triangle_pos = (sim.triangle_pos[0], sim.triangle_pos[1])

    # Draw arena and items
    draw_screen_frame(sim, surface, rect)
    draw_food_items(sim, surface, rect)
    draw_obstacles(sim, surface, rect)
    draw_triangle(sim, surface, rect)

    # Update sensors
    check_food_collision(sim)
    check_obstacle_collision(sim)

    # HUD
    sim.draw_text(surface, f"Food: {sim.food}", 10, 40)
    sim.draw_text(surface, f"Touch: {sim.touch}", 10, 70)
    sim.draw_text(surface, f"Iteration N°:{sim.iteration}", rect.width - 200, 10)

def handle_mouse_click(sim, pos, button):
    if button == 1:
        clicked_on_food = False
        for food_pos in list(sim.food_items):
            distance = math.hypot(pos[0] - food_pos[0], pos[1] - food_pos[1])
            if distance <= 10:
                sim.food_items.remove(food_pos); clicked_on_food = True; break
        if not clicked_on_food:
            sim.food_items.append((pos[0], pos[1]))
    elif button == 3:
        clicked_on_obstacle = False
        for obstacle in list(sim.obstacles):
            rect_obstacle = pygame.Rect(obstacle)
            if rect_obstacle.collidepoint(pos):
                sim.obstacles.remove(obstacle); clicked_on_obstacle = True; break
        if not clicked_on_obstacle:
            sim.obstacles.append((pos[0] - 25, pos[1] - 25, 50, 50))


def init_world_if_needed(sim, rect):
    """Initialize random obstacles and food only once (no overlaps)."""
    # Keep existing lists if another module already created them
    if not hasattr(sim, "food_items") or sim.food_items is None:
        sim.food_items = []
    if not hasattr(sim, "obstacles") or sim.obstacles is None:
        sim.obstacles = []

    if getattr(sim, "_world_initialized", False):
        return

    sim._world_initialized = True

    # Food detection timer (10 cycles after touching a green circle)
    if not hasattr(sim, 'food_timer'):
        sim.food_timer = 0

    # Random layout parameters
    rng = random.Random()  # fresh layout each app launch
    margin = FRAME_THICKNESS + 20
    arena_left = rect.left + margin
    arena_right = rect.right - margin
    arena_top = rect.top + margin
    arena_bottom = rect.bottom - margin

    FOOD_R = 10
    OBS_MIN = 40
    OBS_MAX = 90
    NUM_FOOD = 6
    NUM_OBS = 6

    def rects_overlap(r1, r2):
        return r1.colliderect(r2)

    def circle_overlaps_circle(c1, c2, extra=0):
        return math.hypot(c1[0]-c2[0], c1[1]-c2[1]) < (2*FOOD_R + extra)

    def circle_overlaps_rect(c, r, extra=0):
        # Inflate rect for safety distance
        rr = r.inflate(extra*2, extra*2)
        return rr.collidepoint(c)

    obstacles = []
    foods = []

    # Place obstacles
    for _ in range(NUM_OBS):
        placed = False
        for _attempt in range(200):
            w = rng.randint(OBS_MIN, OBS_MAX)
            h = rng.randint(OBS_MIN, OBS_MAX)
            x = rng.randint(arena_left, max(arena_left, arena_right - w))
            y = rng.randint(arena_top, max(arena_top, arena_bottom - h))
            r = pygame.Rect(x, y, w, h)
            if any(rects_overlap(r, pygame.Rect(o)) for o in obstacles):
                continue
            # Also keep some breathing room from the edges (frame)
            if x < arena_left or y < arena_top or x+w > arena_right or y+h > arena_bottom:
                continue
            obstacles.append((r.x, r.y, r.w, r.h))
            placed = True
            break
        if not placed:
            # If placement fails, just stop adding more
            break

    # Place food (avoid overlap with obstacles and other food)
    for _ in range(NUM_FOOD):
        placed = False
        for _attempt in range(300):
            x = rng.randint(arena_left, arena_right)
            y = rng.randint(arena_top, arena_bottom)
            c = (x, y)
            if any(circle_overlaps_circle(c, f, extra=10) for f in foods):
                continue
            if any(circle_overlaps_rect(c, pygame.Rect(o), extra=FOOD_R+10) for o in obstacles):
                continue
            foods.append(c)
            placed = True
            break
        if not placed:
            break

    # Apply defaults if empty (still keep user-placed items if any were already present)
    if not sim.obstacles:
        sim.obstacles = obstacles
    if not sim.food_items:
        sim.food_items = foods

def draw_screen_frame(sim, surface, rect):
    """Draw a red frame (solid wall) around the arena."""
    pygame.draw.rect(surface, sim.colorsName['red'], rect, FRAME_THICKNESS)

def constrain_triangle_position(sim, rect):
    """Prevent the triangle from leaving the arena (without changing the type of triangle_pos)."""
    # triangle_pos can be a list [x, y], a pygame.Vector2, or a tuple (x, y).
    tp = sim.triangle_pos

    # Read x/y in a type-agnostic way
    if hasattr(tp, 'x') and hasattr(tp, 'y'):
        x, y = float(tp.x), float(tp.y)
    else:
        x, y = float(tp[0]), float(tp[1])

    min_x = rect.left + FRAME_THICKNESS + TRIANGLE_RADIUS
    max_x = rect.right - FRAME_THICKNESS - TRIANGLE_RADIUS
    min_y = rect.top + FRAME_THICKNESS + TRIANGLE_RADIUS
    max_y = rect.bottom - FRAME_THICKNESS - TRIANGLE_RADIUS

    x = max(min_x, min(x, max_x))
    y = max(min_y, min(y, max_y))

    # Write back while preserving the original container type
    if hasattr(tp, 'x') and hasattr(tp, 'y'):
        tp.x = x
        tp.y = y
        sim.triangle_pos = tp
    elif isinstance(tp, list):
        tp[0] = x
        tp[1] = y
        sim.triangle_pos = tp
    else:
        sim.triangle_pos = (x, y)

def draw_triangle(sim, surface, rect):
    angle_radians = math.radians(sim.triangle_angle)
    size = 20
    p1 = (sim.triangle_pos[0] + size * math.cos(angle_radians),
          sim.triangle_pos[1] + size * math.sin(angle_radians))
    p2 = (sim.triangle_pos[0] + size * math.cos(angle_radians + 2.5),
          sim.triangle_pos[1] + size * math.sin(angle_radians + 2.5))
    p3 = (sim.triangle_pos[0] + size * math.cos(angle_radians - 2.5),
          sim.triangle_pos[1] + size * math.sin(angle_radians - 2.5))
    pygame.draw.polygon(surface, sim.colorsName['triangle'], [p1, p2, p3])

def draw_food_items(sim, surface, rect):
    for food_pos in sim.food_items:
        pygame.draw.circle(surface, sim.colorsName['green'], food_pos, 10)

def draw_obstacles(sim, surface, rect):
    for obstacle in sim.obstacles:
        rect_obstacle = pygame.Rect(obstacle)
        pygame.draw.rect(surface, sim.colorsName['red'], rect_obstacle)

def check_food_collision(sim):
    # Food detection: active for 10 cycles after touching any green circle
    # Decrement timer each frame (cycle)
    if getattr(sim, 'food_timer', 0) > 0:
        sim.food_timer -= 1
        sim.food = 20
        return

    sim.food = 0
    for food_pos in sim.food_items:
        distance = math.hypot(sim.triangle_pos[0] - food_pos[0], sim.triangle_pos[1] - food_pos[1])
        if distance < 20:
            sim.food_timer = 10
            sim.food = 20
            return
        elif distance < 100:
            sim.food = max(sim.food, int(100 - distance) // 5)
            sim.tfood = sim.food

def check_obstacle_collision(sim):
    # Touch is true if the worm's position is inside any obstacle block
    sim.touch = False
    for obstacle in sim.obstacles:
        if pygame.Rect(obstacle).collidepoint(sim.triangle_pos):
            sim.touch = True
            break

