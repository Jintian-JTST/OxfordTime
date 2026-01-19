from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random

app = Ursina()

# --- 1. 参数设置 ---
STEVE_HEIGHT = 1.8
EYE_HEIGHT = 1.62
WALK_SPEED = 5.0 
JUMP_HEIGHT = 1.25

# [优化速度] 把 64 改成 48。
# 64x64=4096个点，48x48=2304个点。
# 稍微小一点点，但加载速度快一倍。
WORLD_SIZE = 48 

# --- 2. 材质与颜色 ---
blocks_meta = {
    1: {'color': color.rgb(124, 189, 107), 'name': 'Grass'},
    2: {'color': color.rgb(125, 125, 125), 'name': 'Stone'},
    3: {'color': color.rgb(155, 108, 76),  'name': 'Dirt'},
    4: {'color': color.rgb(20, 20, 200),   'name': 'Obsidian'},
    5: {'color': color.rgb(150, 130, 80),  'name': 'Wood'},
}

current_block_id = 1

# --- 3. 核心方块类 ---
class Voxel(Button):
    def __init__(self, position=(0,0,0), block_id=1):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube', # 必须保留这个，颜色才能生效
            color=blocks_meta[block_id]['color'],
            highlight_color=color.lime,
        )
        self.block_id = block_id

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                hand.swing() 
                if self.block_id != 4: 
                    Voxel(position=self.position + mouse.normal, block_id=current_block_id)
            
            if key == 'left mouse down':
                hand.swing()
                destroy(self)

# --- 4. 地形生成 (加速版) ---
noise_gen = PerlinNoise(octaves=3, seed=random.randint(1, 10000))
scale = 0.05   
amplitude = 6  
offset = WORLD_SIZE // 2

print(f"正在生成 {WORLD_SIZE}x{WORLD_SIZE} 地形...")

# 使用 List 来收集要生成的方块，虽然在 Ursina 里还是要一个个生成，但逻辑更清晰
for z in range(WORLD_SIZE):
    for x in range(WORLD_SIZE):
        cx = x - offset 
        cz = z - offset

        height_value = noise_gen([cx * scale, cz * scale])
        y = floor(height_value * amplitude)
        
        # [顶层] 草方块
        Voxel(position=(cx, y, cz), block_id=1)
        
        # [第二层] 泥土
        Voxel(position=(cx, y-1, cz), block_id=3)
        
        # [优化速度] 去掉了 y-2 的石头层生成。
        # 除非你挖开泥土，否则看不到下面。这能减少 33% 的加载时间。
        # 如果你真的很想挖矿，可以在这里加回来，但会变慢。

print("地形生成完毕！")

# --- 5. 玩家控制器 ---
player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.speed = WALK_SPEED
player.height = STEVE_HEIGHT
player.jump_height = JUMP_HEIGHT
player.camera_pivot.y = EYE_HEIGHT - (STEVE_HEIGHT / 2) 

# 出生在中心高空
player.position = (0, 10, 0)

crosshair = Entity(parent=camera.ui, model='quad', texture='cursor', scale=0.015, color=color.white)

# --- 6. 史蒂夫的手 ---
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            texture='white_cube',
            color=color.rgb(180, 140, 110),
            scale=(0.2, 0.2, 0.8),
            position=(0.4, -0.4, 0.8),
            rotation=(10, -10, 0)
        )

    def swing(self):
        self.animate_rotation((30, -20, 0), duration=0.1)
        self.animate_rotation((10, -10, 0), duration=0.1, delay=0.1)

hand = Hand()

# --- 7. 环境 (修复报错的部分) ---
sky = Sky() 
sky.color = color.rgb(135, 206, 235)

# [错误修复] 不使用 Fog 类，直接设置 scene 属性
scene.fog_color = color.rgb(135, 206, 235)
# 密度越小，雾越远。0.02 大约对应 50 格左右的视距
scene.fog_density = 0.02 

def update():
    global current_block_id
    if held_keys['1']: current_block_id = 1
    if held_keys['2']: current_block_id = 2
    if held_keys['3']: current_block_id = 3
    if held_keys['4']: current_block_id = 4
    if held_keys['5']: current_block_id = 5
    
    if player.y < -30:
        player.position = (0, 10, 0)

app.run()