"""screen_forced_functions.py

Screen: Worm functions (force neurons ON every cycle).

This screen now also provides a random-initialization control panel:
- Initialize all neurons immediately
- Initialize only configured neurons immediately
- Edit min/max initialization bounds with safety clamping

Configured neurons = plotted neurons + forced neurons + active logical groups.
If no configured neuron is found, the configured mode falls back to all neurons.
"""

import pygame


FUNCTIONS = [
    {
        "name": "Food detection (chemosensation)",
        "neurons": ["AWA", "AWB", "AWC", "ASE", "ASI", "ASK"],
        "hint": "Detect food-related odors / chemicals",
    },
    {
        "name": "Food attraction (chemotaxis)",
        "neurons": ["AIY", "AIA", "AIB", "RIM"],
        "hint": "Bias movement toward food gradient",
    },
    {
        "name": "Satiety / feeding state",
        "neurons": ["NSM", "ADF", "AIM"],
        "hint": "Internal feeding modulation (demo mapping)",
    },
    {
        "name": "Hunger drive (seek food)",
        "neurons": ["AIA", "AIY", "AIB", "RIM", "RIC"],
        "hint": "Increase exploration to find food",
    },
    {
        "name": "Frontal impact (head bump)",
        "neurons": ["ASH", "FLP", "OLQ", "CEP"],
        "hint": "Detect head collision / noxious touch",
    },
    {
        "name": "Body touch (gentle)",
        "neurons": ["ALML", "ALMR", "AVM", "PLML", "PLMR"],
        "hint": "Gentle mechanosensation",
    },
    {
        "name": "Contact with ground (ventral)",
        "neurons": ["PVD", "PVQ", "DVA"],
        "hint": "Proprioception / substrate contact (approx.)",
    },
    {
        "name": "Side contact (left)",
        "neurons": ["PVDL", "PVQL", "RIPL"],
        "hint": "Left side contact / pressure (approx.)",
    },
    {
        "name": "Side contact (right)",
        "neurons": ["PVDR", "PVQR", "RIPR"],
        "hint": "Right side contact / pressure (approx.)",
    },
    {
        "name": "Harsh touch / pain-like",
        "neurons": ["PVD", "FLP", "ASH", "ADL"],
        "hint": "Strong mechanical stimulus (avoidance)",
    },
    {
        "name": "Thermosensation (temperature change)",
        "neurons": ["AFD", "AIM", "AIY"],
        "hint": "Temperature gradient / shift",
    },
    {
        "name": "Light sensing / phototaxis",
        "neurons": ["ASJ", "ASH", "ASK"],
        "hint": "Light response (avoid/seek depending on model)",
    },
    {
        "name": "Electrostatic field detection",
        "neurons": ["ASH", "ADL", "AWA"],
        "hint": "Electric field / static charge (speculative)",
    },
    {
        "name": "Vibration / acoustic-like",
        "neurons": ["ALM", "PLM", "AVM"],
        "hint": "Substrate vibration response (approx.)",
    },
    {
        "name": "Osmotic regulation / high osmolarity",
        "neurons": ["ASH", "ADL", "ASE"],
        "hint": "Avoid hyperosmotic conditions",
    },
    {
        "name": "Oxygenation monitoring (O2)",
        "neurons": ["URX", "AQR", "PQR"],
        "hint": "O2 sensing (aerotaxis)",
    },
    {
        "name": "CO2 sensing / avoidance",
        "neurons": ["BAG", "ASE", "AIY"],
        "hint": "Avoid high CO2 (approx.)",
    },
    {
        "name": "pH / acid detection",
        "neurons": ["ASE", "ASH", "ADF"],
        "hint": "Acidic / basic environment (approx.)",
    },
    {
        "name": "Fear / threat state",
        "neurons": ["ASH", "ADL", "AIB", "RIM"],
        "hint": "Increase avoidance / escape",
    },
    {
        "name": "Stress response",
        "neurons": ["RIM", "RIC", "AIB", "AVA"],
        "hint": "General stress modulation (approx.)",
    },
    {
        "name": "Arousal / wakefulness",
        "neurons": ["PDF", "RIS", "RIM"],
        "hint": "Wake/sleep gating (model-dependent)",
    },
    {
        "name": "Forward locomotion (bias)",
        "neurons": ["AVB", "PVC", "DB", "VB"],
        "hint": "Bias to forward movement",
    },
    {
        "name": "Reverse locomotion (bias)",
        "neurons": ["AVA", "AVD", "AVE", "DA", "VA"],
        "hint": "Bias to backward movement",
    },
    {
        "name": "Stop / pause",
        "neurons": ["RIS", "ALA"],
        "hint": "Suppress locomotion (approx.)",
    },
    {
        "name": "Increase speed (arousal locomotion)",
        "neurons": ["RIM", "RIC", "AVB"],
        "hint": "Increase locomotor drive",
    },
    {
        "name": "Decrease speed (caution)",
        "neurons": ["AVA", "AIB"],
        "hint": "Reduce locomotion (approx.)",
    },
    {
        "name": "Left turn",
        "neurons": ["SMDDL", "SMDVL", "RIVL"],
        "hint": "Steer left",
    },
    {
        "name": "Right turn",
        "neurons": ["SMDDR", "SMDVR", "RIVR"],
        "hint": "Steer right",
    },
    {
        "name": "Head swing / exploration",
        "neurons": ["SMD", "RIV"],
        "hint": "More head oscillations",
    },
    {
        "name": "Roaming mode",
        "neurons": ["RIM", "RIC", "AIB"],
        "hint": "Exploration / roaming",
    },
    {
        "name": "Dwelling mode",
        "neurons": ["AIY", "AIZ"],
        "hint": "Local search / dwelling",
    },
    {
        "name": "Local search (after food)",
        "neurons": ["AIY", "AIA", "RIM"],
        "hint": "Tight turns near food (approx.)",
    },
    {
        "name": "Pheromone detection (ascarosides)",
        "neurons": ["ASK", "ADL", "ASI"],
        "hint": "Social chemical cues (approx.)",
    },
    {
        "name": "Egg-laying (demo)",
        "neurons": ["HSN", "VC"],
        "hint": "Example additional pathway",
    },
    {
        "name": "Force touch sensor (sim.touch ON)",
        "neurons": ["TOUCH_SENSOR"],
        "hint": "If your engine supports it, treat as forced sensor",
    },
    {
        "name": "Force food sensor (sim.food ON)",
        "neurons": ["FOOD_SENSOR"],
        "hint": "If your engine supports it, treat as forced sensor",
    },
]


