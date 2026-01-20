from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random
import math

app = Ursina()

# ==================== 游戏配置 ====================
class Config:
    WORLD_SIZE = 50
    RENDER_DISTANCE = 30
    CHUNK_SIZE = 16
    
    STEVE_HEIGHT = 1.8
    EYE_HEIGHT = 1.62
    WALK_SPEED = 5.0
    JUMP_HEIGHT = 1.25
    
    TERRAIN_SCALE = 0.05
    TERRAIN_AMPLITUDE = 8
    TERRAIN_OCTAVES = 3

# ==================== 方块材质定义 ====================
class BlockType:
    GRASS = 1
    STONE = 2
    DIRT = 3
    OBSIDIAN = 4
    WOOD = 5
    SAND = 6
    WATER = 7
    LEAVES = 8

BLOCKS = {
    BlockType.GRASS: {
        'color': color.rgb(124, 189, 107),
        'name': '草方块',
        'breakable': True
    },
    BlockType.STONE: {
        'color': color.rgb(125, 125, 125),
        'name': '石头',
        'breakable': True
    },
    BlockType.DIRT: {
        'color': color.rgb(155, 108, 76),
        'name': '泥土',
        'breakable': True
    },
    BlockType.OBSIDIAN: {
        'color': color.rgb(20, 20, 200),
        'name': '黑曜石',
        'breakable': False
    },
    BlockType.WOOD: {
        'color': color.rgb(150, 110, 70),
        'name': '木头',
        'breakable': True
    },
    BlockType.SAND: {
        'color': color.rgb(230, 220, 170),
        'name': '沙子',
        'breakable': True
    },
    BlockType.WATER: {
        'color': color.rgba(50, 100, 200, 150),
        'name': '水',
        'breakable': False
    },
    BlockType.LEAVES: {
        'color': color.rgb(50, 150, 50),
        'name': '树叶',
        'breakable': True
    },
}

# ==================== 方块类 ====================
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), block_type=BlockType.GRASS):
        self.block_type = block_type
        block_info = BLOCKS[block_type]
        
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=block_info['color'],
            highlight_color=color.lime if block_info['breakable'] else color.red,
        )
        
        # 半透明方块设置
        if block_type == BlockType.WATER:
            self.alpha = 0.6

    def input(self, key):
        if self.hovered:
            # 右键放置方块
            if key == 'right mouse down':
                game_manager.place_block(self.position + mouse.normal)
            
            # 左键破坏方块
            if key == 'left mouse down':
                game_manager.break_block(self)

# ==================== 地形生成器 ====================
class TerrainGenerator:
    def __init__(self):
        self.noise = PerlinNoise(
            octaves=Config.TERRAIN_OCTAVES,
            seed=random.randint(1, 100000)
        )
        self.offset = Config.WORLD_SIZE // 2
    
    def get_height(self, x, z):
        """获取指定坐标的地形高度"""
        noise_value = self.noise([x * Config.TERRAIN_SCALE, z * Config.TERRAIN_SCALE])
        return floor(noise_value * Config.TERRAIN_AMPLITUDE)
    
    def generate_world(self):
        """生成整个世界"""
        print(f"正在生成 {Config.WORLD_SIZE}x{Config.WORLD_SIZE} 世界...")
        blocks = []
        
        for z in range(Config.WORLD_SIZE):
            for x in range(Config.WORLD_SIZE):
                cx = x - self.offset
                cz = z - self.offset
                
                y = self.get_height(cx, cz)
                
                # 生成草方块层
                blocks.append(Voxel(position=(cx, y, cz), block_type=BlockType.GRASS))
                
                # 生成泥土层 (2层)
                for i in range(1, 3):
                    blocks.append(Voxel(position=(cx, y - i, cz), block_type=BlockType.DIRT))
                
                # 生成石头层 (3层)
                for i in range(3, 6):
                    blocks.append(Voxel(position=(cx, y - i, cz), block_type=BlockType.STONE))
                
                # 随机生成树
                if random.random() < 0.02 and y > 0:
                    self.generate_tree(cx, y + 1, cz, blocks)
        
        print(f"世界生成完成！共 {len(blocks)} 个方块")
        return blocks
    
    def generate_tree(self, x, y, z, blocks):
        """生成一棵树"""
        tree_height = random.randint(4, 6)
        
        # 树干
        for i in range(tree_height):
            blocks.append(Voxel(position=(x, y + i, z), block_type=BlockType.WOOD))
        
        # 树叶 (简单的球形)
        leaf_y = y + tree_height - 1
        for lx in range(-2, 3):
            for lz in range(-2, 3):
                for ly in range(0, 3):
                    if abs(lx) + abs(lz) + abs(ly) <= 3:
                        if not (lx == 0 and lz == 0 and ly < 2):
                            blocks.append(Voxel(
                                position=(x + lx, leaf_y + ly, z + lz),
                                block_type=BlockType.LEAVES
                            ))

