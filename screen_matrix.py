import math
import pygame
from connectome import postsynaptic

def _build_layout(rect, count):
    if count <= 0:
        return 1, 1, rect.width, rect.height
    grid_size = int(math.ceil(math.sqrt(count)))
    cell_width = rect.width / grid_size
    cell_height = rect.height / grid_size
    return grid_size, grid_size, cell_width, cell_height

def _cell_center(index, grid_size, cell_width, cell_height):
    row = index // grid_size
    col = index % grid_size
    return int(col * cell_width + cell_width / 2), int(row * cell_height + cell_height / 2)

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    neuron_names = list(postsynaptic.keys())
    if not neuron_names:
        sim.draw_text(surface, 'Aucun neurone.', 10, 10)
        return

    grid_size, _, cell_width, cell_height = _build_layout(rect, len(neuron_names))
    threshold = float(getattr(sim, 'threshold', 30))
    max_radius = max(6, int(min(cell_width, cell_height) * 0.33))
    min_radius = max(4, int(max_radius * 0.42))
    sim.matrix_hitboxes = []

    for idx, neuron_name in enumerate(neuron_names):
        cx, cy = _cell_center(idx, grid_size, cell_width, cell_height)
        state = postsynaptic[neuron_name]
        current_value = float(state[getattr(sim, 'thisState', 0)])
        previous_value = float(state[getattr(sim, 'PreviousValue', 2)])

        fired = current_value >= threshold and previous_value < threshold
        updated = abs(current_value - previous_value) > 1e-9

        color = (255,0,0) if fired else ((0,255,0) if updated else (0,0,255))
        norm = min(abs(current_value) / threshold, 1.0) if threshold > 1e-9 else 0.0
        radius = int(min_radius + (max_radius - min_radius) * norm)

        pygame.draw.circle(surface, color, (cx, cy), radius)

        if neuron_name in getattr(sim, 'forced_active_neurons', set()):
            pygame.draw.circle(surface, (255,255,255), (cx, cy), radius + 3, 2)

        sim.matrix_hitboxes.append((pygame.Rect(cx-radius-4, cy-radius-4, (radius+4)*2, (radius+4)*2), neuron_name))
        name_color = sim.colorsName['red'] if neuron_name in sim.neuron_data else sim.WHITE
        sim.draw_text(surface, neuron_name, cx-22, cy-max_radius-26, name_color, font_size=18)

    sim.draw_text(surface, f'Iteration N°:{sim.iteration}', 10, 10)

def handle_mouse_click(sim, pos, button):
    for hit_rect, neuron_name in getattr(sim, 'matrix_hitboxes', []):
        if hit_rect.collidepoint(pos):
            if button == 1:
                if neuron_name in sim.forced_active_neurons:
                    sim.forced_active_neurons.remove(neuron_name)
                else:
                    sim.forced_active_neurons.add(neuron_name)
            elif button == 3:
                if neuron_name in sim.neuron_data:
                    del sim.neuron_data[neuron_name]
                    sim.scale_reset = True
                else:
                    color = sim.colors[len(sim.neuron_data) % len(sim.colors)]
                    sim.neuron_data[neuron_name] = {'values': [], 'activation_times': [], 'color': color}
            return
