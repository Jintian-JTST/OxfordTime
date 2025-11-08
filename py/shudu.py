# sudoku50.py
# 目标：生成 9x9 数独题，恰好 50 个空格，且唯一解，打印“非常美观”的网格。
# 纯 Python，无第三方依赖；默认对称挖空（180° 旋转对称），一般机器 ~1s 内完成。

from __future__ import annotations
import random, time
from typing import List, Tuple, Optional

ALL_BITS = 0b1111111110  # 使用 bit1..bit9（忽略 bit0）
DIGITS = range(1, 10)

def box_id(i: int) -> int:
    r, c = divmod(i, 9)
    return (r // 3) * 3 + (c // 3)

def sym_idx(i: int) -> int:
    r, c = divmod(i, 9)
    rr, cc = 8 - r, 8 - c
    return rr * 9 + cc

def iter_bits(mask: int):
    m = mask
    while m:
        b = m & -m
        yield b.bit_length() - 1  # bit1->1, ..., bit9->9
        m ^= b

class Board:
    __slots__ = ("cells", "row", "col", "box")

    def __init__(self):
        self.cells = [0] * 81
        self.row = [0] * 9
        self.col = [0] * 9
        self.box = [0] * 9

    def copy(self) -> "Board":
        b = Board()
        b.cells = self.cells[:]
        b.row = self.row[:]
        b.col = self.col[:]
        b.box = self.box[:]
        return b

    def place(self, i: int, d: int):
        r, c = divmod(i, 9)
        bit = 1 << d
        self.cells[i] = d
        self.row[r] |= bit
        self.col[c] |= bit
        self.box[box_id(i)] |= bit

    def remove(self, i: int, d: int):
        r, c = divmod(i, 9)
        bit = ~(1 << d)
        self.cells[i] = 0
        self.row[r] &= bit
        self.col[c] &= bit
        self.box[box_id(i)] &= bit

    def can_mask(self, i: int) -> int:
        r, c = divmod(i, 9)
        used = self.row[r] | self.col[c] | self.box[box_id(i)]
        return (~used) & ALL_BITS

    def blanks(self) -> int:
        return self.cells.count(0)

    def is_full(self) -> bool:
        return 0 not in self.cells

# —— 求解器（计数到 2 就停，用于唯一性校验）——
def count_solutions(bd: Board, limit: int = 2) -> int:
    cells, row, col, box = bd.cells, bd.row, bd.col, bd.box
    count = 0

    def select_mrv() -> Tuple[int, int]:
        best_i, best_mask, best_cnt = -1, 0, 10
        for i, v in enumerate(cells):
            if v == 0:
                mask = (~(row[i//9] | col[i%9] | box[box_id(i)])) & ALL_BITS
                cnt = mask.bit_count()
                if cnt == 0:
                    return -2, 0  # 无解剪枝
                if cnt < best_cnt:
                    best_i, best_mask, best_cnt = i, mask, cnt
                    if cnt == 1:
                        break
        return best_i, best_mask  # 若 best_i==-1 则盘面已满

    def dfs():
        nonlocal count
        if count >= limit:
            return
        i, mask = select_mrv()
        if i == -2:
            return                # 死路
        if i == -1:
            count += 1            # 找到一解
            return
        r, c, bi = i//9, i%9, box_id(i)
        for d in iter_bits(mask):  # 固定升序，便于尽快发现第二解
            bit = 1 << d
            cells[i] = d
            row[r] |= bit; col[c] |= bit; box[bi] |= bit
            dfs()
            if count >= limit:
                # 回溯前先撤销
                row[r] &= ~bit; col[c] &= ~bit; box[bi] &= ~bit
                cells[i] = 0
                return
            row[r] &= ~bit; col[c] &= ~bit; box[bi] &= ~bit
            cells[i] = 0

    dfs()
    return count

# —— 随机完整解生成（MRV + 随机尝试）——
def _solve_fill_random(bd: Board, rnd: random.Random) -> bool:
    if bd.is_full():
        return True
    # MRV 选点
    best_i, best_mask, best_cnt = -1, 0, 10
    for i, v in enumerate(bd.cells):
        if v == 0:
            mask = bd.can_mask(i)
            cnt = mask.bit_count()
            if cnt == 0:
                return False
            if cnt < best_cnt:
                best_i, best_mask, best_cnt = i, mask, cnt
                if cnt == 1:
                    break
    cand = list(iter_bits(best_mask))
    rnd.shuffle(cand)
    for d in cand:
        bd.place(best_i, d)
        if _solve_fill_random(bd, rnd):
            return True
        bd.remove(best_i, d)
    return False

def generate_full_solution(seed: Optional[int]) -> Board:
    rnd = random.Random(seed)
    b = Board()
    # 每行随机“破冰”一个格子以加速
    for r in range(9):
        i = r * 9 + rnd.randrange(9)
        mask = b.can_mask(i)
        if mask:
            d = rnd.choice(list(iter_bits(mask)))
            b.place(i, d)
    # 回溯填满
    if not _solve_fill_random(b, rnd):
        # 极小概率失败，换种子重来
        return generate_full_solution(rnd.randrange(1 << 30))
    return b

# —— 生成恰好 50 空格的对称题（唯一解）——
def make_puzzle_50(seed: Optional[int] = None, timeout: float = 1.0) -> Tuple[Board, Board]:
    t0 = time.perf_counter()
    rnd = random.Random(seed)

    target_blanks = 50
    pairs_template = [(i, sym_idx(i)) for i in range(81) if i < sym_idx(i)]  # 40 对
    # 50 是偶数，无需考虑中心格

    while time.perf_counter() - t0 <= timeout:
        sol = generate_full_solution(rnd.randrange(1 << 30))
        puzzle = sol.copy()

        blanks = 0
        pairs = pairs_template[:]
        rnd.shuffle(pairs)

        # 逐对尝试挖空，验证唯一性，直到达到 25 对（即 50 空）
        for (a, b) in pairs:
            if blanks >= target_blanks or time.perf_counter() - t0 > timeout:
                break
            if puzzle.cells[a] == 0 or puzzle.cells[b] == 0:
                continue
            if blanks + 2 > target_blanks:
                continue

            da, db = puzzle.cells[a], puzzle.cells[b]
            puzzle.remove(a, da); puzzle.remove(b, db)

            # 唯一性校验（找到第 2 个解就停）
            if count_solutions(puzzle.copy(), limit=2) == 1:
                blanks += 2
            else:
                # 回滚
                puzzle.place(a, da); puzzle.place(b, db)

            if blanks == target_blanks:
                return puzzle, sol

        # 若本轮没凑够 50 空，换一个完整解重试（仍在总超时内）
    raise RuntimeError("未能在设定超时内生成 50 空且唯一解的题目。可适当提高 timeout 或更换 seed。")

# —— 漂亮的网格渲染（Unicode 边框）——
TOP    = "┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓"
MID    = "┠───┼───┼───╂───┼───┼───╂───┼───┼───┨"
BOX    = "┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫"
BOTTOM = "┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛"

def render_grid(b: Board, title: str) -> str:
    lines = [title, TOP]
    for r in range(9):
        row = ["┃"]
        for c in range(9):
            v = b.cells[r*9 + c]
            ch = str(v) if v else "·"
            sep = "┃" if c in (2, 5) else "│"
            row.append(f" {ch} ")
            row.append(sep)
        row[-1] = "┃"  # 最后一个分隔符替换为边框
        lines.append("".join(row))
        if r == 8:
            lines.append(BOTTOM)
        elif r in (2, 5):
            lines.append(BOX)
        else:
            lines.append(MID)
    return "\n".join(lines)

# —— CLI 演示 —— 
if __name__ == "__main__":
    seed = 20251108     # 可改，便于复现
    timeout = 1.0       # 若机器较慢，可设为 1.5~2.0
    t0 = time.perf_counter()
    puzzle, solution = make_puzzle_50(seed=seed, timeout=timeout)
    used = time.perf_counter() - t0

    print(render_grid(puzzle, "题目（恰好 50 空・唯一解）"))
    print()
    print(render_grid(solution, "解"))
    print(f"\n生成用时：{used*1000:.1f} ms（超时阈值 {timeout:.1f} s）")
