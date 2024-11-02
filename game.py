import arcade
import random
import time
from queue import PriorityQueue
import arcade.gui
from collections import deque

# Constantes du jeu
PADDING = 25
TILE_SIZE = 50
OBJ_SIZE = TILE_SIZE - 10
NB_TILES = 20
MAP_SIZE = NB_TILES * TILE_SIZE
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 100
MENU_WIDTH = BUTTON_WIDTH * 2 + PADDING
SCREEN_WIDTH = TILE_SIZE * NB_TILES + PADDING * 3 + MENU_WIDTH
SCREEN_HEIGHT = TILE_SIZE * NB_TILES + PADDING * 2
INVENTORY_HEIGHT = 300
INVENTORY_SIZE = 3
MOVE_DELAY = 0.2  # 250 ms

class MiniJeuArcade(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Mini jeu 2D")
        self.tile_map = None
        self.player = None
        self.inventory = []
        self.fruits = ['banane', 'pomme', 'fraise']
        self.items_on_map = {}
        self.path = []  # Chemin calculé
        self.path_index = 0  # Indice du prochain pas à suivre
        self.inventory = deque(maxlen=INVENTORY_SIZE)  # Inventaire limité à 3 objets

        # Create a horizontale BoxGroup to align buttons
        self.action_box = arcade.gui.UIBoxLayout(vertical=False, x=SCREEN_WIDTH-MENU_WIDTH-PADDING, y=SCREEN_HEIGHT-PADDING)
        self.chat_box = arcade.gui.UIBoxLayout(vertical=True, x=SCREEN_WIDTH-MENU_WIDTH-PADDING, y=SCREEN_HEIGHT//2)

        # Créer le bouton de ramassage
        pick_up_button = arcade.gui.UIFlatButton(text="Ramasser", width=BUTTON_WIDTH, style={'bg_color': arcade.color.MAUVE_TAUPE})
        pick_up_button.on_click = self.pick_up_item
        self.action_box.add(pick_up_button.with_space_around(right=PADDING))

        # Créer le bouton de dépôt
        drop_button = arcade.gui.UIFlatButton(text="Déposer", width=BUTTON_WIDTH, style={'bg_color': arcade.color.MAUVE_TAUPE})
        drop_button.on_click = self.drop_item
        self.action_box.add(drop_button)

        # Ajoutez ce bloc de code dans la méthode __init__ juste après la création des boutons de ramassage et de dépôt
        self.text_input = arcade.gui.UIInputText(
          text_color=arcade.color.BLACK,
          font_size=12,
          height=100,
          width=200,
          text='Hello ..',
          multiline=True,
        )
        self.chat_box.add(self.text_input)

        send_button = arcade.gui.UIFlatButton(text="Envoyer", width=BUTTON_WIDTH, style={'bg_color': arcade.color.MAUVE_TAUPE})
        send_button.on_click = self.send_text
        self.chat_box.add(send_button)

        # Créer le gestionnaire d'interface utilisateur
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.manager.add(self.action_box)
        self.manager.add(self.chat_box)


    def setup(self):
        """Initialisation de la carte et du personnage."""
        # Background
        arcade.set_background_color((250, 235, 235))

        # Création de la carte & positionnement du personnage
        self.tile_map = [[None for _ in range(NB_TILES)] for _ in range(NB_TILES)]
        x_start = random.randint(0, NB_TILES - 1)
        y_start = random.randint(0, NB_TILES - 1)
        self.player = {'x': x_start, 'y': y_start}  # Position initiale du personnage

        # Chargement des textures
        self.player_texture = arcade.load_texture("images/robot.png")
        self.fruit_textures = {
            'banane': arcade.load_texture("images/banane.png"),
            'pomme': arcade.load_texture("images/pomme.png"),
            'fraise': arcade.load_texture("images/poire.png")
        }

        # Placement aléatoire des objets sur la carte
        for _ in range(20):  # Exemple : 20 fruits aléatoires
            x = random.randint(0, NB_TILES - 1)
            y = random.randint(0, NB_TILES - 1)
            fruit = random.choice(self.fruits)
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
                # if (col, row) in self.items_on_map.keys():
                #     arcade.draw_rectangle_filled(x + TILE_SIZE // 2, y + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE, arcade.color.MAUVELOUS)
                # else:
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

        # Afficher l'inventaire au-dessus des boutons
        arcade.draw_text(f"Inventaire ({len(self.inventory)}/{INVENTORY_SIZE})", SCREEN_WIDTH-MENU_WIDTH-PADDING, SCREEN_HEIGHT-BUTTON_HEIGHT-2*PADDING - 7, arcade.color.MAUVE_TAUPE, 14)
        arcade.draw_rectangle_outline(SCREEN_WIDTH-MENU_WIDTH-PADDING + MENU_WIDTH//2, SCREEN_HEIGHT-BUTTON_HEIGHT-3*PADDING -INVENTORY_HEIGHT//2, MENU_WIDTH, INVENTORY_HEIGHT, arcade.color.MAUVE_TAUPE)
        for i, item in enumerate(self.inventory):
            arcade.draw_text(item, SCREEN_WIDTH-MENU_WIDTH-PADDING + 10, SCREEN_HEIGHT-BUTTON_HEIGHT-4*PADDING - 20*i, arcade.color.MAUVE_TAUPE, 14)

        # Afficher les boutons
        self.manager.draw()



    def on_mouse_press(self, x, y, button, modifiers):
        grid_x = (x - PADDING) // TILE_SIZE
        grid_y = (y - PADDING) // TILE_SIZE

        if 0 <= grid_x < NB_TILES and 0 <= grid_y < NB_TILES:
            self.path = self.a_star(self.player['x'], self.player['y'], grid_x, grid_y)
            if self.path:
                self.path_index = 0  # Réinitialise l'index de l'étape
                arcade.unschedule(self.move_along_path)  # Arrête le déplacement actuel
                arcade.schedule(self.move_along_path, MOVE_DELAY)  # Planifie la fonction de déplacement


    def a_star(self, start_x, start_y, goal_x, goal_y):
        """Implémentation de l'algorithme A*."""
        def heuristic(x1, y1, x2, y2):
            return abs(x1 - x2) + abs(y1 - y2)

        open_set = PriorityQueue()
        open_set.put((0, (start_x, start_y)))
        came_from = {}
        g_score = {pos: float('inf') for pos in [(x, y) for x in range(NB_TILES) for y in range(NB_TILES)]}
        g_score[(start_x, start_y)] = 0
        f_score = g_score.copy()
        f_score[(start_x, start_y)] = heuristic(start_x, start_y, goal_x, goal_y)

        while not open_set.empty():
            _, current = open_set.get()
            if current == (goal_x, goal_y):
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

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

    def move_along_path(self, delta_time):
        """Déplace le personnage le long du chemin avec un délai."""
        if self.path_index < len(self.path):
            self.player['x'], self.player['y'] = self.path[self.path_index]
            self.path_index += 1
            self.on_draw()  # Redessine l'écran pour montrer le mouvement
        else:
            arcade.unschedule(self.move_along_path)  # Arrête la planification lorsque le déplacement est terminé

    def pick_up_item(self, event):
        current_pos = (self.player['x'], self.player['y'])
        if current_pos in self.items_on_map:
            item = self.items_on_map[current_pos]
            if len(self.inventory) == INVENTORY_SIZE:  # Si l'inventaire est plein
                dropped_item = self.inventory.popleft()  # Retirer l'objet le plus ancien
                self.items_on_map[current_pos] = dropped_item  # Le déposer sur la cellule
            else:
                del self.items_on_map[current_pos]  # Retirer l'objet de la carte
            self.inventory.append(item)  # Ajouter l'objet à l'inventaire

    def drop_item(self, event):
        current_pos = (self.player['x'], self.player['y'])
        if self.inventory and current_pos not in self.items_on_map:
            item_to_drop = self.inventory.pop()  # Retirer le dernier objet de l'inventaire
            self.items_on_map[current_pos] = item_to_drop  # Le déposer sur la carte
        elif self.inventory and current_pos in self.items_on_map:
            # Échange avec l'objet existant
            existing_item = self.items_on_map[current_pos]
            item_to_drop = self.inventory.pop()
            self.items_on_map[current_pos] = item_to_drop
            self.inventory.append(existing_item)
    
    def send_text(self, event):
        print("Texte envoyé :", self.text_input.text)
        self.text_input.text = ""  # Efface le texte après l'envoi




if __name__ == "__main__":
    window = MiniJeuArcade()
    window.setup()
    arcade.run()
