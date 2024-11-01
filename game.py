import arcade
import random


# Constantes du jeu
PADDING = 25
TILE_SIZE = 25
MAP_SIZE = 40
SCREEN_WIDTH = TILE_SIZE * MAP_SIZE + PADDING * 2
SCREEN_HEIGHT = TILE_SIZE * MAP_SIZE + PADDING * 2
INVENTORY_SIZE = 3

class MiniJeuArcade(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Mini jeu 2D")
        self.tile_map = None
        self.player = None
        self.inventory = []
        self.fruits = ['banane', 'pomme', 'fraise']
        self.items_on_map = {}

    def setup(self):
        """Initialisation de la carte et du personnage."""
        self.tile_map = [[None for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        x_start = random.randint(0, MAP_SIZE - 1)
        y_start = random.randint(0, MAP_SIZE - 1)
        self.player = {'x': x_start, 'y': y_start}  # Position initiale du personnage

        # Placement aléatoire des objets sur la carte
        for _ in range(20):  # Exemple : 20 fruits aléatoires
            x = random.randint(0, MAP_SIZE - 1)
            y = random.randint(0, MAP_SIZE - 1)
            fruit = random.choice(self.fruits)
            self.items_on_map[(x, y)] = fruit

    def on_draw(self):
        """Rendu de l'écran."""
        arcade.start_render()
        # Dessiner la grille
        for row in range(MAP_SIZE):
            for col in range(MAP_SIZE):
                x = col * TILE_SIZE + PADDING
                y = row * TILE_SIZE + PADDING
                arcade.draw_rectangle_outline(x + TILE_SIZE // 2, y + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE, arcade.color.WHITE)

        # Dessiner les objets sur la carte
        for (x, y), fruit in self.items_on_map.items():
            position_x = x * TILE_SIZE + TILE_SIZE // 2 + PADDING
            position_y = y * TILE_SIZE + TILE_SIZE // 2 + PADDING
            color = arcade.color.YELLOW if fruit == 'banane' else arcade.color.RED if fruit == 'pomme' else arcade.color.PINK
            arcade.draw_circle_filled(position_x, position_y, TILE_SIZE // 4, color)

        # Dessiner le personnage
        arcade.draw_rectangle_filled(self.player['x'] * TILE_SIZE + TILE_SIZE // 2 + PADDING,
                                     self.player['y'] * TILE_SIZE + TILE_SIZE // 2 + PADDING,
                                     TILE_SIZE, TILE_SIZE, arcade.color.BLUE)

        # Afficher l'inventaire
        y_offset = SCREEN_HEIGHT - 30
        for item in self.inventory:
            arcade.draw_text(item, SCREEN_WIDTH - 150, y_offset, arcade.color.WHITE, 12)
            y_offset -= 20

    # def on_mouse_press(self, x, y, button, modifiers):
    #     """Gérer le clic de la souris pour le déplacement."""
    #     grid_x = x // TILE_SIZE
    #     grid_y = y // TILE_SIZE
    #     # A* pour définir le chemin à suivre


    # def on_key_press(self, key, modifiers):
    #     """Actions supplémentaires comme déposer un objet."""
    #     if key == arcade.key.SPACE:
    #         if self.inventory:
    #             item = self.inventory.pop()
    #             self.items_on_map[(self.player['x'], self.player['y'])] = item

if __name__ == "__main__":
    window = MiniJeuArcade()
    window.setup()
    arcade.run()
