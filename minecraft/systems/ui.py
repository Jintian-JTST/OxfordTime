from ursina import *
from minecraft.config.blocks import BlockRegistry, BlockID

class UIManager:
    def __init__(self):
        self.available_blocks = [
            BlockID.GRASS, BlockID.STONE, BlockID.DIRT,
            BlockID.WOOD, BlockID.SAND, BlockID.OBSIDIAN
        ]
        self.current_slot = 0
        self.slots = []
        self.setup()

    def setup(self):
        Entity(parent=camera.ui, model='quad',
               scale=0.015, rotation_z=45)

        for i,b in enumerate(self.available_blocks):
            slot = Entity(
                parent=camera.ui,
                model='quad',
                scale=(0.08,0.08),
                position=(-0.3+i*0.1,-0.45),
                color=BlockRegistry.get(b)['color']
            )
            self.slots.append(slot)

        self.selector = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.09,0.09),
            color=color.yellow,
            position=self.slots[0].position
        )

    def select_slot(self, i):
        if 0 <= i < len(self.slots):
            self.current_slot = i
            self.selector.position = self.slots[i].position

    def get_current_block_id(self):
        return self.available_blocks[self.current_slot]
