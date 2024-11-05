import arcade
import random
import time
from queue import PriorityQueue
import arcade.gui
from collections import deque
from constants import *
from llm_request import make_request, make_prompt, extract_thoughts_and_command

class CookoBot(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "CookoBot")
        self.player = None
        self.action_queue : list[ tuple[any, any]] = []
        self.inventory = []
        self.objects = ['Banane', 'Pomme', 'Poire']
        self.items_on_map = {}
        self.path = []  # Chemin calculé
        self.path_index = 0  # Indice du prochain pas à suivre
        self.step_count = 0  # Compteur de pas
        self.action_count = 0  # Compteur d'actions
        self.inventory = deque(maxlen=INVENTORY_SIZE)  # Inventaire limité à 3 objets

        # Create a horizontale BoxGroup to align buttons
        self.action_box = arcade.gui.UIBoxLayout(vertical=False, x=MENU_X, y=INVENTORY_BUTTON_Y)
        self.chat_box = arcade.gui.UIBoxLayout(vertical=True, x=INSTRUCTION_TEXT_X, y=INSTRUCTION_TEXT_Y)

        # Créer le bouton de ramassage
        pick_up_button = arcade.gui.UIFlatButton(text="Ramasser", width=BUTTON_WIDTH, style={'bg_color': arcade.color.MAUVE_TAUPE})
        pick_up_button.on_click = self.action_pick
        self.action_box.add(pick_up_button.with_space_around(right=PADDING))

        # Créer le bouton de dépôt
        drop_button = arcade.gui.UIFlatButton(text="Déposer", width=BUTTON_WIDTH, style={'bg_color': arcade.color.MAUVE_TAUPE})
        drop_button.on_click = self.action_drop
        self.action_box.add(drop_button)

        # Créer la zone de texte
        self.text_input = arcade.gui.UIInputText(height=INSTRUCTION_TEXT_HEIGHT, width=INSTRUCTION_TEXT_WIDTH,
            text_color=arcade.color.MAUVE_TAUPE, font_size=14, text="Attrape une pomme !", multiline=True)
        self.chat_box.add(self.text_input)

        # Créer le bouton d'envoi
        send_button = arcade.gui.UIFlatButton(text="Envoyer", width=BUTTON_WIDTH, style={'bg_color': arcade.color.MAUVE_TAUPE})
        send_button.on_click = self.send_instruction
        self.chat_box.add(send_button.with_space_around(top=PADDING+INSTRUCTION_BOX_PADDING))

        # Créer le gestionnaire d'interface utilisateur
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.manager.add(self.action_box)
        self.manager.add(self.chat_box)

    def setup(self):
        """Initialisation de la carte et du personnage."""
        # Background
        arcade.set_background_color(BACKGROUND_COLOR)

        # Création de la carte & positionnement du personnage
        x_start = random.randint(0, NB_TILES - 1)
        y_start = random.randint(0, NB_TILES - 1)
        self.player = {'x': x_start, 'y': y_start}  # Position initiale du personnage

        # Chargement des textures
        self.player_texture = arcade.load_texture("images/robot.png")
        self.fruit_textures = {
            'Banane': arcade.load_texture("images/banane.png"),
            'Pomme': arcade.load_texture("images/pomme.png"),
            'Poire': arcade.load_texture("images/poire.png")
        }

        # Placement aléatoire des objets sur la carte
        for _ in range(NB_OBJ):  # NB_OBJ objects aléatoires
            x = random.randint(0, NB_TILES - 1)
            y = random.randint(0, NB_TILES - 1)
            fruit = random.choice(self.objects)
            self.items_on_map[(x, y)] = fruit
        
    def on_draw(self):
        """Rendu de l'écran."""
        arcade.start_render()

        # Dessiner le chemin restant en orange
        if self.path and self.path_index < len(self.path):
            for step in self.path[self.path_index:]:
                position_x = step[0] * TILE_SIZE + TILE_SIZE // 2 + PADDING
                position_y = step[1] * TILE_SIZE + TILE_SIZE // 2 + PADDING
                arcade.draw_rectangle_filled(position_x, position_y, TILE_SIZE, TILE_SIZE, (220, 205, 205))

        # Dessiner la grille
        arcade.draw_rectangle_outline(PADDING + MAP_SIZE//2, PADDING + MAP_SIZE//2, MAP_SIZE, MAP_SIZE, arcade.color.MAUVE_TAUPE, border_width=4)
        for row in range(NB_TILES):
            for col in range(NB_TILES):
                x = col * TILE_SIZE + PADDING
                y = row * TILE_SIZE + PADDING
                arcade.draw_rectangle_outline(x + TILE_SIZE // 2, y + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE, arcade.color.MAUVE_TAUPE)
        
        # Dessiner les objets sur la carte
        for (x, y), fruit in self.items_on_map.items():
            position_x = x * TILE_SIZE + TILE_SIZE // 2 + PADDING
            position_y = y * TILE_SIZE + TILE_SIZE // 2 + PADDING
            arcade.draw_texture_rectangle(position_x, position_y, OBJ_SIZE, OBJ_SIZE, self.fruit_textures[fruit])

        # Dessiner le personnage
        arcade.draw_texture_rectangle(
            self.player['x'] * TILE_SIZE + TILE_SIZE // 2 + PADDING,
            self.player['y'] * TILE_SIZE + TILE_SIZE // 2 + PADDING,
            OBJ_SIZE, OBJ_SIZE, self.player_texture
        )

        # Afficher le compteur de pas
        arcade.draw_texture_rectangle(POINT_BOX_X, POINT_BOX_Y, LOGO_SIZE, LOGO_SIZE, arcade.load_texture("images/walk.png"))
        arcade.draw_text(f"{self.step_count}", POINT_BOX_X+LOGO_SIZE-10, POINT_BOX_Y-LOGO_SIZE//2+10, arcade.color.MAUVE_TAUPE, 16, font_name="Comic Sans MS")

        # Afficher le compteur d'actions
        arcade.draw_texture_rectangle(POINT_BOX_X+MENU_WIDTH//2, POINT_BOX_Y, LOGO_SIZE, LOGO_SIZE, arcade.load_texture("images/star.png"))
        arcade.draw_text(f"{self.action_count}", POINT_BOX_X+MENU_WIDTH//2+LOGO_SIZE-10, POINT_BOX_Y-LOGO_SIZE//2+10, arcade.color.MAUVE_TAUPE, 16, font_name="Comic Sans MS")

        # Afficher l'inventaire au-dessus des boutons
        arcade.draw_text(f"Inventaire ({len(self.inventory)}/{INVENTORY_SIZE})", MENU_X, INVENTORY_TITLE_Y, arcade.color.MAUVE_TAUPE, 16, font_name="Comic Sans MS")
        arcade.draw_rectangle_outline(MENU_X + MENU_WIDTH//2, INVENTORY_BOX_Y - INVENTORY_BOX_HEIGHT//2, MENU_WIDTH, INVENTORY_BOX_HEIGHT, arcade.color.MAUVE_TAUPE)
        for i, item in enumerate(self.inventory):
            arcade.draw_text(item, INVENTORY_TEXT_X, INVENTORY_TEXT_Y - INVENTORY_TEXT_HEIGHT*i, arcade.color.MAUVE_TAUPE, 16, font_name="Comic Sans MS")
            # arcade.draw_text(item, INVENTORY_TEXT_X, INVENTORY_TEXT_Y - INVENTORY_TEXT_HEIGHT*i, arcade.color.MAUVE_TAUPE, 14, font_name="Comic Sans MS")

        # Afficher le chat
        arcade.draw_text("Instruction", MENU_X, INSTRUCTION_TITLE_Y, arcade.color.MAUVE_TAUPE, 16, font_name="Comic Sans MS")
        arcade.draw_rectangle_outline(MENU_X + MENU_WIDTH//2, INSTRUCTION_BOX_Y-INSTRUCTION_BOX_HEIGHT//2, MENU_WIDTH, INSTRUCTION_BOX_HEIGHT, arcade.color.MAUVE_TAUPE)

        # Afficher les boutons
        self.manager.draw()

    def next_action(self):
        if len(self.action_queue) == 0:
            print("Action terminé")
            return
        action, value  = self.action_queue.pop(0)
        if value:
            print(f"Action: {action.__name__}({value})")
            action(value)
        else:
            action()

    def on_mouse_press(self, x, y, button, modifiers):
        # Convertir les coordonnées de la souris en coordonnées de la grille
        grid_x = (x - PADDING) // TILE_SIZE
        grid_y = (y - PADDING) // TILE_SIZE

        # Vérifier si la case est valide
        if 0 <= grid_x < NB_TILES and 0 <= grid_y < NB_TILES:
            # Calculer le chemin vers la case
            self.path = self.a_star(self.player['x'], self.player['y'], grid_x, grid_y)
            if self.path:
                self.path_index = 0  # Réinitialise l'index de l'étape
                self.action_move()

    def a_star(self, start_x, start_y, goal_x, goal_y):
        """Implémentation de l'algorithme A*."""
        def heuristic(x1, y1, x2, y2):
            return abs(x1 - x2) + abs(y1 - y2)

        # Initialisation des structures de données
        open_set = PriorityQueue()
        open_set.put((0, (start_x, start_y)))
        came_from = {}
        g_score = {pos: float('inf') for pos in [(x, y) for x in range(NB_TILES) for y in range(NB_TILES)]}
        g_score[(start_x, start_y)] = 0
        f_score = g_score.copy()
        f_score[(start_x, start_y)] = heuristic(start_x, start_y, goal_x, goal_y)

        # Recherche du chemin
        while not open_set.empty():
            # Extraire le nœud avec le score f le plus bas
            _, current = open_set.get()

            # Vérifier si on a atteint la destination
            if current == (goal_x, goal_y):
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            # Parcourir les voisins
            x, y = current
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Déplacement N/S/E/O
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < NB_TILES and 0 <= neighbor[1] < NB_TILES:  # Vérifier les limites
                    tentative_g_score = g_score[(x, y)] + 1
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = (x, y)
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor[0], neighbor[1], goal_x, goal_y)
                        open_set.put((f_score[neighbor], neighbor))

        return None  # Aucun chemin trouvé

    def move_along_path(self, delta_time=MOVE_DELAY):
        """Déplace le personnage le long du chemin avec un délai."""
        # Vérifie si le chemin n'est pas terminé
        if self.path_index < len(self.path):
            # Déplace le personnage à l'étape suivante
            self.player['x'], self.player['y'] = self.path[self.path_index]
            self.path_index += 1
            self.step_count += 1 # Incrémente le compteur de pas
            self.on_draw()  # Redessine l'écran pour montrer le mouvement
        else:
            arcade.unschedule(self.move_along_path)  # Arrête la planification lorsque le déplacement est terminé
            self.next_action()
    
    def action_move_to(self, coord):
        self.path = self.a_star(self.player['x'], self.player['y'], coord[0], coord[1])
        if self.path:
            self.path_index = 0
        self.action_move()

    
    def action_move(self, event=None):
        # Execute le mouvement
        self.action_count += 1  # Incrémente le compteur d'actions
        arcade.unschedule(self.move_along_path)  # Arrête le déplacement actuel
        arcade.schedule(self.move_along_path, MOVE_DELAY)  # Planifie la fonction de déplacement

    def action_pick(self, event=None):
        """Ramasse un objet sur la carte."""
        # Vérifie si le joueur est sur une case avec un objet
        current_pos = (self.player['x'], self.player['y'])
        if current_pos in self.items_on_map:
            item = self.items_on_map[current_pos]
            if len(self.inventory) == INVENTORY_SIZE:  # Si l'inventaire est plein
                dropped_item = self.inventory.popleft()  # Retirer l'objet le plus ancien
                self.items_on_map[current_pos] = dropped_item  # Le déposer sur la cellule
            else:
                del self.items_on_map[current_pos]  # Retirer l'objet de la carte
            self.inventory.append(item)  # Ajouter l'objet à l'inventaire
            self.action_count += 1  # Incrémente le compteur d'actions
        self.next_action()

    def action_drop(self, event=None):
        """Dépose un objet sur la carte."""
        # Vérifie si l'inventaire n'est pas vide
        if not self.inventory:
            return None
        
        # Execute l'action
        current_pos = (self.player['x'], self.player['y'])
        self.action_count += 1  # Incrémente le compteur d'actions
        if current_pos not in self.items_on_map:
            # Déposer l'objet sur la carte
            item_to_drop = self.inventory.popleft()  # Retirer le dernier objet de l'inventaire
            self.items_on_map[current_pos] = item_to_drop  # Le déposer sur la carte
        elif current_pos in self.items_on_map:
            # Échange avec l'objet existant
            existing_item = self.items_on_map[current_pos] # Récupérer l'objet existant
            item_to_drop = self.inventory.popleft() # Retirer le dernier objet de l'inventaire
            self.items_on_map[current_pos] = item_to_drop # Le déposer sur la carte
            self.inventory.append(existing_item) # Ajouter l'objet existant à l'inventaire
        self.next_action()
    
    def send_instruction(self, event=None):
        print("Instruction de l'utilisateur:", self.text_input.text)

        ## --- Uncomment this part to use LLM --- ##

        # Demande au LLM de produire la commande
        prompt = make_prompt(self.text_input.text, self.items_on_map, self.player, self.inventory)
        answer = make_request(prompt)
        thoughts, actions_output = extract_thoughts_and_command(answer)
        
        # Affiche les informations extraites
        print("THOUGHTS:", thoughts)
        print("ACTIONS:", actions_output)

        # Vérifie si les informations ont été extraites avec succès
        if thoughts is None or actions_output is None:
            print("Erreur lors de l'extraction des informations")
            return None
    

        ## --- Uncomment this part to use LLM --- ##
        
        # Actions possibles
        actions = {
            'PICK': self.action_pick,
            'DROP': self.action_drop,
            'MOVE': self.action_move_to,
        }
        # Extrait l'action de l'entrée utilisateur
        for action in actions_output:
                
            # Update la valeur de l'entrée utilisateur par la commande extraite de la réponse du LLM
            self.text_input.text = action
            text_split = self.text_input.text.split(" ")
            if len(text_split) == 2:
                action, coordinates = text_split
            else:
                action, coordinates = text_split[0], None

            # Exécute l'action correspondante
            if action in actions:
                if action == 'MOVE' and coordinates:
                    # Calculer le chemin vers les coordonnées spécifiées
                    x, y = coordinates.split(",")
                    self.action_queue.append((actions[action], (int(x),int(y))))
                else:
                    # Append action to the queue
                    self.action_queue.append((actions[action], None))

            self.text_input.clear()
            self.text_input.trigger_render()
            

        self.next_action()

            

if __name__ == "__main__":
    window = CookoBot()
    window.setup()
    arcade.run()
