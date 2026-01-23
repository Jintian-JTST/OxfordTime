from ursina import *
from minecraft.config.blocks import BlockRegistry

class Voxel(Entity):
    def __init__(self, position, block_id):
        self.block_id = block_id
        info = BlockRegistry.get(block_id)

        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=info['color'],
            scale=1,
            collider='box'  # <--- 必须有这一行！否则你会穿过地面，鼠标也选不中它
        )
        self.breakable = info['breakable']