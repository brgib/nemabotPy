"""screen_menu.py

Main menu screen: mosaic of images (thumbnails) representing each display screen.

User interactions:
- Mouse: click a tile to open the corresponding screen.
- Keyboard (when the menu is visible):
  - Arrow keys move the selection rectangle (wrap-around).
  - Enter/Space opens the selected tile.

Implementation notes:
- Menu entries are defined in `Simulator.menu_items`.
- This module only renders and performs hit-testing; screen switching is done
  by `nemabot.set_screen()`.
"""

import pygame


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
    margin_bottom = int(rect.height * 0.10)

    available_w = rect.width - 2 * margin_x
    available_h = rect.height - margin_top - margin_bottom

    # Spacing is proportional to screen width but clamped.
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


def draw(sim, surface, rect):
    """Render the mosaic menu."""
    surface.fill(sim.BLACK)

    title_y = int(rect.height * 0.05)
    sim.draw_text(surface, "Nemabot – Menu", rect.centerx, title_y, sim.colorsName['green'], font_size=52, align='center')
    sim.draw_text(surface, "Click a tile or use arrows + Enter/Space", rect.centerx, title_y + 45, sim.WHITE, font_size=28, align='center')

    items = sim.menu_items
    n = len(items)
    if n == 0:
        sim.draw_text(surface, "No menu items.", rect.centerx, rect.centery, sim.WHITE, font_size=36, align='center')
        sim.menu_buttons = []
        return

    cols, rows = _compute_grid(rect, n)
    tile_w, tile_h, sx, sy, start_x, start_y = _compute_tile_geometry(rect, cols, rows)

    sim.menu_buttons = []

    for idx, item in enumerate(items):
        r = idx // cols
        c = idx % cols
        x = start_x + c * (tile_w + sx)
        y = start_y + r * (tile_h + sy)
        tile_rect = pygame.Rect(x, y, tile_w, tile_h)

        thumb = sim.get_menu_thumbnail(item["image"], (tile_w, tile_h))
        surface.blit(thumb, tile_rect.topleft)

        # Selection / frame
        if idx == sim.menu_selection_index:
            pygame.draw.rect(surface, sim.colorsName['red'], tile_rect, 6, border_radius=14)
        else:
            pygame.draw.rect(surface, sim.WHITE, tile_rect, 2, border_radius=14)

        # Label under the tile
        label_y = tile_rect.bottom + 10
        sim.draw_text(surface, item.get("label", ""), tile_rect.centerx, label_y, sim.WHITE, font_size=26, align='center')

        sim.menu_buttons.append((tile_rect, idx))

    # Footer status (useful during debug)
    sim.draw_text(
        surface,
        f"Iter/s: {sim.iterations_per_second}    Iteration: {sim.iteration}",
        20,
        rect.height - 40,
        sim.WHITE,
        font_size=24,
    )


def handle_mouse_click(sim, pos):
    """Handle tile selection and activation from mouse clicks."""
    for tile_rect, idx in sim.menu_buttons:
        if tile_rect.collidepoint(pos):
            sim.menu_selection_index = idx
            _activate_selected(sim)
            return


def _activate_selected(sim):
    """Open the screen associated with the currently selected menu item."""
    if not sim.menu_items:
        return
    idx = max(0, min(sim.menu_selection_index, len(sim.menu_items) - 1))
    attr = sim.menu_items[idx].get("attr")
    if not attr:
        return

    # Reset all screens, then activate the requested one.
    sim.display_menu_screen = False
    sim.display_movement_screen = False
    sim.display_neuron_matrix = False
    sim.display_curve_screen = False
    sim.display_wave_screen = False
    sim.display_help_screen = False
    sim.display_worm_screen = False
    sim.display_options_screen = False

    setattr(sim, attr, True)


def handle_key(sim, key, cols_hint=3):
    """Keyboard handling specific to the menu.

    This function is called from `nemabot.handle_key()` when the menu is active.
    """
    if key == pygame.K_LEFT:
        sim.move_menu_selection(dx=-1, dy=0, cols=cols_hint)
    elif key == pygame.K_RIGHT:
        sim.move_menu_selection(dx=1, dy=0, cols=cols_hint)
    elif key == pygame.K_UP:
        sim.move_menu_selection(dx=0, dy=-1, cols=cols_hint)
    elif key == pygame.K_DOWN:
        sim.move_menu_selection(dx=0, dy=1, cols=cols_hint)
    elif key in (pygame.K_RETURN, pygame.K_SPACE):
        _activate_selected(sim)
