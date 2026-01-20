from ursina import *
from ursina.shaders import unlit_shader  # 引入无光照着色器

app = Ursina()

# 1. 设置背景为红色，测试背景渲染
window.color = color.red

# 2. 创建一个绿色方块，强制使用无光照着色器，不使用纹理
cube = Entity(
    model='cube',
    color=color.green,
    scale=2,
    texture=None,            # 绝对不要纹理
    shader=unlit_shader      # 强制指定着色器
)

print("正在运行测试...")
app.run()