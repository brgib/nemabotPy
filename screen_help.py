# Auto-generated Nemabot multi-file package (autoscale only on Waves).


import pygame

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    sim.draw_text(surface, "Nemabot – Aide & Raccourcis", rect.centerx, 20, sim.colorsName['green'], font_size=40, align='center')
    y = 70; lh = 30
    sim.draw_text(surface, "Général :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "ESC: Quitter    F11: Plein écran    K: 4K", 40, y); y += lh
    sim.draw_text(surface, "P: Pas-à-pas ON/OFF    S: Un pas (si pas-à-pas)", 40, y); y += lh
    sim.draw_text(surface, "+ / - : Itérations/s", 40, y); y += lh
    sim.draw_text(surface, "E (Courbes): menu groupes    ⌫ (Courbes): reset échelle    A (Courbes): autoscale ON/OFF", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Écrans :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "H: Aide    M: Matrice    C: Waves (courbes)    X: Déclenchements (raster)    D: Déplacement    W: Ver    O: Options", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Déplacement (D) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "ClicG: Nourriture    ClicD: Obstacle    F: Stimulus nourriture    T: Neurones tactiles", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Matrice (M) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "ClicG: Forcer ON/OFF    ClicD: Ajouter/retirer des waves/raster", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Waves (C) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Tracé de valeurs; autoscale uniquement ici (A).", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Déclenchements (X) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Raster des fronts montants (>= seuil).", 40, y); y += lh

    sim.draw_text(surface, f"Iter/s: {sim.iterations_per_second}    Iteration: {sim.iteration}    Food: {sim.food}    Touch: {sim.touch}", 20, rect.height - 40)
