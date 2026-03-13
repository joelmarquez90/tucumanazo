#!/usr/bin/env python3
"""
cut_sprites.py — Recorta sprites individuales del tucumanazo sprite sheet.

Uso: cd /Users/joel/workspace/tucumanazo && python3 tools/cut_sprites.py

Output:
  assets/sprites/{idle,approach,windup,impact1,blood,stagger,ko}_player.png  (mitad izquierda)
  assets/sprites/{idle,approach,windup,impact1,blood,stagger,ko}_enemy.png   (mitad derecha)
"""
from PIL import Image
import numpy as np
import os

# Mapa de celdas: (col, row) → nombre
CELL_NAMES = {
    (0, 0): 'idle',
    (1, 0): 'approach',
    (2, 0): 'windup',
    (3, 0): 'impact1',
    (0, 1): 'blood',
    (1, 1): 'stagger',
    (2, 1): 'ko',
    (3, 1): 'walk',   # se divide en walk_a y walk_b
}

def chroma_key(arr):
    r = arr[..., 0].astype(int)
    g = arr[..., 1].astype(int)
    b = arr[..., 2].astype(int)
    mask = (g > 100) & (g > r * 1.2) & (g > b * 1.2)
    out = arr.copy()
    out[mask, 3] = 0
    return out

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
    print(f"  → {path} ({w}×{h}px)")

img = Image.open('assets/sprites.png').convert('RGBA')
arr = np.array(img)
H, W = arr.shape[:2]
COLS, ROWS = 4, 2
cell_w, cell_h = W // COLS, H // ROWS

print(f"Sheet: {W}×{H}px, cells: {cell_w}×{cell_h}px")
os.makedirs('assets/sprites', exist_ok=True)

for (col, row), name in CELL_NAMES.items():
    x0, y0 = col * cell_w, row * cell_h
    cell = arr[y0:y0+cell_h, x0:x0+cell_w].copy()
    cell = chroma_key(cell)

    if name == 'walk':
        # legacy — no longer used, skip
        pass
    else:
        # Split cada celda en mitad izquierda (player) y mitad derecha (enemy)
        mid = cell_w // 2
        for suffix, sx in [('player', 0), ('enemy', mid)]:
            half = cell[:, sx:sx+mid]
            half = tight_crop(half)
            save(half, f'assets/sprites/{name}_{suffix}.png')

print("\nListo. Sprites guardados en assets/sprites/")
