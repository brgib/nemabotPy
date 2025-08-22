# Auto-generated split of Nemabot into multi-file structure.
# You can move these into your repo and run nemabot.py


import pygame

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    sim.draw_text(surface, "Commandes Générales :", 10, 10, sim.colorsName['green'], font_size=36)
    sim.draw_text(surface, "P: Mode pas à pas (toggle)  |  S: Un pas", 10, 50)
    sim.draw_text(surface, "M: Matrice  |  D: Déplacement  |  C: Courbes  |  X: Vagues  |  W: Ver  |  O: Options  |  H: Aide", 10, 80)
    sim.draw_text(surface, "F: Ajouter nourriture  |  T: Toggle touché  |  F11: Plein écran  |  K: 4K", 10, 110)

    dynamic_y = rect.height - 140
    sim.draw_text(surface, f"Mode 4K: {'Activé' if sim.is_4k_mode else 'Désactivé'}", 10, dynamic_y)
    sim.draw_text(surface, f"Food: {sim.food}", 10, dynamic_y + 30)
    sim.draw_text(surface, f"Touch: {sim.touch}", 10, dynamic_y + 60)
    sim.draw_text(surface, f"Iteration N°:{sim.iteration}", 10, dynamic_y + 90)
    sim.draw_text(surface, f"Iter/s: {sim.iterations_per_second}", 10, dynamic_y + 120)
