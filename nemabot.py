import time
import pygame
import sys
import math
import random  # Pour la génération de nombres aléatoires
from connectome import *


class NemabotSimulation:
    def __init__(self):
        pygame.init()

        # Résolution par défaut
        self.WIDTH, self.HEIGHT = 1920, 1080

        # Variables pour gérer le mode 4K
        self.is_4k_mode = False

        # Détection de la résolution de l'écran
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h

        # Définition de la résolution initiale
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Nemabot")

        try:
            self.background_image = pygame.image.load("ver_c_elegans_01_1920.jpg").convert()
            self.background_image = pygame.transform.scale(self.background_image, (self.WIDTH, self.HEIGHT))
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image : {e}")
            sys.exit(1)

        # Couleurs
        self.colorsName = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'triangle': (0, 0, 255)
        }

        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (255, 165, 0), (75, 0, 130),
            (238, 130, 238), (0, 128, 128), (128, 128, 0), (128, 0, 128),
            (192, 192, 192), (255, 20, 147), (0, 191, 255), (50, 205, 50)
        ]

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # Taille de police par défaut
        self.base_font_size = 32
        self.font_size = self.base_font_size
        self.font = pygame.font.Font(None, self.font_size)

        # Variables pour le contrôle des écrans
        self.display_movement_screen = False
        self.display_curve_screen = False
        self.display_neuron_matrix = False
        self.display_wave_screen = False
        self.display_help_screen = True
        self.display_worm_screen = False

        # Position et paramètres initiaux du ver (triangle)
        self.triangle_pos = [self.WIDTH // 2, self.HEIGHT // 2]
        self.triangle_angle = 0
        self.triangle_speed = 4

        self.display_options_screen = False

        self.food_items = []
        self.obstacles = []
        self.food = 0
        self.touch = False

        # Autres variables du programme
        self.game_active = False
        self.running = False
        self.start_time = 0
        self.current_time = 0

        # Données pour le suivi des neurones
        self.neuron_data = {}

        # Modes de simulation
        self.step_mode = True
        self.step_ready = False
        self.touch_neurons_active = False
        self.fullscreen_mode = False

        self.neurones = []
        self.time_values = []
        self.dist = 15
        self.tfood = 0
        self.log_created = False

        self.accumright = 0
        self.accumleft = 0
        self.thisState = 0
        self.nextState = 1
        self.PreviousValue = 2
        self.activated = 3
        self.decroissance = 4
        self.iteration = 0

        self.file = None

        # Pré-configurations de neurones
        self.preconfigured_sets = {
            'Muscles Tête': ['MVL01', 'MVL02', 'MVD01', 'MVD02', 'MDR01', 'MDR02', 'MVR01', 'MVR02'],
            'Muscles Ventraux': ['MVL07', 'MVL08', 'MVL09', 'MVR07', 'MVR08', 'MVR09'],
            'Muscles Dorsaux': ['MDL07', 'MDL08', 'MDL09', 'MVR07', 'MVR08', 'MVR09'],
            'Muscles Dorsaux gauche': ['MDL07', 'MDL08', 'MDL09', 'MDL10', 'MDL11', 'MDL12', 'MDL13', 'MDL14', 'MDL15', 'MDL16', 'MDL17', 'MDL18', 'MDL19', 'MDL20', 'MDL21', 'MDL22', 'MDL23'],
            'Muscles Ventraux gauche': ['MVL07', 'MVL08', 'MVL09', 'MVL10', 'MVL11', 'MVL12', 'MVL13', 'MVL14', 'MVL15', 'MVL16', 'MVL17', 'MVL18', 'MVL19', 'MVL20', 'MVL21', 'MVL22', 'MVL23'],
            'Muscle Dorsaux droite': ['MDR07', 'MDR08', 'MDR09', 'MDR10', 'MDR11', 'MDR12', 'MDR13', 'MDR14', 'MDR15', 'MDR16', 'MDR17', 'MDR18', 'MDR19', 'MDR20', 'MDL21', 'MDR22', 'MDR23'],
            'Muscle Ventraux droite': ['MVR07', 'MVR08', 'MVR09', 'MVR10', 'MVR11', 'MVR12', 'MVR13', 'MVR14', 'MVR15', 'MVR16', 'MVR17', 'MVR18', 'MVR19', 'MVR20', 'MVL21', 'MVR22', 'MVR23']
        }

        # Variables pour le menu déroulant et l'échelle
        self.dropdown_menu_visible = False
        self.dropdown_menu_rect = None
        self.scale_reset = False

        # Ensemble des neurones forcés à l'activation
        self.forced_active_neurons = set()

        # --- Nouveauté : contrôle du taux d'itération ---
        self.iterations_per_second = 10  # Nombre d'itérations (simulation) par seconde
        self.simulation_time_accumulator = 0.0

        # Fonctions physiologiques C. elegans (NOUVELLE)
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

    def draw_options_screen(self, surface, rect):
        surface.fill(self.BLACK)
        self.draw_text(surface, "Options : Activation des fonctions du ver", rect.width // 2, 30, self.colorsName['green'], font_size=40, align='center')
        start_y = 100
        for idx, func in enumerate(self.worm_functions):
            btn_x = rect.width // 2 - 300
            btn_y = start_y + idx * 56
            btn_w = 600
            btn_h = 44
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            color = (80, 200, 80) if func['active'] else (160, 60, 60)
            pygame.draw.rect(surface, color, btn_rect, border_radius=14)
            pygame.draw.rect(surface, self.WHITE, btn_rect, 2, border_radius=14)
            label = f"{func['name']} : {'ON' if func['active'] else 'OFF'}"
            self.draw_text(surface, label, btn_x + btn_w // 2, btn_y + btn_h // 2 - 10, self.BLACK, font_size=24, align='center')
        self.draw_text(surface, "O : retour  |  Cliquez sur chaque ligne pour (dés)activer", rect.width // 2, rect.height - 45, self.WHITE, font_size=26, align='center')


    def update_forced_active_neurons(self):
        self.forced_active_neurons.clear()
        for func in self.worm_functions:
            if func['active']:
                for n in func['neurons']:
                    for key in postsynaptic:
                        if key.startswith(n):
                            self.forced_active_neurons.add(key)


    def handle_mouse_click_options(self, pos):
        rect = self.screen.get_rect()
        start_y = 100
        for idx, func in enumerate(self.worm_functions):
            btn_x = rect.width // 2 - 300
            btn_y = start_y + idx * 56
            btn_w = 600
            btn_h = 44
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            if btn_rect.collidepoint(pos):
                func['active'] = not func['active']
                self.update_forced_active_neurons()
                break


    def toggle_fullscreen(self):
        self.fullscreen_mode = not self.fullscreen_mode
        if self.fullscreen_mode:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    def toggle_4k_mode(self):
        self.is_4k_mode = not self.is_4k_mode
        if self.is_4k_mode:
            self.WIDTH, self.HEIGHT = 3840, 2160
        else:
            self.WIDTH, self.HEIGHT = 1920, 1080

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        if self.is_4k_mode:
            self.font_size = int(self.base_font_size * 0.75)
        else:
            self.font_size = self.base_font_size
        self.font = pygame.font.Font(None, self.font_size)

        self.background_image = pygame.image.load("ver_c_elegans_01.jpg").convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.WIDTH, self.HEIGHT))

    def motorcontrol(self):
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
            turnratio = float(self.accumright) / float(self.accumleft)
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
            turnratio = float(self.accumright) / float(self.accumleft)
            if turnratio <= 0.6:
                self.left_rot()
            elif turnratio >= 2:
                self.right_rot()
            self.fwd()
        else:
            self.stop()

        self.accumleft = 0
        self.accumright = 0

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

        for neuron in self.forced_active_neurons:
            postsynaptic[neuron][self.thisState] = threshold
            postsynaptic[neuron][self.nextState] = threshold

        for _, idx in masked_indices:
            ps = neuron_list[idx]

            if postsynaptic[ps][self.nextState] > postsynaptic[ps][self.thisState]:
                postsynaptic[ps][self.decroissance] = 0
            else:
               # postsynaptic[ps][self.nextState] = postsynaptic[ps][self.nextState] * math.exp(-0.001 * postsynaptic[ps][self.decroissance])
               postsynaptic[ps][self.nextState] = postsynaptic[ps][self.nextState] * 0.9 # 0.8
            #postsynaptic[ps][self.decroissance] = 1 + postsynaptic[ps][self.decroissance]

            if postsynaptic[ps][self.thisState] >= threshold:
                if ps[:3] not in muscles:
                    self.fire_neuron(ps)
                    postsynaptic[ps][self.nextState] = NegthresholdHyperpolarisation #Negthreshold NegthresholdHyperpolarisation
#                if postsynaptic[ps][self.nextState] >= threshold:
#                    postsynaptic[ps][self.nextState] -= postsynaptic[ps][self.thisState]
            else:
               postsynaptic[ps][self.PreviousValue] = postsynaptic[ps][self.thisState]
            if postsynaptic[ps][self.nextState] < Negthreshold:
                postsynaptic[ps][self.nextState] = Negthreshold

        for _, idx in masked_indices:
            ps = neuron_list[idx] 
            if postsynaptic[ps][self.nextState] < Negthreshold and  postsynaptic[ps][self.nextState] != NegthresholdHyperpolarisation :
                postsynaptic[ps][self.nextState] = Negthreshold
            postsynaptic[ps][self.thisState] = postsynaptic[ps][self.nextState]

#        for neuron in self.forced_active_neurons:
#            postsynaptic[neuron][self.thisState] = threshold
#            postsynaptic[neuron][self.nextState] = threshold

        self.motorcontrol()
        self.iteration += 1

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

    def simulation(self):
        self.current_time = time.time() - self.start_time
        self.time_values.append(self.current_time)

        if self.touch or (self.touch_neurons_active and 0 < self.dist < 30):
            self.activate_touch_neurons()
        else:
            if self.food > 15:
                self.dendrite_accumulate("ADFL")
                self.dendrite_accumulate("ADFR")
                self.dendrite_accumulate("ASGR")
                self.dendrite_accumulate("ASGL")
                self.dendrite_accumulate("ASIL")
                self.dendrite_accumulate("ASIR")
                self.dendrite_accumulate("ASJR")
                self.dendrite_accumulate("ASJL")
        self.run_connectome()
        self.update_worm_movement()

        if self.tfood > 30:
            self.tfood = 0

        for neuron, data in self.neuron_data.items():
            activation_value = postsynaptic[neuron][self.thisState]
            data['values'].append(activation_value)
            if activation_value > threshold:
                data['activation_times'].append(self.iteration)

        neurone_values_str = f"{self.iteration}," + ",".join(str(postsynaptic[pscheck][self.thisState]) for pscheck in postsynaptic) + '\n'
        self.file.write(neurone_values_str)

    def draw_neurones(self, surface, rect):
        surface.fill(self.BLACK)
        left_margin = 150
        bottom_margin = 50
        top_margin = 50
        right_margin = 50

        plot_width = rect.width - left_margin - right_margin
        plot_height = rect.height - top_margin - bottom_margin

        for idx, (neuron, data) in enumerate(self.neuron_data.items()):
            color = data['color']
            self.draw_text(surface, neuron, 10, top_margin + idx * 20, color)

        max_iterations = len(self.time_values)
        if max_iterations < 2:
            return

        self.draw_text(surface, f"Iteration N°:{self.iteration}", rect.width - 200, 10)
        pygame.draw.line(surface, self.WHITE, (left_margin, top_margin), (left_margin, rect.height - bottom_margin))
        pygame.draw.line(surface, self.WHITE, (left_margin, rect.height - bottom_margin), (rect.width - right_margin, rect.height - bottom_margin))

        if not self.neuron_data:
            return

        if self.scale_reset:
            self.scale_reset = False
            self.max_value = max([max(data['values']) for data in self.neuron_data.values()] + [1])
            self.min_value = min([min(data['values']) for data in self.neuron_data.values()] + [-1])
        else:
            self.max_value = getattr(self, 'max_value', max([max(data['values']) for data in self.neuron_data.values()] + [1]))
            self.min_value = getattr(self, 'min_value', min([min(data['values']) for data in self.neuron_data.values()] + [-1]))

        scale_x = plot_width / max(max_iterations - 1, 1)
        scale_y = plot_height / (self.max_value - self.min_value)

        for i in range(5):
            y_value = self.min_value + i * (self.max_value - self.min_value) / 4
            y_pos = rect.height - bottom_margin - (y_value - self.min_value) * scale_y
            self.draw_text(surface, f"{y_value:.2f}", left_margin - 40, y_pos - 10)
            pygame.draw.line(surface, self.WHITE, (left_margin - 5, y_pos), (left_margin, y_pos))

        num_ticks = min(8, max_iterations - 1)
        for i in range(num_ticks + 1):
            x_index = int(i * (max_iterations - 1) / num_ticks)
            x_value = self.time_values[x_index]
            x_pos = left_margin + x_index * scale_x
            self.draw_text(surface, f"{int(x_value)}", x_pos - 10, rect.height - bottom_margin + 10)
            pygame.draw.line(surface, self.WHITE, (x_pos, rect.height - bottom_margin), (x_pos, rect.height - bottom_margin + 5))

        for neuron, data in self.neuron_data.items():
            values = data['values']
            color = data['color']
            points = []
            for i in range(len(values)):
                x = left_margin + i * scale_x
                y = rect.height - bottom_margin - (values[i] - self.min_value) * scale_y
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, 2)

        if not self.is_4k_mode:
            self.draw_text(surface, f"Iteration N°:{self.iteration}", rect.width - 200, 10)

        if self.dropdown_menu_visible:
            self.draw_dropdown_menu(surface)

    def draw_dropdown_menu(self, surface):
        menu_width = 200
        menu_height = 30 * len(self.preconfigured_sets)
        menu_x = 150
        menu_y = 10

        self.dropdown_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(surface, (50, 50, 50), self.dropdown_menu_rect)

        for idx, set_name in enumerate(self.preconfigured_sets.keys()):
            option_rect = pygame.Rect(menu_x, menu_y + idx * 30, menu_width, 30)
            pygame.draw.rect(surface, (100, 100, 100), option_rect)
            self.draw_text(surface, set_name, menu_x + 10, menu_y + idx * 30 + 5, self.WHITE)

    def draw_nemabot(self, surface, rect):
        surface.fill(self.BLACK)
        self.draw_triangle(surface, rect)
        self.draw_food_items(surface, rect)
        self.draw_obstacles(surface, rect)
        self.check_food_collision()
        self.check_obstacle_collision()

        if not self.is_4k_mode:
            self.draw_text(surface, f"Food: {self.food}", 10, 40)
            self.draw_text(surface, f"Touch: {self.touch}", 10, 70)
            self.draw_text(surface, f"Iteration N°:{self.iteration}", rect.width - 200, 10)

    def draw_neuron_matrix(self, surface, rect):
        surface.fill(self.BLACK)

        num_neurons = len(postsynaptic)
        grid_size = int(math.ceil(math.sqrt(num_neurons)))
        cell_width = rect.width / grid_size
        cell_height = rect.height / grid_size

        max_radius = int(min(cell_width, cell_height) // 2 - 10)
        neuron_idx = 0
        neuron_positions = {}
        for i in range(grid_size):
            for j in range(grid_size):
                if neuron_idx >= num_neurons:
                    break
                neuron_name = list(postsynaptic.keys())[neuron_idx]
                value = postsynaptic[neuron_name][2]
                value0 = postsynaptic[neuron_name][0]

                radius = max(2, min(max_radius, int(abs(value) * max_radius)))
                if neuron_name in self.forced_active_neurons:
                    color = self.colorsName['red']
                else:
                    color = (0, 255, 0) if value != value0 > 0 else (0, 0, 255)

                center_x = int(j * cell_width + cell_width // 2)
                center_y = int(i * cell_height + cell_height // 2)

                pygame.draw.circle(surface, color, (center_x, center_y), radius)
                neuron_positions[neuron_name] = (center_x, center_y)

                neuron_idx += 1

        for neuron_name, (center_x, center_y) in neuron_positions.items():
            name_color = self.colorsName['red'] if neuron_name in self.neuron_data else self.WHITE
            font_size = 24
            self.draw_text(surface, neuron_name, center_x - 20, center_y - 30, name_color, font_size=font_size)

        if not self.is_4k_mode:
            self.draw_text(surface, f"Iteration N°:{self.iteration}", 10, 10)

    def draw_wave_screen(self, surface, rect):
        surface.fill(self.BLACK)
        left_margin = 50
        right_margin = 50
        top_margin = 50
        bottom_margin = 50

        plot_width = rect.width - left_margin - right_margin
        plot_height = rect.height - top_margin - bottom_margin

        neurons = list(self.neuron_data.keys())
        num_neurons = len(neurons)

        if num_neurons == 0:
            self.draw_text(surface, "Aucun neurone sélectionné pour l'affichage.", left_margin, top_margin, color=self.WHITE, font_size=24)
            return

        num_columns = 1
        neurons_per_column = math.ceil(num_neurons / num_columns)
        neuron_spacing = 9

        max_iterations = self.iteration if self.iteration else 1
        scale_x = plot_width / max_iterations

        pygame.draw.line(surface, self.WHITE, (left_margin, top_margin), (left_margin, rect.height - bottom_margin))
        pygame.draw.line(surface, self.WHITE, (left_margin, rect.height - bottom_margin), (rect.width - right_margin, rect.height - bottom_margin))

        for idx, neuron in enumerate(neurons):
            column = idx // neurons_per_column
            row = idx % neurons_per_column

            y_pos = top_margin + row * neuron_spacing
            name_x = left_margin - 10 - (column * 100)
            name_align = 'right'
            self.draw_text(surface, neuron, name_x, y_pos - 10, color=self.neuron_data[neuron]['color'], font_size=16, align=name_align)

            pygame.draw.line(surface, self.WHITE, (left_margin, y_pos), (rect.width - right_margin, y_pos))

            activation_times = self.neuron_data[neuron]['activation_times']
            for t in activation_times:
                x_pos = left_margin + t * scale_x
                pygame.draw.line(surface, self.neuron_data[neuron]['color'], (x_pos, y_pos - 5), (x_pos, y_pos + 5), 2)

        num_ticks = 10
        for i in range(num_ticks + 1):
            t = int(i * max_iterations / num_ticks)
            x_pos = left_margin + t * scale_x
            self.draw_text(surface, str(t), x_pos - 10, rect.height - bottom_margin + 10)
            pygame.draw.line(surface, self.WHITE, (x_pos, rect.height - bottom_margin), (x_pos, rect.height - bottom_margin + 5))

        self.draw_text(surface, f"Iteration N°:{self.iteration}", rect.width - 200, 10)


    def update_worm_movement(self):
        """
        Met à jour pour chaque segment du ver le facteur de contraction (affectant la longueur)
        et le décalage de courbure (affectant la trajectoire) à partir de l'activation
        des muscles locomoteurs (neurones MDLxx, MDRxx, MVLxx et MVRxx).

        Dans ce modèle, la contraction est linéaire par rapport à l'activation neuronale,
        augmentant proportionnellement jusqu'à une saturation définie par 'saturation_value'.
        """
        num_segments = 17  # Correspond aux muscles numérotés de 07 à 23
        if not hasattr(self, 'muscle_segments'):
            self.muscle_segments = [{} for _ in range(num_segments)]
        
        contraction_scale = 0.1  # À contraction maximale, le segment conserve 50 % de sa longueur de base
        max_offset = 30         # Décalage maximal (en pixels) pour la courbure de la vue du dessus
        saturation_value = threshold  # On considère 'threshold' comme la valeur de saturation

        for i in range(num_segments):
            muscle_num = f"{7 + i:02d}"  # Par exemple "07", "08", … "23"
            # Récupération des activations pour chaque muscle (ou 0 si non présent)
            act_MDL = postsynaptic.get(f"MDL{muscle_num}", [0, 0, 0])[self.thisState] if f"MDL{muscle_num}" in postsynaptic else 0
            act_MDR = postsynaptic.get(f"MDR{muscle_num}", [0, 0, 0])[self.thisState] if f"MDR{muscle_num}" in postsynaptic else 0
            act_MVL = postsynaptic.get(f"MVL{muscle_num}", [0, 0, 0])[self.thisState] if f"MVL{muscle_num}" in postsynaptic else 0
            act_MVR = postsynaptic.get(f"MVR{muscle_num}", [0, 0, 0])[self.thisState] if f"MVR{muscle_num}" in postsynaptic else 0

            # Moyennes dorsale et ventrale
            dorsal_avg = (act_MDL + act_MDR) / 2.0
            ventral_avg = (act_MVL + act_MVR) / 2.0

            # Calcul de l'activation moyenne (linéairement) avec saturation
            raw_activation = (dorsal_avg + ventral_avg) / 2.0
            normalized_activation = min(max(raw_activation, 0), saturation_value) / saturation_value

            # Calcul du facteur de longueur :
            # 1 signifie aucune contraction et contraction_scale la contraction maximale
            length_factor = 1 - normalized_activation * (1 - contraction_scale)

            # Le décalage de courbure est proportionnel à la différence entre activations dorsale et ventrale
            normalized_curvature = (dorsal_avg - ventral_avg) #/ saturation_value
            curvature_offset = max_offset * normalized_curvature

            self.muscle_segments[i] = {
                "length_factor": length_factor,
                "curvature_offset": curvature_offset,
                "contraction": normalized_activation
            }


    # --- Nouvelle routine pour mettre à jour les paramètres de mouvement du ver ---
    def update_worm_movement_old(self):
        """
        Met à jour pour chaque segment du ver le facteur de contraction (affectant la longueur)
        et le décalage de courbure (affectant la trajectoire) à partir de l'activation
        des muscles locomoteurs (neurones MDLxx, MDRxx, MVLxx et MVRxx).
        """
        num_segments = 17  # Correspond aux muscles numérotés de 07 à 23
        # Initialisation de self.muscle_segments si ce n'est pas déjà fait
        if not hasattr(self, 'muscle_segments'):
            self.muscle_segments = [{} for _ in range(num_segments)]
        
        contraction_scale = 0.5  # Pour une activation maximale, le segment ne conserve que 50 % de sa longueur de base
        max_offset = 30         # Décalage maximal (en pixels) pour la courbure de la vue du dessus

        for i in range(num_segments):
            muscle_num = f"{7 + i:02d}"  # Par exemple "07", "08", … "23"
            # Récupération des activations pour chaque muscle concerné, ou 0 si le neurone n'est pas présent
            act_MDL = postsynaptic.get(f"MDL{muscle_num}", [0,0,0])[self.thisState] if f"MDL{muscle_num}" in postsynaptic else 0
            act_MDR = postsynaptic.get(f"MDR{muscle_num}", [0,0,0])[self.thisState] if f"MDR{muscle_num}" in postsynaptic else 0
            act_MVL = postsynaptic.get(f"MVL{muscle_num}", [0,0,0])[self.thisState] if f"MVL{muscle_num}" in postsynaptic else 0
            act_MVR = postsynaptic.get(f"MVR{muscle_num}", [0,0,0])[self.thisState] if f"MVR{muscle_num}" in postsynaptic else 0

            # Moyennes dorsale et ventrale
            dorsal_avg = (act_MDL + act_MDR) / 2.0
            ventral_avg = (act_MVL + act_MVR) / 2.0

            # Contraction globale (si les deux côtés se contractent, le segment se raccourcit)
            contraction = (dorsal_avg + ventral_avg) / 2.0/ threshold  # Valeur entre 0 et 1

            # Calcul du facteur de longueur : 1 = aucune contraction, 1 - (1 - contraction_scale) = contraction maximale
            length_factor = 1 - contraction * (1 - contraction_scale)

            # Le décalage de courbure dépend de la différence entre dorsal et ventral
            curvature = (dorsal_avg - ventral_avg)/threshold
            curvature_offset = max_offset * curvature

            # Enregistrer les paramètres pour ce segment
            self.muscle_segments[i] = {
                "length_factor": length_factor,
                "curvature_offset": curvature_offset,
                "contraction": contraction  # Pour le choix de la couleur par exemple
            }


    def draw_worm(self, surface, rect):
        surface.fill(self.BLACK)
        half_height = rect.height // 2
        profile_rect = pygame.Rect(0, 0, rect.width, half_height)
        top_rect = pygame.Rect(0, half_height, rect.width, rect.height - half_height)

        profile_surface = surface.subsurface(profile_rect)
        top_surface = surface.subsurface(top_rect)

        self.draw_worm_profile(profile_surface, profile_surface.get_rect())
        self.draw_worm_top(top_surface, top_surface.get_rect())

    def draw_worm_profile(self, surface, rect):
        surface.fill(self.BLACK)
        if not hasattr(self, 'muscle_segments'):
            self.muscle_segments = [{"length_factor": 1.0, "curvature_offset": 0.0, "contraction": 0.0} for _ in range(17)]
        num_segments = len(self.muscle_segments)
        total_length = rect.width * 0.9
        L_base = total_length / num_segments
        center_y = rect.centery
        segment_height = 40
        x = rect.left + (rect.width - total_length) / 2

        self.draw_text(surface, "Vue de profil", rect.left + 10, rect.top + 10, self.colorsName['green'], font_size=24)

        for segment in self.muscle_segments:
            length_factor = segment["length_factor"]
            contraction = segment["contraction"]
            segment_length = L_base * length_factor
            contraction_intensity = (1 - length_factor) / (1 - 0.5)
            contraction_intensity = max(0, min(contraction_intensity, 1))
            color = (
                int(contraction_intensity * 255),
                int((1 - contraction_intensity) * 255),
                0
            )
            segment_rect = pygame.Rect(int(x), int(center_y - segment_height/2), int(segment_length), segment_height)
            pygame.draw.rect(surface, color, segment_rect)
            pygame.draw.rect(surface, self.WHITE, segment_rect, 2)
            x += segment_length

    def draw_worm_top(self, surface, rect):
        surface.fill(self.BLACK)
        if not hasattr(self, 'muscle_segments'):
            self.muscle_segments = [{"length_factor": 1.0, "curvature_offset": 0.0, "contraction": 0.0} for _ in range(17)]
        num_segments = len(self.muscle_segments)
        total_length = rect.width * 0.9
        L_base = total_length / num_segments
        points = []
        x = rect.left + (rect.width - total_length) / 2
        y = rect.centery
        points.append((x, y))
        for segment in self.muscle_segments:
            length_factor = segment["length_factor"]
            segment_length = L_base * length_factor
            curvature_offset = segment["curvature_offset"]
            x += segment_length
            new_y = y + curvature_offset
            points.append((x, new_y))
        self.draw_text(surface, "Vue du dessus", rect.left + 10, rect.top + 10, self.colorsName['green'], font_size=24)
        if len(points) > 1:
            pygame.draw.lines(surface, self.colorsName['triangle'], False, points, 8)
        for p in points:
            pygame.draw.circle(surface, self.WHITE, (int(p[0]), int(p[1])), 10)

    def draw_help(self, surface, rect):
        surface.fill(self.BLACK)

        self.draw_text(surface, "Commandes Générales :", 10, 10, self.colorsName['green'], font_size=36)
        self.draw_text(surface, "P: Mode pas à pas (activation/désactivation)", 10, 50)
        self.draw_text(surface, "S: Avancer d'un pas (en mode pas à pas)", 10, 80)
        self.draw_text(surface, "F: Ajouter de la nourriture", 10, 110)
        self.draw_text(surface, "T: Activer/Désactiver touché", 10, 140)
        self.draw_text(surface, "K: Basculer le mode 4K (activation/désactivation)", 10, 170)
        self.draw_text(surface, "F11: Mode plein écran (activation/désactivation)", 10, 200)
        self.draw_text(surface, "ESC: Quitter", 10, 230)

        self.draw_text(surface, "Commandes par écran :", 10, 270, self.colorsName['green'], font_size=36)
        self.draw_text(surface, "M: Afficher matrice des neurones", 10, 310)
        self.draw_text(surface, "   - Clic gauche: Activer/Désactiver un neurone", 30, 340)
        self.draw_text(surface, "   - Clic droit: Sélectionner/Désélectionner pour le tracé", 30, 370)
        self.draw_text(surface, "D: Afficher écran de déplacement", 10, 400)
        self.draw_text(surface, "   - Clic gauche: Ajouter/Supprimer nourriture", 30, 430)
        self.draw_text(surface, "   - Clic droit: Ajouter/Supprimer obstacle", 30, 460)
        self.draw_text(surface, "C: Afficher écran de tracé", 10, 490)
        self.draw_text(surface, "   - E: Ouvrir/Fermer le menu des neurones", 30, 520)
        self.draw_text(surface, "   - Suppr: Réinitialiser les échelles", 30, 550)
        self.draw_text(surface, "X: Afficher écran des vagues d'activation", 10, 580)
        
        # Affichage des informations dynamiques
        dynamic_y = rect.height - 130
        self.draw_text(surface, f"Mode 4K: {'Activé' if self.is_4k_mode else 'Désactivé'}", 10, dynamic_y)
        self.draw_text(surface, f"Food: {self.food}", 10, dynamic_y + 30)
        self.draw_text(surface, f"Touch: {self.touch}", 10, dynamic_y + 60)
        self.draw_text(surface, f"Iteration N°:{self.iteration}", 10, dynamic_y + 90)
        # Affichage du taux d'itération (modifiable avec + et -)
        self.draw_text(surface, f"Iter/s: {self.iterations_per_second}", 10, dynamic_y + 120)

    def draw_text(self, surface, text, x, y, color=None, font_size=None, align='left'):
        if color is None:
            color = self.WHITE

        font = pygame.font.Font(None, font_size) if font_size is not None else self.font
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        if align == 'left':
            textrect.topleft = (x, y)
        elif align == 'right':
            textrect.topright = (x, y)
        elif align == 'center':
            textrect.center = (x, y)
        surface.blit(textobj, textrect)

    def handle_mouse_click(self, pos, button):

        if self.display_options_screen:
            if button == 1:
                self.handle_mouse_click_options(pos)
            return

        if self.is_4k_mode:
            quadrant_width = self.WIDTH // 2
            quadrant_height = self.HEIGHT // 2
            x, y = pos

            if x < quadrant_width and y < quadrant_height:
                pass
            elif x >= quadrant_width and y < quadrant_height:
                offset_pos = (x - quadrant_width, y)
                self.handle_mouse_click_neuron_matrix(offset_pos, button)
            elif x < quadrant_width and y >= quadrant_height:
                if self.dropdown_menu_visible:
                    self.handle_mouse_click_dropdown_menu((x, y - quadrant_height))
            elif x >= quadrant_width and y >= quadrant_height:
                offset_pos = (x - quadrant_width, y - quadrant_height)
                self.handle_mouse_click_movement_screen(offset_pos, button)
        else:
            if self.display_neuron_matrix:
                self.handle_mouse_click_neuron_matrix(pos, button)
            elif self.display_movement_screen:
                self.handle_mouse_click_movement_screen(pos, button)
            elif self.display_curve_screen and self.dropdown_menu_visible:
                self.handle_mouse_click_dropdown_menu(pos)

    def handle_mouse_click_dropdown_menu(self, pos):
        if self.dropdown_menu_rect and self.dropdown_menu_rect.collidepoint(pos):
            relative_y = pos[1] - self.dropdown_menu_rect.top
            option_height = 30
            index = relative_y // option_height
            if 0 <= index < len(self.preconfigured_sets):
                set_name = list(self.preconfigured_sets.keys())[index]
                self.select_preconfigured_set(set_name)
            self.dropdown_menu_visible = False
        else:
            self.dropdown_menu_visible = False

    def handle_mouse_click_neuron_matrix(self, pos, button):
        rect = pygame.Rect(0, 0, self.WIDTH // 2, self.HEIGHT // 2) if self.is_4k_mode else self.screen.get_rect()
        num_neurons = len(postsynaptic)
        grid_size = int(math.ceil(math.sqrt(num_neurons)))
        cell_width = rect.width / grid_size
        cell_height = rect.height / grid_size

        neuron_idx = 0
        for i in range(grid_size):
            for j in range(grid_size):
                if neuron_idx >= num_neurons:
                    break
                neuron_name = list(postsynaptic.keys())[neuron_idx]
                cell_rect = pygame.Rect(int(j * cell_width), int(i * cell_height), int(cell_width), int(cell_height))
                if cell_rect.collidepoint(pos):
                    if button == 1:
                        if neuron_name in self.forced_active_neurons:
                            self.forced_active_neurons.remove(neuron_name)
                        else:
                            self.forced_active_neurons.add(neuron_name)
                    elif button == 3:
                        if neuron_name in self.neuron_data:
                            self.remove_neuron(neuron_name)
                        else:
                            self.add_neuron(neuron_name)
                    break
                neuron_idx += 1

    def handle_mouse_click_movement_screen(self, pos, button):
        rect = pygame.Rect(0, 0, self.WIDTH // 2, self.HEIGHT // 2) if self.is_4k_mode else self.screen.get_rect()
        if button == 1:
            clicked_on_food = False
            for food_pos in self.food_items:
                distance = math.hypot(pos[0] - food_pos[0], pos[1] - food_pos[1])
                if distance <= 10:
                    self.food_items.remove(food_pos)
                    clicked_on_food = True
                    break
            if not clicked_on_food:
                self.food_items.append((pos[0], pos[1]))
        elif button == 3:
            clicked_on_obstacle = False
            for obstacle in self.obstacles:
                rect_obstacle = pygame.Rect(obstacle)
                if rect_obstacle.collidepoint(pos):
                    self.obstacles.remove(obstacle)
                    clicked_on_obstacle = True
                    break
            if not clicked_on_obstacle:
                self.obstacles.append((pos[0] - 25, pos[1] - 25, 50, 50))

    def add_neuron(self, neuron_name, color=None):
        if color is None:
            color = self.colors[len(self.neuron_data) % len(self.colors)]
        if neuron_name not in self.neuron_data:
            self.neuron_data[neuron_name] = {'values': [], 'activation_times': [], 'color': color}
            self.scale_reset = True

    def remove_neuron(self, neuron_name):
        if neuron_name in self.neuron_data:
            del self.neuron_data[neuron_name]
            self.scale_reset = True

    def activate_touch_neurons(self):
        for n in ["FLPR", "FLPL", "ASHL", "ASHR", "IL1VL", "IL1VR", "OLQDL", "OLQDR", "OLQVR", "OLQVL"]:
            self.dendrite_accumulate(n)

    def add_food(self):
        self.tfood += 10

    def handle_key_press(self, event):
        if event.key == pygame.K_p:
            self.step_mode = not self.step_mode
            self.step_ready = False
        elif event.key == pygame.K_o:  # <--- NOUVEAU !
            self.display_options_screen = not self.display_options_screen
            if self.display_options_screen:
                self.display_movement_screen = False
                self.display_neuron_matrix = False
                self.display_curve_screen = False
                self.display_wave_screen = False
                self.display_help_screen = False
                self.display_worm_screen = False
        elif event.key == pygame.K_f:
            self.add_food()
        elif event.key == pygame.K_t:
            self.touch_neurons_active = not self.touch_neurons_active
        elif event.key == pygame.K_F11:
            self.toggle_fullscreen()
        elif event.key == pygame.K_m:
            self.display_neuron_matrix = True
            self.display_movement_screen = False
            self.display_curve_screen = False
            self.display_wave_screen = False
            self.display_help_screen = False
        elif event.key == pygame.K_s and self.step_mode:
            self.step_ready = True
        elif event.key == pygame.K_ESCAPE:
            self.quit_game()
        elif event.key == pygame.K_d:
            self.display_movement_screen = True
            self.display_neuron_matrix = False
            self.display_curve_screen = False
            self.display_wave_screen = False
            self.display_help_screen = False
            self.display_worm_screen = False
        elif event.key == pygame.K_c:
            self.display_curve_screen = True
            self.display_movement_screen = False
            self.display_neuron_matrix = False
            self.display_wave_screen = False
            self.display_help_screen = False
            self.display_worm_screen = False
        elif event.key == pygame.K_h:
            self.display_help_screen = True
            self.display_movement_screen = False
            self.display_curve_screen = False
            self.display_neuron_matrix = False
            self.display_wave_screen = False
            self.display_worm_screen = False
        elif event.key == pygame.K_x:
            self.display_wave_screen = True
            self.display_movement_screen = False
            self.display_curve_screen = False
            self.display_neuron_matrix = False
            self.display_help_screen = False
            self.display_worm_screen = False
        elif event.key == pygame.K_w:
            self.display_wave_screen = False
            self.display_movement_screen = False
            self.display_curve_screen = False
            self.display_neuron_matrix = False
            self.display_help_screen = False
            self.display_worm_screen = True
        elif event.key == pygame.K_k:
            self.toggle_4k_mode()
        elif event.key == pygame.K_e:
            if self.display_curve_screen or self.is_4k_mode:
                self.dropdown_menu_visible = not self.dropdown_menu_visible
        # --- Nouveauté : ajuster le taux d'itération avec + et - ---
        elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
            self.iterations_per_second += 5
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.iterations_per_second = max(1, self.iterations_per_second - 5)
        elif event.key == pygame.K_BACKSPACE:
            self.scale_reset = True

    def select_preconfigured_set(self, set_name):
        neuron_list = self.preconfigured_sets[set_name]
        for neuron_name in neuron_list:
            self.add_neuron(neuron_name)

    def game_loop(self):
        clock = pygame.time.Clock()
        while self.game_active:
            dt = clock.tick(60) / 1000.0  # dt en secondes
            self.simulation_time_accumulator += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                if event.type == pygame.KEYDOWN:
                    self.handle_key_press(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos, event.button)

            if not self.running:
                self.start_simulation()

            if not self.step_mode or (self.step_mode and self.step_ready):
                # On exécute autant d'itérations que le temps accumulé le permet,
                # garantissant ainsi un nombre constant d'itérations par seconde.
                while self.simulation_time_accumulator >= 1.0 / self.iterations_per_second:
                    self.simulation()
                    self.simulation_time_accumulator -= 1.0 / self.iterations_per_second
                self.step_ready = False


            if self.display_options_screen:
                self.draw_options_screen(self.screen, self.screen.get_rect())
            elif self.display_movement_screen:
                self.draw_nemabot(self.screen, self.screen.get_rect())

            if self.is_4k_mode:
                self.draw_all_quadrants()
            else:
                if self.display_movement_screen:
                    self.draw_nemabot(self.screen, self.screen.get_rect())
                elif self.display_neuron_matrix:
                    self.draw_neuron_matrix(self.screen, self.screen.get_rect())
                elif self.display_curve_screen:
                    self.draw_neurones(self.screen, self.screen.get_rect())
                elif self.display_wave_screen:
                    self.draw_wave_screen(self.screen, self.screen.get_rect())
                elif self.display_help_screen:
                    self.draw_help(self.screen, self.screen.get_rect())
                elif self.display_worm_screen:
                    self.draw_worm(self.screen, self.screen.get_rect())
                else:
                    self.draw_help(self.screen, self.screen.get_rect())

            pygame.display.flip()

    def draw_all_quadrants(self):
        quadrant_width = 1920
        quadrant_height = 1080

        help_surface = pygame.Surface((quadrant_width, quadrant_height))
        matrix_surface = pygame.Surface((quadrant_width, quadrant_height))
        curve_surface = pygame.Surface((quadrant_width, quadrant_height))
        movement_surface = pygame.Surface((quadrant_width, quadrant_height))

        self.draw_help(help_surface, help_surface.get_rect())
        self.draw_neuron_matrix(matrix_surface, matrix_surface.get_rect())
        self.draw_neurones(curve_surface, curve_surface.get_rect())
        self.draw_nemabot(movement_surface, movement_surface.get_rect())

        self.screen.blit(help_surface, (0, 0))
        self.screen.blit(matrix_surface, (quadrant_width, 0))
        self.screen.blit(curve_surface, (0, quadrant_height))
        self.screen.blit(movement_surface, (quadrant_width, quadrant_height))

    def quit_game(self):
        self.game_active = False
        self.running = False
        if self.file:
            self.file.close()
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            if not self.game_active:
                self.main_menu()
                self.game_active = True
            self.game_loop()

    def start_game(self):
        self.game_active = True
        self.running = False
        self.run()

    def main_menu(self):
        self.screen.blit(self.background_image, (0, 0))
        self.draw_text(self.screen, 'Welcome to Nemabot Simulation', self.WIDTH // 2 - 200, self.HEIGHT // 2 - 50, self.WHITE, font_size=64)
        self.draw_text(self.screen, 'Press any key to start', self.WIDTH // 2 - 150, self.HEIGHT // 2 + 20, self.WHITE, font_size=32)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def draw_triangle(self, surface, rect):
        angle_radians = math.radians(self.triangle_angle)
        size = 20

        p1 = (self.triangle_pos[0] + size * math.cos(angle_radians),
              self.triangle_pos[1] + size * math.sin(angle_radians))
        p2 = (self.triangle_pos[0] + size * math.cos(angle_radians + 2.5),
              self.triangle_pos[1] + size * math.sin(angle_radians + 2.5))
        p3 = (self.triangle_pos[0] + size * math.cos(angle_radians - 2.5),
              self.triangle_pos[1] + size * math.sin(angle_radians - 2.5))

        if self.is_4k_mode:
            p1 = (p1[0] % rect.width, p1[1] % rect.height)
            p2 = (p2[0] % rect.width, p2[1] % rect.height)
            p3 = (p3[0] % rect.width, p3[1] % rect.height)

        pygame.draw.polygon(surface, self.colorsName['triangle'], [p1, p2, p3])

    def draw_food_items(self, surface, rect):
        for food_pos in self.food_items:
            pos = food_pos if not self.is_4k_mode else (food_pos[0] % rect.width, food_pos[1] % rect.height)
            pygame.draw.circle(surface, self.colorsName['green'], pos, 10)

    def draw_obstacles(self, surface, rect):
        for obstacle in self.obstacles:
            rect_obstacle = pygame.Rect(obstacle)
            if self.is_4k_mode:
                rect_obstacle.x %= rect.width
                rect_obstacle.y %= rect.height
            pygame.draw.rect(surface, self.colorsName['red'], rect_obstacle)

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

    def check_food_collision(self):
        self.food = 0
        for food_pos in self.food_items:
            distance = math.hypot(self.triangle_pos[0] - food_pos[0], self.triangle_pos[1] - food_pos[1])
            if distance < 20:
                self.food = 20
            elif distance < 100:
                self.food = max(self.food, int(100 - distance) // 5)
                self.tfood = self.food

    def check_obstacle_collision(self):
        self.touch = False
        for obstacle in self.obstacles:
            if pygame.Rect(obstacle).collidepoint(self.triangle_pos):
                self.touch = True
                break

    def move_triangle(self):
        pass  # Méthode placeholder si besoin d'une future implémentation


if __name__ == "__main__":
    nemabot_simulation = NemabotSimulation()
    nemabot_simulation.run()
