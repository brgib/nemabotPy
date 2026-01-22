"""screen_worm.py

Worm schematic screen.

Renders a simplified worm representation in two views:
- Profile view (segment length scaling indicates contraction)
- Top view (polyline indicates curvature along the body)

The segment state is updated by `Simulator.update_worm_movement()`.
"""

import math
import pygame

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    half_height = rect.height // 2
    profile_rect = pygame.Rect(0, 0, rect.width, half_height)
    top_rect = pygame.Rect(0, half_height, rect.width, rect.height - half_height)
    profile_surface = surface.subsurface(profile_rect)
    top_surface = surface.subsurface(top_rect)
    draw_worm_profile(sim, profile_surface, profile_surface.get_rect())
    draw_worm_top(sim, top_surface, top_surface.get_rect())

def draw_worm_profile(sim, surface, rect):
    surface.fill(sim.BLACK)
    if not hasattr(sim, 'muscle_segments'):
        sim.muscle_segments = [{"length_factor": 1.0, "curvature_offset": 0.0, "contraction": 0.0} for _ in range(17)]
    num_segments = len(sim.muscle_segments)
    total_length = rect.width * 0.9
    L_base = total_length / num_segments
    center_y = rect.centery
    segment_height = 40
    x = rect.left + (rect.width - total_length) / 2
    sim.draw_text(surface, "Vue de profil", rect.left + 10, rect.top + 10, sim.colorsName['green'], font_size=24)
    for segment in sim.muscle_segments:
        length_factor = segment["length_factor"]
        segment_length = L_base * length_factor
        contraction_intensity = (1 - length_factor) / (1 - 0.5)
        contraction_intensity = max(0, min(contraction_intensity, 1))
        color = (int(contraction_intensity * 255), int((1 - contraction_intensity) * 255), 0)
        segment_rect = pygame.Rect(int(x), int(center_y - segment_height/2), int(segment_length), segment_height)
        pygame.draw.rect(surface, color, segment_rect)
        pygame.draw.rect(surface, sim.WHITE, segment_rect, 2)
        x += segment_length


def draw_worm_top(sim, surface, rect):
    surface.fill(sim.BLACK)

    if not hasattr(sim, 'muscle_segments'):
        return

    num_segments = len(sim.muscle_segments)
    total_length = rect.width * 0.9
    L_base = total_length / num_segments

    x = rect.left + (rect.width - total_length) / 2
    y = rect.centery
    angle = 0.0  # angle cumulé du corps

    points = [(x, y)]

    for segment in sim.muscle_segments:
        # Longueur contractée (OK)
        seg_len = L_base * segment["length_factor"]

        # Courbure → angle (et non déplacement vertical)
        curvature = segment["curvature_offset"]
        angle += curvature * 0.002  # facteur d’échelle à ajuster

        # Cinématique correcte
        x += seg_len * math.cos(angle)
        y += seg_len * math.sin(angle)

        points.append((x, y))

    sim.draw_text(surface, "Vue du dessus", rect.left + 10, rect.top + 10,
                  sim.colorsName['green'], font_size=24)

    if len(points) > 1:
        pygame.draw.lines(surface, sim.colorsName['triangle'], False, points, 6)

    for p in points:
        pygame.draw.circle(surface, sim.WHITE, (int(p[0]), int(p[1])), 6)


def draw_worm_top_old(sim, surface, rect):
    surface.fill(sim.BLACK)
    if not hasattr(sim, 'muscle_segments'):
        sim.muscle_segments = [{"length_factor": 1.0, "curvature_offset": 0.0, "contraction": 0.0} for _ in range(17)]
    num_segments = len(sim.muscle_segments)
    total_length = rect.width * 0.9
    L_base = total_length / num_segments
    points = []
    x = rect.left + (rect.width - total_length) / 2
    y = rect.centery
    points.append((x, y))
    for segment in sim.muscle_segments:
        length_factor = segment["length_factor"]
        segment_length = L_base * length_factor
        curvature_offset = segment["curvature_offset"]
        x += segment_length
        new_y = y + curvature_offset
        points.append((x, new_y))
    sim.draw_text(surface, "Vue du dessus", rect.left + 10, rect.top + 10, sim.colorsName['green'], font_size=24)
    if len(points) > 1:
        pygame.draw.lines(surface, sim.colorsName['triangle'], False, points, 8)
    for p in points:
        pygame.draw.circle(surface, sim.WHITE, (int(p[0]), int(p[1])), 10)
