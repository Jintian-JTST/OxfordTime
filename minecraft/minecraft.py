from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise  # 引入新安装的噪声库
import random

app = Ursina()

# --- 1. 参数设置 (参考 Minecraft Wiki) ---
STEVE_HEIGHT = 1.8
EYE_HEIGHT = 1.62
WALK_SPEED = 5.0 
JUMP_HEIGHT = 1.25

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
            #texture='white_cube',
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

# --- 4. 地形生成 (修正版) ---
# 使用 perlin_noise 库
noise_gen = PerlinNoise(octaves=3, seed=random.randint(1, 10000))
scale = 0.1   # 地形平滑度：越小越平缓
amplitude = 6 # 地形高度差：越大山越高
WORLD_SIZE = 30  # 世界大小
offset = WORLD_SIZE // 2

for z in range(WORLD_SIZE):
    for x in range(WORLD_SIZE):
        # 让坐标以中心为原点，这样地图会向四周扩展
        cx = x - offset 
        cz = z - offset

        # 计算高度: noise返回 -0.5 到 0.5，我们需要把它放大并取整
        height_value = noise_gen([cx * scale, cz * scale])
        y = floor(height_value * amplitude)
        
        # 放置顶层草方块
        Voxel(position=(x, y, z), block_id=1)
        
        # 为了美观，填充下面两层
        Voxel(position=(x, y-1, z), block_id=3) # 泥土
        Voxel(position=(x, y-2, z), block_id=2) # 石头
        
        # 如果太深了，封底基岩（防止看到虚空）
        Voxel(position=(x, -4, z), block_id=2) 

# --- 5. 玩家控制器 ---
player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.speed = WALK_SPEED
player.height = STEVE_HEIGHT
player.jump_height = JUMP_HEIGHT
player.camera_pivot.y = EYE_HEIGHT - (STEVE_HEIGHT / 2) 

# 初始位置设高一点，防止出生在方块里
player.y = 5 

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

# --- 7. 环境 ---
sky = Sky(texture='sky_default')
scene.fog_color = color.rgb(200, 230, 255)
scene.fog_density = 0.04

def update():
    global current_block_id
    if held_keys['1']: current_block_id = 1
    if held_keys['2']: current_block_id = 2
    if held_keys['3']: current_block_id = 3
    if held_keys['4']: current_block_id = 4
    if held_keys['5']: current_block_id = 5
    
    if player.y < -10:
        player.position = (10, 10, 10)

app.run()