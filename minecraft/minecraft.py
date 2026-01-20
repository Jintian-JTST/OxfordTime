from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random
import math
from ursina.shaders import basic_lighting_shader
from ursina.shaders import unlit_shader
from ursina import application
application.lighting = False

app = Ursina()

# ==================== Game Configuration ====================
class Config:
    WORLD_SIZE = 20
    RENDER_DISTANCE = 30
    CHUNK_SIZE = 16
    
    STEVE_HEIGHT = 1.8
    EYE_HEIGHT = 1.62
    WALK_SPEED = 5.0
    JUMP_HEIGHT = 1.25
    
    TERRAIN_SCALE = 0.05
    TERRAIN_AMPLITUDE = 8
    TERRAIN_OCTAVES = 3

# ==================== Block Type Definitions ====================
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
        'name': 'Grass',
        'breakable': True
    },
    BlockType.STONE: {
        'color': color.rgb(125, 125, 125),
        'name': 'Stone',
        'breakable': True
    },
    BlockType.DIRT: {
        'color': color.rgb(155, 108, 76),
        'name': 'Dirt',
        'breakable': True
    },
    BlockType.OBSIDIAN: {
        'color': color.rgb(20, 20, 200),
        'name': 'Obsidian',
        'breakable': False
    },
    BlockType.WOOD: {
        'color': color.rgb(150, 110, 70),
        'name': 'Wood',
        'breakable': True
    },
    BlockType.SAND: {
        'color': color.rgb(230, 220, 170),
        'name': 'Sand',
        'breakable': True
    },
    BlockType.WATER: {
        'color': color.rgba(50, 100, 200, 150),
        'name': 'Water',
        'breakable': False
    },
    BlockType.LEAVES: {
        'color': color.rgb(50, 150, 50),
        'name': 'Leaves',
        'breakable': True
    },
}

# ==================== Voxel Class ====================
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), block_type=BlockType.GRASS):
        self.block_type = block_type
        block_info = BLOCKS[block_type]
        
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=None,              # 1. 必须是 None
            color=block_info['color'],
            shader=unlit_shader,       # 2. 强制使用 unlit_shader
            highlight_color=color.lime if block_info['breakable'] else color.red,
            # 删掉 unlit=False 或 unlit=True，因为我们要直接控制 shader
        )
        
        # Semi-transparent blocks
        if block_type == BlockType.WATER:
            self.alpha = 0.6

    def input(self, key):
        if self.hovered:
            # Right click to place block
            if key == 'right mouse down':
                game_manager.place_block(self.position + mouse.normal)
            
            # Left click to break block
            if key == 'left mouse down':
                game_manager.break_block(self)

# ==================== Terrain Generator ====================
class TerrainGenerator:
    def __init__(self):
        self.noise = PerlinNoise(
            octaves=Config.TERRAIN_OCTAVES,
            seed=random.randint(1, 100000)
        )
        self.offset = Config.WORLD_SIZE // 2
    
    def get_height(self, x, z):
        """Get terrain height at specified coordinates"""
        noise_value = self.noise([x * Config.TERRAIN_SCALE, z * Config.TERRAIN_SCALE])
        return floor(noise_value * Config.TERRAIN_AMPLITUDE)
    
    def generate_world(self):
        """Generate the entire world"""
        print(f"Generating {Config.WORLD_SIZE}x{Config.WORLD_SIZE} world...")
        blocks = []
        
        for z in range(Config.WORLD_SIZE):
            for x in range(Config.WORLD_SIZE):
                cx = x - self.offset
                cz = z - self.offset
                
                y = self.get_height(cx, cz)
                
                # Generate grass layer
                blocks.append(Voxel(position=(cx, y, cz), block_type=BlockType.GRASS))
                
                # Generate dirt layers (2 layers)
                for i in range(1, 3):
                    blocks.append(Voxel(position=(cx, y - i, cz), block_type=BlockType.DIRT))
                
                # Generate stone layers (3 layers)
                for i in range(3, 6):
                    blocks.append(Voxel(position=(cx, y - i, cz), block_type=BlockType.STONE))
                
                # Randomly generate trees
                if random.random() < 0.02 and y > 0:
                    self.generate_tree(cx, y + 1, cz, blocks)
        
        print(f"World generation complete! Total blocks: {len(blocks)}")
        return blocks
    
    def generate_tree(self, x, y, z, blocks):
        """Generate a tree"""
        tree_height = random.randint(4, 6)
        
        # Tree trunk
        for i in range(tree_height):
            blocks.append(Voxel(position=(x, y + i, z), block_type=BlockType.WOOD))
        
        # Leaves (simple sphere shape)
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

