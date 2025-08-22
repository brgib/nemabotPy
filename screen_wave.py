# Auto-generated Nemabot multi-file package (autoscale only on Waves).


import pygame
import math

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    left_margin = 50
    right_margin = 50
    top_margin = 50
    bottom_margin = 50

    plot_width = rect.width - left_margin - right_margin
    plot_height = rect.height - top_margin - bottom_margin

    neurons = list(sim.neuron_data.keys())

    if len(neurons) == 0:
        sim.draw_text(surface, "Aucun neurone sélectionné pour l'affichage.", left_margin, top_margin, color=sim.WHITE, font_size=24)
        return

    neuron_spacing = 9  # simple layout

    max_iterations = max(1, sim.iteration)
    scale_x = plot_width / max_iterations

    pygame.draw.line(surface, sim.WHITE, (left_margin, top_margin), (left_margin, rect.height - bottom_margin))
    pygame.draw.line(surface, sim.WHITE, (left_margin, rect.height - bottom_margin), (rect.width - right_margin, rect.height - bottom_margin))

    for idx, neuron in enumerate(neurons):
        y_pos = top_margin + idx * neuron_spacing
        name_x = left_margin - 10
        sim.draw_text(surface, neuron, name_x, y_pos - 10, color=sim.neuron_data[neuron]['color'], font_size=16, align='right')
        pygame.draw.line(surface, sim.WHITE, (left_margin, y_pos), (rect.width - right_margin, y_pos))
        for t in sim.neuron_data[neuron]['activation_times']:
            x_pos = left_margin + t * scale_x
            pygame.draw.line(surface, sim.neuron_data[neuron]['color'], (x_pos, y_pos - 5), (x_pos, y_pos + 5), 2)

    num_ticks = 10
    for i in range(num_ticks + 1):
        t = int(i * max_iterations / num_ticks)
        x_pos = left_margin + t * scale_x
        sim.draw_text(surface, str(t), x_pos - 10, rect.height - bottom_margin + 10)
        pygame.draw.line(surface, sim.WHITE, (x_pos, rect.height - bottom_margin), (x_pos, rect.height - bottom_margin + 5))

    sim.draw_text(surface, f"Iteration N°:{sim.iteration}", rect.width - 200, 10)
