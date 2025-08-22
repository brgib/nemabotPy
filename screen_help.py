# Auto-generated Nemabot multi-file package (with requested fixes).


import pygame

def draw(sim, surface, rect):
    surface.fill(sim.BLACK)
    # Header / title
    sim.draw_text(surface, "Nemabot – Aide & Raccourcis", rect.centerx, 20, sim.colorsName['green'], font_size=40, align='center')

    y = 70
    lh = 30
    # Général
    sim.draw_text(surface, "Général :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "ESC: Quitter    F11: Plein écran    K: 4K (quadrillage 2×2)", 40, y); y += lh
    sim.draw_text(surface, "P: Basculer pas-à-pas    S: Avancer d'un pas (si pas-à-pas)", 40, y); y += lh
    sim.draw_text(surface, "+ / - : Ajuster les itérations par seconde", 40, y); y += lh
    sim.draw_text(surface, "E: Ouvrir/fermer le menu des neurones (écran Courbes)", 40, y); y += lh
    sim.draw_text(surface, "Retour arrière (⌫): Réinitialiser les échelles (Courbes)", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Navigation entre écrans :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "H: Aide    M: Matrice    C: Courbes    X: Vagues    D: Déplacement    W: Ver    O: Options", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Déplacement (D) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Clic gauche: Ajouter/Supprimer un point de nourriture", 40, y); y += lh
    sim.draw_text(surface, "Clic droit: Ajouter/Supprimer un obstacle", 40, y); y += lh
    sim.draw_text(surface, "F: Ajouter un stimulus 'nourriture'    T: Activer/Désactiver neurones tactiles", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Matrice (M) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Clic gauche: Forcer (ON/OFF) l'activation d'un neurone", 40, y); y += lh
    sim.draw_text(surface, "Clic droit: Ajouter/retirer le neurone de la sélection de tracé", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Courbes (C) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Tracé des valeurs des neurones sélectionnés (depuis la Matrice)", 40, y); y += lh
    sim.draw_text(surface, "E: Ouvre un menu de groupes préconfigurés (p.ex. muscles tête, dorsaux...)", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Vagues (X) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Affiche un raster d'activation (> seuil) des neurones sélectionnés", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Ver (W) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Vue profil + dessus, dépend des activations musculaires (MDL/MDR/MVL/MVR)", 40, y); y += lh

    y += 10
    sim.draw_text(surface, "Options (O) :", 20, y, sim.colorsName['green'], font_size=32); y += lh
    sim.draw_text(surface, "Activer/Désactiver des fonctions physiologiques du ver (photodétection, thermo...)", 40, y); y += lh
    sim.draw_text(surface, "Les fonctions actives forcent des ensembles de neurones à franchir le seuil", 40, y); y += lh

    # Footer with live info
    sim.draw_text(surface, f"Iter/s: {sim.iterations_per_second}    Iteration: {sim.iteration}    Food: {sim.food}    Touch: {sim.touch}", 20, rect.height - 40)
