"""screen_forced_functions.py

Screen: Worm functions (force neurons ON every cycle).

Purpose
-------
This screen provides a large grid of toggle buttons. Each button represents a
"worm function" (a sensory modality, internal state, or behavior). When a
button is enabled, it remains RED and its associated neuron list is added to
`sim.forced_neurons`. Your simulation loop can then force those neurons active
each cycle.

Controls
--------
- Arrow keys: move selection (like the main menu)
- Enter / Space: toggle current button (ON/OFF)
- Mouse click: select + toggle
- ESC: return to menu

Integration contract (non-breaking)
-----------------------------------
This module maintains:
- sim.forced_functions_state : dict[str,bool]     # on/off per function name
- sim.forced_neurons         : set[str]           # union of neurons for all active functions
- sim.functions_selection_index : int             # current selection

Important note on neuron lists
------------------------------
The neuron lists below are *suggested* mappings for a C. elegans-inspired model.
Depending on your own neuron naming conventions and implementation details,
you may need to rename, add, or remove neurons.

Authoring approach
------------------
- Keep UI stable and fast (pure pygame drawing).
- Keep toggling logic deterministic and easy to extend: edit FUNCTIONS only.
"""

import pygame


# --------------------------------------------------------------------
# Functions catalog
# --------------------------------------------------------------------
# Each entry:
#   name    : button title
#   neurons : list[str] (displayed below and aggregated into forced_neurons)
#   hint    : short caption to help the user
#
# Naming: use common C. elegans neuron names when plausible, but treat as
#         "logical groups" for your simulation.
FUNCTIONS = [
    # --- Sensory: food / chemicals ---
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

    # --- Sensory: mechanosensation / touch ---
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

    # --- Sensory: temperature / light / fields ---
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

    # --- Internal regulation: osmotic / oxygen / CO2 / pH ---
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

    # --- Internal states: fear / stress / arousal ---
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

    # --- Locomotion primitives ---
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

    # --- Steering / turning ---
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

    # --- Navigation modes ---
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

    # --- Social / pheromone-like (optional) ---
    {
        "name": "Pheromone detection (ascarosides)",
        "neurons": ["ASK", "ADL", "ASI"],
        "hint": "Social chemical cues (approx.)",
    },

    # --- Reproduction / egg-laying (demo) ---
    {
        "name": "Egg-laying (demo)",
        "neurons": ["HSN", "VC"],
        "hint": "Example additional pathway",
    },

    # --- Utility toggles for testing ---
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


# --------------------------------------------------------------------
# State helpers
# --------------------------------------------------------------------
def _ensure_state(sim):
    if not hasattr(sim, "forced_functions_state"):
        sim.forced_functions_state = {}
    if not hasattr(sim, "forced_neurons"):
        sim.forced_neurons = set()
    if not hasattr(sim, "functions_selection_index"):
        sim.functions_selection_index = 0


def _compute_grid(rect, count):
    # Use 3 columns on 1080p, 4 columns on very wide screens
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


def _toggle_selected(sim):
    _ensure_state(sim)
    idx = max(0, min(sim.functions_selection_index, len(FUNCTIONS) - 1))
    name = FUNCTIONS[idx]["name"]
    sim.forced_functions_state[name] = not sim.forced_functions_state.get(name, False)
    _rebuild_forced_neurons(sim)


# --------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------
def draw(sim, surface, rect):
    _ensure_state(sim)
    surface.fill(sim.BLACK)

    title_y = int(rect.height * 0.05)
    sim.draw_text(
        surface,
        "Worm functions (forced neurons)",
        rect.centerx,
        title_y,
        sim.colorsName["green"],
        font_size=52,
        align="center",
    )
    sim.draw_text(
        surface,
        "Arrows to move – Enter/Space to toggle – ESC to return",
        rect.centerx,
        title_y + 45,
        sim.WHITE,
        font_size=26,
        align="center",
    )

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

        # Background: red-ish when active, dark when inactive
        bg = sim.colorsName["red"] if active else (25, 25, 25)
        pygame.draw.rect(surface, bg, tile_rect, border_radius=18)

        # Outline: selection rectangle
        if idx == sim.functions_selection_index:
            pygame.draw.rect(surface, sim.WHITE, tile_rect, 4, border_radius=18)
            pygame.draw.rect(surface, sim.colorsName["red"], tile_rect, 2, border_radius=18)
        else:
            pygame.draw.rect(surface, sim.WHITE, tile_rect, 2, border_radius=18)

        # Text inside tile (3 lines)
        sim.draw_text(surface, name, tile_rect.centerx, tile_rect.top + 26, sim.WHITE, font_size=26, align="center")
        sim.draw_text(surface, neurons, tile_rect.centerx, tile_rect.top + 60, sim.WHITE, font_size=18, align="center")
        sim.draw_text(surface, item.get("hint", ""), tile_rect.centerx, tile_rect.top + 88, sim.WHITE, font_size=16, align="center")

        sim.functions_buttons.append((tile_rect, idx))

    forced_list = ", ".join(sorted(sim.forced_neurons)) if sim.forced_neurons else "(none)"
    sim.draw_text(surface, f"Forced neurons: {forced_list}", 20, rect.height - 40, sim.WHITE, font_size=22)


# --------------------------------------------------------------------
# Input handling
# --------------------------------------------------------------------
def handle_mouse_click(sim, pos):
    _ensure_state(sim)
    for tile_rect, idx in getattr(sim, "functions_buttons", []):
        if tile_rect.collidepoint(pos):
            sim.functions_selection_index = idx
            _toggle_selected(sim)
            return


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
