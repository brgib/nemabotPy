# Auto-generated split of Nemabot into multi-file structure.
# You can move these into your repo and run nemabot.py


import pygame

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    left_margin = 150
    bottom_margin = 50
    top_margin = 50
    right_margin = 50

    plot_width = rect.width - left_margin - right_margin
    plot_height = rect.height - top_margin - bottom_margin

    for idx, (neuron, data) in enumerate(sim.neuron_data.items()):
        color = data['color']
        sim.draw_text(surface, neuron, 10, top_margin + idx * 20, color)

    max_iterations = len(sim.time_values)
    if max_iterations < 2:
        return

    sim.draw_text(surface, f"Iteration N°:{sim.iteration}", rect.width - 200, 10)
    pygame.draw.line(surface, sim.WHITE, (left_margin, top_margin), (left_margin, rect.height - bottom_margin))
    pygame.draw.line(surface, sim.WHITE, (left_margin, rect.height - bottom_margin), (rect.width - right_margin, rect.height - bottom_margin))

    if not sim.neuron_data:
        return

    if sim.scale_reset:
        sim.scale_reset = False
        sim.max_value = max([max(data['values']) for data in sim.neuron_data.values()] + [1])
        sim.min_value = min([min(data['values']) for data in sim.neuron_data.values()] + [-1])
    else:
        sim.max_value = getattr(sim, 'max_value', max([max(data['values']) for data in sim.neuron_data.values()] + [1]))
        sim.min_value = getattr(sim, 'min_value', min([min(data['values']) for data in sim.neuron_data.values()] + [-1]))

    scale_x = plot_width / max(max_iterations - 1, 1)
    scale_y = plot_height / (sim.max_value - sim.min_value + 1e-9)

    for i in range(5):
        y_value = sim.min_value + i * (sim.max_value - sim.min_value) / 4
        y_pos = rect.height - bottom_margin - (y_value - sim.min_value) * scale_y
        sim.draw_text(surface, f"{y_value:.2f}", left_margin - 40, y_pos - 10)
        pygame.draw.line(surface, sim.WHITE, (left_margin - 5, y_pos), (left_margin, y_pos))

    num_ticks = min(8, max_iterations - 1)
    for i in range(num_ticks + 1):
        x_index = int(i * (max_iterations - 1) / num_ticks)
        x_value = sim.time_values[x_index]
        x_pos = left_margin + x_index * scale_x
        sim.draw_text(surface, f"{int(x_value)}", x_pos - 10, rect.height - bottom_margin + 10)
        pygame.draw.line(surface, sim.WHITE, (x_pos, rect.height - bottom_margin), (x_pos, rect.height - bottom_margin + 5))

    for neuron, data in sim.neuron_data.items():
        values = data['values']
        color = data['color']
        points = []
        for i in range(len(values)):
            x = left_margin + i * scale_x
            y = rect.height - bottom_margin - (values[i] - sim.min_value) * scale_y
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, 2)

    if sim.dropdown_menu_visible:
        draw_dropdown(sim, surface)

def draw_dropdown(sim, surface):
    menu_width = 200
    menu_height = 30 * len(sim.preconfigured_sets)
    menu_x = 150
    menu_y = 10
    sim.dropdown_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    pygame.draw.rect(surface, (50, 50, 50), sim.dropdown_menu_rect)
    for idx, set_name in enumerate(sim.preconfigured_sets.keys()):
        option_rect = pygame.Rect(menu_x, menu_y + idx * 30, menu_width, 30)
        pygame.draw.rect(surface, (100, 100, 100), option_rect)
        sim.draw_text(surface, set_name, menu_x + 10, menu_y + idx * 30 + 5, sim.WHITE)

def handle_mouse_click(sim, pos, button):
    if sim.dropdown_menu_rect and sim.dropdown_menu_rect.collidepoint(pos):
        relative_y = pos[1] - sim.dropdown_menu_rect.top
        option_height = 30
        index = relative_y // option_height
        if 0 <= index < len(sim.preconfigured_sets):
            set_name = list(sim.preconfigured_sets.keys())[index]
            for neuron_name in sim.preconfigured_sets[set_name]:
                if neuron_name not in sim.neuron_data:
                    color = sim.colors[len(sim.neuron_data) % len(sim.colors)]
                    sim.neuron_data[neuron_name] = {'values': [], 'activation_times': [], 'color': color}
            sim.scale_reset = True
        sim.dropdown_menu_visible = False
    else:
        sim.dropdown_menu_visible = False
