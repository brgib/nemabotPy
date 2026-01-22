"""nemabot.py

Application entry point.

Responsibilities:
- Show splash screen.
- Run the main loop (events, stepping the simulation, rendering).
- Route keyboard/mouse events to the active screen module.

Menu UX:
- After the splash screen, the default view is the mosaic menu
  (screen_menu.py).
- From any screen: Space or Enter returns to the mosaic menu.
- From the mosaic menu: arrow keys move the selection and Space/Enter opens
  the selected tile.
"""


import pygame
from simulator import Simulator
import screen_menu
import screen_help
import screen_matrix
import screen_curve   # Waves (courbes)
import screen_wave    # Raster (déclenchementws)
import screen_movement
import screen_worm
import screen_options
import screen_excel_loader
import screen_forced_functions

def splash(sim):
    rect = sim.screen.get_rect()
    if sim.background_image is not None:
        sim.screen.blit(sim.background_image, (0, 0))
    else:
        sim.screen.fill(sim.BLACK)
    sim.draw_text(sim.screen, "Nemabot – C. elegans Neural Network Simulator", rect.centerx, rect.centery - 60, sim.WHITE, font_size=72, align='center')
    sim.draw_text(sim.screen, "Press any key to start", rect.centerx, rect.centery + 20, sim.WHITE, font_size=36, align='center')
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            elif event.type == pygame.QUIT:
                waiting = False
                pygame.event.post(pygame.event.Event(pygame.QUIT))

