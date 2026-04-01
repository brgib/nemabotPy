"""simulator.py

Core simulation state and shared utilities.

This module owns the main `Simulator` class:
- Pygame window management (fullscreen, 4K).
- Shared colors, fonts and `draw_text()` helper.
- Simulation control (step mode, iterations per second).
- Global state shared by all screens.

The menu screen (screen_menu.py) relies on `sim.menu_items` and
`sim.menu_selection_index` defined here.
"""


import time
import pygame
import math
import random
import os
# postsynaptic, muscles, musDleft, musVleft, musDright, musVright, threshold, Negthreshold, Negthreshold, Hyperpolarisation, createpostsynaptic
from connectome import *
from excel_connectome_pylightxl import ExcelConnectomePylightxl
from gap_junction import GapJunctionSymmetric

class Simulator:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1920, 1080
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Nemabot")

        # --- Menu (mosaic) state -------------------------------------------------
        # The menu is a grid of clickable thumbnails representing each screen.
        # Files are expected to be alongside the executable (relative paths).
        self.menu_buttons = []  # filled by screen_menu.draw() for click hit-testing
        self.menu_selection_index = 0

        # Define menu entries once, so both keyboard navigation and click routing
        # can target the same list.
        # NOTE: Image files are expected to exist on disk (PNG recommended). If an
        # image cannot be loaded, the menu will render a placeholder tile.
        self.menu_items = [
            {"key": "neuralMatrix", "label": "Neural matrix", "image": "neuralMatrix.png", "attr": "display_neuron_matrix"},
            {"key": "neuralWaves", "label": "Neural waves", "image": "neuralWaves.png", "attr": "display_curve_screen"},
            {"key": "neuralThresholdWaves", "label": "Threshold waves", "image": "neuralThresholdWaves.png", "attr": "display_wave_screen"},
            {"key": "wormSchematic", "label": "Worm schematic", "image": "wormSchematic.png", "attr": "display_worm_screen"},
            {"key": "wormWorld", "label": "Worm world", "image": "wormWorld.png", "attr": "display_movement_screen"},
            {"key": "help", "label": "Help", "image": "help.png", "attr": "display_help_screen"},
        ]

        self._menu_image_cache = {}  # {image_path: pygame.Surface}


        self.colorsName = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'triangle': (0, 0, 255)
        }
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (255, 165, 0), (75, 0, 130),
            (238, 130, 238), (0, 128, 128), (128, 128, 0), (128, 0, 128),
            (192, 192, 192), (255, 20, 147), (0, 191, 255), (50, 205, 50)
        ]
        self.base_font_size = 32
        self.font_size = self.base_font_size
        self.font = pygame.font.Font(None, self.font_size)

        # Display flags
        self.display_movement_screen = False
        self.display_curve_screen = False   # Waves
        self.display_neuron_matrix = False
        self.display_wave_screen = False    # Raster (spikes)
        self.display_help_screen = False
        self.display_menu_screen = True
        self.display_worm_screen = False
        self.display_options_screen = False
        # New screens
        self.display_excel_loader_screen = False
        self.display_forced_functions_screen = False
        self.is_4k_mode = False
        self.fullscreen_mode = False

        # Simulation control (paused by default)
        self.game_active = False
        self.running = False
        self.start_time = 0
        self.current_time = 0
        self.iteration = 0
        self.iterations_per_second = 10
        self.simulation_time_accumulator = 0.0
        self.step_mode = True
        self.step_ready = False
        self.touch_neurons_active = False

        # Data
        self.neuron_data = {}
        self.forced_active_neurons = set()
        # Forced functions screen aggregates into this set (logical neuron names).
        # Your UI (screen_forced_functions.py) maintains sim.forced_neurons.
        self.forced_neurons = set()
        self.forced_functions_state = {}
        self.functions_selection_index = 0
        # Excel loader screen state
        self.excel_path = ""
        self.excel_status = "No file loaded."
        self.loaded_network_from_excel = None
        self.gap_model = None
        self.excel_apply_gap = True
        self.gap_gain = 0.01
        self.dropdown_menu_visible = False
        self.dropdown_menu_rect = None
        self.scale_reset = False
        self.auto_scale_waves = True  # autoscale limited to Waves (curves)

        # Random initialization of neuron states
        self.random_init_min = 0.0
        self.random_init_max = float(threshold) * 1.10
        self.random_init_step = max(0.5, float(threshold) / 20.0)
        self.random_init_target_mode = 'all'  # 'all' or 'configured'
        self.random_init_last_count = 0
        self.random_init_last_range = (self.random_init_min, self.random_init_max)

        self.preconfigured_sets = {
            'Muscles Tête': ['MVL01', 'MVL02', 'MVD01', 'MVD02', 'MDR01', 'MDR02', 'MVR01', 'MVR02'],
            'Muscles Ventraux': ['MVL07', 'MVL08', 'MVL09', 'MVR07', 'MVR08', 'MVR09'],
            'Muscles Dorsaux': ['MDL07', 'MDL08', 'MDL09', 'MVR07', 'MVR08', 'MVR09'],
            'Muscles Dorsaux gauche': ['MDL07', 'MDL08', 'MDL09', 'MDL10', 'MDL11', 'MDL12', 'MDL13', 'MDL14', 'MDL15', 'MDL16', 'MDL17', 'MDL18', 'MDL19', 'MDL20', 'MDL21', 'MDL22', 'MDL23'],
            'Muscles Ventraux gauche': ['MVL07', 'MVL08', 'MVL09', 'MVL10', 'MVL11', 'MVL12', 'MVL13', 'MVL14', 'MVL15', 'MVL16', 'MVL17', 'MVL18', 'MVL19', 'MVL20', 'MVL21', 'MVL22', 'MVL23'],
            'Muscle Dorsaux droite': ['MDR07', 'MDR08', 'MDR09', 'MDR10', 'MDR11', 'MDR12', 'MDR13', 'MDR14', 'MDR15', 'MDR16', 'MDR17', 'MDR18', 'MDR19', 'MDR20', 'MDL21', 'MDR22', 'MDR23'],
            'Muscle Ventraux droite': ['MVR07', 'MVR08', 'MVR09', 'MVR10', 'MVR11', 'MVR12', 'MVR13', 'MVR14', 'MVR15', 'MVR16', 'MVR17', 'MVR18', 'MVR19', 'MVR20', 'MVL21', 'MVR22', 'MVR23']
        }

        # Triangle (movement)
        self.triangle_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        self.triangle_angle = 0
        self.triangle_speed = 4

        # Environment
        self.food_items = []
        self.obstacles = []
        self.food = 0
        self.touch = False

        # postsynaptic columns
        self.thisState = 0
        self.nextState = 1
        self.PreviousValue = 2
        self.activated = 3
        self.decroissance = 4

        self.neurones = []
        self.time_values = []

        # Diagnostics for the threshold screen
        self.max_postsynaptic_value = 0
        self.neurons_above_threshold = []
        self.dist = 15
        self.tfood = 0
        self.log_created = False
        self.file = None

        # Analog muscle model: muscles do not fire like neurons.
        # They integrate excitation continuously, saturate, then relax back to rest.
        self.muscle_input_gain = 0.08
        self.muscle_relaxation = 0.12
        self.muscle_inhibition_gain = 0.20
        self.muscle_max_activation = 100.0
        self.muscle_neighbor_coupling = 0.10
        self.muscle_activation = {}

        # Worm functions (all OFF)
        self.worm_functions = [
            {'name': 'Photodétection (ASI, AFD, AWB, AWC, ASK)', 'neurons': ['ASI', 'AFD', 'AWB', 'AWC', 'ASK'], 'active': False},
            {'name': 'Osmosensation (ASH, FLP, OLQ, IL1, AVM, ALM)', 'neurons': ['ASH', 'FLP', 'OLQ', 'IL1', 'AVM', 'ALM'], 'active': False},
            {'name': 'Chimiosensation (ASE, ASG, ASI, ASK, AWA, AWB, AWC)', 'neurons': ['ASE', 'ASG', 'ASI', 'ASK', 'AWA', 'AWB', 'AWC'], 'active': False},
            {'name': 'Mécanoréception (AVM, ALM, PLM, PVD, FLP, OLQ, IL1)', 'neurons': ['AVM', 'ALM', 'PLM', 'PVD', 'FLP', 'OLQ', 'IL1'], 'active': False},
            {'name': 'Faim / satiété (ADF, ASG, ASI, ASJ, NSM, URX)', 'neurons': ['ADF', 'ASG', 'ASI', 'ASJ', 'NSM', 'URX'], 'active': False},
            {'name': 'Oxygène / CO₂ (URX, AQR, PQR, BAG, SDQ)', 'neurons': ['URX', 'AQR', 'PQR', 'BAG', 'SDQ'], 'active': False},
            {'name': 'Thermosensation (AFD, AWC)', 'neurons': ['AFD', 'AWC'], 'active': False},
            {'name': 'Locomotion (DA, DB, VA, VB, DD, VD)', 'neurons': ['DA', 'DB', 'VA', 'VB', 'DD', 'VD'], 'active': False},
            {'name': 'Muscles pharyngiens (MC, M3, M4, M5, M1, I1, I2, I3)', 'neurons': ['MC', 'M3', 'M4', 'M5', 'M1', 'I1', 'I2', 'I3'], 'active': False},
            {'name': "Réflexe d'évitement (ASH, FLP, AVA, AVB)", 'neurons': ['ASH', 'FLP', 'AVA', 'AVB'], 'active': False},
            {'name': 'Détection étirement/forme (PVD, DVA)', 'neurons': ['PVD', 'DVA'], 'active': False},
            {'name': 'Neurones de contact (OLQ, IL1, CEP)', 'neurons': ['OLQ', 'IL1', 'CEP'], 'active': False},
            {'name': 'Système reproducteur (HSN, VC)', 'neurons': ['HSN', 'VC'], 'active': False},
            {'name': 'Neurones sociaux / spécialisés (RMG, SAA, SAB, URA)', 'neurons': ['RMG', 'SAA', 'SAB', 'URA'], 'active': False},
        ]
        self.update_forced_active_neurons()

        try:
            self.background_image = pygame.image.load("ver_c_elegans_01_1920.jpg").convert()
            self.background_image = pygame.transform.scale(self.background_image, (self.WIDTH, self.HEIGHT))
        except pygame.error:
            self.background_image = None

    def draw_text(self, surface, text, x, y, color=None, font_size=None, align='left'):
        color = color or self.WHITE
        font = pygame.font.Font(None, font_size) if font_size else self.font
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        if align == 'left':
            textrect.topleft = (x, y)
        elif align == 'right':
            textrect.topright = (x, y)
        elif align == 'center':
            textrect.center = (x, y)
        surface.blit(textobj, textrect)

    def update_forced_active_neurons(self):
        """Recompute the set of postsynaptic neurons forced active each cycle.

        Sources:
        - self.worm_functions (legacy option toggles)
        - self.forced_neurons (new forced-functions screen, logical neuron names)

        Special pseudo-neurons (handled elsewhere):
        - FOOD_SENSOR, TOUCH_SENSOR
        """
        self.forced_active_neurons.clear()

        # Legacy worm_functions
        for func in getattr(self, 'worm_functions', []):
            if func.get('active'):
                for n in func.get('neurons', []):
                    for key in postsynaptic:
                        if key.startswith(n):
                            self.forced_active_neurons.add(key)

        # New forced functions screen
        for n in getattr(self, 'forced_neurons', set()):
            if n in ('FOOD_SENSOR', 'TOUCH_SENSOR'):
                continue
            for key in postsynaptic:
                if key.startswith(n):
                    self.forced_active_neurons.add(key)


    # ---------------------------------------------------------------------
    # Menu helpers
    # ---------------------------------------------------------------------
    def get_menu_thumbnail(self, image_path, size):
        """Load + cache menu thumbnails.

        If the image cannot be loaded, returns a placeholder tile surface.
        """
        cache_key = (image_path, size)
        if cache_key in self._menu_image_cache:
            return self._menu_image_cache[cache_key]

        try:
            img = pygame.image.load(image_path).convert_alpha()
            thumb = pygame.transform.smoothscale(img, size)
        except Exception:
            # Placeholder tile
            thumb = pygame.Surface(size, pygame.SRCALPHA)
            thumb.fill((30, 30, 30))
            pygame.draw.rect(thumb, (120, 120, 120), thumb.get_rect(), 2)
            self.draw_text(thumb, "Missing", size[0] // 2, size[1] // 2 - 10, (220, 220, 220), font_size=28, align='center')
            self.draw_text(thumb, image_path, size[0] // 2, size[1] // 2 + 18, (180, 180, 180), font_size=18, align='center')

        self._menu_image_cache[cache_key] = thumb
        return thumb

    def move_menu_selection(self, dx, dy, cols):
        """Move selection in a grid and wrap around horizontally/vertically."""
        n = len(self.menu_items)
        if n == 0:
            self.menu_selection_index = 0
            return

        rows = (n + cols - 1) // cols
        idx = self.menu_selection_index
        r = idx // cols
        c = idx % cols

        # Horizontal move with wrap.
        if dx:
            c = (c + dx) % cols

        # Vertical move with wrap.
        if dy:
            r = (r + dy) % rows

        new_idx = r * cols + c
        # If the target cell is beyond the last item, clamp to last item in row.
        if new_idx >= n:
            new_idx = n - 1
        self.menu_selection_index = new_idx

    def _clamp_random_init_bounds(self):
        """Keep random initialization bounds valid and ordered."""
        try:
            self.random_init_min = float(self.random_init_min)
        except Exception:
            self.random_init_min = 0.0
        try:
            self.random_init_max = float(self.random_init_max)
        except Exception:
            self.random_init_max = self.random_init_min
        if self.random_init_min > self.random_init_max:
            self.random_init_max = self.random_init_min
        if self.random_init_max < self.random_init_min:
            self.random_init_min = self.random_init_max

    def set_random_init_bound(self, which, value):
        if which == 'min':
            self.random_init_min = float(value)
        else:
            self.random_init_max = float(value)
        self._clamp_random_init_bounds()

    def adjust_random_init_bound(self, which, delta):
        if which == 'min':
            self.random_init_min = float(self.random_init_min) + float(delta)
        else:
            self.random_init_max = float(self.random_init_max) + float(delta)
        self._clamp_random_init_bounds()

    def _expand_configured_neuron_names(self):
        configured = set()

        configured.update(getattr(self, 'forced_active_neurons', set()))
        configured.update(getattr(self, 'neuron_data', {}).keys())

        for logical_name in getattr(self, 'forced_neurons', set()):
            if logical_name in ('FOOD_SENSOR', 'TOUCH_SENSOR'):
                continue
            for key in postsynaptic.keys():
                if key.startswith(logical_name):
                    configured.add(key)

        for func in getattr(self, 'worm_functions', []):
            if func.get('active'):
                for logical_name in func.get('neurons', []):
                    for key in postsynaptic.keys():
                        if key.startswith(logical_name):
                            configured.add(key)

        return configured

    def get_random_init_targets(self, mode=None):
        mode = mode or getattr(self, 'random_init_target_mode', 'all')
        if mode == 'configured':
            names = [n for n in postsynaptic.keys() if n in self._expand_configured_neuron_names()]
            if names:
                return names
        return list(postsynaptic.keys())

    def trigger_random_initialization(self, mode=None):
        """Initialize neuron states with random values in the configured range.

        Mode:
          - 'all': all neurons in postsynaptic
          - 'configured': plotted/forced/configured neurons only; falls back to all if empty
        """
        self._clamp_random_init_bounds()
        mode = mode or getattr(self, 'random_init_target_mode', 'all')
        targets = self.get_random_init_targets(mode=mode)
        if not targets:
            self.random_init_last_count = 0
            return 0

        lo = float(self.random_init_min)
        hi = float(self.random_init_max)

        for name in targets:
            if name not in postsynaptic:
                continue
            value = lo if abs(hi - lo) < 1e-12 else random.uniform(lo, hi)
            postsynaptic[name][self.thisState] = value
            postsynaptic[name][self.nextState] = value
            postsynaptic[name][self.PreviousValue] = value
            postsynaptic[name][self.activated] = 1.0 if value >= threshold else 0.0
            postsynaptic[name][self.decroissance] = 0.0

        self.random_init_target_mode = mode
        self.random_init_last_count = len(targets)
        self.random_init_last_range = (lo, hi)

        # Reset muscle integrator so the visible body state follows the new neuron state cleanly.
        self.reset_analog_muscles()
        return len(targets)

    def toggle_fullscreen(self):
        self.fullscreen_mode = not self.fullscreen_mode
        flags = pygame.FULLSCREEN if self.fullscreen_mode else 0
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)

    def toggle_4k_mode(self):
        self.is_4k_mode = not self.is_4k_mode
        self.WIDTH, self.HEIGHT = (3840, 2160) if self.is_4k_mode else (1920, 1080)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font_size = int(self.base_font_size * 0.75) if self.is_4k_mode else self.base_font_size
        self.font = pygame.font.Font(None, self.font_size)
        try:
            img = pygame.image.load("ver_c_elegans_01_1920.jpg").convert()
            self.background_image = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
        except pygame.error:
            pass

    def _all_muscle_names(self):
        return [n for n in postsynaptic.keys() if n[:3] in muscles]

    def reset_analog_muscles(self):
        self.muscle_activation = {n: 0.0 for n in self._all_muscle_names()}

    def update_analog_muscles(self):
        if not self.muscle_activation:
            self.reset_analog_muscles()

        updated = {}
        for name in self._all_muscle_names():
            current = float(self.muscle_activation.get(name, 0.0))
            command = float(postsynaptic.get(name, [0.0, 0.0, 0.0])[self.thisState]) if name in postsynaptic else 0.0
            if command >= 0.0:
                current += self.muscle_input_gain * command
            else:
                current -= self.muscle_inhibition_gain * abs(command)
            current -= self.muscle_relaxation * current
            if current < 0.0:
                current = 0.0
            elif current > self.muscle_max_activation:
                current = self.muscle_max_activation
            updated[name] = current

        # small smoothing along each longitudinal chain to produce cleaner waves
        chains = [
            [f"MDL{i:02d}" for i in range(7, 24)],
            [f"MDR{i:02d}" for i in range(7, 24)],
            [f"MVL{i:02d}" for i in range(7, 24)],
            [f"MVR{i:02d}" for i in range(7, 24)],
        ]
        coupling = max(0.0, min(0.5, self.muscle_neighbor_coupling))
        if coupling > 0.0:
            smoothed = dict(updated)
            for chain in chains:
                for idx, name in enumerate(chain):
                    if name not in updated:
                        continue
                    neighbors = []
                    if idx > 0 and chain[idx - 1] in updated:
                        neighbors.append(updated[chain[idx - 1]])
                    if idx + 1 < len(chain) and chain[idx + 1] in updated:
                        neighbors.append(updated[chain[idx + 1]])
                    if neighbors:
                        mean_n = sum(neighbors) / len(neighbors)
                        smoothed[name] = updated[name] + coupling * (mean_n - updated[name])
            updated = smoothed

        self.muscle_activation = updated

    def motorcontrol(self):
        self.accumleft = 0
        self.accumright = 0
        source = self.muscle_activation if self.muscle_activation else {n: postsynaptic[n][self.thisState] for n in postsynaptic if n[:3] in muscles}
        for pscheck, value in source.items():
            if pscheck in musDleft or pscheck in musVleft:
                self.accumleft += value
            elif pscheck in musDright or pscheck in musVright:
                self.accumright += value
        if self.accumleft == 0 and self.accumright == 0:
            self.stop()
        elif self.accumright <= 0 and self.accumleft < 0:
            self.left_rot(); self.bwd()
        elif self.accumright <= 0 and self.accumleft >= 0:
            self.right_rot()
        elif self.accumright >= 0 and self.accumleft <= 0:
            self.left_rot()
        elif self.accumright >= 0 and self.accumleft > 0:
            self.right_rot(); self.fwd()
        else:
            self.stop()

    def dendrite_accumulate(self, dneuron):
        # If an Excel-loaded connectome is active, use it; otherwise fall back to
        # the hard-coded connectome.py functions.
        if self.loaded_network_from_excel is not None:
            self.loaded_network_from_excel.apply(dneuron, postsynaptic, self.nextState)
            return
        f = eval(dneuron); f()

    def fire_neuron(self, fneuron):
        if fneuron != "MVULVA":
            if self.loaded_network_from_excel is not None:
                self.loaded_network_from_excel.apply(fneuron, postsynaptic, self.nextState)
                return
            f = eval(fneuron); f()

    def set_neuron_value(self, fneuron, value):
        if fneuron != "MVULVA":
            postsynaptic[fneuron][self.nextState] = value

    def bwd(self): self.move_triangle_backward()
    def fwd(self): self.move_triangle_forward()
    def left_rot(self): self.rotate_triangle_left()
    def right_rot(self): self.rotate_triangle_right()
    def stop(self): pass

    def run_connectome(self):
        neuron_list = list(postsynaptic.keys())
        num_neurons = len(neuron_list)
        random_mask = random.randint(0, 0xFFFFFFFF)
        masked_indices = [(idx ^ random_mask, idx) for idx in range(num_neurons)]
        masked_indices.sort()

        for neuron in self.forced_active_neurons:
            postsynaptic[neuron][self.thisState] = threshold
            postsynaptic[neuron][self.nextState] = threshold


        # --- GAP junction coupling (optional, symmetric) ---
        if self.gap_model is not None and self.excel_apply_gap:
            try:
                self.gap_model.apply_step(postsynaptic, self.thisState, self.nextState, gain=self.gap_gain)
            except Exception:
                pass

        for _, idx in masked_indices:
            ps = neuron_list[idx]
            # --- Inverse decay (always applied; prevents runaway growth) ---
            if postsynaptic[ps][self.nextState] > postsynaptic[ps][self.thisState]:
                postsynaptic[ps][self.decroissance] = 0
            else:
                postsynaptic[ps][self.decroissance] += 1

            decay_k = 0.5
            decay_offset = 5.0
            n = postsynaptic[ps][self.decroissance] + 1  # avoid 0
            decay_factor = 1.0 - (decay_k / (n + decay_offset))

            postsynaptic[ps][self.nextState] *= decay_factor
            if postsynaptic[ps][self.nextState] < 0:
                postsynaptic[ps][self.nextState] = 0

            if postsynaptic[ps][self.thisState] >= threshold:
                if ps[:3] not in muscles:
                    self.fire_neuron(ps)
                    postsynaptic[ps][self.nextState] = 0 # NegthresholdHyperpolarisation
            else:
                postsynaptic[ps][self.PreviousValue] = postsynaptic[ps][self.thisState]
            if postsynaptic[ps][self.nextState] < Negthreshold:
                postsynaptic[ps][self.nextState] = Negthreshold

        for _, idx in masked_indices:
            ps = neuron_list[idx]
            if postsynaptic[ps][self.nextState] < Negthreshold and postsynaptic[ps][self.nextState] != NegthresholdHyperpolarisation:
                postsynaptic[ps][self.nextState] = Negthreshold
            postsynaptic[ps][self.thisState] = postsynaptic[ps][self.nextState]

        self.update_analog_muscles()
        self.motorcontrol()
        self.iteration += 1

    
    def load_network_from_excel(self, xlsx_path: str, chem_sheet: str, gap_symmetric_sheet: str | None = None, apply_gap: bool = True) -> bool:
        """Load chemical sheet (+ optional symmetric gap-junction sheet) from XLSX (pylightxl).

        - chem_sheet: e.g. 'herm chem grouped'
        - gap_symmetric_sheet: e.g. 'herm gap jn grouped symmetric' (optional)
        - apply_gap: toggle applying the GAP model during simulation
        """
        try:
            chem = ExcelConnectomePylightxl.load(xlsx_path, sheet_name=chem_sheet)
            self.loaded_network_from_excel = chem
            self.excel_path = xlsx_path
            self.excel_apply_gap = bool(apply_gap)

            # Ensure postsynaptic has entries for all neurons in this network, then reset values.
            chem.ensure_postsynaptic_entries(postsynaptic)
            chem.reset_postsynaptic(postsynaptic)

            # GAP symmetric (optional)
            self.gap_model = None
            if gap_symmetric_sheet:
                gap_net = ExcelConnectomePylightxl.load(xlsx_path, sheet_name=gap_symmetric_sheet)
                gap_net.ensure_postsynaptic_entries(postsynaptic)
                self.gap_model = GapJunctionSymmetric.from_excel_connectome(gap_net)

            self.excel_status = (
                f"Loaded: {os.path.basename(xlsx_path)} | chem='{chem_sheet}'"
                + (f" | gap='{gap_symmetric_sheet}'" if gap_symmetric_sheet else "")
                + f" | neurons: {len(chem.neurons)}"
            )
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.loaded_network_from_excel = None
            self.gap_model = None
            self.excel_status = f"Excel load failed: {e}"
            return False


    def unload_excel_network(self) -> None:
        """Return to the built-in hard-coded connectome.py network."""
        self.loaded_network_from_excel = None
        self.excel_status = "No file loaded."
        createpostsynaptic()

    def start_simulation(self):
        self.neurones = []
        self.time_values = []

        # Diagnostics for the threshold screen
        self.max_postsynaptic_value = 0
        self.neurons_above_threshold = []
        # Initialize postsynaptic storage.
        if self.loaded_network_from_excel is not None:
            self.loaded_network_from_excel.reset_postsynaptic(postsynaptic)
        else:
            createpostsynaptic()
        self.dist = 15
        self.tfood = 0
        if not self.log_created:
            filename = f"nemabot_simulation_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            self.file = open(filename, mode='w')
            neurone_names_str = ",".join(postsynaptic.keys())
            self.file.write(f"iteration,{neurone_names_str}\n")
            self.log_created = True
        self.thisState = 0
        self.nextState = 1
        self.reset_analog_muscles()
        self.running = True
        self.start_time = time.time()

    def step_simulation(self):
        self.current_time = time.time() - self.start_time
        self.time_values.append(self.current_time)

        # Apply pseudo sensors from the forced-functions screen.
        if 'TOUCH_SENSOR' in getattr(self, 'forced_neurons', set()):
            self.touch = True
        if 'FOOD_SENSOR' in getattr(self, 'forced_neurons', set()):
            self.food = max(self.food, 20)

        # Keep forced_active_neurons in sync (in case UI toggles changed)
        self.update_forced_active_neurons()

        if self.touch or (self.touch_neurons_active and 0 < self.dist < 30):
            self.activate_touch_neurons()
        else:
            if self.food > 15:
                for n in ("ADFL","ADFR","ASGR","ASGL","ASIL","ASIR","ASJR","ASJL"):
                    self.dendrite_accumulate(n)

        self.run_connectome()
        self.update_worm_movement()

        if self.tfood > 30:
            self.tfood = 0

        for neuron, data in self.neuron_data.items():
            activation_value = postsynaptic[neuron][self.thisState]
            prev_value = postsynaptic[neuron][self.PreviousValue]
            data['values'].append(activation_value)
            if activation_value >= threshold and prev_value < threshold:
                data['activation_times'].append(self.iteration)

        if self.file:
            neurone_values_str = f"{self.iteration}," + ",".join(str(postsynaptic[pscheck][self.thisState]) for pscheck in postsynaptic) + '\\n'
            self.file.write(neurone_values_str)

    def move_triangle_forward(self):
        self.triangle_pos[0] += self.triangle_speed * math.cos(math.radians(self.triangle_angle))
        self.triangle_pos[1] += self.triangle_speed * math.sin(math.radians(self.triangle_angle))

    def move_triangle_backward(self):
        self.triangle_pos[0] -= self.triangle_speed * math.cos(math.radians(self.triangle_angle))
        self.triangle_pos[1] -= self.triangle_speed * math.sin(math.radians(self.triangle_angle))

    def rotate_triangle_left(self):
        self.triangle_angle -= 5

    def rotate_triangle_right(self):
        self.triangle_angle += 5

    def activate_touch_neurons(self):
        for n in ["FLPR", "FLPL", "ASHL", "ASHR", "IL1VL", "IL1VR", "OLQDL", "OLQDR", "OLQVR", "OLQVL"]:
            self.dendrite_accumulate(n)

    def add_food(self):
        self.tfood += 10

    def update_worm_movement(self):
        num_segments = 17
        if not hasattr(self, 'muscle_segments'):
            self.muscle_segments = [{} for _ in range(num_segments)]
        if not self.muscle_activation:
            self.reset_analog_muscles()

        contraction_scale = 0.55
        max_offset = 24.0
        saturation_value = self.muscle_max_activation if self.muscle_max_activation > 0 else 1.0

        for i in range(num_segments):
            muscle_num = f"{7 + i:02d}"
            act_MDL = float(self.muscle_activation.get(f"MDL{muscle_num}", 0.0))
            act_MDR = float(self.muscle_activation.get(f"MDR{muscle_num}", 0.0))
            act_MVL = float(self.muscle_activation.get(f"MVL{muscle_num}", 0.0))
            act_MVR = float(self.muscle_activation.get(f"MVR{muscle_num}", 0.0))

            dorsal_avg = (act_MDL + act_MDR) / 2.0
            ventral_avg = (act_MVL + act_MVR) / 2.0
            total_activation = max(0.0, (dorsal_avg + ventral_avg) / 2.0)
            normalized_activation = min(total_activation / saturation_value, 1.0)

            # muscles shorten proportionally to activation, without neuronal thresholding
            length_factor = 1.0 - normalized_activation * (1.0 - contraction_scale)

            # dorsal/ventral imbalance bends the body
            curvature_balance = (dorsal_avg - ventral_avg) / saturation_value
            curvature_offset = max(-max_offset, min(max_offset, max_offset * curvature_balance))

            self.muscle_segments[i] = {
                "length_factor": length_factor,
                "curvature_offset": curvature_offset,
                "contraction": normalized_activation,
            }

    def shutdown(self):
        self.game_active = False
        self.running = False
        if self.file:
            self.file.close()
            self.file = None
        pygame.quit()