CONTROL_ITEMS = [
    {"kind": "button", "id": "random_all", "label": "Random init ALL [R]", "hint": "Initialize all neurons now"},
    {"kind": "button", "id": "random_configured", "label": "Random init CONFIGURED [G]", "hint": "Initialize configured neurons now"},
    {"kind": "value", "id": "random_min", "label": "Minimum value", "hint": "Left/Right: decrease/increase"},
    {"kind": "value", "id": "random_max", "label": "Maximum value", "hint": "Left/Right: decrease/increase"},
    {"kind": "toggle", "id": "target_mode", "label": "Default target mode", "hint": "Enter/Left/Right: switch ALL/CONFIGURED"},
]


def _ensure_state(sim):
    if not hasattr(sim, "forced_functions_state"):
        sim.forced_functions_state = {}
    if not hasattr(sim, "forced_neurons"):
        sim.forced_neurons = set()
    if not hasattr(sim, "functions_selection_index"):
        sim.functions_selection_index = 0
    if not hasattr(sim, "functions_focus"):
        sim.functions_focus = "grid"
    if not hasattr(sim, "control_selection_index"):
        sim.control_selection_index = 0
    if not hasattr(sim, "random_init_target_mode"):
        sim.random_init_target_mode = "all"
    if hasattr(sim, "_clamp_random_init_bounds"):
        sim._clamp_random_init_bounds()


