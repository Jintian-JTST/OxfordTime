import pygame
import numpy as np
import math
import sys

# 初始化 pygame（SDL2 → D3D11）
pygame.init()

WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE
)
pygame.display.set_caption("DX11 GPU Stress (Intel Arc / iGPU)")

clock = pygame.time.Clock()

# ====== 负载参数（核心） ======
NUM_RECTS = 400_000   # 先用 40k，后面可以加
RECT_SIZE = 6

# 生成大量物体
positions = np.random.rand(NUM_RECTS, 2)
velocities = (np.random.rand(NUM_RECTS, 2) - 0.5) * 2.0
colors = np.random.randint(50, 255, size=(NUM_RECTS, 3))

print("DX11 GPU stress running. Ctrl+C or close window to stop.")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新位置
    positions += velocities * 0.5
    positions %= 1.0

    screen.fill((0, 0, 0))

    # 大量 draw call（SDL2 → Direct3D 11）
    for i in range(NUM_RECTS):
        x = int(positions[i, 0] * WIDTH)
        y = int(positions[i, 1] * HEIGHT)
        pygame.draw.rect(
            screen,
            colors[i],
            (x, y, RECT_SIZE, RECT_SIZE)
        )

    pygame.display.flip()
    clock.tick(0)  # 不限帧率 → 拉满 GPU

pygame.quit()
sys.exit()
