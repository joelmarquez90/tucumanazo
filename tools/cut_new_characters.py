#!/usr/bin/env python3
"""
cut_new_characters.py — Extrae sprites de assets/new-characters.png.

Row 0: 6 frames player (facing right — correct)
Row 1: 6 frames enemy  (facing right — flip to face left)
Row 2: 4 effect frames (impact stars)
"""
from PIL import Image
import numpy as np
import os

# Frame boundaries measured per row (via alpha gap analysis)
# Row 0 — player (auto-detected from gap analysis):
PLAYER_X_RANGES = [
    (67, 312),    # 0: idle
    (372, 663),   # 1: approach
    (710, 1009),  # 2: windup2 (pre-charge)
    (1041, 1456), # 3: windup  (lunge)
    (1463, 1771), # 4: impact1
    (1829, 2075), # 5: (skip — duplicate idle)
]
PLAYER_NAMES = ['idle_player', 'approach_player', 'windup2_player',
                'windup_player', 'impact1_player', None]

# Row 1 — enemy (frames 0-2 auto, 3-5 split from large block x=956..2075):
# KO frame detected at x=1346..2075 in y=1300..1530 (lying down, bottom of row)
ENEMY_X_RANGES = [
    (71, 310),    # 0: walk/approach
    (378, 598),   # 1: idle ready
    (658, 936),   # 2: first hit reaction
    (956, 1245),  # 3: blood (hands on face)  ← manual split
    (1245, 1680), # 4: stagger                ← manual split
    (1340, 2128), # 5: KO lying down — starts at 1340 (detected via alpha scan)
]
ENEMY_NAMES = ['approach_enemy', 'idle_enemy', 'blood_enemy',
               'stagger_enemy', 'stagger2_enemy', 'ko_enemy']

# KO frame uses a narrower y range to avoid overlap with stagger2 (standing)
ENEMY_KO_Y = (1300, 1530)

# Row 2 — effects (auto-detected):
EFFECT_X_RANGES = [
    (150, 258),   # 0: small spark
    (403, 671),   # 1: big star + blood
    (758, 1015),  # 2: dispersing
    (1171, 1265), # 3: blood drops
]
EFFECT_NAMES = ['star_0', 'star_1', 'star_2', 'star_3']

ROW_Y_RANGES = {
    'player': (77, 702),
    'enemy':  (905, 1530),
    'effects': (1638, 1914),
}

def tight_crop(arr):
    alpha = arr[:, :, 3]
    rows = np.any(alpha > 30, axis=1)
    cols = np.any(alpha > 30, axis=0)
    if not rows.any():
        return arr
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return arr[rmin:rmax+1, cmin:cmax+1]

def save(arr, path):
    Image.fromarray(arr, 'RGBA').save(path)
    h, w = arr.shape[:2]
    print(f'  → {path} ({w}×{h}px)')

img = Image.open('assets/new-characters.png').convert('RGBA')
arr = np.array(img)
os.makedirs('assets/sprites', exist_ok=True)

# Player frames (no flip)
y0, y1 = ROW_Y_RANGES['player']
for (x0, x1), name in zip(PLAYER_X_RANGES, PLAYER_NAMES):
    if name is None:
        continue
    cell = arr[y0:y1, x0:x1].copy()
    save(tight_crop(cell), f'assets/sprites/{name}.png')

# Enemy frames (flip horizontally so they face LEFT)
y0, y1 = ROW_Y_RANGES['enemy']
for i, ((x0, x1), name) in enumerate(zip(ENEMY_X_RANGES, ENEMY_NAMES)):
    is_ko = i == len(ENEMY_X_RANGES) - 1
    ey0, ey1 = ENEMY_KO_Y if is_ko else (y0, y1)
    cell = arr[ey0:ey1, x0:x1].copy()
    flipped = np.fliplr(cell)
    cropped = tight_crop(flipped)
    if is_ko:
        # Trim the right side where stagger2 body bleeds in (starts at x=534)
        cropped = cropped[:, :534]
    save(cropped, f'assets/sprites/{name}.png')

# Effect frames (no flip)
y0, y1 = ROW_Y_RANGES['effects']
for (x0, x1), name in zip(EFFECT_X_RANGES, EFFECT_NAMES):
    cell = arr[y0:y1, x0:x1].copy()
    save(tight_crop(cell), f'assets/sprites/{name}.png')

print('\nListo.')
