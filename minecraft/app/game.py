from ursina import *
from minecraft.systems.world import WorldManager
from minecraft.systems.ui import UIManager
from minecraft.core.player import PlayerController


class MinecraftGame:
    def __init__(self):
        self.app = Ursina()

        # --- 修改开始 ---
        # 暂时把背景改成黑色，方便看清楚方块
        window.color = color.azure  # 或者 color.cyan
        scene.fog_color = window.color        # 暂时关掉雾气，防止远处一片白
        # scene.fog_density = 0.02 
        # scene.fog_color = window.color
        # --- 修改结束 ---

        self.world = WorldManager()
        # ... 后面的代码不变
        self.ui = UIManager()
        self.world.generate_terrain()
        self.player = PlayerController(self.world, self.ui)

        self.app.input = self.input

    def input(self, key):
        # 删掉 super().input(key)
        if key == 'escape':
            application.quit()

    def run(self):
        self.app.run()
