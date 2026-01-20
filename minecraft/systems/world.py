import random, math
from perlin_noise import PerlinNoise
from ursina import destroy
from minecraft.config.settings import Settings
from minecraft.config.blocks import BlockID
from minecraft.core.voxel import Voxel

class WorldManager:
    def __init__(self):
        self.noise = PerlinNoise(
            octaves=Settings.TERRAIN_OCTAVES,
            seed=Settings.SEED
        )
        self.voxels = {}

    def generate_terrain(self):
        offset = Settings.WORLD_SIZE // 2

        for z in range(Settings.WORLD_SIZE):
            for x in range(Settings.WORLD_SIZE):
                wx, wz = x-offset, z-offset
                h = self.get_height(wx, wz)

                self.create_block((wx,h,wz), BlockID.GRASS)
                for d in range(1,4):
                    self.create_block(
                        (wx,h-d,wz),
                        BlockID.DIRT if d < 2 else BlockID.STONE
                    )

                if random.random() < 0.02 and h > 0:
                    self.generate_tree(wx, h+1, wz)

    def get_height(self, x, z):
        v = self.noise([x*Settings.TERRAIN_SCALE, z*Settings.TERRAIN_SCALE])
        return math.floor(v * Settings.TERRAIN_AMPLITUDE)

    def create_block(self, pos, block_id):
        pos = tuple(pos)
        if pos in self.voxels:
            return
        self.voxels[pos] = Voxel(pos, block_id)

    def remove_block(self, voxel):
        pos = tuple(voxel.position)
        if pos in self.voxels:
            del self.voxels[pos]
            destroy(voxel)

    def generate_tree(self, x, y, z):
        h = random.randint(4,6)
        for i in range(h):
            self.create_block((x,y+i,z), BlockID.WOOD)

        for ly in range(2):
            for lx in range(-1,2):
                for lz in range(-1,2):
                    if lx==lz==ly==0: continue
                    self.create_block((x+lx,y+h-2+ly,z+lz), BlockID.LEAVES)
