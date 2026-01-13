"""screen_options.py

Worm functions / feature toggles.

The screen shows a list of high-level functional groups (photodetection,...).
Each row is clickable to enable/disable the group. When a group is enabled,
its associated neurons are added to `sim.forced_active_neurons` via
`Simulator.update_forced_active_neurons()`.
"""


import pygame

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    sim.draw_text(surface, "Options : Activation des fonctions du ver", rect.width // 2, 30, sim.colorsName['green'], font_size=40, align='center')
    start_y = 100
    for idx, func in enumerate(sim.worm_functions):
        btn_x = rect.width // 2 - 300
        btn_y = start_y + idx * 56
        btn_w = 600
        btn_h = 44
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        color = (80, 200, 80) if func['active'] else (160, 60, 60)
        pygame.draw.rect(surface, color, btn_rect, border_radius=14)
        pygame.draw.rect(surface, sim.WHITE, btn_rect, 2, border_radius=14)
        label = f"{func['name']} : {'ON' if func['active'] else 'OFF'}"
        sim.draw_text(surface, label, btn_x + btn_w // 2, btn_y + btn_h // 2 - 10, sim.BLACK, font_size=24, align='center')
    sim.draw_text(surface, "O : retour  |  Cliquez sur chaque ligne pour (dés)activer", rect.width // 2, rect.height - 45, sim.WHITE, font_size=26, align='center')

def handle_mouse_click(sim, pos):
    rect = sim.screen.get_rect()
    start_y = 100
    for idx, func in enumerate(sim.worm_functions):
        btn_x = rect.width // 2 - 300
        btn_y = start_y + idx * 56
        btn_w = 600
        btn_h = 44
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        if btn_rect.collidepoint(pos):
            func['active'] = not func['active']
            sim.update_forced_active_neurons()
            break
