from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from minecraft.config.settings import Settings
from minecraft.config.blocks import BlockRegistry
from minecraft.core.voxel import Voxel



class PlayerController(FirstPersonController):
    def __init__(self, world, ui):
        super().__init__()
        self.world = world
        self.ui = ui

        self.speed = Settings.WALK_SPEED
        self.jump_height = Settings.JUMP_HEIGHT
        self.height = Settings.PLAYER_HEIGHT
        self.gravity = 0.6
        # 确保改成 (0, 30, 0)，给一点高度让你掉下来
        self.position = (0, 30, 0)

        self.hand = Entity(
            parent=self.camera_pivot,
            model='cube',
            scale=(0.2,0.2,0.8),
            position=(0.35,-0.2,0.5),
            rotation=(0,-10,0)
        )
        self.update_hand_color()

    def update_hand_color(self):
        self.hand.color = BlockRegistry.get(
            self.ui.get_current_block_id()
        )['color']

    def input(self, key):
        super().input(key)

        if key in '123456':
            self.ui.select_slot(int(key)-1)
            self.update_hand_color()

        if key == 'left mouse down':
            self.break_block()
        if key == 'right mouse down':
            self.place_block()

    def break_block(self):
        self.animate_hand()
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, Voxel):
            voxel = mouse.hovered_entity
            if voxel.breakable:
                self.world.remove_block(voxel)

    def place_block(self):
        self.animate_hand()
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, Voxel):
            pos = mouse.hovered_entity.position + mouse.normal
            if distance(pos, self.position) > 1.5:
                self.world.create_block(pos, self.ui.get_current_block_id())

    def animate_hand(self):
        self.hand.animate_rotation((30,-10,0), duration=0.1)
        self.hand.animate_rotation((0,-10,0), delay=0.1)
