import random

class Settings:
    # 世界
    SEED = random.randint(0, 100000)
    WORLD_SIZE = 5
    CHUNK_SIZE = 16

    # 地形
    TERRAIN_SCALE = 0.05
    TERRAIN_AMPLITUDE = 8
    TERRAIN_OCTAVES = 3

    # 玩家
    WALK_SPEED = 5.0
    RUN_SPEED = 8.0
    JUMP_HEIGHT = 1.25
    PLAYER_HEIGHT = 1.8
