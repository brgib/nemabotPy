# Auto-generated Nemabot multi-file package (with requested fixes).


import pygame
import math

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    draw_triangle(sim, surface, rect)
    draw_food_items(sim, surface, rect)
    draw_obstacles(sim, surface, rect)
    check_food_collision(sim)
    check_obstacle_collision(sim)

    sim.draw_text(surface, f"Food: {sim.food}", 10, 40)
    sim.draw_text(surface, f"Touch: {sim.touch}", 10, 70)
    sim.draw_text(surface, f"Iteration N°:{sim.iteration}", rect.width - 200, 10)

def handle_mouse_click(sim, pos, button):
    rect = sim.screen.get_rect()
    if button == 1:
        clicked_on_food = False
        for food_pos in list(sim.food_items):
            distance = math.hypot(pos[0] - food_pos[0], pos[1] - food_pos[1])
            if distance <= 10:
                sim.food_items.remove(food_pos)
                clicked_on_food = True
                break
        if not clicked_on_food:
            sim.food_items.append((pos[0], pos[1]))
    elif button == 3:
        clicked_on_obstacle = False
        for obstacle in list(sim.obstacles):
            rect_obstacle = pygame.Rect(obstacle)
            if rect_obstacle.collidepoint(pos):
                sim.obstacles.remove(obstacle)
                clicked_on_obstacle = True
                break
        if not clicked_on_obstacle:
            sim.obstacles.append((pos[0] - 25, pos[1] - 25, 50, 50))

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
    sim.food = 0
    for food_pos in sim.food_items:
        distance = math.hypot(sim.triangle_pos[0] - food_pos[0], sim.triangle_pos[1] - food_pos[1])
        if distance < 20:
            sim.food = 20
        elif distance < 100:
            sim.food = max(sim.food, int(100 - distance) // 5)
            sim.tfood = sim.food

def check_obstacle_collision(sim):
    sim.touch = False
    for obstacle in sim.obstacles:
        if pygame.Rect(obstacle).collidepoint(sim.triangle_pos):
            sim.touch = True
            break
