# Auto-generated Nemabot multi-file package (with requested fixes).


import math
import pygame
from connectome import postsynaptic, muscles

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)

    num_neurons = len(postsynaptic)
    if num_neurons == 0:
        sim.draw_text(surface, "Aucun neurone.", 10, 10)
        return

    grid_size = int(math.ceil(math.sqrt(num_neurons)))
    cell_width = rect.width / grid_size
    cell_height = rect.height / grid_size
    max_radius = int(min(cell_width, cell_height) // 2 - 10)
    neuron_idx = 0
    neuron_positions = {}

    for i in range(grid_size):
        for j in range(grid_size):
            if neuron_idx >= num_neurons:
                break
            neuron_name = list(postsynaptic.keys())[neuron_idx]
            value = postsynaptic[neuron_name][2]
            value0 = postsynaptic[neuron_name][0]

            radius = max(2, min(max_radius, int(abs(value) * max_radius)))
            if neuron_name in sim.forced_active_neurons:
                color = sim.colorsName['red']
            else:
                color = (0, 255, 0) if value != value0 > 0 else (0, 0, 255)

            center_x = int(j * cell_width + cell_width // 2)
            center_y = int(i * cell_height + cell_height // 2)

            pygame.draw.circle(surface, color, (center_x, center_y), radius)
            neuron_positions[neuron_name] = (center_x, center_y)

            neuron_idx += 1

    for neuron_name, (center_x, center_y) in neuron_positions.items():
        name_color = sim.colorsName['red'] if neuron_name in sim.neuron_data else sim.WHITE
        sim.draw_text(surface, neuron_name, center_x - 20, center_y - 30, name_color, font_size=24)

    sim.draw_text(surface, f"Iteration N°:{sim.iteration}", 10, 10)

def handle_mouse_click(sim, pos, button):
    rect = sim.screen.get_rect()
    num_neurons = len(postsynaptic)
    grid_size = int(math.ceil(math.sqrt(num_neurons)))
    cell_width = rect.width / grid_size
    cell_height = rect.height / grid_size

    neuron_idx = 0
    for i in range(grid_size):
        for j in range(grid_size):
            if neuron_idx >= num_neurons:
                break
            neuron_name = list(postsynaptic.keys())[neuron_idx]
            cell_rect = pygame.Rect(int(j * cell_width), int(i * cell_height), int(cell_width), int(cell_height))
            if cell_rect.collidepoint(pos):
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
                        sim.scale_reset = True
                return
            neuron_idx += 1