def _compute_grid(rect, count):
    cols = 3 if rect.width < 2200 else 4
    rows = (count + cols - 1) // cols
    return cols, rows


def _compute_tiles(rect, cols, rows, bottom_reserve):
    margin_x = int(rect.width * 0.06)
    margin_top = int(rect.height * 0.14)
    margin_bottom = bottom_reserve

    available_w = rect.width - 2 * margin_x
    available_h = rect.height - margin_top - margin_bottom

    spacing_x = max(18, int(rect.width * 0.012))
    spacing_y = max(18, int(rect.height * 0.018))

    tile_w = int((available_w - spacing_x * (cols - 1)) / cols)
    tile_h = int((available_h - spacing_y * (rows - 1)) / max(1, rows))

    start_x = rect.left + margin_x
    start_y = rect.top + margin_top

    return tile_w, tile_h, spacing_x, spacing_y, start_x, start_y


def _rebuild_forced_neurons(sim):
    forced = set()
    for item in FUNCTIONS:
        if sim.forced_functions_state.get(item["name"], False):
            forced.update(item["neurons"])
    sim.forced_neurons = forced


def _toggle_selected(sim):
    _ensure_state(sim)
    idx = max(0, min(sim.functions_selection_index, len(FUNCTIONS) - 1))
    name = FUNCTIONS[idx]["name"]
    sim.forced_functions_state[name] = not sim.forced_functions_state.get(name, False)
    _rebuild_forced_neurons(sim)


def _toggle_target_mode(sim):
    sim.random_init_target_mode = "configured" if sim.random_init_target_mode == "all" else "all"


def _activate_control(sim):
    item = CONTROL_ITEMS[max(0, min(sim.control_selection_index, len(CONTROL_ITEMS) - 1))]
    cid = item["id"]
    if cid == "random_all":
        sim.trigger_random_initialization(mode="all")
    elif cid == "random_configured":
        sim.trigger_random_initialization(mode="configured")
    elif cid == "target_mode":
        _toggle_target_mode(sim)


def _adjust_control(sim, direction):
    step = getattr(sim, "random_init_step", 1.0)
    item = CONTROL_ITEMS[max(0, min(sim.control_selection_index, len(CONTROL_ITEMS) - 1))]
    cid = item["id"]

    if cid == "random_min":
        sim.adjust_random_init_bound("min", direction * step)
    elif cid == "random_max":
        sim.adjust_random_init_bound("max", direction * step)
    elif cid == "target_mode":
        _toggle_target_mode(sim)


def _draw_control_value(sim, surface, rect, item, selected):
    cid = item["id"]
    if cid == "random_min":
        value_text = f"{sim.random_init_min:.2f}"
    elif cid == "random_max":
        value_text = f"{sim.random_init_max:.2f}"
    else:
        value_text = sim.random_init_target_mode.upper()

    pygame.draw.rect(surface, (25, 25, 25), rect, border_radius=16)
    if selected:
        pygame.draw.rect(surface, sim.colorsName["red"], rect, 5, border_radius=16)
    else:
        pygame.draw.rect(surface, sim.WHITE, rect, 2, border_radius=16)

    sim.draw_text(surface, item["label"], rect.left + 16, rect.top + 10, sim.WHITE, font_size=26, align="left")
    sim.draw_text(surface, value_text, rect.right - 16, rect.top + 10, sim.colorsName["green"], font_size=28, align="right")
    sim.draw_text(surface, item["hint"], rect.left + 16, rect.top + 42, sim.WHITE, font_size=18, align="left")


