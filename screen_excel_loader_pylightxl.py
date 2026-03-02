import re
import os
import pygame

try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

from excel_matrix_pylightxl import list_sheets, pylightxl_available, pylightxl_error


def _ensure_state(sim):
    if not hasattr(sim, "__dict__"):
        return
    sim.excel_path = getattr(sim, "excel_path", "")
    sim.excel_status = getattr(sim, "excel_status", "No file loaded.")
    sim.excel_sheets = getattr(sim, "excel_sheets", [])
    sim.excel_models = getattr(sim, "excel_models", [])  # list[dict{name, chem, gap}]
    sim.excel_model_index = getattr(sim, "excel_model_index", 0)
    sim.excel_apply_gap = getattr(sim, "excel_apply_gap", True)
    sim._excel_ignore_textinput_once = getattr(sim, "_excel_ignore_textinput_once", False)


def _open_dialog():
    if tk is None or filedialog is None:
        return None
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    root.destroy()
    return path



def _find_sheet(sheets, *, must_contain):
    """Find the first sheet whose *word tokens* contain all required tokens.

    Important: avoids the classic trap where 'asymmetric' contains 'symmetric' as a substring.
    We tokenize sheet names into alphanum words, then match tokens on words.
    """
    want = [t.lower() for t in must_contain]
    for s in sheets:
        low = s.lower()
        words = re.findall(r"[a-z0-9]+", low)
        if all(t in words for t in want):
            return s
    return None


def _build_models(sheets):
    """Build model presets from SI7-like workbook sheet names."""
    models = []
    # canonical names used in your SI7 file
    candidates = [
        ("Hermaphrodite", "herm"),
        ("Male", "male"),
        ("Juvenile", "juvenile"),
    ]
    for label, prefix in candidates:
        chem = _find_sheet(sheets, must_contain=[prefix, "chem", "grouped"])
        gap = _find_sheet(sheets, must_contain=[prefix, "gap", "jn", "grouped", "symmetric"])
        if chem:
            models.append({"name": label, "chem": chem, "gap": gap or ""})
    return models


def _refresh_workbook_state(sim):
    """Load sheet names and build model list from the current excel_path."""
    sim.excel_sheets = list_sheets(sim.excel_path)
    sim.excel_models = _build_models(sim.excel_sheets)
    sim.excel_model_index = 0 if sim.excel_models else 0


def handle_key(sim, key):
    _ensure_state(sim)
    if not hasattr(sim, "__dict__"):
        return

    if key in (pygame.K_ESCAPE, pygame.K_SPACE):
        sim.display_excel_loader_screen = False
        sim.display_menu_screen = True
        return

    if key == pygame.K_o:
        sim._excel_ignore_textinput_once = True
        if tk is None or filedialog is None:
            sim.excel_status = "tkinter not available: type the path manually."
            return
        path = _open_dialog()
        if path:
            sim.excel_path = path
            if not pylightxl_available():
                sim.excel_sheets = []
                sim.excel_models = []
                sim.excel_model_index = 0
                sim.excel_status = "pylightxl not available: " + pylightxl_error()
                return
            try:
                _refresh_workbook_state(sim)
                if sim.excel_models:
                    sim.excel_status = f"Selected: {os.path.basename(path)} ({len(sim.excel_models)} models detected)"
                else:
                    sim.excel_status = f"Selected: {os.path.basename(path)} (no model sheets detected)"
            except Exception as e:
                sim.excel_sheets = []
                sim.excel_models = []
                sim.excel_model_index = 0
                sim.excel_status = f"Excel error: {e}"
        return

    if key in (pygame.K_UP, pygame.K_PAGEUP):
        if sim.excel_models:
            sim.excel_model_index = max(0, sim.excel_model_index - 1)
        return

    if key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
        if sim.excel_models:
            sim.excel_model_index = min(len(sim.excel_models) - 1, sim.excel_model_index + 1)
        return

    if key == pygame.K_j:
        sim.excel_apply_gap = not sim.excel_apply_gap
        return

    if key == pygame.K_BACKSPACE:
        if sim.excel_path:
            sim.excel_path = sim.excel_path[:-1]
        return

    if key == pygame.K_RETURN:
        if not sim.excel_path:
            sim.excel_status = "No path. Press O or type a file path."
            return
        if not os.path.isfile(sim.excel_path):
            sim.excel_status = "File not found: " + sim.excel_path
            return
        if not pylightxl_available():
            sim.excel_status = "pylightxl not available: " + pylightxl_error()
            return

        # Ensure workbook parsed
        if not sim.excel_sheets or not sim.excel_models:
            try:
                _refresh_workbook_state(sim)
            except Exception as e:
                sim.excel_status = f"Excel error: {e}"
                return

        if not sim.excel_models:
            sim.excel_status = "No compatible model found in workbook (need '* chem grouped' sheets)."
            return

        model = sim.excel_models[sim.excel_model_index]
        chem_sheet = model["chem"]
        gap_sheet = model["gap"] or None

        if not hasattr(sim, "load_network_from_excel"):
            sim.excel_status = "Simulator has no load_network_from_excel(). Replace simulator.py with patched version."
            return

        try:
            ok = sim.load_network_from_excel(
                sim.excel_path,
                chem_sheet,
                gap_symmetric_sheet=gap_sheet,
                apply_gap=bool(sim.excel_apply_gap),
            )
            if ok:
                sim.excel_status = f"Loaded: {model['name']} (chem + gap symmetric)"
            else:
                err = getattr(sim, "excel_last_error", "")
                sim.excel_status = "Load failed: " + (err if err else "returned False")
        except Exception as e:
            sim.excel_status = "Load failed: " + str(e)
        return