# ==================== Game Manager ====================
class GameManager:
    def __init__(self):
        self.current_block = BlockType.GRASS
        self.blocks = []
        self.hand = None
        self.ui = None
        
    def place_block(self, position):
        """Place a block"""
        # Boundary check
        if abs(position.x) >= Config.WORLD_SIZE or abs(position.z) >= Config.WORLD_SIZE:
            return
        
        # Cannot place at player position
        if distance(position, player.position) < 1.5:
            return
        
        # Create block
        new_block = Voxel(position=position, block_type=self.current_block)
        self.blocks.append(new_block)
        self.hand.swing()
        
        # Print to console instead of UI
        print(f"Placed {BLOCKS[self.current_block]['name']}")
    
    def break_block(self, block):
        """Break a block"""
        if not BLOCKS[block.block_type]['breakable']:
            print(f"{BLOCKS[block.block_type]['name']} cannot be destroyed!")
            return
        
        self.hand.swing()
        if block in self.blocks:
            self.blocks.remove(block)
        destroy(block)
        print(f"Broke {BLOCKS[block.block_type]['name']}")
    
    def select_block(self, block_type):
        """Select block type"""
        if block_type in BLOCKS:
            self.current_block = block_type
            self.ui.update_selection()
            self.hand.color = BLOCKS[block_type]['color']
            print(f"Selected: {BLOCKS[block_type]['name']}")

# ==================== Player Hand ====================
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            # ========== 修改开始：修复手臂显示 ==========
            texture=None,          # 1. 不要纹理
            shader=unlit_shader,   # 2. 强制无光照着色器
            # =========================================
            color=BLOCKS[BlockType.GRASS]['color'],
            scale=(0.2, 0.2, 0.8),
            position=(0.4, -0.4, 0.8),
            rotation=(10, -10, 0)
        )
    
    def swing(self):
        """Hand swing animation"""
        self.animate_rotation((30, -20, 0), duration=0.1)
        self.animate_rotation((10, -10, 0), duration=0.1, delay=0.1)