def _draw_control_button(sim, surface, rect, item, selected):
    pygame.draw.rect(surface, (25, 25, 25), rect, border_radius=16)
    if selected:
        pygame.draw.rect(surface, sim.colorsName["red"], rect, 5, border_radius=16)
    else:
        pygame.draw.rect(surface, sim.WHITE, rect, 2, border_radius=16)

    sim.draw_text(surface, item["label"], rect.centerx, rect.top + 14, sim.WHITE, font_size=28, align="center")
    sim.draw_text(surface, item["hint"], rect.centerx, rect.top + 46, sim.WHITE, font_size=18, align="center")


def draw(sim, surface, rect):
    _ensure_state(sim)
    surface.fill(sim.BLACK)

    title_y = int(rect.height * 0.04)
    sim.draw_text(surface, "Worm functions (forced neurons)", rect.centerx, title_y, sim.colorsName["green"], font_size=50, align="center")
    sim.draw_text(surface, "Arrows: move  |  Enter: toggle/activate  |  R: init all  |  G: init configured  |  Space/ESC: menu", rect.centerx, title_y + 42, sim.WHITE, font_size=24, align="center")

    panel_h = int(rect.height * 0.25)
    bottom_reserve = panel_h + 26

    count = len(FUNCTIONS)
    cols, rows = _compute_grid(rect, count)
    tile_w, tile_h, sx, sy, start_x, start_y = _compute_tiles(rect, cols, rows, bottom_reserve)

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

        bg = sim.colorsName["red"] if active else (25, 25, 25)
        pygame.draw.rect(surface, bg, tile_rect, border_radius=18)

        if sim.functions_focus == "grid" and idx == sim.functions_selection_index:
            pygame.draw.rect(surface, sim.colorsName["red"], tile_rect, 6, border_radius=18)
        else:
            pygame.draw.rect(surface, sim.WHITE, tile_rect, 2, border_radius=18)

        sim.draw_text(surface, name, tile_rect.centerx, tile_rect.top + 22, sim.WHITE, font_size=24, align="center")
        sim.draw_text(surface, neurons, tile_rect.centerx, tile_rect.top + 54, sim.WHITE, font_size=17, align="center")
        sim.draw_text(surface, item.get("hint", ""), tile_rect.centerx, tile_rect.top + 82, sim.WHITE, font_size=15, align="center")

        sim.functions_buttons.append((tile_rect, idx))

    panel_rect = pygame.Rect(int(rect.width * 0.05), rect.height - panel_h, int(rect.width * 0.90), panel_h - 10)
    pygame.draw.rect(surface, (12, 12, 12), panel_rect, border_radius=18)
    pygame.draw.rect(surface, sim.WHITE, panel_rect, 2, border_radius=18)
    sim.draw_text(surface, "Random initialization", panel_rect.left + 18, panel_rect.top + 12, sim.colorsName["green"], font_size=30, align="left")

    button_w = int((panel_rect.width - 54) / 2)
    button_h = 80
    top_y = panel_rect.top + 50
    left_button = pygame.Rect(panel_rect.left + 18, top_y, button_w, button_h)
    right_button = pygame.Rect(panel_rect.left + 36 + button_w, top_y, button_w, button_h)

    sim.random_control_rects = []
    _draw_control_button(sim, surface, left_button, CONTROL_ITEMS[0], sim.functions_focus == "controls" and sim.control_selection_index == 0)
    _draw_control_button(sim, surface, right_button, CONTROL_ITEMS[1], sim.functions_focus == "controls" and sim.control_selection_index == 1)
    sim.random_control_rects.append((left_button, 0))
    sim.random_control_rects.append((right_button, 1))

    row_y = top_y + button_h + 12
    row_h = 58
    row_gap = 8
    for idx, item in enumerate(CONTROL_ITEMS[2:], start=2):
        row_rect = pygame.Rect(panel_rect.left + 18, row_y, panel_rect.width - 36, row_h)
        _draw_control_value(sim, surface, row_rect, item, sim.functions_focus == "controls" and sim.control_selection_index == idx)
        sim.random_control_rects.append((row_rect, idx))
        row_y += row_h + row_gap

    threshold_text = f"Threshold: {getattr(sim, 'random_init_step', 1.0) * 20.0:.2f}   Current range: [{sim.random_init_min:.2f} ; {sim.random_init_max:.2f}]"
    sim.draw_text(surface, threshold_text, panel_rect.right - 18, panel_rect.bottom - 28, sim.WHITE, font_size=20, align="right")

    configured_count = len(sim.get_random_init_targets(mode="configured"))
    forced_list = ", ".join(sorted(sim.forced_neurons)) if sim.forced_neurons else "(none)"
    sim.draw_text(surface, f"Forced neurons: {forced_list}", 20, rect.height - 34, sim.WHITE, font_size=20)
    sim.draw_text(surface, f"Configured target count: {configured_count}", rect.width - 20, rect.height - 34, sim.WHITE, font_size=20, align="right")


