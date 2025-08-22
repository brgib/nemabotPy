# Auto-generated split of Nemabot into multi-file structure.
# You can move these into your repo and run nemabot.py


import pygame
from simulator import Simulator

# Screens
import screen_help
import screen_matrix
import screen_curve
import screen_wave
import screen_movement
import screen_worm
import screen_options

def main():
    sim = Simulator()
    clock = pygame.time.Clock()

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

        if not sim.running:
            sim.start_simulation()

        if not sim.step_mode or (sim.step_mode and sim.step_ready):
            target = 1.0 / max(1, sim.iterations_per_second)
            while sim.simulation_time_accumulator >= target:
                sim.step_simulation()
                sim.simulation_time_accumulator -= target
            sim.step_ready = False

        rect = sim.screen.get_rect()
        if sim.display_help_screen:
            screen_help.draw(sim, sim.screen, rect)
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
        elif sim.display_options_screen:
            screen_options.draw(sim, sim.screen, rect)
        else:
            screen_help.draw(sim, sim.screen, rect)

        pygame.display.flip()

    sim.shutdown()

def handle_key(sim, event):
    k = event.key
    if k == pygame.K_ESCAPE:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    elif k == pygame.K_h:
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
        # touch toggle (if you later wire a flag in Simulator you can use it)
        pass
    elif k == pygame.K_e:
        sim.dropdown_menu_visible = not sim.dropdown_menu_visible

def set_screen(sim, help=False, matrix=False, curve=False, wave=False, movement=False, worm=False, options=False):
    sim.display_help_screen = help
    sim.display_neuron_matrix = matrix
    sim.display_curve_screen = curve
    sim.display_wave_screen = wave
    sim.display_movement_screen = movement
    sim.display_worm_screen = worm
    sim.display_options_screen = options

def route_mouse(sim, pos, button):
    if sim.display_neuron_matrix:
        screen_matrix.handle_mouse_click(sim, pos, button)
    elif sim.display_movement_screen:
        screen_movement.handle_mouse_click(sim, pos, button)
    elif sim.display_curve_screen:
        screen_curve.handle_mouse_click(sim, pos, button)
    elif sim.display_options_screen:
        screen_options.handle_mouse_click(sim, pos)

if __name__ == "__main__":
    main()