# ==================== 游戏管理器 ====================
class GameManager:
    def __init__(self):
        self.current_block = BlockType.GRASS
        self.blocks = []
        self.hand = None
        self.ui = None
        
    def place_block(self, position):
        """放置方块"""
        # 边界检查
        if abs(position.x) >= Config.WORLD_SIZE or abs(position.z) >= Config.WORLD_SIZE:
            return
        
        # 不能放置在玩家位置
        if distance(position, player.position) < 1.5:
            return
        
        # 创建方块
        new_block = Voxel(position=position, block_type=self.current_block)
        self.blocks.append(new_block)
        self.hand.swing()
    
    def break_block(self, block):
        """破坏方块"""
        if not BLOCKS[block.block_type]['breakable']:
            print(f"{BLOCKS[block.block_type]['name']} 无法破坏！")
            return
        
        self.hand.swing()
        if block in self.blocks:
            self.blocks.remove(block)
        destroy(block)
    
    def select_block(self, block_type):
        """选择方块类型"""
        if block_type in BLOCKS:
            self.current_block = block_type
            self.ui.update_selection()
            self.hand.color = BLOCKS[block_type]['color']

# ==================== 玩家手部 ====================
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            texture='white_cube',
            color=BLOCKS[BlockType.GRASS]['color'],
            scale=(0.2, 0.2, 0.8),
            position=(0.4, -0.4, 0.8),
            rotation=(10, -10, 0)
        )
    
    def swing(self):
        """挥手动画"""
        self.animate_rotation((30, -20, 0), duration=0.1)
        self.animate_rotation((10, -10, 0), duration=0.1, delay=0.1)

# ==================== UI界面 ====================
class GameUI:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.hotbar_slots = []
        self.selection_indicator = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 准星
        Entity(
            parent=camera.ui,
            model='quad',
            texture='cursor',
            scale=0.015,
            color=color.white
        )
        
        # 快捷栏
        block_types = [
            BlockType.GRASS,
            BlockType.STONE,
            BlockType.DIRT,
            BlockType.WOOD,
            BlockType.SAND
        ]
        
        for i, block_type in enumerate(block_types):
            # 槽位背景
            slot = Entity(
                parent=camera.ui,
                model='quad',
                color=color.rgb(60, 60, 60),
                position=(-0.25 + i * 0.13, -0.45),
                scale=(0.1, 0.1)
            )
            
            # 方块预览
            preview = Entity(
                parent=slot,
                model='cube',
                color=BLOCKS[block_type]['color'],
                scale=0.5,
                rotation=(20, 20, 0)
            )
            
            # 数字标签
            Entity(
                parent=slot,
                model='quad',
                text=str(i + 1),
                color=color.white,
                scale=0.5,
                position=(0, 0.6, -0.1)
            )
            
            self.hotbar_slots.append({
                'slot': slot,
                'preview': preview,
                'block_type': block_type
            })
        
        # 选择指示器
        self.selection_indicator = Entity(
            parent=camera.ui,
            model='quad',
            color=color.clear,
            outline_color=color.yellow,
            outline_thickness=3,
            scale=(0.11, 0.11),
            position=self.hotbar_slots[0]['slot'].position
        )
        
        # 方块名称显示
        self.block_name = Text(
            text=BLOCKS[BlockType.GRASS]['name'],
            origin=(0, 1),
            position=(-0.85, 0.45),
            scale=2,
            color=color.white
        )
    
    def update_selection(self):
        """更新选择指示器位置"""
        for i, slot_info in enumerate(self.hotbar_slots):
            if slot_info['block_type'] == self.game_manager.current_block:
                self.selection_indicator.position = slot_info['slot'].position
                self.block_name.text = BLOCKS[self.game_manager.current_block]['name']
                slot_info['slot'].color = color.rgb(100, 100, 100)
            else:
                slot_info['slot'].color = color.rgb(60, 60, 60)

