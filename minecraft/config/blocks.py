from ursina import color

class BlockID:
    GRASS = 1
    STONE = 2
    DIRT = 3
    OBSIDIAN = 4
    WOOD = 5
    SAND = 6
    LEAVES = 7


class BlockRegistry:
    DATA = {
        BlockID.GRASS:    {'color': color.rgb(124,189,107), 'breakable': True},
        BlockID.STONE:    {'color': color.rgb(125,125,125), 'breakable': True},
        BlockID.DIRT:     {'color': color.rgb(155,108,76),  'breakable': True},
        BlockID.OBSIDIAN: {'color': color.rgb(20,20,200),   'breakable': False},
        BlockID.WOOD:     {'color': color.rgb(150,110,70),  'breakable': True},
        BlockID.SAND:     {'color': color.rgb(230,220,170), 'breakable': True},
        BlockID.LEAVES:   {'color': color.rgb(50,150,50),   'breakable': True},
    }

    @staticmethod
    def get(block_id):
        return BlockRegistry.DATA.get(block_id, BlockRegistry.DATA[BlockID.GRASS])
