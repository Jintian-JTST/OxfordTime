import random

class Settings:
    # 世界
    SEED = random.randint(0, 100000)
    WORLD_SIZE = 40  # <--- 改回 30 或 40 (现在电脑带得动了！)
    CHUNK_SIZE = 16

    # 地形
    TERRAIN_SCALE = 0.05
    TERRAIN_AMPLITUDE = 8
    TERRAIN_OCTAVES = 3

    # 玩家
    WALK_SPEED = 8.0     # <--- 稍微改快一点，走路更爽
    RUN_SPEED = 12.0
    JUMP_HEIGHT = 1.5    # <--- 跳得稍微高一点，防止被地面缝隙绊倒
    PLAYER_HEIGHT = 1.8