def handle_text(sim, text):
    _ensure_state(sim)
    if not hasattr(sim, "__dict__"):
        return
    if getattr(sim, "_excel_ignore_textinput_once", False):
        sim._excel_ignore_textinput_once = False
        return
    if text:
        sim.excel_path += text


def draw(sim, surface, rect):
    _ensure_state(sim)
    if not hasattr(sim, "__dict__"):
        return

    surface.fill(sim.BLACK)

    title_y = int(rect.height * 0.05)
    sim.draw_text(surface, "Load neuron network (Excel)", rect.centerx, title_y,
                  sim.colorsName['green'], font_size=52, align='center')
    sim.draw_text(surface, "O: open dialog   Enter: load model   Up/Down: select model   J: apply gap   Space/ESC: menu",
                  rect.centerx, title_y + 45, sim.WHITE, font_size=24, align='center')

    box = pygame.Rect(int(rect.width * 0.08), int(rect.height * 0.22), int(rect.width * 0.84), 70)
    pygame.draw.rect(surface, (25, 25, 25), box, border_radius=14)
    pygame.draw.rect(surface, sim.WHITE, box, 2, border_radius=14)
    sim.draw_text(surface, sim.excel_path, box.left + 20, box.centery, sim.WHITE, font_size=26, align='left')

    sim.draw_text(surface, sim.excel_status, rect.centerx, int(rect.height * 0.32), sim.WHITE, font_size=24, align='center')

    left = pygame.Rect(int(rect.width * 0.08), int(rect.height * 0.40), int(rect.width * 0.52), int(rect.height * 0.52))
    pygame.draw.rect(surface, (15, 15, 15), left, border_radius=14)
    pygame.draw.rect(surface, (120, 120, 120), left, 2, border_radius=14)
    sim.draw_text(surface, "Models", left.left + 15, left.top + 15, sim.WHITE, font_size=24, align='left')

    if not sim.excel_models:
        sim.draw_text(surface, "(no model detected)", left.left + 20, left.top + 55, (180, 180, 180), font_size=20, align='left')
    else:
        y = left.top + 55
        max_lines = int((left.height - 70) / 28)
        start = max(0, sim.excel_model_index - max_lines // 2)
        end = min(len(sim.excel_models), start + max_lines)
        start = max(0, end - max_lines)

        for idx in range(start, end):
            m = sim.excel_models[idx]
            color = (255, 255, 0) if idx == sim.excel_model_index else (200, 200, 200)
            sim.draw_text(surface, m["name"], left.left + 25, y, color, font_size=22, align='left')
            y += 28

    right = pygame.Rect(int(rect.width * 0.64), int(rect.height * 0.40), int(rect.width * 0.28), int(rect.height * 0.52))
    pygame.draw.rect(surface, (15, 15, 15), right, border_radius=14)
    pygame.draw.rect(surface, (120, 120, 120), right, 2, border_radius=14)
    sim.draw_text(surface, "Load plan", right.left + 15, right.top + 15, sim.WHITE, font_size=24, align='left')

    if sim.excel_models:
        model = sim.excel_models[sim.excel_model_index]
        chem = model["chem"]
        gap = model["gap"] if model["gap"] else "(missing)"
        sim.draw_text(surface, f"Chemical: {chem}", right.left + 15, right.top + 60, sim.WHITE, font_size=20, align='left')
        sim.draw_text(surface, f"GAP symmetric: {gap}", right.left + 15, right.top + 90, sim.WHITE, font_size=20, align='left')
    else:
        sim.draw_text(surface, "Chemical: (none)", right.left + 15, right.top + 60, sim.WHITE, font_size=20, align='left')
        sim.draw_text(surface, "GAP symmetric: (none)", right.left + 15, right.top + 90, sim.WHITE, font_size=20, align='left')

    sim.draw_text(surface, f"[J] Apply GAP model: {'ON' if sim.excel_apply_gap else 'OFF'}",
                  right.left + 15, right.top + 140, sim.WHITE, font_size=20, align='left')

    if not pylightxl_available():
        sim.draw_text(surface, "pylightxl not available: " + pylightxl_error(),
                      rect.centerx, rect.height - 30, (255, 180, 180), font_size=20, align='center')