# ==================== 初始化游戏 ====================
# 创建游戏管理器
game_manager = GameManager()

# 生成地形
terrain_gen = TerrainGenerator()
game_manager.blocks = terrain_gen.generate_world()

# 创建玩家
player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.speed = Config.WALK_SPEED
player.height = Config.STEVE_HEIGHT
player.jump_height = Config.JUMP_HEIGHT
player.camera_pivot.y = Config.EYE_HEIGHT - (Config.STEVE_HEIGHT / 2)
player.position = (0, 15, 0)

# 创建手部
game_manager.hand = Hand()

# 创建UI
game_manager.ui = GameUI(game_manager)

# 设置环境
sky = Sky()
sky.color = color.rgb(135, 206, 235)
scene.fog_color = color.rgb(135, 206, 235)
scene.fog_density = 0.015

# 环境光
AmbientLight(color=color.rgba(255, 255, 255, 0.8))
DirectionalLight(y=2, z=3, shadows=True)

# ==================== 输入处理 ====================
def input(key):
    """全局输入处理"""
    # 数字键选择方块
    if key in '12345':
        index = int(key) - 1
        if index < len(game_manager.ui.hotbar_slots):
            block_type = game_manager.ui.hotbar_slots[index]['block_type']
            game_manager.select_block(block_type)
    
    # 鼠标滚轮切换方块
    elif key == 'scroll up':
        current_index = next(
            (i for i, s in enumerate(game_manager.ui.hotbar_slots) 
             if s['block_type'] == game_manager.current_block),
            0
        )
        new_index = (current_index - 1) % len(game_manager.ui.hotbar_slots)
        game_manager.select_block(game_manager.ui.hotbar_slots[new_index]['block_type'])
    
    elif key == 'scroll down':
        current_index = next(
            (i for i, s in enumerate(game_manager.ui.hotbar_slots) 
             if s['block_type'] == game_manager.current_block),
            0
        )
        new_index = (current_index + 1) % len(game_manager.ui.hotbar_slots)
        game_manager.select_block(game_manager.ui.hotbar_slots[new_index]['block_type'])
    
    # ESC 退出游戏
    elif key == 'escape':
        application.quit()

# ==================== 游戏循环 ====================
time_passed = 0

def update():
    """每帧更新"""
    global time_passed
    time_passed += time.dt
    
    # 玩家掉出世界重生
    if player.y < -30:
        player.position = (0, 15, 0)
        player.velocity = Vec3(0, 0, 0)
    
    # 简单的昼夜循环
    cycle_speed = 0.02
    brightness = (math.sin(time_passed * cycle_speed) + 1) / 2 * 0.5 + 0.5
    sky.color = color.rgb(
        135 * brightness,
        206 * brightness,
        235 * brightness
    )

# 运行游戏
print("\n=== Minecraft 游戏控制 ===")
print("WASD - 移动")
print("空格 - 跳跃")
print("鼠标 - 视角")
print("左键 - 破坏方块")
print("右键 - 放置方块")
print("1-5 - 选择方块")
print("滚轮 - 切换方块")
print("ESC - 退出游戏")
print("========================\n")

app.run()