def handle_mouse_click(sim, pos):
    _ensure_state(sim)

    for tile_rect, idx in getattr(sim, "functions_buttons", []):
        if tile_rect.collidepoint(pos):
            sim.functions_focus = "grid"
            sim.functions_selection_index = idx
            _toggle_selected(sim)
            return

    for control_rect, idx in getattr(sim, "random_control_rects", []):
        if control_rect.collidepoint(pos):
            sim.functions_focus = "controls"
            sim.control_selection_index = idx
            _activate_control(sim)
            return


def handle_key(sim, key):
    _ensure_state(sim)

    count = len(FUNCTIONS)
    cols, _rows = _compute_grid(pygame.Rect(0, 0, 1920, 1080), count)
    num_controls = len(CONTROL_ITEMS)

    if key == pygame.K_r:
        sim.trigger_random_initialization(mode="all")
        return
    if key == pygame.K_g:
        sim.trigger_random_initialization(mode="configured")
        return

    if sim.functions_focus == "grid":
        if key == pygame.K_LEFT:
            sim.functions_selection_index = (sim.functions_selection_index - 1) % count
        elif key == pygame.K_RIGHT:
            sim.functions_selection_index = (sim.functions_selection_index + 1) % count
        elif key == pygame.K_UP:
            sim.functions_selection_index = (sim.functions_selection_index - cols) % count
        elif key == pygame.K_DOWN:
            next_idx = sim.functions_selection_index + cols
            if next_idx >= count:
                sim.functions_focus = "controls"
                sim.control_selection_index = 0
            else:
                sim.functions_selection_index = next_idx
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            _toggle_selected(sim)
        elif key == pygame.K_ESCAPE:
            if hasattr(sim, "display_forced_functions_screen"):
                sim.display_forced_functions_screen = False
            if hasattr(sim, "display_menu_screen"):
                sim.display_menu_screen = True
        return

    if sim.functions_focus == "controls":
        if key == pygame.K_LEFT:
            if sim.control_selection_index in (0, 1):
                sim.control_selection_index = max(0, sim.control_selection_index - 1)
            else:
                _adjust_control(sim, -1)
        elif key == pygame.K_RIGHT:
            if sim.control_selection_index in (0, 1):
                sim.control_selection_index = min(1, sim.control_selection_index + 1)
            else:
                _adjust_control(sim, 1)
        elif key == pygame.K_UP:
            if sim.control_selection_index in (0, 1):
                sim.functions_focus = "grid"
            else:
                sim.control_selection_index = max(0, sim.control_selection_index - 1)
        elif key == pygame.K_DOWN:
            sim.control_selection_index = min(num_controls - 1, sim.control_selection_index + 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            _activate_control(sim)
        elif key == pygame.K_ESCAPE:
            if hasattr(sim, "display_forced_functions_screen"):
                sim.display_forced_functions_screen = False
            if hasattr(sim, "display_menu_screen"):
                sim.display_menu_screen = True
