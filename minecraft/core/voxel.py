from ursina import *
# 注意：这里必须带上 minecraft. 前缀
from minecraft.config.blocks import BlockRegistry 

class Voxel(Entity):  # 改为继承 Entity，速度快 10 倍
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
            collider='box' # 必须手动加碰撞箱
        )

        self.breakable = info['breakable']