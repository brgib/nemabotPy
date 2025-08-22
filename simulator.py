# Auto-generated split of Nemabot into multi-file structure.
# You can move these into your repo and run nemabot.py


import time
import pygame
import math
import random
from connectome import *  # expects postsynaptic, muscles, musDleft, musVleft, musDright, musVright, threshold, Negthreshold, NegthresholdHyperpolarisation, createpostsynaptic

class Simulator:
    """
    Central state + utilities. Screens receive this instance.
    """
    def __init__(self):
        pygame.init()

        # Resolution / screen
        self.WIDTH, self.HEIGHT = 1920, 1080
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Nemabot")

        # Colors / font
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
        self.display_curve_screen = False
        self.display_neuron_matrix = False
        self.display_wave_screen = False
        self.display_help_screen = True
        self.display_worm_screen = False
        self.display_options_screen = False
        self.is_4k_mode = False
        self.fullscreen_mode = False

        # Simulation control
        self.game_active = False
        self.running = False
        self.start_time = 0
        self.current_time = 0
        self.iteration = 0
        self.iterations_per_second = 10
        self.simulation_time_accumulator = 0.0
        self.step_mode = True
        self.step_ready = False

        # Neuron data and selection
        self.neuron_data = {}
        self.forced_active_neurons = set()
        self.dropdown_menu_visible = False
        self.dropdown_menu_rect = None
        self.scale_reset = False

        # Preconfigured sets (copied from original file)
        self.preconfigured_sets = {
            'Muscles Tête': ['MVL01', 'MVL02', 'MVD01', 'MVD02', 'MDR01', 'MDR02', 'MVR01', 'MVR02'],
            'Muscles Ventraux': ['MVL07', 'MVL08', 'MVL09', 'MVR07', 'MVR08', 'MVR09'],
            'Muscles Dorsaux': ['MDL07', 'MDL08', 'MDL09', 'MVR07', 'MVR08', 'MVR09'],
            'Muscles Dorsaux gauche': ['MDL07', 'MDL08', 'MDL09', 'MDL10', 'MDL11', 'MDL12', 'MDL13', 'MDL14', 'MDL15', 'MDL16', 'MDL17', 'MDL18', 'MDL19', 'MDL20', 'MDL21', 'MDL22', 'MDL23'],
            'Muscles Ventraux gauche': ['MVL07', 'MVL08', 'MVL09', 'MVL10', 'MVL11', 'MVL12', 'MVL13', 'MVL14', 'MVL15', 'MVL16', 'MVL17', 'MVL18', 'MVL19', 'MVL20', 'MVL21', 'MVL22', 'MVL23'],
            'Muscle Dorsaux droite': ['MDR07', 'MDR08', 'MDR09', 'MDR10', 'MDR11', 'MDR12', 'MDR13', 'MDR14', 'MDR15', 'MDR16', 'MDR17', 'MDR18', 'MDR19', 'MDR20', 'MDL21', 'MDR22', 'MDR23'],
            'Muscle Ventraux droite': ['MVR07', 'MVR08', 'MVR09', 'MVR10', 'MVR11', 'MVR12', 'MVR13', 'MVR14', 'MVR15', 'MVR16', 'MVR17', 'MVR18', 'MVR19', 'MVR20', 'MVL21', 'MVR22', 'MVR23']
        }

        # Triangle (movement screen)
        self.triangle_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        self.triangle_angle = 0
        self.triangle_speed = 4

        # Environment
        self.food_items = []
        self.obstacles = []
        self.food = 0
        self.touch = False

        # columns in postsynaptic
        self.thisState = 0
        self.nextState = 1
        self.PreviousValue = 2
        self.activated = 3
        self.decroissance = 4

        # misc
        self.neurones = []
        self.time_values = []
        self.dist = 15
        self.tfood = 0
        self.log_created = False
        self.file = None

        # Worm functions (options screen)
        self.worm_functions = [
            {'name': 'Photodétection (ASI, AFD, AWB, AWC, ASK)', 'neurons': ['ASI', 'AFD', 'AWB', 'AWC', 'ASK'], 'active': True},
            {'name': 'Osmosensation (ASH, FLP, OLQ, IL1, AVM, ALM)', 'neurons': ['ASH', 'FLP', 'OLQ', 'IL1', 'AVM', 'ALM'], 'active': True},
            {'name': 'Chimiosensation (ASE, ASG, ASI, ASK, AWA, AWB, AWC)', 'neurons': ['ASE', 'ASG', 'ASI', 'ASK', 'AWA', 'AWB', 'AWC'], 'active': True},
            {'name': 'Mécanoréception (AVM, ALM, PLM, PVD, FLP, OLQ, IL1)', 'neurons': ['AVM', 'ALM', 'PLM', 'PVD', 'FLP', 'OLQ', 'IL1'], 'active': True},
            {'name': 'Faim / satiété (ADF, ASG, ASI, ASJ, NSM, URX)', 'neurons': ['ADF', 'ASG', 'ASI', 'ASJ', 'NSM', 'URX'], 'active': True},
            {'name': 'Oxygène / CO₂ (URX, AQR, PQR, BAG, SDQ)', 'neurons': ['URX', 'AQR', 'PQR', 'BAG', 'SDQ'], 'active': True},
            {'name': 'Thermosensation (AFD, AWC)', 'neurons': ['AFD', 'AWC'], 'active': True},
            {'name': 'Locomotion (DA, DB, VA, VB, DD, VD)', 'neurons': ['DA', 'DB', 'VA', 'VB', 'DD', 'VD'], 'active': True},
            {'name': 'Muscles pharyngiens (MC, M3, M4, M5, M1, I1, I2, I3)', 'neurons': ['MC', 'M3', 'M4', 'M5', 'M1', 'I1', 'I2', 'I3'], 'active': True},
            {'name': "Réflexe d'évitement (ASH, FLP, AVA, AVB)", 'neurons': ['ASH', 'FLP', 'AVA', 'AVB'], 'active': True},
            {'name': 'Détection étirement/forme (PVD, DVA)', 'neurons': ['PVD', 'DVA'], 'active': True},
            {'name': 'Neurones de contact (OLQ, IL1, CEP)', 'neurons': ['OLQ', 'IL1', 'CEP'], 'active': True},
            {'name': 'Système reproducteur (HSN, VC)', 'neurons': ['HSN', 'VC'], 'active': True},
            {'name': 'Neurones sociaux / spécialisés (RMG, SAA, SAB, URA)', 'neurons': ['RMG', 'SAA', 'SAB', 'URA'], 'active': True},
        ]
        self.update_forced_active_neurons()

        # Background image (optional, ignore errors)
        try:
            self.background_image = pygame.image.load("ver_c_elegans_01_1920.jpg").convert()
            self.background_image = pygame.transform.scale(self.background_image, (self.WIDTH, self.HEIGHT))
        except pygame.error:
            self.background_image = None

    # ---------- small utilities ----------
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

    def toggle_fullscreen(self):
        self.fullscreen_mode = not self.fullscreen_mode
        flags = pygame.FULLSCREEN if self.fullscreen_mode else 0
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)

    def toggle_4k_mode(self):
        self.is_4k_mode = not self.is_4k_mode
        self.WIDTH, self.HEIGHT = (3840, 2160) if self.is_4k_mode else (1920, 1080)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        if self.is_4k_mode:
            self.font_size = int(self.base_font_size * 0.75)
        else:
            self.font_size = self.base_font_size
        self.font = pygame.font.Font(None, self.font_size)
        # reload bg if exists
        try:
            img = pygame.image.load("ver_c_elegans_01.jpg").convert()
            self.background_image = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
        except pygame.error:
            pass

    # ---------- options helpers ----------
    def update_forced_active_neurons(self):
        self.forced_active_neurons.clear()
        for func in self.worm_functions:
            if func['active']:
                for n in func['neurons']:
                    for key in postsynaptic:
                        if key.startswith(n):
                            self.forced_active_neurons.add(key)

    # ---------- connectome & movement (from original) ----------
    def motorcontrol(self):
        self.accumleft = 0
        self.accumright = 0
        for pscheck in postsynaptic:
            if pscheck in musDleft or pscheck in musVleft:
                self.accumleft += postsynaptic[pscheck][self.thisState]
            elif pscheck in musDright or pscheck in musVright:
                self.accumright += postsynaptic[pscheck][self.thisState]

        new_speed = abs(self.accumleft) + abs(self.accumright)
        new_speed = min(max(new_speed, 75), 150)

        if self.accumleft == 0 and self.accumright == 0:
            self.stop()
        elif self.accumright <= 0 and self.accumleft < 0:
            turnratio = float(self.accumright) / float(self.accumleft) if self.accumleft != 0 else 0
            if turnratio <= 0.6:
                self.left_rot()
            elif turnratio >= 2:
                self.right_rot()
            self.bwd()
        elif self.accumright <= 0 and self.accumleft >= 0:
            self.right_rot()
        elif self.accumright >= 0 and self.accumleft <= 0:
            self.left_rot()
        elif self.accumright >= 0 and self.accumleft > 0:
            turnratio = float(self.accumright) / float(self.accumleft) if self.accumleft != 0 else 0
            if turnratio <= 0.6:
                self.left_rot()
            elif turnratio >= 2:
                self.right_rot()
            self.fwd()
        else:
            self.stop()

    def dendrite_accumulate(self, dneuron):
        f = eval(dneuron)
        f()

    def fire_neuron(self, fneuron):
        if fneuron != "MVULVA":
            f = eval(fneuron)
            f()

    def set_neuron_value(self, fneuron, value):
        if fneuron != "MVULVA":
            postsynaptic[fneuron][self.nextState] = value

    def bwd(self):
        self.move_triangle_backward()

    def fwd(self):
        self.move_triangle_forward()

    def left_rot(self):
        self.rotate_triangle_left()

    def right_rot(self):
        self.rotate_triangle_right()

    def stop(self):
        pass

    def run_connectome(self):
        neuron_list = list(postsynaptic.keys())
        num_neurons = len(neuron_list)
        random_mask = random.randint(0, 0xFFFFFFFF)
        masked_indices = [(idx ^ random_mask, idx) for idx in range(num_neurons)]
        masked_indices.sort()

        # force active neurons
        for neuron in self.forced_active_neurons:
            postsynaptic[neuron][self.thisState] = threshold
            postsynaptic[neuron][self.nextState] = threshold

        for _, idx in masked_indices:
            ps = neuron_list[idx]

            if postsynaptic[ps][self.nextState] > postsynaptic[ps][self.thisState]:
                postsynaptic[ps][self.decroissance] = 0
            else:
                postsynaptic[ps][self.nextState] = postsynaptic[ps][self.nextState] * 0.9

            if postsynaptic[ps][self.thisState] >= threshold:
                if ps[:3] not in muscles:
                    self.fire_neuron(ps)
                    postsynaptic[ps][self.nextState] = NegthresholdHyperpolarisation
            else:
                postsynaptic[ps][self.PreviousValue] = postsynaptic[ps][self.thisState]
            if postsynaptic[ps][self.nextState] < Negthreshold:
                postsynaptic[ps][self.nextState] = Negthreshold

        for _, idx in masked_indices:
            ps = neuron_list[idx]
            if postsynaptic[ps][self.nextState] < Negthreshold and postsynaptic[ps][self.nextState] != NegthresholdHyperpolarisation:
                postsynaptic[ps][self.nextState] = Negthreshold
            postsynaptic[ps][self.thisState] = postsynaptic[ps][self.nextState]

        self.motorcontrol()
        self.iteration += 1

    # ----- simulation lifecycle -----
    def start_simulation(self):
        self.neurones = []
        self.time_values = []

        createpostsynaptic()
        self.dist = 15
        self.tfood = 0

        if not self.log_created:
            filename = f"nemabot_simulation_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            self.file = open(filename, mode='w')
            neurone_names_str = ",".join(postsynaptic.keys())
            header = f"iteration,{neurone_names_str}\n"
            self.file.write(header)
            self.log_created = True

        self.thisState = 0
        self.nextState = 1

        self.running = True
        self.start_time = time.time()

    def step_simulation(self):
        self.current_time = time.time() - self.start_time
        self.time_values.append(self.current_time)

        if self.touch or (False and 0 < self.dist < 30):  # touch handling could be extended
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
            data['values'].append(activation_value)
            if activation_value > threshold:
                data['activation_times'].append(self.iteration)

        if self.file:
            neurone_values_str = f"{self.iteration}," + ",".join(str(postsynaptic[pscheck][self.thisState]) for pscheck in postsynaptic) + '\\n'
            self.file.write(neurone_values_str)

    # ----- movement helpers used by movement screen -----
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

    # ----- worm kinematics (profile/top) -----
    def update_worm_movement(self):
        num_segments = 17  # muscles 07..23
        if not hasattr(self, 'muscle_segments'):
            self.muscle_segments = [{} for _ in range(num_segments)]

        contraction_scale = 0.1
        max_offset = 30
        saturation_value = threshold

        for i in range(num_segments):
            muscle_num = f"{7 + i:02d}"
            act_MDL = postsynaptic.get(f"MDL{muscle_num}", [0, 0, 0])[self.thisState] if f"MDL{muscle_num}" in postsynaptic else 0
            act_MDR = postsynaptic.get(f"MDR{muscle_num}", [0, 0, 0])[self.thisState] if f"MDR{muscle_num}" in postsynaptic else 0
            act_MVL = postsynaptic.get(f"MVL{muscle_num}", [0, 0, 0])[self.thisState] if f"MVL{muscle_num}" in postsynaptic else 0
            act_MVR = postsynaptic.get(f"MVR{muscle_num}", [0, 0, 0])[self.thisState] if f"MVR{muscle_num}" in postsynaptic else 0

            dorsal_avg = (act_MDL + act_MDR) / 2.0
            ventral_avg = (act_MVL + act_MVR) / 2.0

            raw_activation = (dorsal_avg + ventral_avg) / 2.0
            normalized_activation = min(max(raw_activation, 0), saturation_value) / saturation_value

            length_factor = 1 - normalized_activation * (1 - contraction_scale)

            normalized_curvature = (dorsal_avg - ventral_avg)
            curvature_offset = max_offset * normalized_curvature

            self.muscle_segments[i] = {
                "length_factor": length_factor,
                "curvature_offset": curvature_offset,
                "contraction": normalized_activation
            }

    # ----- shutdown -----
    def shutdown(self):
        self.game_active = False
        self.running = False
        if self.file:
            self.file.close()
            self.file = None
        pygame.quit()