# ==================== Game UI ====================
class GameUI:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.hotbar_slots = []
        self.selection_indicator = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI - Pure graphical, no text"""
        # Crosshair
        Entity(
            parent=camera.ui,
            model='quad',
            scale=0.015,
            color=color.white
        )
        
        # Hotbar
        block_types = [
            BlockType.GRASS,
            BlockType.STONE,
            BlockType.DIRT,
            BlockType.WOOD,
            BlockType.SAND
        ]
        
        for i, block_type in enumerate(block_types):
            # Slot background
            slot = Entity(
                parent=camera.ui,
                model='quad',
                color=color.rgb(60, 60, 60),
                position=(-0.25 + i * 0.13, -0.45),
                scale=(0.1, 0.1)
            )
            
            # Block preview (3D cube)
            preview = Entity(
                parent=slot,
                model='cube',
                # ========== 修改开始：修复UI图标显示 ==========
                texture=None,          # 1. 不要纹理
                shader=unlit_shader,   # 2. 强制无光照着色器
                # ==========================================
                color=BLOCKS[block_type]['color'],
                scale=0.5,
                rotation=(20, 20, 0)
            )
            
            self.hotbar_slots.append({
                'slot': slot,
                'preview': preview,
                'block_type': block_type
            })
        
        # Selection indicator (yellow border)
        self.selection_indicator = Entity(
            parent=camera.ui,
            model='quad',
            color=color.yellow,
            scale=(0.12, 0.12),
            position=self.hotbar_slots[0]['slot'].position,
            z=-0.01
        )
        
        # Inner dark square to create border effect
        Entity(
            parent=self.selection_indicator,
            model='quad',
            color=color.rgb(60, 60, 60),
            scale=0.85,
            z=0.01
        )
    
    def update_selection(self):
        """Update selection indicator position"""
        for i, slot_info in enumerate(self.hotbar_slots):
            if slot_info['block_type'] == self.game_manager.current_block:
                self.selection_indicator.position = slot_info['slot'].position
                slot_info['slot'].color = color.rgb(100, 100, 100)
            else:
                slot_info['slot'].color = color.rgb(60, 60, 60)

# ==================== Initialize Game ====================
# Create game manager
game_manager = GameManager()

# Generate terrain
terrain_gen = TerrainGenerator()
game_manager.blocks = terrain_gen.generate_world()

# Create player
player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0.5
player.speed = Config.WALK_SPEED
player.height = Config.STEVE_HEIGHT
player.jump_height = Config.JUMP_HEIGHT
player.camera_pivot.y = Config.EYE_HEIGHT - (Config.STEVE_HEIGHT / 2)
player.position = (0, 50, 0)

# Create hand
game_manager.hand = Hand()

# Create UI
game_manager.ui = GameUI(game_manager)

# Setup environment
# Setup environment
# sky = Sky()  <-- 必须删掉/注释
scene.fog_density = 0  # <-- 必须设置为 0，防止远处的白色雾遮挡
scene.fog_color = color.white # 即使有雾也是白的，容易误导，干脆不管它
window.color = color.rgb(135, 206, 235)

# ==================== Input Handling ====================
def input(key):
    """Global input handling"""
    # Number keys to select blocks
    if key in '12345':
        index = int(key) - 1
        if index < len(game_manager.ui.hotbar_slots):
            block_type = game_manager.ui.hotbar_slots[index]['block_type']
            game_manager.select_block(block_type)
    
    # Mouse wheel to switch blocks
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
    
    # ESC to quit
    elif key == 'escape':
        application.quit()
    
    # F3 for debug info
    elif key == 'f3':
        print(f"\n=== Debug Info ===")
        print(f"Player Position: {player.position}")
        print(f"Current Block: {BLOCKS[game_manager.current_block]['name']}")
        print(f"Total Blocks: {len(game_manager.blocks)}")
        print(f"==================\n")

# ==================== Game Loop ====================
time_passed = 0

def update():
    """Update every frame"""
    global time_passed
    time_passed += time.dt
    
    # Player respawn if fallen out of world
    if player.y < -30:
        player.position = (0, 15, 0)
        player.velocity = Vec3(0, 0, 0)
        print("Respawned!")
    
    # Simple day/night cycle
    cycle_speed = 0.02
    brightness = (math.sin(time_passed * cycle_speed) + 1) / 2 * 0.5 + 0.5
    # window.color = ...  <--- 这一行删掉，改成下面这行：
    window.color = color.rgb(135, 206, 235)


# Run game
print("\n" + "="*50)
print("    MINECRAFT-STYLE GAME")
print("="*50)
print("\nCONTROLS:")
print("  WASD       - Move")
print("  Space      - Jump")
print("  Mouse      - Look around")
print("  Left Click - Break block")
print("  Right Click- Place block")
print("  1-5        - Select block type")
print("  Scroll     - Switch block type")
print("  F3         - Debug info")
print("  ESC        - Quit game")
print("\nBLOCK TYPES:")
print("  1 = Grass (green)")
print("  2 = Stone (gray)")
print("  3 = Dirt (brown)")
print("  4 = Wood (wood color)")
print("  5 = Sand (yellow)")
print("\nNOTE: Block selection feedback in console")
print("="*50 + "\n")

app.run()