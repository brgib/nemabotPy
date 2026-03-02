"""screen_forced_functions.py

Screen: Worm functions (force neurons ON every cycle).

- Displays a grid of toggle buttons.
- Each button shows a function name and the neuron(s) affected.
- When activated, the button stays red; press again to disable.
- Arrow keys move selection; Enter/Space toggles.
- ESC returns to the main menu.

Integration contract (lightweight and non-breaking):
- This module maintains:
    sim.forced_functions_state : dict[str,bool]
    sim.forced_neurons         : set[str]
- Your simulation loop should read `sim.forced_neurons` and force these neurons
  active each cycle (wherever your neuron update is implemented).
"""

import pygame


FUNCTIONS = [
    {"name": "Forward locomotion", "neurons": ["AVB", "PVC", "DB", "VB"], "hint": "Bias to forward movement"},
    {"name": "Reverse locomotion", "neurons": ["AVA", "AVD", "AVE", "DA", "VA"], "hint": "Bias to backward movement"},
    {"name": "Left turn", "neurons": ["SMDDL", "SMDVL", "RIVL"], "hint": "Steer left"},
    {"name": "Right turn", "neurons": ["SMDDR", "SMDVR", "RIVR"], "hint": "Steer right"},
    {"name": "Head swing / exploration", "neurons": ["SMD", "RIV"], "hint": "More head oscillations"},
    {"name": "Food seeking", "neurons": ["AWA", "AWC", "ASE", "AIY"], "hint": "Chemotaxis / attraction"},
    {"name": "Avoid obstacles (touch)", "neurons": ["ALM", "AVM", "PLM"], "hint": "Mechanosensation"},
    {"name": "Light avoidance", "neurons": ["ASJ", "ASH"], "hint": "Phototaxis / aversion"},
    {"name": "Roaming mode", "neurons": ["RIM", "RIC", "AIB"], "hint": "Exploration / roaming"},
    {"name": "Dwelling mode", "neurons": ["AIY", "AIZ"], "hint": "Local search / dwelling"},
    {"name": "Osmotic stress response", "neurons": ["ASH", "ADL"], "hint": "High osmolarity avoidance"},
    {"name": "Egg-laying (demo)", "neurons": ["HSN", "VC"], "hint": "Example additional pathway"},
]


def _ensure_state(sim):
    if not hasattr(sim, "forced_functions_state"):
        sim.forced_functions_state = {}
    if not hasattr(sim, "forced_neurons"):
        sim.forced_neurons = set()
    if not hasattr(sim, "functions_selection_index"):
        sim.functions_selection_index = 0


def _compute_grid(rect, count):
    cols = 3 if rect.width < 2200 else 4
    rows = (count + cols - 1) // cols
    return cols, rows


def _compute_tiles(rect, cols, rows):
    margin_x = int(rect.width * 0.06)
    margin_y = int(rect.height * 0.14)

    available_w = rect.width - 2 * margin_x
    available_h = rect.height - 2 * margin_y

    spacing_x = max(18, int(rect.width * 0.012))
    spacing_y = max(18, int(rect.height * 0.018))

    tile_w = int((available_w - spacing_x * (cols - 1)) / cols)
    tile_h = int((available_h - spacing_y * (rows - 1)) / rows)

    start_x = rect.left + margin_x
    start_y = rect.top + margin_y

    return tile_w, tile_h, spacing_x, spacing_y, start_x, start_y


def _rebuild_forced_neurons(sim):
    forced = set()
    for item in FUNCTIONS:
        if sim.forced_functions_state.get(item["name"], False):
            forced.update(item["neurons"])
    sim.forced_neurons = forced


def draw(sim, surface, rect):
    _ensure_state(sim)
    surface.fill(sim.BLACK)

    title_y = int(rect.height * 0.05)
    sim.draw_text(surface, "Worm functions (forced neurons)", rect.centerx, title_y, sim.colorsName['green'], font_size=52, align='center')
    sim.draw_text(surface, "Arrows to move – Enter to toggle – Space/ESC to return", rect.centerx, title_y + 45, sim.WHITE, font_size=26, align='center')

    count = len(FUNCTIONS)
    cols, rows = _compute_grid(rect, count)
    tile_w, tile_h, sx, sy, start_x, start_y = _compute_tiles(rect, cols, rows)

    sim.functions_buttons = []

    for idx, item in enumerate(FUNCTIONS):
        r = idx // cols
        c = idx % cols
        x = start_x + c * (tile_w + sx)
        y = start_y + r * (tile_h + sy)
        tile_rect = pygame.Rect(x, y, tile_w, tile_h)

        name = item["name"]
        neurons = ", ".join(item["neurons"])
        active = sim.forced_functions_state.get(name, False)

        bg = sim.colorsName['red'] if active else (25, 25, 25)
        pygame.draw.rect(surface, bg, tile_rect, border_radius=18)

        if idx == sim.functions_selection_index:
            # Thicker selection outline (similar to main menu)
            pygame.draw.rect(surface, sim.colorsName['red'], tile_rect, 6, border_radius=18)
        else:
            pygame.draw.rect(surface, sim.WHITE, tile_rect, 2, border_radius=18)

        sim.draw_text(surface, name, tile_rect.centerx, tile_rect.top + 26, sim.WHITE, font_size=28, align='center')
        sim.draw_text(surface, neurons, tile_rect.centerx, tile_rect.top + 62, sim.WHITE, font_size=20, align='center')
        sim.draw_text(surface, item.get("hint", ""), tile_rect.centerx, tile_rect.top + 92, sim.WHITE, font_size=18, align='center')

        sim.functions_buttons.append((tile_rect, idx))

    forced_list = ", ".join(sorted(sim.forced_neurons)) if sim.forced_neurons else "(none)"
    sim.draw_text(surface, f"Forced neurons: {forced_list}", 20, rect.height - 40, sim.WHITE, font_size=22)


def handle_mouse_click(sim, pos):
    _ensure_state(sim)
    for tile_rect, idx in getattr(sim, "functions_buttons", []):
        if tile_rect.collidepoint(pos):
            sim.functions_selection_index = idx
            _toggle_selected(sim)
            return


def _toggle_selected(sim):
    _ensure_state(sim)
    idx = max(0, min(sim.functions_selection_index, len(FUNCTIONS) - 1))
    name = FUNCTIONS[idx]["name"]
    sim.forced_functions_state[name] = not sim.forced_functions_state.get(name, False)
    _rebuild_forced_neurons(sim)


def handle_key(sim, key):
    _ensure_state(sim)

    count = len(FUNCTIONS)
    cols, _rows = _compute_grid(pygame.Rect(0, 0, 1920, 1080), count)

    if key == pygame.K_LEFT:
        sim.functions_selection_index = (sim.functions_selection_index - 1) % count
    elif key == pygame.K_RIGHT:
        sim.functions_selection_index = (sim.functions_selection_index + 1) % count
    elif key == pygame.K_UP:
        sim.functions_selection_index = (sim.functions_selection_index - cols) % count
    elif key == pygame.K_DOWN:
        sim.functions_selection_index = (sim.functions_selection_index + cols) % count
    elif key in (pygame.K_RETURN, pygame.K_SPACE):
        _toggle_selected(sim)
    elif key == pygame.K_ESCAPE:
        if hasattr(sim, "display_forced_functions_screen"):
            sim.display_forced_functions_screen = False
        if hasattr(sim, "display_menu_screen"):
            sim.display_menu_screen = True
