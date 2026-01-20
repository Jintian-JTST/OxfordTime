from ursina import *
from minecraft.systems.world import WorldManager
from minecraft.systems.ui import UIManager
from minecraft.core.player import PlayerController


class MinecraftGame:
    def __init__(self):
        self.app = Ursina()

        window.color = color.rgb(135,206,235)
        scene.fog_density = 0.02
        scene.fog_color = window.color

        self.world = WorldManager()
        self.ui = UIManager()
        self.world.generate_terrain()
        self.player = PlayerController(self.world, self.ui)

        self.app.input = self.input

    def input(self, key):
        if key == 'escape':
            application.quit()

    def run(self):
        self.app.run()
