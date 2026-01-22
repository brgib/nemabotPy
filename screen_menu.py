"""screen_menu.py

Main menu screen: mosaic of images (thumbnails) representing each display screen,
plus a bottom action bar with:
- Quit
- Load neural network (Excel)
- Worm functions (force neurons ON)

User interactions:
- Mouse: click a tile or an action button.
- Keyboard (when the menu is visible):
  - Arrow keys move the selection rectangle (wrap-around).
  - Enter/Space opens the selected tile / triggers the selected action.

Implementation notes:
- Menu entries (tiles) are defined in `Simulator.menu_items`.
- This module only renders and performs hit-testing; screen switching is done
  by setting boolean flags on `sim`.
"""

import pygame


# ----------------------------
# Layout helpers
# ----------------------------

def _compute_grid(rect, item_count):
    """Compute an aesthetically balanced grid for `item_count` tiles."""
    if item_count <= 4:
        cols = 2
    elif item_count <= 6:
        cols = 3
    else:
        cols = 4

    rows = (item_count + cols - 1) // cols
    return cols, rows


def _compute_tile_geometry(rect, cols, rows):
    """Return (tile_w, tile_h, spacing_x, spacing_y, start_x, start_y)."""
    # Safe margins so the menu remains pleasant in 1080p and 4K.
    margin_x = int(rect.width * 0.06)
    margin_top = int(rect.height * 0.12)
    margin_bottom = int(rect.height * 0.18)  # leave room for action bar

    available_w = rect.width - 2 * margin_x
    available_h = rect.height - margin_top - margin_bottom

    # Spacing is proportional to screen size but clamped.
    spacing_x = max(25, int(rect.width * 0.015))
    spacing_y = max(25, int(rect.height * 0.020))

    # Compute tile size, keeping a 16:9-ish aspect ratio.
    tile_w = int((available_w - spacing_x * (cols - 1)) / cols)
    tile_h = int(tile_w * 9 / 16)

    # If the computed height doesn't fit, recompute from height.
    max_tile_h = int((available_h - spacing_y * (rows - 1)) / rows)
    if tile_h > max_tile_h:
        tile_h = max_tile_h
        tile_w = int(tile_h * 16 / 9)

    total_w = cols * tile_w + (cols - 1) * spacing_x
    total_h = rows * tile_h + (rows - 1) * spacing_y

    start_x = rect.centerx - total_w // 2
    start_y = rect.top + margin_top + (available_h - total_h) // 2

    return tile_w, tile_h, spacing_x, spacing_y, start_x, start_y


def _compute_action_bar(rect):
    """Compute geometry for the bottom action buttons."""
    bar_h = int(rect.height * 0.12)
    bar_top = rect.bottom - bar_h - int(rect.height * 0.04)

    margin_x = int(rect.width * 0.10)
    available_w = rect.width - 2 * margin_x

    btn_h = int(bar_h * 0.70)
    btn_w = int(available_w / 3) - 20
    spacing = int((available_w - 3 * btn_w) / 2)

    y = bar_top + (bar_h - btn_h) // 2
    x1 = rect.left + margin_x
    x2 = x1 + btn_w + spacing
    x3 = x2 + btn_w + spacing

    return [
        pygame.Rect(x1, y, btn_w, btn_h),
        pygame.Rect(x2, y, btn_w, btn_h),
        pygame.Rect(x3, y, btn_w, btn_h),
    ]


# ----------------------------
# Selection / activation helpers
# ----------------------------

def _reset_all_screens(sim):
    """Reset all known screen flags to False."""
    flags = [
        "display_menu_screen",
        "display_movement_screen",
        "display_neuron_matrix",
        "display_curve_screen",
        "display_wave_screen",
        "display_help_screen",
        "display_worm_screen",
        "display_options_screen",
        # Newly added screens
        "display_excel_loader_screen",
        "display_forced_functions_screen",
    ]
    for f in flags:
        if hasattr(sim, f):
            setattr(sim, f, False)


def _activate_selected_tile(sim):
    """Open the screen associated with the currently selected menu tile."""
    if not sim.menu_items:
        return

    idx = max(0, min(sim.menu_selection_index, len(sim.menu_items) - 1))
    attr = sim.menu_items[idx].get("attr")
    if not attr:
        return

    _reset_all_screens(sim)
    setattr(sim, attr, True)


def _request_quit():
    """Ask the application to quit in a robust way."""
    pygame.event.post(pygame.event.Event(pygame.QUIT))


def _activate_action(sim, action_key):
    """Trigger one of the bottom action buttons."""
    if action_key == "quit":
        _request_quit()
        return

    _reset_all_screens(sim)

    if action_key == "excel":
        setattr(sim, "display_excel_loader_screen", True)
        return

    if action_key == "functions":
        setattr(sim, "display_forced_functions_screen", True)
        return


def _ensure_menu_state(sim):
    """Ensure expected menu state attributes exist."""
    if not hasattr(sim, "menu_selection_index"):
        sim.menu_selection_index = 0

    # Focus can be 'tiles' or 'actions'
    if not hasattr(sim, "menu_focus"):
        sim.menu_focus = "tiles"

    # 0..2 for the action buttons
    if not hasattr(sim, "menu_action_index"):
        sim.menu_action_index = 0


# ----------------------------
# Rendering
# ----------------------------

