"""screen_help.py

Nemabot - Help & Controls

"""

import pygame


def draw(sim, surface, rect):
    surface.fill(sim.BLACK)

    # ----------------------------
    # Typography / layout tuning
    # ----------------------------
    title_fs = 56
    section_fs = 38
    body_fs = 30
    bullet_fs = 28
    line_h = 34

    top = 16
    header_h = 92
    margin_x = int(rect.width * 0.045)
    gap = int(rect.width * 0.05)
    col_w = (rect.width - 2 * margin_x - gap) // 2

    left_x = margin_x
    right_x = margin_x + col_w + gap

    y_left = top + header_h
    y_right = top + header_h

    bottom_reserve = 90  # keep room for FPS/HUD that might be drawn elsewhere
    max_y = rect.height - bottom_reserve

    green = sim.colorsName["green"] if hasattr(sim, "colorsName") else sim.WHITE

    # ----------------------------
    # Small helpers
    # ----------------------------
    def _wrap_draw(x, y, text, fs, color):
        """Draw text wrapped inside current column width."""
        font = pygame.font.Font(None, fs)
        words = text.split(" ")
        cur = ""
        yy = y
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= col_w:
                cur = test
            else:
                sim.draw_text(surface, cur, x, yy, color, font_size=fs, align="left")
                yy += line_h
                cur = w
        if cur:
            sim.draw_text(surface, cur, x, yy, color, font_size=fs, align="left")
            yy += line_h
        return yy

    def section(col, text):
        nonlocal y_left, y_right
        if col == "left":
            y_left = _wrap_draw(left_x, y_left, text, section_fs, green)
            y_left += 4
        else:
            y_right = _wrap_draw(right_x, y_right, text, section_fs, green)
            y_right += 4

    def line(col, text, fs=body_fs, color=None):
        nonlocal y_left, y_right
        c = color or sim.WHITE
        if col == "left":
            y_left = _wrap_draw(left_x, y_left, text, fs, c)
        else:
            y_right = _wrap_draw(right_x, y_right, text, fs, c)

    def bullet(col, text):
        nonlocal y_left, y_right
        if col == "left":
            y_left = _wrap_draw(left_x + 16, y_left, "- " + text, bullet_fs, sim.WHITE)
        else:
            y_right = _wrap_draw(right_x + 16, y_right, "- " + text, bullet_fs, sim.WHITE)

    def block_gap(col, px=10):
        nonlocal y_left, y_right
        if col == "left":
            y_left += px
        else:
            y_right += px

    # ----------------------------
    # Title + quick reminder
    # ----------------------------
    sim.draw_text(surface, "Nemabot - Help & Controls", rect.centerx, top, green, font_size=title_fs, align="center")
    sim.draw_text(
        surface,
        "SPACE: open/return  |  ESC: return (ESC in menu quits)",
        rect.width - margin_x,
        top + 54,
        sim.WHITE,
        font_size=26,
        align="right",
    )

    # ============================================================
    # LEFT COLUMN: COMMON CONTROLS
    # ============================================================
    section("left", "Common controls")
    bullet("left", "Menu navigation: Arrow keys move the tile selection.")
    bullet("left", "SPACE (in menu): open the selected screen or action bar button.")
    bullet("left", "Mouse (in menu): click a tile or an action bar button.")
    bullet("left", "SPACE (in any screen): return to the menu.")
    bullet("left", "ESC: return to the menu; ESC in menu quits the program.")

    block_gap("left", 12)
    section("left", "Screen shortcuts (from anywhere)")
    line("left", "H: Help   M: Matrix   C: Curves   X: Raster   D: Movement   W: Worm   O: Options", fs=bullet_fs)

    block_gap("left", 12)
    section("left", "Simulation / display")
    bullet("left", "P: step-by-step mode ON/OFF")
    bullet("left", "S: execute one step (only in step-by-step mode)")
    bullet("left", "+ / -: change speed (iterations per second)")
    bullet("left", "F11: fullscreen toggle")
    bullet("left", "K: 4K mode toggle (if supported)")

    block_gap("left", 12)
    section("left", "Stimuli (debug)")
    bullet("left", "F: inject a Food stimulus (sim.add_food())")
    bullet("left", "T: toggle touch neurons (touch_neurons_active)")

    # ============================================================
    # RIGHT COLUMN: PER-SCREEN CONTROLS
    # ============================================================
    section("right", "Per-screen controls")

    line("right", "Matrix (M):", fs=section_fs, color=green)
    bullet("right", "Left click on a neuron: force ON/OFF")
    bullet("right", "Right click on a neuron: add/remove from plots (Curves/Raster)")

    block_gap("right", 10)
    line("right", "Curves (C):", fs=section_fs, color=green)
    bullet("right", "Shows activation values for selected neurons")
    bullet("right", "E: group menu   |   A: autoscale ON/OFF   |   Backspace: reset scale")

    block_gap("right", 10)
    line("right", "Raster (X):", fs=section_fs, color=green)
    bullet("right", "Shows spike times (rising edges, >= threshold) for selected neurons")

    block_gap("right", 10)
    line("right", "Movement (D):", fs=section_fs, color=green)
    bullet("right", "Left click: add/remove food (green circle)")
    bullet("right", "Right click: add/remove obstacle (red square)")
    bullet("right", "The triangle worm stays inside the red arena frame")

    block_gap("right", 10)
    line("right", "Options (O):", fs=section_fs, color=green)
    bullet("right", "Up/Down: move selection")
    bullet("right", "ENTER: toggle selected option")
    bullet("right", "Mouse: click a line to toggle ON/OFF")

    block_gap("right", 10)
    line("right", "Action bar tools:", fs=section_fs, color=green)
    bullet("right", "Excel loader: keyboard-based path entry, then ENTER to load")
    bullet("right", "Worm functions: Arrow keys + ENTER (or mouse) to toggle")

    # ----------------------------
    # Safety note if text overflows
    # ----------------------------
    if y_left > max_y:
        sim.draw_text(surface, "Note: left column overflow (reduce font or increase window).", left_x, max_y - 30, (200, 200, 200), font_size=24, align="left")
    if y_right > max_y:
        sim.draw_text(surface, "Note: right column overflow (reduce font or increase window).", right_x, max_y - 30, (200, 200, 200), font_size=24, align="left")