def main():
    sim = Simulator()
    clock = pygame.time.Clock()
    splash(sim)
    sim.game_active = True
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        sim.simulation_time_accumulator += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_key(sim, event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                route_mouse(sim, event.pos, event.button)
            elif event.type == pygame.TEXTINPUT:
                if getattr(sim, 'display_excel_loader_screen', False):
                    screen_excel_loader.handle_text(sim, event.text)

        if not sim.running:
            sim.start_simulation()

        if sim.step_mode:
            if sim.step_ready:
                sim.step_simulation()
                sim.step_ready = False
        else:
            target = 1.0 / max(1, sim.iterations_per_second)
            while sim.simulation_time_accumulator >= target:
                sim.step_simulation()
                sim.simulation_time_accumulator -= target

        rect = sim.screen.get_rect()
        if sim.display_help_screen:
            screen_help.draw(sim, sim.screen, rect)
        elif sim.display_menu_screen:
            screen_menu.draw(sim, sim.screen, rect)
        elif sim.display_neuron_matrix:
            screen_matrix.draw(sim, sim.screen, rect)
        elif sim.display_curve_screen:
            screen_curve.draw(sim, sim.screen, rect)
        elif sim.display_wave_screen:
            screen_wave.draw(sim, sim.screen, rect)
        elif sim.display_movement_screen:
            screen_movement.draw(sim, sim.screen, rect)
        elif sim.display_worm_screen:
            screen_worm.draw(sim, sim.screen, rect)
        elif sim.display_excel_loader_screen:
            screen_excel_loader.draw(sim, sim.screen, rect)
        elif sim.display_forced_functions_screen:
            screen_forced_functions.draw(sim, sim.screen, rect)
        elif sim.display_options_screen:
            screen_options.draw(sim, sim.screen, rect)
        else:
            screen_help.draw(sim, sim.screen, rect)
        pygame.display.flip()
    sim.shutdown()

def handle_key(sim, event):
    k = event.key

    # ------------------------------------------------------------------
    # ESC behavior:
    # - If we are in the main menu, ESC quits the program.
    # - From any other screen, ESC returns to the main menu.
    # ------------------------------------------------------------------
    if k == pygame.K_ESCAPE:
        if getattr(sim, 'display_menu_screen', False):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        else:
            set_screen(sim, menu=True)
        return

    # ------------------------------------------------------------------
    # SPACE behavior (user request):
    # - From the menu: open the selected tile / action.
    # - From any other screen: return to the menu.
    # ------------------------------------------------------------------
    if k == pygame.K_SPACE:
        if getattr(sim, 'display_menu_screen', False):
            screen_menu.handle_key(sim, k)
        else:
            set_screen(sim, menu=True)
        return

    # ------------------------------------------------------------------
    # ENTER behavior:
    # - Reserved for in-screen interactions (not for navigating menu).
    #   In particular, Options uses ENTER to toggle items.
    # - Excel / Forced-functions keep their own ENTER handling.
    # ------------------------------------------------------------------
    if k == pygame.K_RETURN:
        if getattr(sim, 'display_options_screen', False):
            screen_options.handle_key(sim, k)
        elif getattr(sim, 'display_excel_loader_screen', False):
            screen_excel_loader.handle_key(sim, k)
        elif getattr(sim, 'display_forced_functions_screen', False):
            screen_forced_functions.handle_key(sim, k)
        # In other screens, ENTER does nothing by design.
        return

    # If the menu is visible, arrow keys should navigate the mosaic.
    if getattr(sim, 'display_menu_screen', False) and k in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
        cols = 3 if len(sim.menu_items) <= 6 else 4
        screen_menu.handle_key(sim, k, cols_hint=cols)
        return

    # If Options screen is visible, let arrows move selection.
    if getattr(sim, 'display_options_screen', False) and k in (pygame.K_UP, pygame.K_DOWN):
        screen_options.handle_key(sim, k)
        return

    # If forced-functions screen is visible, arrow keys navigate that grid.
    if getattr(sim, 'display_forced_functions_screen', False) and k in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
        screen_forced_functions.handle_key(sim, k)
        return

    # If Excel loader screen is visible, forward most keys to it.
    if getattr(sim, 'display_excel_loader_screen', False):
        screen_excel_loader.handle_key(sim, k)
        return

    # Quick shortcuts
    if k == pygame.K_h:
        set_screen(sim, help=True)
    elif k == pygame.K_m:
        set_screen(sim, matrix=True)
    elif k == pygame.K_c:
        set_screen(sim, curve=True)
    elif k == pygame.K_x:
        set_screen(sim, wave=True)
    elif k == pygame.K_d:
        set_screen(sim, movement=True)
    elif k == pygame.K_w:
        set_screen(sim, worm=True)
    elif k == pygame.K_o:
        set_screen(sim, options=True)
    elif k == pygame.K_p:
        sim.step_mode = not sim.step_mode
        sim.step_ready = False
        if not sim.step_mode:
            sim.simulation_time_accumulator = 0.0
    elif k == pygame.K_s and sim.step_mode:
        sim.step_ready = True
    elif k == pygame.K_k:
        sim.toggle_4k_mode()
    elif k == pygame.K_F11:
        sim.toggle_fullscreen()
    elif k in (pygame.K_PLUS, pygame.K_KP_PLUS):
        sim.iterations_per_second += 5
    elif k in (pygame.K_MINUS, pygame.K_KP_MINUS):
        sim.iterations_per_second = max(1, sim.iterations_per_second - 5)
    elif k == pygame.K_f:
        sim.add_food()
    elif k == pygame.K_t:
        sim.touch_neurons_active = not sim.touch_neurons_active
    elif k == pygame.K_e:
        sim.dropdown_menu_visible = not sim.dropdown_menu_visible
    elif k == pygame.K_BACKSPACE:
        if sim.display_curve_screen:
            sim.scale_reset = True
    elif k == pygame.K_a:
        if sim.display_curve_screen:
            sim.auto_scale_waves = not sim.auto_scale_waves


def set_screen(sim, menu=False, help=False, matrix=False, curve=False, wave=False, movement=False, worm=False, options=False,
               excel=False, forced_functions=False):
    """Activate exactly one screen (and disable all others).

    This prevents UI routing bugs where multiple display_* flags stay True and
    keyboard/mouse events go to the wrong screen.
    """
    sim.display_menu_screen = bool(menu)
    sim.display_help_screen = bool(help)
    sim.display_neuron_matrix = bool(matrix)
    sim.display_curve_screen = bool(curve)    # Waves
    sim.display_wave_screen = bool(wave)      # Raster
    sim.display_movement_screen = bool(movement)
    sim.display_worm_screen = bool(worm)
    sim.display_options_screen = bool(options)

    # Additional screens
    sim.display_excel_loader_screen = bool(excel)
    sim.display_forced_functions_screen = bool(forced_functions)


def route_mouse(sim, pos, button):
    if sim.display_neuron_matrix:
        screen_matrix.handle_mouse_click(sim, pos, button)
    elif sim.display_movement_screen:
        screen_movement.handle_mouse_click(sim, pos, button)
    elif sim.display_curve_screen:
        screen_curve.handle_mouse_click(sim, pos, button)
    elif sim.display_excel_loader_screen:
        # Excel screen currently uses keyboard primarily; keep click for future extensions
        pass
    elif sim.display_forced_functions_screen:
        screen_forced_functions.handle_mouse_click(sim, pos)
    elif sim.display_options_screen:
        screen_options.handle_mouse_click(sim, pos)
    elif sim.display_menu_screen:
        screen_menu.handle_mouse_click(sim, pos)


if __name__ == "__main__":
    main()