def draw(sim, surface, rect):
    """Render the mosaic menu + action bar."""
    _ensure_menu_state(sim)

    surface.fill(sim.BLACK)

    title_y = int(rect.height * 0.05)
    sim.draw_text(surface, "Nemabot – Menu", rect.centerx, title_y, sim.colorsName['green'], font_size=52, align='center')
    sim.draw_text(surface, "Click a tile or use arrows + Enter/Space", rect.centerx, title_y + 45, sim.WHITE, font_size=28, align='center')

    items = sim.menu_items
    n = len(items)

    # --- Tiles ---
    sim.menu_buttons = []
    cols_hint = 3  # default used by nemabot.handle_key; we override dynamically
    if n == 0:
        sim.draw_text(surface, "No menu items.", rect.centerx, rect.centery, sim.WHITE, font_size=36, align='center')
    else:
        cols, rows = _compute_grid(rect, n)
        cols_hint = cols
        tile_w, tile_h, sx, sy, start_x, start_y = _compute_tile_geometry(rect, cols, rows)

        for idx, item in enumerate(items):
            r = idx // cols
            c = idx % cols
            x = start_x + c * (tile_w + sx)
            y = start_y + r * (tile_h + sy)
            tile_rect = pygame.Rect(x, y, tile_w, tile_h)

            thumb = sim.get_menu_thumbnail(item["image"], (tile_w, tile_h))
            surface.blit(thumb, tile_rect.topleft)

            # Selection / frame
            is_selected = (sim.menu_focus == "tiles" and idx == sim.menu_selection_index)
            if is_selected:
                pygame.draw.rect(surface, sim.colorsName['red'], tile_rect, 6, border_radius=14)
            else:
                pygame.draw.rect(surface, sim.WHITE, tile_rect, 2, border_radius=14)

            # Label under the tile
            label_y = tile_rect.bottom + 10
            sim.draw_text(surface, item.get("label", ""), tile_rect.centerx, label_y, sim.WHITE, font_size=26, align='center')

            sim.menu_buttons.append((tile_rect, idx))

    # --- Action bar ---
    action_rects = _compute_action_bar(rect)
    actions = [
        ("quit", "Quit"),
        ("excel", "Load Excel network"),
        ("functions", "Worm functions"),
    ]

    sim.menu_action_buttons = []
    for i, (key, label) in enumerate(actions):
        r = action_rects[i]

        # Button background
        pygame.draw.rect(surface, (30, 30, 30), r, border_radius=16)

        # Selection outline
        is_selected = (sim.menu_focus == "actions" and sim.menu_action_index == i)
        if is_selected:
            pygame.draw.rect(surface, sim.colorsName['red'], r, 6, border_radius=16)
        else:
            pygame.draw.rect(surface, sim.WHITE, r, 2, border_radius=16)

        sim.draw_text(surface, label, r.centerx, r.centery, sim.WHITE, font_size=30, align='center')

        # Small subtitle
        subtitle = ""
        if key == "quit":
            subtitle = "Exit the application"
        elif key == "excel":
            subtitle = "Import a neuron network from .xlsx"
        elif key == "functions":
            subtitle = "Toggle worm features (force neurons)"
        sim.draw_text(surface, subtitle, r.centerx, r.centery + 26, sim.WHITE, font_size=20, align='center')

        sim.menu_action_buttons.append((r, key))

    # Footer status (useful during debug)
    sim.draw_text(
        surface,
        f"Iter/s: {sim.iterations_per_second}    Iteration: {sim.iteration}",
        20,
        rect.height - 40,
        sim.WHITE,
        font_size=24,
    )

    # Store cols so key handler can use the correct wrap geometry for tiles
    sim._menu_cols_hint = cols_hint


# ----------------------------
# Input handling
# ----------------------------

def handle_mouse_click(sim, pos):
    """Handle tile selection / activation and action bar clicks."""
    _ensure_menu_state(sim)

    # Click on a tile
    for tile_rect, idx in getattr(sim, "menu_buttons", []):
        if tile_rect.collidepoint(pos):
            sim.menu_focus = "tiles"
            sim.menu_selection_index = idx
            _activate_selected_tile(sim)
            return

    # Click on an action button
    for btn_rect, action_key in getattr(sim, "menu_action_buttons", []):
        if btn_rect.collidepoint(pos):
            sim.menu_focus = "actions"
            sim.menu_action_index = ["quit", "excel", "functions"].index(action_key)
            _activate_action(sim, action_key)
            return


def handle_key(sim, key, cols_hint=3):
    """Keyboard handling specific to the menu.

    This function is called from `nemabot.handle_key()` when the menu is active.
    """
    _ensure_menu_state(sim)
    cols_hint = getattr(sim, "_menu_cols_hint", cols_hint)

    if sim.menu_focus == "tiles":
        if key == pygame.K_LEFT:
            sim.move_menu_selection(dx=-1, dy=0, cols=cols_hint)
        elif key == pygame.K_RIGHT:
            sim.move_menu_selection(dx=1, dy=0, cols=cols_hint)
        elif key == pygame.K_UP:
            sim.move_menu_selection(dx=0, dy=-1, cols=cols_hint)
        elif key == pygame.K_DOWN:
            # If user goes down from the last tile row, jump to actions
            if sim.menu_items:
                n = len(sim.menu_items)
                current_row = sim.menu_selection_index // cols_hint
                last_row = (n - 1) // cols_hint
                if current_row >= last_row:
                    sim.menu_focus = "actions"
                    sim.menu_action_index = 0
                else:
                    sim.move_menu_selection(dx=0, dy=1, cols=cols_hint)
            else:
                sim.menu_focus = "actions"
                sim.menu_action_index = 0
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            _activate_selected_tile(sim)

    else:  # actions
        if key == pygame.K_LEFT:
            sim.menu_action_index = (sim.menu_action_index - 1) % 3
        elif key == pygame.K_RIGHT:
            sim.menu_action_index = (sim.menu_action_index + 1) % 3
        elif key == pygame.K_UP:
            sim.menu_focus = "tiles"
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            action_key = ["quit", "excel", "functions"][sim.menu_action_index]
            _activate_action(sim, action_key)
