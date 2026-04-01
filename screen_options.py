import math
import pygame


def _ensure_options_state(sim):
    if not hasattr(sim, "options_selection_index"):
        sim.options_selection_index = 0


def _wrap_text(font, text, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _layout(rect, count):
    cols = 2 if count > 8 else 1
    rows = int(math.ceil(count / max(cols, 1)))
    margin_x = int(rect.width * 0.05)
    top = 100
    bottom = 90
    gutter = 28
    usable_w = rect.width - 2 * margin_x - gutter * (cols - 1)
    col_w = usable_w // cols
    usable_h = rect.height - top - bottom
    row_h = max(44, min(62, usable_h // max(rows, 1)))
    return cols, rows, margin_x, top, col_w, row_h, gutter


def _get_button_rect(rect, idx, count):
    cols, rows, margin_x, top, col_w, row_h, gutter = _layout(rect, count)
    rows_per_col = int(math.ceil(count / cols))
    col = idx // rows_per_col
    row = idx % rows_per_col
    x = margin_x + col * (col_w + gutter)
    y = top + row * row_h
    return pygame.Rect(x, y, col_w, row_h)


def draw(sim, surface, rect):
    _ensure_options_state(sim)
    surface.fill(sim.BLACK)

    title_fs = 40 if rect.width <= 1920 else 48
    body_fs = 20 if rect.width <= 1920 else 24
    hint_fs = 24 if rect.width <= 1920 else 28

    sim.draw_text(surface, "Options : Activation des fonctions du ver",
                  rect.width // 2, 28, sim.colorsName['green'], font_size=title_fs, align='center')

    count = len(sim.worm_functions)
    if count == 0:
        sim.draw_text(surface, "Aucune fonction disponible.", rect.centerx, rect.centery, sim.WHITE, font_size=28, align='center')
        return

    font = pygame.font.Font(None, body_fs)
    sim.option_hitboxes = []

    for idx, func in enumerate(sim.worm_functions):
        btn_rect = _get_button_rect(rect, idx, count)
        active = bool(func.get('active', False))
        fill = (70, 170, 70) if active else (110, 55, 55)
        pygame.draw.rect(surface, fill, btn_rect, border_radius=14)

        if idx == sim.options_selection_index:
            pygame.draw.rect(surface, (255, 255, 255), btn_rect, 4, border_radius=14)
        else:
            pygame.draw.rect(surface, sim.WHITE, btn_rect, 2, border_radius=14)

        label = f"{func['name']} : {'ON' if active else 'OFF'}"
        text_lines = _wrap_text(font, label, btn_rect.width - 24)
        y = btn_rect.top + max(6, (btn_rect.height - len(text_lines) * (body_fs - 2)) // 2)
        for line in text_lines[:2]:
            sim.draw_text(surface, line, btn_rect.centerx, y, sim.BLACK, font_size=body_fs, align='center')
            y += body_fs - 2

        sim.option_hitboxes.append((btn_rect, idx))

    sim.draw_text(surface,
                  "ENTER : (dés)activer  |  ↑/↓ : naviguer  |  SPACE : retour menu  |  ESC : retour menu",
                  rect.width // 2, rect.height - 42, sim.WHITE, font_size=hint_fs, align='center')


def handle_mouse_click(sim, pos):
    _ensure_options_state(sim)
    count = len(sim.worm_functions)
    hitboxes = getattr(sim, 'option_hitboxes', None)
    if hitboxes is None:
        rect = sim.screen.get_rect()
        hitboxes = [(_get_button_rect(rect, idx, count), idx) for idx in range(count)]

    for btn_rect, idx in hitboxes:
        if btn_rect.collidepoint(pos):
            sim.options_selection_index = idx
            sim.worm_functions[idx]['active'] = not sim.worm_functions[idx]['active']
            sim.update_forced_active_neurons()
            break


def handle_key(sim, key):
    _ensure_options_state(sim)

    count = max(1, len(sim.worm_functions))
    if key == pygame.K_UP:
        sim.options_selection_index = (sim.options_selection_index - 1) % count
    elif key == pygame.K_DOWN:
        sim.options_selection_index = (sim.options_selection_index + 1) % count
    elif key == pygame.K_RETURN:
        idx = max(0, min(sim.options_selection_index, len(sim.worm_functions) - 1))
        if sim.worm_functions:
            sim.worm_functions[idx]['active'] = not sim.worm_functions[idx]['active']
            sim.update_forced_active_neurons()
